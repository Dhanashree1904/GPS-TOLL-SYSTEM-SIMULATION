import geopandas as gpd

# Load the GeoJSON data
geojson_file = 'C:/Users/Dhanashree/OneDrive/Desktop/intel project/map.geojson'
data = gpd.read_file(geojson_file)

# Extract roads, tolls, and points
roads = data[data['geometry'].apply(lambda x: x.geom_type == 'LineString')]
tolls = data[data['geometry'].apply(lambda x: x.geom_type == 'Polygon')]
points = data[data['geometry'].apply(lambda x: x.geom_type == 'Point')]

# Save to GeoPackage
roads.to_file('roads.gpkg', layer='roads', driver='GPKG')
tolls.to_file('tolls.gpkg', layer='tolls', driver='GPKG')
points.to_file('points.gpkg', layer='points', driver='GPKG')
