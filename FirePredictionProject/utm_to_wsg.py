import os
import glob
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

os.environ['PROJ_LIB'] = r'C:\Users\Su_Us\anaconda3\envs\myenv\Library\share\proj'

def reproject_raster(input_file, output_file, dst_crs):
    with rasterio.open(input_file) as src:
        transform, width, height = calculate_default_transform(src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(output_file, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear
                )

input_folder = "D:\\Fire_Data\\150"
output_folder = "D:\\Fire_Data\\150"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

tif_files = glob.glob(os.path.join(input_folder, "*.tif"))

for i, tif_file in enumerate(tif_files):
    print(f"Reprojecting {i + 1}/{len(tif_files)}: {os.path.basename(tif_file)}")

    file_name, _ = os.path.splitext(os.path.basename(tif_file))
    output_file = os.path.join(output_folder, f"{file_name}_wgs84.tif")

    dst_crs = 'EPSG:4326'

    reproject_raster(tif_file, output_file, dst_crs)
