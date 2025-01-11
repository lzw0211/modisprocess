import os
import re
from datetime import datetime, timedelta

# 文件目录路径
directory = "E:\hohai\modis\GNSS\mod123\mod3\modis"

# 遍历文件目录中的所有文件
for filename in os.listdir(directory):
    # 匹配MOD或MYD文件名模式，包括 .dat 和 .hdr 文件
    match = re.match(r'(MOD|MYD)05_L2\.A(\d{4})(\d{3})\.(\d{4})\.\d+\.\d+_Swath_2D_1_georef\.(dat|hdr)', filename)

    if match:
        # 提取日期（年份和一年中的第几天）
        year = int(match.group(2))  # 提取年份，如2010
        day_of_year = int(match.group(3))  # 提取一年中的第几天，如024

        # 将"年+天数"转换为具体日期
        date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        formatted_date = date.strftime('%Y%m%d')  # 转换为YYYYMMDD格式

        # 提取时间
        time = match.group(4)  # 0245

        # 提取文件扩展名
        extension = match.group(5)  # dat 或 hdr

        # 构造新的文件名，格式为nir+日期+时间，没有下划线
        new_filename = f"nir{formatted_date}{time}.{extension}"
        # new_filename = f"ir{formatted_date}{time}.{extension}"

        # 构造完整的文件路径
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)

        # 重命名文件
        os.rename(old_file, new_file)

        print(f"Renamed: {filename} -> {new_filename}")
