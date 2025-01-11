import os
import numpy as np
from osgeo import gdal

# 设置输入和输出目录
input_dir = "E:\hohai\modis\GNSS/transformer\mod2\modis"  # GeoTIFF文件所在的目录
output_dir = "E:\hohai\modis\GNSS/transformer\mod2\modis"  # 提取波段后保存的目录
band_names = [
    'Georef [Band 17 Radiance] (0.905000)',
    'Georef [Band 18 Radiance] (0.936000)',
    'Georef [Band 19 Radiance] (0.940000)'
]  # 需要提取的波段名称
nodata_value = 0
# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历输入目录中的所有GeoTIFF文件
for filename in os.listdir(input_dir):
    if filename.endswith(".dat"):  # 只处理.tif文件
        filepath = os.path.join(input_dir, filename)

        # 打开GeoTIFF文件
        dataset = gdal.Open(filepath)
        if dataset is None:
            print(f"无法打开文件: {filepath}")
            continue

        # 获取所有波段的名称
        band_count = dataset.RasterCount
        band_names_in_file = [dataset.GetRasterBand(i + 1).GetDescription() for i in range(band_count)]

        # 检查目标波段是否存在
        for band_name in band_names:
            if band_name in band_names_in_file:
                band_index = band_names_in_file.index(band_name) + 1  # 波段索引是从1开始的
                band = dataset.GetRasterBand(band_index)

                # 读取波段数据
                band_data = band.ReadAsArray()

                # 生成输出文件路径
                output_filepath = os.path.join(output_dir,
                                               f"{os.path.splitext(filename)[0]}_{band_name.replace('/', '_').replace(' ', '_')}.tif")

                # 创建一个新的GeoTIFF文件保存提取的波段数据
                driver = gdal.GetDriverByName('GTiff')
                out_dataset = driver.Create(output_filepath, dataset.RasterXSize, dataset.RasterYSize, 1,
                                            gdal.GDT_Float32)

                # 设置地理信息和投影信息
                out_dataset.SetGeoTransform(dataset.GetGeoTransform())
                out_dataset.SetProjection(dataset.GetProjection())

                # 设置NoData值
                out_dataset.GetRasterBand(1).SetNoDataValue(nodata_value)

                # 写入数据
                out_dataset.GetRasterBand(1).WriteArray(band_data)

                # 关闭数据集
                out_dataset = None
                print(f"波段 {band_name} 提取完成: {output_filepath}")
            else:
                print(f"文件 {filename} 不包含波段 {band_name}")

        # 关闭数据集
        dataset = None
