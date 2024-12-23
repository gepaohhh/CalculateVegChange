import rasterio as rio
import numpy as np
from osgeo import gdal

def read_ndvi(ndvi_path):
    """Read NDVI data from file"""
    dataset = gdal.Open(ndvi_path)
    if dataset is None:
        raise ValueError("Could not open NDVI file")
    ndvi_array = dataset.GetRasterBand(1).ReadAsArray()
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    del dataset
    return ndvi_array, geotransform, projection

def cal_fvc(ndvi_array):
    valid_mask = ~np.isnan(ndvi_array)
    fvc = np.zeros_like(ndvi_array, dtype=np.float32)
    # ndvimin, ndvimax = np.nanpercentile(ndvi, [5, 95], method='nearest')
    ndvi_soil, ndvi_veg = np.nanpercentile(ndvi_array[valid_mask], [5, 95], method='nearest')
    fvc[valid_mask] = (ndvi_array[valid_mask] - ndvi_soil) / (ndvi_veg - ndvi_soil)
    fvc = np.clip(fvc, 0, 1)
    return fvc 

def classify_fvc(fvc):
    """Classify FVC data into 5 classes"""
    fvc_class = np.zeros_like(fvc, dtype=np.uint8)
    fvc_class[np.isnan(fvc)] = 0
    fvc_class[fvc < 0.1] = 1
    fvc_class[(fvc >= 0.1) & (fvc < 0.3)] = 2
    fvc_class[(fvc >= 0.3) & (fvc < 0.5)] = 3
    fvc_class[(fvc >= 0.5) & (fvc < 0.7)] = 4
    fvc_class[fvc >= 0.7] = 5
    return fvc_class

def save_fvc(fvc, output_path, geotransform, projection):
    """Save FVC data to file"""
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_path, fvc.shape[1], fvc.shape[0], 1, gdal.GDT_Int32)
    dataset.SetGeoTransform(geotransform)
    dataset.SetProjection(projection)
    dataset.GetRasterBand(1).WriteArray(fvc)
    dataset.FlushCache()
    del dataset

if __name__ == "__main__":
    ndvi_array, geotransform, projection = read_ndvi("../NDVI/ndvi_2017.tif")
    fvc = cal_fvc(ndvi_array)
    save_fvc(fvc, "../NDVI/fvc_2017.tif", geotransform, projection)
    fvc_class = classify_fvc(fvc)
    save_fvc(fvc_class, "../NDVI/fvc_class_2017.tif", geotransform, projection)