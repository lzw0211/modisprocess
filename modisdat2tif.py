import os
from osgeo import gdal

# 设置输入和输出文件夹路径
input_folder = r"F:\modis\aoi3\nir\dat\temp"
output_folder = r'F:\modis\aoi3\nir\tif\temp'

# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历所有dat文件
for filename in os.listdir(input_folder):
    if filename.endswith('.dat'):
        # 构建完整的输入输出路径
        input_path = os.path.join(input_folder, filename)
        day = filename.split('.')[1]
        time = filename.split('.')[2]
        doy = []
        doy = 'nir' + day[1:] + time
        # output_path = os.path.join(output_folder, filename.replace('.dat', '.tif'))
        output_path = os.path.join(output_folder, doy+'.tif')
        # 使用gdal打开dat文件
        dataset = gdal.Open(input_path)

        # 设置NoData值为0
        dataset.GetRasterBand(1).SetNoDataValue(0)

        # 使用gdal_translate将dat文件转换为tif
        gdal.Translate(output_path, dataset, format="GTiff", noData=0)

        print(f"Converted {input_path} to {output_path}")

