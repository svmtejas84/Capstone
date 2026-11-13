"""Train four same-information neural baselines using the v3 cell runner.

This starts only after the five-variant matched regularizer matrix. MLP and TCN
saved v2m fits are audited separately; no historical results are overwritten.
"""
import argparse
import json
import torch
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext, ARR, FIT, V3
from final_blr_results.controlled_validation_v3.scripts.train_controls import (
    BASE_CFG,HORIZONS,SEEDS,LRS,train_cell,atomic_json)

MODELS=["gru_only","vanilla_gcn","st_gru_gcn","adaptive_graph_st"]


class BaselineContext(CutoffContext):
    def __init__(self,model_name,horizon):
        self.model_name=model_name
        super().__init__(horizon,BASE_CFG,ARR,FIT)

    def make(self,name):
        return super().make(self.model_name)

    def forward(self,model,name,x,anchor,wind):
        return super().forward(model,self.model_name,x,anchor,wind)


def main():
    p=argparse.ArgumentParser();p.add_argument("--stage",choices=["selection","final"],required=True)
    args=p.parse_args()
    assert torch.cuda.is_available()
    root=V3/"training/baselines";root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name in MODELS:
        for h in HORIZONS:
            ctx=BaselineContext(name,h)
            if args.stage=="selection":
                cells=[(lr,11) for lr in LRS]
            else:
                candidates=[json.loads((root/name/"selection"/f"h{h}_lr{lr:g}"/"COMPLETE.json").read_text()) for lr in LRS]
                lr=min(candidates,key=lambda r:(r["validation_mae"],r["learning_rate"]))["learning_rate"]
                cells=[(lr,s) for s in SEEDS]
            for lr,seed in cells:
                sub=(f"h{h}_lr{lr:g}" if args.stage=="selection" else f"h{h}_seed{seed}")
                out=root/name/args.stage/sub
                result=train_cell(ctx,"zero",lr,seed,out,select=args.stage=="selection")
                result=dict(result,baseline_model=name)
                atomic_json(out/"model_identity.json",dict(model=name,horizon=h,seed=seed,lr=lr,
                         input_protocol="v2m timestamp-causal historical observations",architecture_source="src/stpignn/models_v2.py or models_v3.py"))
                rows.append(result);print(json.dumps(result),flush=True)
    atomic_json(root/f"{args.stage}_summary.json",rows)
    (root/f"{args.stage}_COMPLETE").write_text("COMPLETE\n")


if __name__=="__main__":main()
