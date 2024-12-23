from osgeo import gdal
from osgeo import gdal_array
import numpy as np
from matplotlib import pyplot as plt
import cv2 as cv

# 辐射定标
class Landsat8Reader(object):
    def __init__(self):
        self.base_path = r"F:\NanJinLandset\2017\LC08_L1TP_120038_20170721_20170728_01_T1"
        self.bands = 7
        self.band_file_name = []
        self.nan_position = []
 
    def read(self):
        for band in range(self.bands):
            band_name = self.base_path + "_B" + str(band + 1) + ".tif"
            self.band_file_name.append(band_name)
 
        ds = gdal.Open(self.band_file_name[0])
 
        image_dt = ds.GetRasterBand(1).DataType
        image = np.zeros((ds.RasterYSize, ds.RasterXSize, self.bands),
                         dtype=np.float)
        for band in range(self.bands):
            ds = gdal.Open(self.band_file_name[band])
            band_image = ds.GetRasterBand(1)
            image[:, :, band] = band_image.ReadAsArray()
 
        self.nan_position = np.where(image == 0)
        image[self.nan_position] = np.nan
 
        del ds
 
        return image
 
    def write(self, image, file_name, bands, format='GTIFF'):
        ds = gdal.Open(self.band_file_name[0])
        projection = ds.GetProjection()
        geotransform = ds.GetGeoTransform()
        x_size = ds.RasterXSize
        y_size = ds.RasterYSize
        del ds
        band_count = bands
        dtype = gdal.GDT_Float32
 
        driver = gdal.GetDriverByName(format)
        new_ds = driver.Create(file_name, x_size, y_size, band_count, dtype)
        new_ds.SetGeoTransform(geotransform)
        new_ds.SetProjection(projection)
 
        for band in range(self.bands):
            new_ds.GetRasterBand(band + 1).WriteArray(image[:, :, band])
            new_ds.FlushCache()
 
        del new_ds
 
    def show_true_color(self, image):
        index = np.array([3, 2, 1])
        true_color_image = image[:, :, index].astype(np.float32)
        strech_image = TwoPercentLinear(true_color_image)
        plt.imshow(strech_image)
 
    def show_CIR_color(self, image):
        index = np.array([4, 3, 2])
        true_color_image = image[:, :, index].astype(np.float32)
        strech_image = TwoPercentLinear(true_color_image)
        plt.imshow(strech_image)
 
    def radiometric_calibration(self):
        # 辐射定标
        image = self.read()
 
        def get_calibration_parameters():
            filename = self.base_path + "_MTL" + ".txt"
            f = open(filename, 'r')
            # f = open(r'D:\ProfessionalProfile\LandsatImage\LC08_L1TP_134036_20170808_20170813_01_T1\LC08_L1TP_134036_20170808_20170813_01_T1_MTL.txt', 'r')
            # readlines()方法读取整个文件所有行，保存在一个列表(list)变量中，每行作为一个元素，但读取大文件会比较占内存。
            metadata = f.readlines()
            f.close()
            multi_parameters = []
            add_parameters = []
            parameter_start_line = 0
            for lines in metadata:
                # split()方法通过指定分隔符对字符串进行切片，如果参数 num 有指定值，则分隔 num+1 个子字符串。
                # 无指定值，默认为 -1, 即分隔所有符合要求的。
                test_line = lines.split('=')
                if test_line[0] == '    RADIANCE_MULT_BAND_1 ':
                    break
                else:
                    parameter_start_line = parameter_start_line + 1
 
            for lines in range(parameter_start_line, parameter_start_line + 11):
                parameter = float(metadata[lines].split('=')[1])
                multi_parameters.append(parameter)
 
            # 由于RADIANCE_MULT_BAND参数和RADIANCE_ADD_BAND参数是挨着的，所以直接+11个参数即可
            for lines in range(parameter_start_line + 11, parameter_start_line + 22):
                parameter = float(metadata[lines].split('=')[1])
                add_parameters.append(parameter)
 
            return multi_parameters, add_parameters
 
        multi_parameters, add_parameters = get_calibration_parameters()
        cali_image = np.zeros_like(image, dtype=np.float32)
 
        for band in range(self.bands):
            gain = multi_parameters[band]
            offset = add_parameters[band]
            # 辐射定标像元 = DN * 增益 + 偏置，线性关系。
            cali_image[:, :, band] = image[:, :, band] * gain + offset
 
        del image
        return cali_image

# 拉伸显示
def TwoPercentLinear(image, max_out=255, min_out=0):
    b, g, r = cv.split(image)
    def gray_process(gray, maxout = max_out, minout = min_out):
        high_value = np.percentile(gray, 98)
        low_value = np.percentile(gray, 2)
        truncated_gray = np.clip(gray, a_min=low_value, a_max=high_value) 
        processed_gray = ((truncated_gray - low_value)/(high_value - low_value)) * (maxout - minout)
        return processed_gray
    r_p = gray_process(r)
    g_p = gray_process(g)
    b_p = gray_process(b)
    result = cv.merge((b_p, g_p, r_p))
    return np.uint8(result)

 
if __name__ == "__main__":
    reader = Landsat8Reader()
    image = reader.read()
    # 辐射定标
    cali_image = reader.radiometric_calibration()
    # 保存路径
    file_path = r'D:\YAOGANGAILUN\NanJinNDVI_ChangeDetection\2017_process\2017cali.tif'
    reader.write(cali_image, file_path, reader.bands)