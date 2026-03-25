import requests
import pandas as pd
import time
import geopy.distance
from tqdm import tqdm

SELECTION_RADIUS_MI = 10

API_KEY = ""

"""
Many of the resturants collected during the API calling are not relevant (perhaps they are not within Boston or have too few reviews.)

Another function of this file is to calculate transit time using Google Distance Matrix API
"""


df = pd.read_csv('boston_restaurants_raw.csv')

# covnert types to list of strings
df['types'] = df['types'].str.split(', ')

# filter the list to only include restruants with at least one of these types
keywords = {'restaurant', 'bar', 'cafe', 'bakery'}
df_filtered = df[df['types'].apply(lambda x: bool(keywords & set(x)))]

# remove entries with these keywords
remove_keywords = {'night_club','gas_station','city_hall'}
df_filtered = df_filtered[~df_filtered['types'].apply(lambda x: bool(set(remove_keywords) & set(x)))]

# only keep entries where the review_count is > 50
df_filtered = df_filtered[df_filtered['review_count'].notna() & (df_filtered['review_count'] >= 50)].copy()

# create columns 'bar', 'cafe', 'resturant', 'bakery' and label them true/false accordingly
for res_type in ['bar', 'cafe', 'restaurant', 'bakery']:
    df_filtered[res_type] = df_filtered['types'].apply(lambda x: res_type in x)

# measure distance from the NEU sign!
NEU_coords = (42.340313, -71.088449)

# remove anything greater than 20 miles from NEU
df_filtered = df_filtered[
    df_filtered.apply(lambda row: geopy.distance.geodesic(NEU_coords, (row['latitude'], row['longitude'])).mi <= SELECTION_RADIUS_MI, axis=1)
].copy()


# use the API to get travel time by public transport
def get_transit_times_batch(dest_coords, origin_lat, origin_lon, api_key):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": f"{origin_lat},{origin_lon}",
        "destinations": "|".join(f"{lat},{lon}" for lat, lon in dest_coords),
        "mode": "transit",
        "departure_time": "now",
        "key": api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    result = response.json()

    if result['status'] != 'OK':
        print(f"API error: {result['status']}")
        return [None] * len(dest_coords)

    return [
        el['duration']['value'] / 60 if el['status'] == 'OK' else None
        for el in result['rows'][0]['elements']
    ]

# the origin is the NEU sign
origin_lat, origin_lon = NEU_coords[0], NEU_coords[1]

coords = list(zip(df_filtered['latitude'], df_filtered['longitude']))
batch_size = 25
results = []

# this is a simple ticker that lets you watch it
for i in tqdm(range(0, len(coords), batch_size)):
    batch = coords[i:i+batch_size]
    try:
        results.extend(get_transit_times_batch(batch, origin_lat, origin_lon, API_KEY))
    except Exception as e:
        print(f"Batch {i//batch_size} failed: {e}")
        results.extend([None] * len(batch))
    time.sleep(0.1)

df_filtered['transit_minutes'] = results


print(f"Filtered length: {len(df_filtered)}")
df_filtered.to_csv('boston_restaurants.csv')