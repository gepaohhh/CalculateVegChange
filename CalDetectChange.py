import rasterio as rio
import numpy as np
from osgeo import gdal

def read_fvc(fvc_path):
    """Read fvc data from file"""
    dataset = gdal.Open(fvc_path)
    if dataset is None:
        raise ValueError("Could not open fvc file")
    fvc_array = dataset.GetRasterBand(1).ReadAsArray()
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    del dataset
    return fvc_array, geotransform, projection

def fvc_change(fvc_init,fvc_final):
    change = fvc_final - fvc_init
    change_classes = np.zeros_like(change, dtype=np.int8)
    change_classes[np.isnan(change)] = -99
    change_classes[(change < -2)] = 1 #明显增加
    change_classes[(change >= -2) & (change < 0)] = 2 #略微增加
    change_classes[(change == 0)] = 3 #不变
    change_classes[(change > 0) & (change <= 2)] = 4 #略微减少
    change_classes[(change > 2)] = 5 #明显减少
    return change_classes

def save_fvc_change(change_img, output_path, geotransform, projection):
    """Save change_img data to file"""
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_path, change_img.shape[1], change_img.shape[0], 1, gdal.GDT_CInt32)
    dataset.SetGeoTransform(geotransform)
    dataset.SetProjection(projection)
    dataset.GetRasterBand(1).WriteArray(change_img)
    dataset.FlushCache()
    del dataset

if __name__ == "__main__":
    fvc_init_path = "../NDVI/fvc_class_2013_clip.tif"
    fvc_final_path = "../NDVI/fvc_class_2017_clip.tif"
    fvc_init_array, geotransform, projection = read_fvc(fvc_init_path)
    fvc_final_array, _, _ = read_fvc(fvc_final_path)
    change_img = fvc_change(fvc_init_array, fvc_final_array)
    save_fvc_change(change_img, "../ChangeDetect/fvc_change_2013_2017.tif", geotransform, projection)