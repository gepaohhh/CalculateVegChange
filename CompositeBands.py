import rasterio

file_list = [r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B1.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B2.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B3.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B4.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B5.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B6.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B7.tiff',
             r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017_B8.tiff']

# Read metadata of first file
with rasterio.open(file_list[0]) as src0:
    meta = src0.meta

# Update meta to reflect the number of layers
meta.update(count = len(file_list))

# Read each layer and write it to stack
with rasterio.open(r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_clip_combine\2017.tiff', 'w', **meta) as dst:
    for id, layer in enumerate(file_list, start=1):
        with rasterio.open(layer) as src1:
            dst.write_band(id, src1.read(1))