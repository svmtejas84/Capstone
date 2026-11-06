from pathlib import Path
import pandas as pd
P=Path('final_blr_results/ieee_paper_evidence'); f=P/'results/SPATIAL_GENERALIZATION.csv';d=pd.read_csv(f);d=d[~d.protocol.astype(str).str.startswith(('W6 corrected station LOSO forecast','v2o retrospective same-hour LOSO reconstruction'))].copy()
# W6 per-station matched population
w=pd.read_csv('final_blr_results/city_scale/spatial_validation/loso_per_station_comparison.csv')
for _,r in w.iterrows():d.loc[len(d)]={'protocol':'W6 corrected station LOSO forecast; same 14,583-pair population','method':r.method,'station_id':r.station_id,'n_pairs':r.n,'mae_ug_m3':r.mae,'rmse_ug_m3':r.rmse,'r2':r.r2,'coverage':'per-station saved count','source':'final_blr_results/city_scale/spatial_validation/loso_per_station_comparison.csv'}
for method,mae,rmse,r2 in [('stpignn_original',22.314,40.821,-.213),('ridge_weather_static',20.624,35.462,.085),('station_train_mean',20.634,38.614,-.085),('idw',22.633,40.676,-.204),('ordinary_kriging',22.588,40.562,-.197),('gp_rbf',24.123,41.070,-.227)]:
 d.loc[len(d)]={'protocol':'W6 corrected station LOSO forecast; same 14,583-pair population','method':method,'station_id':'pooled','n_pairs':14583,'mae_ug_m3':mae,'rmse_ug_m3':rmse,'r2':r2,'coverage':'100%; matched common mask','source':'final_blr_results/city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md'}
# v2o per-site retrospective same-hour reconstruction
v=pd.read_csv('final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_RESULTS.csv')
rename={'idw_p2':'fixed_IDW_p2','nearest':'nearest_observed_monitor','train_other_station_mean':'training_only_other_station_mean'}
for _,r in v.iterrows():d.loc[len(d)]={'protocol':'v2o retrospective same-hour LOSO reconstruction; method-specific coverage','method':rename.get(r.method,r.method),'station_id':r.station_id,'n_pairs':r.n,'mae_ug_m3':r.mae,'rmse_ug_m3':r.rmse,'r2':r.r2,'coverage':r.coverage,'source':'final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_RESULTS.csv'}
for method,n,cov,mae,rmse,r2 in [('fixed_IDW_p2',12328,0.8454,23.133,42.606,-.176),('nearest_observed_monitor',13616,.9337,26.640,46.743,-.510),('training_only_other_station_mean',14583,1,20.563,38.480,-.078)]:
 d.loc[len(d)]={'protocol':'v2o retrospective same-hour LOSO reconstruction; method-specific coverage','method':method,'station_id':'pooled','n_pairs':n,'mae_ug_m3':mae,'rmse_ug_m3':rmse,'r2':r2,'coverage':cov,'source':'final_blr_results/citywide_extension/v2o/SPATIAL_VALIDATION_VERDICT.md'}
d.to_csv(f,index=False)
# refresh export and manifest checksums later
pd.read_csv(f).to_csv(P/'tables/export/SPATIAL_GENERALIZATION.csv',index=False)
print('spatial rows',len(d))
