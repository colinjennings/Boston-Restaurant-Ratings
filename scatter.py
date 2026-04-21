import altair as alt
import pandas as pd

df = pd.read_csv('collect_data/boston_restaurants.csv')

# drop rows with no price info
df = df.dropna(subset=['price_category'])

# base scatter plot
points = alt.Chart(df).mark_circle(size=60, opacity=0.85).encode(
    x=alt.X('rating:Q', title='Rating', scale=alt.Scale(domain=[2.9, 5.1])),
    y=alt.Y('review_count:Q', title='Number of Reviews', scale=alt.Scale(type='log')),
    color=alt.Color(
        "price_category:N",
        title="Price Category",
        scale=alt.Scale(
            domain=['$', '$$', '$$$', '$$$$'],
            range=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728']
        )
    ),
    tooltip=['name', 'rating', 'review_count', 'price_category',
             'neighborhood', 'transit_minutes']
).properties(
    width="container",
    height=400
).interactive()

# regression line
line = alt.Chart(df).mark_line(color='black', strokeDash=[5, 5]).transform_regression(
    'rating', 'review_count'
).encode(
    x='rating:Q',
    y=alt.Y('review_count:Q', scale=alt.Scale(type='log'))
)

chart = points + line

chart.save('website_output/scatter_plot.html', embed_options={'actions': False})