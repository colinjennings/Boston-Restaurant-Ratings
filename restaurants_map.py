import folium
import pandas as pd

df = pd.read_csv('collect_data/boston_restaurants.csv')

# make map centered on boston, using a different tile set
boston_map = folium.Map(
    location=[42.36, -71.06],
    zoom_start=12,
    tiles="CartoDB positron"
    )

# add a marker for each restaurant, colored by price
for i, row in df.iterrows():
    price = row.get('price_category', '')

    if price == '$':
        color = '#2ca02c'
    elif price == '$$':
        color = '#1f77b4'
    elif price == '$$$':
        color = '#ff7f0e'
    elif price == '$$$$':
        color = '#d62728'
    else:
        color = 'gray'

    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=4,
        color=color,
        fill=True,
        fill_opacity=0.85,
        popup=f"{row['name']} - {row['rating']} stars - {price}",
        tooltip=row['name']
    ).add_to(boston_map)

boston_map.save('website_output/boston_map.html')
print("done")
