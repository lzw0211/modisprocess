import os
from datetime import datetime
from osgeo import gdal,gdalconst

# 设置输入和输出文件夹路径
input_folder = r'F:\modis\aoi3\band\tif\temp'
output_folder = r"F:\modis\aoi3\band\tif\band2"

# 指定裁剪的地理范围（xmin, ymin, xmax, ymax）
# clip_extent = [-125.3,31.7,-113,42]
clip_extent = [-1.5,43.2,7.1,50.3]


# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 获取文件夹中所有tif文件
tif_files =sorted([f for f in os.listdir(input_folder) if f.endswith('band2.tif')])########################################

# # 按文件名中某一部分（例如日期或时间）(排序
# tif_files = sorted(
#     [f for f in os.listdir(input_folder) if f.endswith('.tif')],
#     key=lambda x: int(x[7:10])  # 假设文件名第7到10位是日期
# )

# 用于存储同一天的文件
day_files = {}

# 遍历所有文件并按日期分组
for filename in tif_files:
    # 提取日期和时间信息nir
    # day = filename[7:10]  # 文件名中提取天数（8-10位）
    # time = filename[10:14]  # 文件名中提取时间（11-14位）

    # # 提取日期和时间信息band
    day = filename[5:8]  # 文件名中提取天数（8-10位）
    time = filename[8:12]  # 文件名中提取时间（11-14位）

    # 生成一个日期+时间的键
    date_time_key = f"{day}-{time}"

    # 存储文件路径
    file_path = os.path.join(input_folder, filename)

    if day not in day_files:
        day_files[day] = []

    # 将文件按天分组
    day_files[day].append((file_path, time))

# 对于每一天，进行合并并裁剪
for day, files in day_files.items():
    # 根据时间排序，取最早的时间作为文件名
    # files.sort(key=lambda x: x[1])  # 按时间排序AOI2
    files.sort(key=lambda x: x[1], reverse=True)  # 按时间降序排序AOI3
    earliest_file = files[0][0]  # 最早的文件路径

    # 合并文件（使用gdal.BuildVRT）
    file_list = [file[0] for file in files]  # 获取该天的所有文件路径
    output_name = f"band2_{day}_{files[0][1]}.tif"  # 输出文件名#########################################################
    output_path = os.path.join(output_folder, output_name)

    src_nodata_value = 'nan'  # 输入数据的 NoData 值
    dst_nodata_value = 'nan' # 输出数据的 NoData 值（可以是相同的，也可以不同）

    # 使用gdal.Warp进行合并并处理NoData
    warp_options = gdal.WarpOptions(
        format="GTiff",
        creationOptions=["TILED=YES", "BIGTIFF=YES", "COMPRESS=LZW", "NUM_THREADS=ALL"],  # 支持多线程
        multithread=True,  # 支持多线程
        warpMemoryLimit=1024 * 8,  # 内存使用8GB
        outputBounds=clip_extent,  # 裁剪范围
        resampleAlg="max",
        srcNodata=src_nodata_value,  # 输入数据的 NoData 值
        dstNodata=dst_nodata_value,  # 输出数据的 NoData 值

    )

    # 执行合并并裁剪
    result = gdal.Warp(output_path, file_list, options=warp_options)

    # 检查是否成功生成栅格
    if result is None:
        print(f"Failed to merge files for day {day}.")
    else:
        print(f"Merged and clipped files for day {day} saved as {output_path}")

    # 清理
    del result

    #
    # vrt = gdal.BuildVRT('/vsimem/temp.vrt', file_list)#, options=vrt_options)
    #
    # if vrt is None:
    #     print(f"Failed to create VRT for day {day}")
    #     continue
    # nodata_value = vrt.GetRasterBand(1).GetNoDataValue()

#     # 合并所有同一天的文件
#     # 使用gdal_merge.py（如果gdal_merge.py在路径中）
#     # command = f"gdal_merge.py -o {output_path} -of GTiff {' '.join(file_list)}"
#     # os.system(command)
#
#     gdal.Warp(
#         output_path+output_name,
#         file_list,
#         options=gdal.WarpOptions(
#             format="GTiff",
#             creationOptions=["TILED=YES", "BIGTIFF=YES", "COMPRESS=LZW", "NUM_THREADS=ALL"],  # NUM_THREADS=ALL 调动所有CPU
#             multithread=True,  # 支持多线程
#             warpMemoryLimit=1024 * 8  # 内存使用8G，单位为MB（可根据系统情况调整）
#         )
#     )
#
#
#
#     # 使用gdalwarp进行裁剪
#     # gdal.Warp(output_path, output_path, outputBounds=clip_extent)
#
#     print(f"Merged and clipped files for day {day} saved as {output_path}")
#
