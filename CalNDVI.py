import numpy as np
import rasterio

def load_landsat_bands(nir_path, red_path):
    """
    Load NIR (Band 5) and RED (Band 4) bands from Landsat 8
    """
    with rasterio.open(nir_path) as nir_src:
        nir_band = nir_src.read(1)
        profile = nir_src.profile
    
    with rasterio.open(red_path) as red_src:
        red_band = red_src.read(1)
    
    return nir_band, red_band, profile

def calculate_ndvi(nir_band, red_band):
    """
    Calculate NDVI from NIR and Red bands
    """
    # Convert to float for calculation
    nir = nir_band.astype(float)
    red = red_band.astype(float)
    # Add small number to denominator to avoid division by zero
    ndvi = (nir - red) / (nir + red + 1e-10)
    # Clip values to valid NDVI range (-1 to 1)
    ndvi = np.clip(ndvi, -1, 1)
    return ndvi

def save_ndvi(ndvi, output_path, profile):
    """
    Save NDVI result to a GeoTIFF file
    """
    # Update the profile for NDVI output
    profile.update(
        dtype=rasterio.float32,
        count=1,
        nodata=None
    )
    
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)

def main():
    # Paths to your Landsat 8 bands
    nir_path = r"D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_process\LC08_L1TP_120038_20170721_20170728_01_T1_B5.TIF"  # NIR band (Band 5)
    red_path = r"D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_process\LC08_L1TP_120038_20170721_20170728_01_T1_B4.TIF"  # Red band (Band 4)
    output_path = r"D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\NDVI\ndvi_2017.tif"
    
    # Load bands
    nir_band, red_band, profile = load_landsat_bands(nir_path, red_path)
    
    # Calculate NDVI
    ndvi = calculate_ndvi(nir_band, red_band)
    
    # Save result
    save_ndvi(ndvi, output_path, profile)

if __name__ == "__main__":
    main()