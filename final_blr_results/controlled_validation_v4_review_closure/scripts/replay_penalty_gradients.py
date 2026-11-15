"""No optimizer step: replay first frozen training batch through saved selected checkpoints."""
import csv,json,hashlib
from pathlib import Path
import numpy as np,torch
from src.stpignn.physics_v2 import batched_penalty
from final_blr_results.controlled_validation_v3.scripts.train_controls import V3,ARR,FIT,BASE_CFG,hash_file
from final_blr_results.controlled_validation_v3.scripts.smoke_gpu import CutoffContext
from final_blr_results.controlled_validation_v4_review_closure.scripts.train_sensitivity import V4,VARIANTS,wind_masks

rows=[]
for h in [1,3,6,12,24]:
 ctx=CutoffContext(h,BASE_CFG,ARR,FIT)
 index,x,y,valid,anchor,wind=next(ctx.batches('train'))
 variants=['zero','true_wind','laplacian']+ (VARIANTS if h==6 else [])
 for v in variants:
  root=V4 if v in VARIANTS else V3
  ckpt=root/'training/final'/f'h{h}_seed11_{v}'/'best.pt'
  record=json.loads((ckpt.parent/'COMPLETE.json').read_text())
  assert hash_file(ckpt)==record['checkpoint_sha256']
  payload=torch.load(ckpt,map_location='cpu',weights_only=False)
  assert payload['array_sha256']==hash_file(ARR)
  model=ctx.make('stpignn_lambda0');model.load_state_dict(payload['state_dict'],strict=True)
  # cuDNN GRU backward is unavailable in eval mode. This enables autograd
  # without any optimizer or parameter update; the backbone has no dropout.
  model.train()
  z=ctx.forward(model,'stpignn_lambda0',x,anchor,wind)
  target=(torch.log1p(y.clamp_min(0))-ctx.mu)/ctx.sd
  data=((z-target).square()*valid).sum()/valid.sum().clamp_min(1)
  pm=torch.expm1(z*ctx.sd+ctx.mu)/ctx.physical_scale
  if v in ('laplacian','laplacian_matched'):
   mask=torch.ones((len(index),ctx.edge_index.shape[1]),device=ctx.device,dtype=torch.bool)
   raw=batched_penalty(pm,ctx.edge_index,mask,ctx.edge_distance,'laplacian')
  else:
   masks=ctx.corrected_wind_mask if v in ('zero','true_wind') else wind_masks(ctx,v)
   mask=torch.as_tensor(masks[index-h].copy(),device=ctx.device)
   raw=batched_penalty(pm,ctx.edge_index,mask,ctx.edge_distance,'corrected_mask')
  lam=float(record['effective_lambda_at_best'])
  ps=list(model.parameters())
  gd=torch.autograd.grad(data,ps,retain_graph=True,allow_unused=True)
  gr=torch.autograd.grad(raw,ps,allow_unused=True)
  dvec=torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for g,p in zip(gd,ps)])
  rvec=torch.cat([(g if g is not None else torch.zeros_like(p)).reshape(-1) for g,p in zip(gr,ps)])*lam
  dn=float(torch.linalg.vector_norm(dvec));rn=float(torch.linalg.vector_norm(rvec))
  cos=float(torch.dot(dvec,rvec)/(torch.linalg.vector_norm(dvec)*torch.linalg.vector_norm(rvec)+1e-20)) if rn else 0.
  rows.append(dict(horizon_hours=h,variant=v,seed=11,batch_target_start=int(index[0]),batch_target_end=int(index[-1]),batch_hours=len(index),observed_targets=int(valid.sum()),active_arcs=int(mask.sum()),raw_supervised_loss=float(data),raw_regularization_loss=float(raw),effective_lambda=lam,weighted_regularization_loss=float(lam*raw),supervised_gradient_norm=dn,weighted_penalty_gradient_norm=rn,gradient_ratio=rn/dn if dn else np.nan,gradient_cosine=cos,checkpoint_sha256=hash_file(ckpt)))
  print(h,v,'ratio',rn/dn if dn else np.nan,flush=True)
  del model,z,pm,data,raw,gd,gr,dvec,rvec
p=V4/'PENALTY_GRADIENT_REPLAY.csv'
with p.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
print(len(rows),p)
