"""Numerical audit charts from saved V4 CSVs; no new model computation."""
from pathlib import Path
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('final_blr_results/controlled_validation_v4_review_closure')
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150,'savefig.dpi':300})
def save(fig,name):
 for ext in ['png','pdf','svg']:fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight')
 plt.close(fig)

r=pd.read_csv(ROOT/'COMPLETE_MODEL_AND_BASELINE_REGISTER.csv')
methods=['zero','true_wind','shuffled_wind','rotated_wind','laplacian','gru_only','tcn','mlp','adaptive_graph_st','persistence','same_hour_yesterday','weather_ridge','climatology_hod_dow','station_train_mean','vanilla_gcn','st_gru_gcn']
p=r.pivot(index='method',columns='horizon_hours',values='mae_ug_m3').loc[methods]
fig,ax=plt.subplots(figsize=(8.5,6.1));im=ax.imshow(p.values,aspect='auto',cmap='viridis_r',vmin=8,vmax=22)
ax.set_yticks(range(len(p)),[x.replace('_',' ') for x in p.index]);ax.set_xticks(range(len(p.columns)),[f'{h} h' for h in p.columns]);ax.set_xlabel('Forecast horizon');ax.set_title('V3 matched-population MAE, 14,583 pairs per horizon (exposed test)')
for i in range(len(p)):
 for j in range(len(p.columns)):ax.text(j,i,f'{p.values[i,j]:.2f}',ha='center',va='center',fontsize=8,color='white' if p.values[i,j]<12 or p.values[i,j]>19 else 'black')
fig.colorbar(im,ax=ax,label='MAE (µg/m³)');save(fig,'F1_complete_baseline_mae')

q=pd.read_csv(ROOT/'statistical_analysis/GRAPH_ARCHITECTURE_CONTRASTS.csv');fig,ax=plt.subplots(figsize=(8.5,4.2))
labels=[];x=[];low=[];high=[]
for _,row in q.iterrows():labels.append(f"{int(row.horizon_hours)}h vs {row.contrast.split('_minus_')[-1].replace('_',' ')}");x.append(row.paired_delta_mae_ug_m3);low.append(row.ci95_low_ug_m3);high.append(row.ci95_high_ug_m3)
y=np.arange(len(x));ax.errorbar(x,y,xerr=[np.array(x)-low,np.array(high)-x],fmt='o',color='#1f77b4',ecolor='#4c4c4c',capsize=2);ax.axvline(0,color='black',lw=.8);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlabel('Unregularized GINEConv–GRU minus comparator MAE (µg/m³)');ax.set_title('Architecture contrasts; seven-day moving-block intervals');save(fig,'F2_graph_architecture_contrasts')

q=pd.read_csv(ROOT/'COMPLETE_20_CONTRAST_RESULTS.csv');fig,ax=plt.subplots(figsize=(8.5,5.5))
labels=[f"{int(row.horizon_hours)}h vs {row.contrast.split('minus_')[-1].replace('_',' ')}" for _,row in q.iterrows()]
x=q.paired_delta_mae_ug_m3.to_numpy();lo=q.ci95_low_ug_m3.to_numpy();hi=q.ci95_high_ug_m3.to_numpy();y=np.arange(len(q))
ax.errorbar(x,y,xerr=[x-lo,hi-x],fmt='o',color='#c44e52',ecolor='#4c4c4c',capsize=2);ax.axvline(0,color='black',lw=.8);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlabel('True wind minus comparator MAE (µg/m³)');ax.set_title('Frozen 20 directional contrasts; exposed test');save(fig,'F3_directional_contrasts')

q=pd.read_csv(ROOT/'ANCHOR_AGE_AND_ERROR.csv');buckets=['1h','2-3h','4-6h','7-12h','13-24h','>24h','none'];p=q.pivot(index='horizon_hours',columns='anchor_age_bucket',values='fraction')[buckets]
fig,ax=plt.subplots(figsize=(7.5,3.8));bottom=np.zeros(len(p))
colors=plt.cm.tab20.colors
for i,col in enumerate(p.columns):ax.bar([str(h)+' h' for h in p.index],p[col],bottom=bottom,label=col,color=colors[i]);bottom+=p[col].values
ax.set_ylim(0,1);ax.set_ylabel('Fraction of scored targets');ax.set_xlabel('Forecast horizon');ax.set_title('Age of latest genuinely observed PM2.5 at issue time');ax.legend(ncol=4,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.2));save(fig,'F4_anchor_age')

if (ROOT/'statistical_analysis/V4_SIX_CONTRASTS.csv').exists():
 q=pd.read_csv(ROOT/'statistical_analysis/V4_SIX_CONTRASTS.csv');fig,ax=plt.subplots(figsize=(8,3.3));x=q.paired_delta_mae_ug_m3.to_numpy();lo=q.ci95_low_ug_m3.to_numpy();hi=q.ci95_high_ug_m3.to_numpy();y=np.arange(len(q));labels=q.contrast.str.replace('true_wind_006_minus_','',regex=False).str.replace('_',' ',regex=False)
 ax.errorbar(x,y,xerr=[x-lo,hi-x],fmt='o',color='#4c72b0',capsize=3);ax.axvline(0,color='black',lw=.8);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlabel('True-wind 0.06 minus new control MAE (µg/m³)');ax.set_title('Six-hour V4 sensitivity; exposed test');save(fig,'F5_v4_sensitivity')
print('figures',len(list(OUT.glob('*.png'))))
