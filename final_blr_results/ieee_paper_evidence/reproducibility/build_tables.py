from pathlib import Path
import pandas as pd
P=Path('final_blr_results/ieee_paper_evidence'); R=P/'results'; S=P/'figures/source_data'
# standard-format forecast table with clear protocol provenance
ens=pd.read_csv('final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv')
prim=pd.read_csv('final_blr_results/baselines/v2m/comparisons/primary_ten_comparisons.csv')
sec=pd.read_csv('final_blr_results/baselines/v2m/comparisons/secondary_comparisons.csv')
out=[]
for _,r in ens.iterrows():
 out.append({'protocol':'v2m summary table (historical ST-PIGNN rows retain v2j protocol)','record_type':'ensemble_or_historical_benchmark','horizon_hours':r.get('horizon_hours'),'model':r.get('model'),'comparison':r.get('aggregation'),'mae_ug_m3':r.get('mae'),'rmse_ug_m3':r.get('rmse'),'r2':r.get('r2'),'n_pairs':r.get('n_pairs'),'delta_mae_ug_m3':None,'ci_low':None,'ci_high':None,'raw_p':None,'holm_p':None,'source':'final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','verification':'saved summary; weather inputs differ by model generation'})
for _,r in prim.iterrows():
 out.append({'protocol':'v2m frozen ten primary comparisons; cross-protocol','record_type':'paired_holm_comparison','horizon_hours':r.get('horizon_hours'),'model':str(r.get('model'))+'_vs_'+str(r.get('baseline')),'comparison':r.get('comparison_type'),'mae_ug_m3':None,'rmse_ug_m3':None,'r2':None,'n_pairs':r.get('n_pairs'),'delta_mae_ug_m3':r.get('paired_mae_difference'),'ci_low':r.get('ci_low'),'ci_high':r.get('ci_high'),'raw_p':r.get('raw_sign_flip_p'),'holm_p':r.get('holm_p_10'),'source':'final_blr_results/baselines/v2m/comparisons/primary_ten_comparisons.csv','verification':'frozen reported paired test; Bengali data repeatedly exposed'})
for _,r in sec.iterrows():
 out.append({'protocol':'v2m secondary descriptive comparisons','record_type':'secondary_comparison','horizon_hours':r.get('horizon_hours'),'model':str(r.get('model'))+'_vs_'+str(r.get('baseline')),'comparison':r.get('comparison_type'),'mae_ug_m3':None,'rmse_ug_m3':None,'r2':None,'n_pairs':r.get('n_pairs'),'delta_mae_ug_m3':r.get('difference'),'ci_low':r.get('ci_low'),'ci_high':r.get('ci_high'),'raw_p':None,'holm_p':None,'source':'final_blr_results/baselines/v2m/comparisons/secondary_comparisons.csv','verification':'secondary descriptive; not a new comparison family'})
pd.DataFrame(out).to_csv(R/'FORECASTING_COMPARISONS.csv',index=False)
# preserve complete source tables adjacent
for f in ['primary_ten_comparisons.csv','secondary_comparisons.csv','individual_seed_metrics.csv','selected_configurations.csv']:
 pd.read_csv('final_blr_results/baselines/v2m/comparisons/'+f).to_csv(S/('v2m_'+f),index=False)
# spatial standardized rows
sp=[]
for _,r in pd.read_csv('final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv').iterrows():
 for key,label in [('train_only_spatial_mean','train_only_spatial_mean'),('forecast_idw','forecast_IDW'),('forecast_decoder','compact_decoder')]:
  sp.append({'protocol':'v2r h6 forecast-origin LOSO','method':label,'station_id':r.station_id,'n_pairs':r.n_observations,'mae_ug_m3':r[f'{key}_mae'],'rmse_ug_m3':r[f'{key}_rmse'],'r2':r[f'{key}_r2'],'coverage':'scored','source':'final_blr_results/final_research_v2r/citywide/spatial_decoder/per_station_test_metrics.csv'})
for method,mae,rmse,r2,n,protocol,source in [
 ('ST-PIGNN',22.314,40.821,-.213,14583,'W6 corrected station LOSO','final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md'),('weather_static_ridge',20.624,35.462,.085,14583,'W6 corrected station LOSO','final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md'),('retrospective_IDW',23.133,42.606,-.176,12328,'v2o same-hour spatial reconstruction','final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_VERDICT.md'),('retrospective_train_mean',20.563,38.480,-.078,14583,'v2o same-hour spatial reconstruction','final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_VERDICT.md')]:
 sp.append({'protocol':protocol,'method':method,'station_id':'pooled','n_pairs':n,'mae_ug_m3':mae,'rmse_ug_m3':rmse,'r2':r2,'coverage':'see source report; different populations across protocols','source':source})
pd.DataFrame(sp).to_csv(R/'SPATIAL_GENERALIZATION.csv',index=False)
# enhance citywide detailed rows
city=pd.read_csv('final_blr_results/final_research_v2r/citywide/road_predictions/citywide_benchmarks.csv');city.to_csv(S/'v2r_citywide_benchmarks.csv',index=False)
# table manifest count adjustment
print('forecast rows',len(out),'spatial rows',len(sp))
