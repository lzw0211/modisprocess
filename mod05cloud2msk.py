import numpy as np
from osgeo import gdal


def process_cloud_mask(input_tif, output_tif):
    try:
        # 读取输入数据
        dataset = gdal.Open(input_tif)
        if not dataset:
            raise Exception(f"无法打开文件：{input_tif}")

        # 获取栅格的空间参考和地理信息
        geo_transform = dataset.GetGeoTransform()
        projection = dataset.GetProjection()
        cell_size_x = geo_transform[1]  # 水平方向像素分辨率
        cell_size_y = geo_transform[5]  # 垂直方向像素分辨率
        x_min = geo_transform[0]
        y_min = geo_transform[3]

        # 将栅格转换为NumPy数组
        cloud_mask_array = dataset.ReadAsArray()
        valid_mask = ~np.isnan(cloud_mask_array)

        # 创建全尺寸掩膜数组
        masked_values_full = np.zeros_like(cloud_mask_array, dtype=np.uint8)

        # 位运算处理（提取第1-2位）
        valid_pixels = cloud_mask_array[valid_mask].astype(int)
        masked_values_full[valid_mask] = np.bitwise_and(
            np.right_shift(valid_pixels, 1),  # 右移1位获取第1-2位
            0b00000011  # 保留最后两位
        )

        # 分类映射
        classification_dict = {0: 1, 1: 2, 2: 3, 3: 4}
        final_classification = np.zeros_like(cloud_mask_array, dtype=np.uint8)

        # 应用分类
        for key, value in classification_dict.items():
            final_classification[(valid_mask) & (masked_values_full == key)] = value

        # 保留原始NoData
        final_classification[~valid_mask] = 0

        # 创建输出栅格
        driver = gdal.GetDriverByName('GTiff')
        out_dataset = driver.Create(
            output_tif,
            dataset.RasterXSize,
            dataset.RasterYSize,
            1,  # 一个波段
            gdal.GDT_Byte
        )

        # 设置输出栅格的地理信息和投影
        out_dataset.SetGeoTransform(geo_transform)
        out_dataset.SetProjection(projection)

        # 写入数据
        out_band = out_dataset.GetRasterBand(1)
        out_band.WriteArray(final_classification)

        # 设置NoData值
        out_band.SetNoDataValue(0)

        # 清理
        out_band.FlushCache()
        out_dataset.FlushCache()

        print(f"处理成功：{output_tif}")

    except Exception as e:
        print(f"错误：{str(e)}")


if __name__ == "__main__":
    process_cloud_mask(
        r"E:\hohai\modis\test\MYD05_L2.A2020144.1130.061.2020145150546_Swath_2D_1_georef.dat",
        r'E:\hohai\modis\test\processed_cloud_mask2.tif'
    )
