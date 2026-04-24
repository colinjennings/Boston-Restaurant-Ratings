import altair as alt
import pandas as pd

df = pd.read_csv('collect_data/boston_restaurants.csv')
# drop rows with no price info
df = df.dropna(subset=['price_category'])

# get only the section of line in the region we are plotting
base = alt.Chart(df.query('3.2 <= rating <= 5.0'))

# band the confidence interval
band = base.mark_area(opacity=0.3).transform_aggregate(
    mean_reviews='mean(review_count)',
    se_reviews='stderr(review_count)',
    groupby=['rating']
).transform_calculate(
    ci_upper='datum.mean_reviews + 1.96 * datum.se_reviews',
    ci_lower='datum.mean_reviews - 1.96 * datum.se_reviews',
    label='"95% confidence interval"'
).encode(
    x=alt.X('rating:Q', title='Rating', scale=alt.Scale(domain=[3.2, 5])),
    y=alt.Y('ci_lower:Q', title='Number of Reviews', scale=alt.Scale(domain=[0, 1000])),
    y2=alt.Y2('ci_upper:Q'),
    color=alt.Color('label:N', scale=alt.Scale(
        domain=['Mean review count', '95% confidence interval'],
        range=['black', '#1f77b4']
    ), title=None)
)

# add the line
line = base.mark_line(strokeDash=[5, 5]).transform_aggregate(
    mean_reviews='mean(review_count)',
    groupby=['rating']
).transform_calculate(
    label='"Mean review count"'
).encode(
    x=alt.X('rating:Q', title='Rating', scale=alt.Scale(domain=[3.2, 5])),
    y=alt.Y('mean_reviews:Q', title='Number of Reviews', scale=alt.Scale(domain=[0, 1000])),
    color=alt.Color('label:N', scale=alt.Scale(
        domain=['Mean review count', '95% confidence interval'],
        range=['black', '#1f77b4']
    ), title=None)
)

# combine the plots and scale it to container width
chart = (band + line).properties(
    width="container",
    height=400
)

chart.save('website_output/line_plot.html', embed_options={'actions': False})