import ee
import pandas as pd
from datetime import datetime, timedelta

# Initialize Google Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-suray1906firefire')

def load_and_filter_image_collection(row):
    """Load and filter Sentinel-2 image collection based on a dataframe row."""
    # Define the geometry of interest.
    geometry = ee.Geometry.Rectangle([row['x_min'], row['y_min'], row['x_max'], row['y_max']])

    # Load the Sentinel-2 ImageCollection.
    s2 = ee.ImageCollection('COPERNICUS/S2') \
        .filterDate(row['dt_start'], row['dt_end']) \
        .filterBounds(geometry) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))

    return s2

def calculate_nbr(image):
    """Calculate the NBR (Normalized Burn Ratio) index from an image."""
    nbr = image.expression(
        '(B12 - B8A - B3 - B2) / (B12 + B8A + B3 + B2)',
        {
            'B2': image.select('B2'),  # Красный
            'B3': image.select('B3'),  # Зелёный
            'B8A': image.select('B8A'),  # Железо-2
            'B12': image.select('B12')  # SWIR
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
                image=image.select(['B4', 'B11', 'B2']),
                description=f"{description_prefix}_RGB_Image_S2_{image_id}_{index}",
                scale=20,
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
                description=f"{description_prefix}_NBR_Image_S2_{image_id}_{index}",
                scale=20,
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
        s2 = load_and_filter_image_collection(row)
        num_images = s2.size().getInfo()
        fire_number = row['fire_id']
        
        if num_images > 0:
            image_list = s2.sort('system:time_start').toList(num_images)
            
            # Export each image in both RGB and NBR format
            for i in range(num_images):
                image = ee.Image(image_list.get(i))
                export_image(image, i, fire_number, geometry, "RGB")
                export_image(image, i, fire_number, geometry, "NBR")
            
            # Export one additional image between dt_end and dt_end + 20 days if available
            end_date = datetime.strptime(row['dt_end'], '%Y-%m-%d')
            post_end_date = end_date + timedelta(days=20)
            additional_images = ee.ImageCollection('COPERNICUS/S2') \
                .filterDate(row['dt_end'], post_end_date.strftime('%Y-%m-%d')) \
                .filterBounds(geometry) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
                .sort('system:time_start')
            
            if additional_images.size().getInfo() > 0:
                additional_image = ee.Image(additional_images.first())
                export_image(additional_image, 'final', fire_number, geometry, "RGB")
                export_image(additional_image, 'final', fire_number, geometry, "NBR")
            else:
                print(f"No additional image found for {fire_number} in the range {row['dt_end']} to {post_end_date}")
        else:
            print(f"Для {fire_number} с номером строки {index} не найдено изображений.")

# Example call (comment out in production)
process_images_from_table(r"C:\fire\GEE_fire_6.csv")
