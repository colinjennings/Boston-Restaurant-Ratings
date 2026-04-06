import pandas as pd
import geopandas as gpd

df = pd.read_csv('boston_restaurants.csv')

neighborhoods_bos = gpd.read_file("boston_neighborhood_boundaries/Boston_Neighborhood_Boundaries.shp")
neighborhoods_cam = gpd.read_file("BOUNDARY_CDDNeighborhoods.shp")

gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df.longitude, df.latitude), 
    crs="EPSG:4326"
)

neighborhoods_bos = neighborhoods_bos.to_crs("EPSG:4326")
neighborhoods_cam = neighborhoods_cam.to_crs("EPSG:4326")

# First pass: Boston neighborhoods
result = gpd.sjoin(gdf, neighborhoods_bos[['name', 'geometry']], how='left', predicate='within')
gdf['neighborhood'] = result['name_right']

# Second pass: fill unmatched rows with Cambridge neighborhoods
unmatched = gdf['neighborhood'].isna()
result_cam = gpd.sjoin(gdf[unmatched], neighborhoods_cam[['NAME', 'geometry']], how='left', predicate='within')
gdf.loc[unmatched, 'neighborhood'] = result_cam['NAME']

df['neighborhood'] = gdf['neighborhood']
df.to_csv('boston_restaurants.csv', index=False)