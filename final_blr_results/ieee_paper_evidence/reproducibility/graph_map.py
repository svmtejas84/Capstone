from pathlib import Path
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Transformer
P=Path('final_blr_results/ieee_paper_evidence');src=P/'figures/source_data';out=P/'figures/export'
road=pd.read_csv('final_blr_results/final_research_v2r/citywide/road_predictions/map_points_20251008T0700Z.csv')
st=pd.read_csv('results/stations_v2.csv')
t=Transformer.from_crs(4326,32643,always_xy=True); st['x'],st['y']=t.transform(st.longitude.to_numpy(),st.latitude.to_numpy()); st[['station_id','x','y']].to_csv(src/'station_coordinates_projected.csv',index=False)
fig,ax=plt.subplots(figsize=(6,5));ax.scatter(road.utm_x_m/1000,road.utm_y_m/1000,s=.5,c='#c7c7c7',alpha=.35,rasterized=True,label='Road-node estimate locations');ax.scatter(st.x/1000,st.y/1000,s=24,c='#c44e52',edgecolor='white',linewidth=.4,label='15 monitoring stations');ax.set(xlabel='UTM easting (km)',ylabel='UTM northing (km)');ax.legend(frameon=False,fontsize=8);fig.suptitle('Road network locations and monitoring stations',fontsize=12,y=.98);fig.tight_layout(rect=[0,0,1,.93]);fig.savefig(out/'fig13_road_graph_station_locations.png',bbox_inches='tight');fig.savefig(out/'fig13_road_graph_station_locations.pdf',bbox_inches='tight')
m=pd.read_csv(P/'figures/figure_manifest.csv');m.loc[len(m)]=['fig13_road_graph_station_locations','Road network locations and monitoring stations','export/fig13_road_graph_station_locations.png; export/fig13_road_graph_station_locations.pdf','final_blr_results/final_research_v2r/citywide/road_predictions/map_points_20251008T0700Z.csv','figures/source_data/station_coordinates_projected.csv','Road nodes are locations, not monitors or labeled observations; station coordinates projected from results/stations_v2.csv.','python final_blr_results/ieee_paper_evidence/reproducibility/graph_map.py'];m.to_csv(P/'figures/figure_manifest.csv',index=False);print(len(m))
