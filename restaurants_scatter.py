import altair as alt
import pandas as pd

df = pd.read_csv('boston_restaurants.csv')

# drop rows with no price info
df = df.dropna(subset=['price_category'])

scatter = alt.Chart(df).mark_circle(size=60).encode(
    x=alt.X('rating:Q', title='Rating'),
    y=alt.Y('review_count:Q', title='Number of Reviews'),
    color=alt.Color('price_category:N', title='Price Level'),
    tooltip=['name', 'rating', 'review_count', 'price_category', 'neighborhood']
).properties(
    title='Rating vs Number of Reviews',
    width=600,
    height=400
).interactive()

scatter.save('scatter_plot.html')
print("done")
