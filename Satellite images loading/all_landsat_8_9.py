import ee
import pandas as pd
from datetime import datetime, timedelta

# Initialize Google Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-suray1906firefire')

def load_and_filter_image_collection(row):
    """Load and filter Landsat 8 and 9 image collections based on a dataframe row."""
    # Define the geometry of interest.
    geometry = ee.Geometry.Rectangle([row['x_min'], row['y_min'], row['x_max'], row['y_max']])

    # Load the Landsat 8 and 9 ImageCollections.
    landsat8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    landsat9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')

    # Merge collections, filter by date and bounds, and select the required bands.
    combined = landsat8.merge(landsat9) \
        .filterDate(row['dt_start'], row['dt_end']) \
        .filterBounds(geometry) \
        .filter(ee.Filter.lt('CLOUD_COVER', 10)) \
        .select(['SR_B4', 'SR_B2', 'SR_B5', 'SR_B6', 'SR_B7'])

    return combined

def calculate_nbr(image):
    """Calculate the NBR (Normalized Burn Ratio) index from an image."""
    nbr = image.expression(
        '(B7 - B5) / (B7 + B5)',
        {
            'B5': image.select('SR_B5'),  # NIR
            'B7': image.select('SR_B7')   # SWIR2
        }
    )
    return nbr

def export_image(image, index, description_prefix, geometry, image_type):
    """Function to export images as GeoTIFF with specific image type."""
    try:
        image_id = image.id().getInfo()
        if image_type == "RGB":
            # Export RGB image
            export_task = ee.batch.Export.image.toDrive(
                image=image.select(['SR_B4', 'SR_B6', 'SR_B2']),
                description=f"{description_prefix}_RGB_Image_L8L9_{image_id}_{index}",
                scale=30,
                region=geometry,
                fileFormat='GeoTIFF',
                folder=f"{description_prefix}",
                crs='EPSG:4326'
            )
        elif image_type == "NBR":
            # Export NBR image
            nbr_image = calculate_nbr(image)
            export_task = ee.batch.Export.image.toDrive(
                image=nbr_image,
                description=f"{description_prefix}_NBR_Image_L8L9_{image_id}_{index}",
                scale=30,
                region=geometry,
                fileFormat='GeoTIFF',
                folder=f"{description_prefix}",
                crs='EPSG:4326'
            )
        export_task.start()
    except ee.ee_exception.EEException as e:
        print(f"Failed to export image: {str(e)}")

def process_images_from_table(file_path):
    """Process images from a table with coordinates and dates, exporting RGB and NBR images."""
    df = pd.read_csv(file_path, sep=';')

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        geometry = ee.Geometry.Rectangle([row['x_min'], row['y_min'], row['x_max'], row['y_max']])
        # Load and filter the image collection
        landsat_collection = load_and_filter_image_collection(row)
        num_images = landsat_collection.size().getInfo()
        fire_number = row['fire_id']

        if num_images > 0:
            image_list = landsat_collection.sort('system:time_start').toList(num_images)

            # Export each image in both RGB and NBR format
            for i in range(num_images):
                image = ee.Image(image_list.get(i))
                export_image(image, i, fire_number, geometry, "RGB")
                export_image(image, i, fire_number, geometry, "NBR")

            # Export one additional image between dt_end and dt_end + 20 days if available
            end_date = datetime.strptime(row['dt_end'], '%Y-%m-%d')
            post_end_date = end_date + timedelta(days=50)
            additional_images = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').merge(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')) \
                .filterDate(row['dt_end'], post_end_date.strftime('%Y-%m-%d')) \
                .filterBounds(geometry) \
                .filter(ee.Filter.lt('CLOUD_COVER', 10)) \
                .select(['SR_B4', 'SR_B2', 'SR_B5', 'SR_B6', 'SR_B7']) \
                .sort('system:time_start')

            if additional_images.size().getInfo() > 0:
                additional_image = ee.Image(additional_images.first())
                export_image(additional_image, 'final', fire_number, geometry, "RGB")
                export_image(additional_image, 'final', fire_number, geometry, "NBR")
            else:
                print(f"No additional image found for {fire_number} in the range {row['dt_end']} to {post_end_date}")
        else:
            print(f"Для {fire_number} с номером строки {index} не найдено изображений.")

process_images_from_table(r"C:\fire\GEE_fire_6.csv")
