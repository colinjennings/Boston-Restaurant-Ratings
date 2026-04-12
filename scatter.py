import altair as alt
import pandas as pd

df = pd.read_csv('collect_data/boston_restaurants.csv')

# drop rows with no price info
df = df.dropna(subset=['price_category'])

# base scatter plot
points = alt.Chart(df).mark_circle(size=60, opacity=0.6).encode(
    x=alt.X('rating:Q', title='Rating', scale=alt.Scale(domain=[3.0, 5.0])),
    y=alt.Y('review_count:Q', title='Number of Reviews'),
    color=alt.Color('price_level:Q', title='Price Level',
                    scale=alt.Scale(scheme='orangered')),
    tooltip=['name', 'rating', 'review_count', 'price_category',
             'neighborhood', 'transit_minutes']
).properties(
    width=450,
    height=400
).interactive()

# regression line
line = alt.Chart(df).mark_line(color='black', strokeDash=[5, 5]).transform_regression(
    'rating', 'review_count'
).encode(
    x='rating:Q',
    y='review_count:Q'
)

chart = points + line

chart.save('website_output/scatter_plot.html', embed_options={'actions': False})

