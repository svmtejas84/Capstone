"""One training batch per same-information baseline; no optimizer update."""
import json
import torch
from final_blr_results.controlled_validation_v3.scripts.train_baselines import BaselineContext,MODELS
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,BASE_CFG

def main():
    assert torch.cuda.is_available()
    rows=[]
    for name in MODELS:
        ctx=BaselineContext(name,6)
        index,x,y,mask,anchor,wind=next(ctx.batches("train"))
        model=ctx.make("stpignn_lambda0")
        z=ctx.forward(model,"stpignn_lambda0",x,anchor,wind)
        target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
        loss=((z-target).square()*mask).sum()/mask.sum().clamp_min(1)
        assert bool(torch.isfinite(loss))
        loss.backward()
        assert all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in model.parameters())
        rows.append(dict(model=name,batch=list(x.shape),parameters=sum(p.numel() for p in model.parameters()),
                         observed=int(mask.sum()),loss=float(loss.detach()),finite_gradients=True))
    p=V3/"verification/baseline_smoke.json";p.write_text(json.dumps(rows,indent=2)+"\n")
    print(json.dumps(rows,indent=2))

if __name__=="__main__":main()
