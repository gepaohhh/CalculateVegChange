import rasterio
import geopandas as gpd
from rasterio.mask import mask
from rasterio.warp import transform_geom
import numpy as np
from osgeo import gdal

def clip_raster_with_shapefile(raster_path, 
                             shapefile_path, 
                             output_path,
                             all_touched=False,
                             invert=False):
    """
    Clip a raster using a shapefile with additional options
    
    Parameters:
    raster_path: str, path to input raster
    shapefile_path: str, path to input shapefile
    output_path: str, path for output clipped raster
    all_touched: bool, if True, all pixels touched by geometries will be included
    invert: bool, if True, clips everything outside the geometry
    """
    try:
        # Read the shapefile
        shapefile = gpd.read_file(shapefile_path)
        
        with rasterio.open(raster_path) as src:
            # Check if shapefile is empty
            if shapefile.empty:
                raise ValueError("Shapefile is empty")
            
            # Ensure the shapefile has the same CRS as the raster
            if shapefile.crs != src.crs:
                print(f"Reprojecting shapefile from {shapefile.crs} to {src.crs}")
                shapefile = shapefile.to_crs(src.crs)
            
            # Get the geometry in GeoJSON format
            shapes = shapefile.geometry.values
            
            # Perform the clip
            clipped_array, clipped_transform = mask(
                src,
                shapes,
                crop=True,
                all_touched=all_touched,
                invert=invert,
                nodata=src.nodata
            )
            
            # Check if the result is empty
            if np.all(clipped_array == src.nodata):
                print("Warning: Clipped result contains only NoData values")
            
            # Copy the metadata
            out_meta = src.meta.copy()
            
            # Update the metadata
            out_meta.update({
                "driver": "GTiff",
                "height": clipped_array.shape[1],
                "width": clipped_array.shape[2],
                "transform": clipped_transform,
                "nodata": src.nodata
            })
            
            # Write the clipped raster
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(clipped_array)
                
            print(f"Clipped raster saved to: {output_path}")
            print(f"Output shape: {clipped_array.shape}")
            
            return True
            
    except rasterio.errors.RasterioIOError:
        print("Error: Unable to read the raster file")
        return False
    except gpd.io.file.fiona.errors.DriverError:
        print("Error: Unable to read the shapefile")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False

# Example usage with additional options
def main():
    raster_paths = [r"../NDVI/fvc_class_2013.tif",
                    r"../NDVI/fvc_class_2017.tif"]
    shapefile_path = r"F:\NanJinLandset\nj\nanjing.shp"
    output_paths = [r"../NDVI/fvc_class_2013_clip.tif",
                    r"../NDVI/fvc_class_2017_clip.tif"]
    
    # Clip with all pixels that touch the geometry
    for i in range(len(raster_paths)):
        clip_raster_with_shapefile(
            raster_path=raster_paths[i],
            shapefile_path=shapefile_path,
            output_path=output_paths[i],
            all_touched=True,  # Include all touched pixels
            invert=False       # Clip inside the geometry
        )

def clip_raster_with_shapefile(input_raster, input_shapefile, output_raster):
    """
    Clip a raster (TIFF) file using a shapefile
    
    Args:
        input_raster (str): Path to input raster file
        input_shapefile (str): Path to input shapefile for clipping
        output_raster (str): Path to save the clipped raster
    """
    try:
        # Create the cutting command
        warp_options = gdal.WarpOptions(
            cutlineDSName=input_shapefile,
            cropToCutline=True,
            dstNodata=gdal.FillNodata  # Set this to your desired nodata value if needed
        )
        
        # Perform the clipping
        gdal.Warp(
            output_raster,
            input_raster,
            options=warp_options
        )
        
        print(f"Successfully clipped raster to: {output_raster}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Define your input and output paths
    # input_raster_path = [r"../NDVI/fvc_class_2013.tif",
    #                      r"../NDVI/fvc_class_2017.tif"]
    input_raster_path = [r"../ChangeDetect/fvc_change_2013_2017.tif"]
    shapefile_path = r"F:\NanJinLandset\nj\nanjing.shp"
    # output_raster_path = [r"../NDVI/fvc_class_2013_clip.tif",
    #                       r"../NDVI/fvc_class_2017_clip.tif"]
    output_raster_path = [r"../ChangeDetect/fvc_change_2013_2017_clip.tif"]
    for i in range(len(input_raster_path)):
        clip_raster_with_shapefile(input_raster_path[i], shapefile_path, output_raster_path[i])