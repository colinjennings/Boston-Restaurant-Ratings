import folium
import pandas as pd

df = pd.read_csv('boston_restaurants.csv')

# make map centered on boston
boston_map = folium.Map(location=[42.36, -71.06], zoom_start=12)

# add a marker for each restaurant, colored by price
for i, row in df.iterrows():
    price = row.get('price_category', '')

    if price == '$':
        color = 'green'
    elif price == '$$':
        color = 'blue'
    elif price == '$$$':
        color = 'orange'
    elif price == '$$$$':
        color = 'red'
    else:
        color = 'gray'

    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=4,
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=f"{row['name']} - {row['rating']} stars - {price}",
        tooltip=row['name']
    ).add_to(boston_map)

boston_map.save('boston_map.html')
print("done")
