import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, LineString, Point, Polygon

def load_geojson(file_path):
    """Load GeoJSON file into a GeoDataFrame."""
    with open(file_path, 'r') as f:
        geojson_data = json.load(f)

    # Parse the features from GeoJSON data
    features = geojson_data["features"]

    # Extract geometries and properties
    geometries = [shape(feature["geometry"]) for feature in features]
    properties = [feature["properties"] for feature in features]

    # Handle geometries explicitly and create a DataFrame
    geometries_dict = [{'geometry': geom} for geom in geometries]
    properties_df = pd.DataFrame(properties)
    geometries_df = pd.DataFrame(geometries_dict)

    # Combine properties and geometries DataFrames
    combined_df = pd.concat([properties_df, geometries_df], axis=1)

    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(combined_df, geometry='geometry')
    
    return gdf

def prepare_data(file_path):
    """Prepare and save the categorized GeoDataFrames."""
    gdf = load_geojson(file_path)
    
    # Categorize the data
    roads_df = gdf[gdf['geometry'].apply(lambda x: isinstance(x, LineString)) & gdf['road'].notnull()]
    tolls_df = gdf[gdf['geometry'].apply(lambda x: isinstance(x, Polygon)) & gdf['toll'].notnull()]
    points_df = gdf[gdf['geometry'].apply(lambda x: isinstance(x, Point)) & gdf['points'].notnull()]

    # Save the DataFrames to CSV files for the simulation to use
    roads_df.to_csv('roads.csv', index=False)
    tolls_df.to_csv('tolls.csv', index=False)
    points_df.to_csv('points.csv', index=False)
    
    print("Data preparation complete. DataFrames saved to CSV files.")

if __name__ == "__main__":
    geojson_file_path = 'C:/Users/Dhanashree/OneDrive/Desktop/intel project/map.geojson'
    prepare_data(geojson_file_path)
