"""Sample fixed station-edge midpoints from the local SRTM raster using rasterio."""
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform


ROOT=Path(__file__).resolve().parents[1]


def main():
    z=np.load(ROOT/"results/data_v2g_arrays.npz")
    xy=z["coordinates"].astype(float)
    n=len(xy); neighbours=4
    distance=np.linalg.norm(xy[:,None,:]-xy[None,:,:],axis=-1)
    np.fill_diagonal(distance,np.inf)
    closest=np.argsort(distance,axis=1)[:,:neighbours]
    source=np.repeat(np.arange(n),neighbours); destination=closest.reshape(-1)
    midpoint=(xy[source]+xy[destination])/2
    with rasterio.open(ROOT/"data/dem/bangalore_srtm1.tif") as ds:
        xx,yy=transform("EPSG:32643",ds.crs,midpoint[:,0].tolist(),midpoint[:,1].tolist())
        values=np.array([sample[0] for sample in ds.sample(zip(xx,yy))],float)
        if ds.nodata is not None:
            values[values==ds.nodata]=np.nan
    np.save(ROOT/"results/dem_midpoint_v2g.npy",values.astype(np.float32))
    print({"edges":len(values),"finite":int(np.isfinite(values).sum()),"raster_crs":str(ds.crs)})


if __name__=="__main__":
    main()
