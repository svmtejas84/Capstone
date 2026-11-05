"""Essential synthetic CPU checks; training requires CUDA."""
import torch

from final_blr_results.baselines.v2m.reproducibility.train_v2m import MLP, TCN


def check(model):
    x = torch.randn(2, 12, 3, 18, requires_grad=True)
    y = model(x)
    assert y.shape == (2, 3) and torch.isfinite(y).all()
    (y ** 2).mean().backward()
    assert torch.isfinite(x.grad).all()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    with torch.no_grad():
        changed = x.detach().clone()
        changed[:, :, 2, :] += 100
        assert torch.allclose(model(x.detach())[:, :2], model(changed)[:, :2], atol=1e-5)


def test_causality():
    m = TCN()
    x = torch.randn(2, 12, 3, 18)
    a = m.representations(x)
    changed = x.clone()
    changed[:, 8:, :, :] += 100
    b = m.representations(changed)
    assert torch.allclose(a[..., :8], b[..., :8], atol=1e-5)


if __name__ == "__main__":
    check(MLP())
    check(TCN())
    test_causality()
    print("MLP/TCN shape, finite gradient, station independence, temporal causality passed")
