"""Training-only wind-control mask invariants, without model fitting or test scoring."""
import json
import numpy as np
import torch
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import BASE_CFG, wind_masks


def main():
    assert torch.cuda.is_available()
    c=CutoffContext(6,BASE_CFG,ARR,FIT)
    true=wind_masks(c,"true_wind")
    shuffled=wind_masks(c,"shuffled_wind")
    rotated=wind_masks(c,"rotated_wind")
    train=np.unique(c.hours["train"]-6)
    assert true.shape==shuffled.shape==rotated.shape
    month=c.times.year.to_numpy()*12+c.times.month.to_numpy()
    for key in np.unique(month):
        ix=np.flatnonzero(month==key)
        assert np.array_equal(np.sort(true[ix].sum(axis=1)),np.sort(shuffled[ix].sum(axis=1)))
    assert np.any(true[train]!=shuffled[train]) and np.any(true[train]!=rotated[train])
    assert np.array_equal(shuffled,wind_masks(c,"shuffled_wind"))
    result=dict(train_issue_hours=len(train),true_active=int(true[train].sum()),
                shuffled_active=int(shuffled[train].sum()),rotated_active=int(rotated[train].sum()),
                true_shuffled_different_fraction=float(np.mean(true[train]!=shuffled[train])),
                true_rotated_different_fraction=float(np.mean(true[train]!=rotated[train])),
                shuffle_deterministic=True,shuffle_preserves_monthly_active_arc_distribution=True,
                shuffle_uses_target_availability=False)
    p=V3/"verification/wind_controls.json";p.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
