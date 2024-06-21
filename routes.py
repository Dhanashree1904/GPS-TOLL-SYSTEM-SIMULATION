import geopandas as gpd
import os

# Load the GeoJSON data
geojson_file = r'C:\Users\Admin\Desktop\Intel Project\map.geojson'
data = gpd.read_file(geojson_file)

# Extract roads, tolls, and points
roads = data[data['geometry'].apply(lambda x: x.geom_type == 'LineString')]
tolls = data[data['geometry'].apply(lambda x: x.geom_type == 'Polygon')]
points = data[data['geometry'].apply(lambda x: x.geom_type == 'Point')]

# Save to GeoPackage
output_path = r'C:\Users\Admin\Desktop\Intel Project'  # Base directory for saving the GeoPackage files
roads.to_file(os.path.join(output_path, 'roads.gpkg'), layer='roads', driver='GPKG')
tolls.to_file(os.path.join(output_path, 'tolls.gpkg'), layer='tolls', driver='GPKG')
points.to_file(os.path.join(output_path, 'points.gpkg'), layer='points', driver='GPKG')

print("GeoPackage files created successfully.")
