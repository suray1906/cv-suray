import subprocess
import pandas as pd

def run_wind_ninja(elevation_file, output_path, wind_speed, wind_direction):
    command = [
        "C:\\WindNinja\\WindNinja-3.8.0\\bin\\WindNinja_cli.exe",
        "--num_threads", "4",
        "--elevation_file", elevation_file,
        "--initialization_method", "domainAverageInitialization",
        "--time_zone", "auto-detect",
        "--input_speed", str(wind_speed),
        "--input_speed_units", "mps",
        "--output_speed_units", "mps",
        "--input_direction", str(wind_direction),
        "--uni_air_temp", "25",
        "--air_temp_units", "C",
        "--input_wind_height", "10",
        "--units_input_wind_height", "m",
        "--output_wind_height", "10",
        "--units_output_wind_height", "m",
        "--mesh_resolution", "30",
        "--units_mesh_resolution", "m",
        "--write_ascii_output", "true",
        "--ascii_out_resolution", "30",
        "--units_ascii_out_resolution", "m",
       # "--write_shapefile_output", "true",
        #"--shape_out_resolution", "-1",
       # "--units_shape_out_resolution", "m",
       # "--write_pdf_output", "true",
      #  "--units_pdf_out_resolution", "m",
       # "--output_path", output_path,
        "--number_of_iterations", "300"
    ]

    subprocess.run(command, check=True)


wind_data = pd.read_csv('D:\\Fire_Data\\wind.csv', sep=';', parse_dates=[0])

print(wind_data.columns)
print(wind_data.to_string())

elevation_file = "D:\\Fire_Data\\150\\68151_utm.tif"
output_path = "D:\\Fire_Data\\150"

for i, row in wind_data.iterrows():
    wind_speed = row['speed(m/s)']
    wind_direction = row['dir']
    run_wind_ninja(elevation_file, output_path, wind_speed, wind_direction)
