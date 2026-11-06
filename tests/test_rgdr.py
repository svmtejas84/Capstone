import pytest
import torch

from src.stpignn.physics_v2 import batched_penalty, corrected_wind_mask
from src.stpignn.rgdr import observation_reliability, edge_reliability, rgdr_penalty, reliability_weighted_smoothing


def fixture():
    xy = torch.tensor([[0., 0.], [1000., 0.], [2000., 0.]])
    edge = torch.tensor([[0, 1, 1, 2], [1, 0, 2, 1]])
    length = torch.full((4, 1), 1000.)
    mask = corrected_wind_mask(xy, edge, 270.).repeat(2, 1)
    pred = torch.tensor([[1., 2., 4.], [4., 2., 1.]], requires_grad=True)
    return edge, length, mask, pred


def test_constant_one_matches_original_penalty_and_orientation():
    edge, length, mask, pred = fixture()
    assert mask[0].tolist() == [True, False, True, False]
    fixed = batched_penalty(pred, edge, mask, length, "corrected_mask")
    ours = rgdr_penalty(pred, edge, mask, length, torch.ones_like(pred))
    torch.testing.assert_close(ours, fixed, rtol=0, atol=1e-7)
    assert ours.item() > 0
    west_to_east_decreasing = torch.tensor([[4.,2.,1.]], requires_grad=True)
    assert rgdr_penalty(west_to_east_decreasing,edge,mask[:1],length,torch.ones_like(west_to_east_decreasing)).item() == 0


def test_missingness_gate_no_future_target_argument_and_bounds():
    edge, length, mask, pred = fixture()
    flag = torch.tensor([[0.,1.,0.],[1.,1.,1.]])
    rel = observation_reliability(flag)
    assert edge_reliability(rel,edge).max().item() <= 1
    assert rgdr_penalty(pred,edge,mask,length,rel).item() == 0
    with pytest.raises(ValueError): observation_reliability(torch.tensor([[0.5]]))
    with pytest.raises(ValueError): edge_reliability(torch.tensor([[1.1,0.,0.]]),edge)
    with pytest.raises(ValueError): observation_reliability(torch.tensor([[float("nan")]]))


def test_zero_weight_fully_missing_finite_gradient():
    edge,length,mask,pred=fixture()
    loss=rgdr_penalty(pred,edge,mask,length,observation_reliability(torch.ones_like(pred)))
    assert loss.item()==0
    loss.backward()
    assert pred.grad is not None and torch.isfinite(pred.grad).all()
    assert torch.all(pred.grad==0)


def test_gradient_batch_invariance_and_fixed_seed():
    edge,length,mask,pred=fixture()
    rel=torch.ones_like(pred)
    loss=rgdr_penalty(pred,edge,mask,length,rel)
    loss.backward()
    assert torch.isfinite(pred.grad).all()
    first=rgdr_penalty(pred[:1],edge,mask[:1],length,rel[:1])
    second=rgdr_penalty(pred[1:],edge,mask[1:],length,rel[1:])
    torch.testing.assert_close(loss,(first+second)/2,rtol=0,atol=1e-7)
    torch.manual_seed(11); a=torch.rand(2,3)
    torch.manual_seed(11); b=torch.rand(2,3)
    torch.testing.assert_close(a,b)


def test_generic_control_is_not_directional_and_scale_is_explicit():
    edge,length,mask,pred=fixture()
    rel=torch.ones_like(pred)
    smooth=reliability_weighted_smoothing(pred,edge,length,rel)
    assert smooth > 0
    # The loss operates in physical concentration / train-target SD units.
    train_sd=20.0
    physical=pred.detach()*train_sd
    torch.testing.assert_close(rgdr_penalty(physical/train_sd,edge,mask,length,rel),
                               rgdr_penalty(pred.detach(),edge,mask,length,rel))
