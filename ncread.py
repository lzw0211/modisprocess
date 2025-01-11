import os
os.environ["PATH"] = "D:\\anaconda3\\envs\\ERA\\Lib\\site-packages\\osgeo;"
os.environ["PYTHONPATH"] = "D:\\anaconda3\\envs\\ERA\\Lib\\site-packages\\osgeo;"
import gdal
from osgeo import gdal
import xarray as xr
import rasterio
from rasterio.transform import from_origin
import pandas as pd

# 输入和输出路径
input_folder = 'E:\hohai\modis\GNSS/transformer\mod10103\era'
output_folder = input_folder

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)

# 获取文件夹中所有 .nc 文件
nc_files = [f for f in os.listdir(input_folder) if f.endswith('.nc')]
# nc_files = [f for f in os.listdir(input_folder) if f.endswith('.grib')]

# 遍历每个 .nc 文件
for nc_file in nc_files:
    # 读取 .nc 文件
    ds = xr.open_dataset(os.path.join(input_folder, nc_file))
    print(ds.variables)
    # 提取时间变量
    time_var = pd.to_datetime(ds['valid_time'].values)  # 转换为 pandas 时间格式

    # 遍历每个时间步
    for i, time_step in enumerate(time_var):
        # 格式化文件名：eraYYYYMMDDHHMM
        timestamp = time_step.strftime('tm%Y%m%d%H%M')
        output_tif = os.path.join(output_folder, f"{timestamp}.tif")

        # 提取数据（ 'tcwv'水汽tp降水t2m温度sp压力
        data_array = ds['t2m'].isel(valid_time=i).values

        # 获取地理坐标信息
        lon = ds['longitude'].values
        lat = ds['latitude'].values
        xres = lon[1] - lon[0]  # 经度方向分辨率
        yres = lat[0] - lat[1]  # 纬度方向分辨率

        transform = from_origin(lon.min() - xres / 2, lat.max() + yres / 2, lon[1] - lon[0], lat[0] - lat[1])

        # 导出为 .tif 文件
        with rasterio.open(
                output_tif, 'w', driver='GTiff', height=data_array.shape[0],
                width=data_array.shape[1], count=1, dtype=data_array.dtype,
                crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(data_array, 1)

    ds.close()

print("批量导出完成。")
