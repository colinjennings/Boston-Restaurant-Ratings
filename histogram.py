
import pandas as pd
import altair as alt

# Load your dataset
df = pd.read_csv("collect_data/boston_restaurants.csv")  # replace with your actual filename

# Create histogram
chart = alt.Chart(df).mark_bar(opacity=0.85, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
    alt.X(
        "transit_minutes:Q",
        bin=alt.Bin(maxbins=30),
        title="Transit Time (minutes)"
    ),
    alt.Y(
        "count():Q",
        title="Number of Restaurants"
    ),
    alt.Color(
        "price_category:N",
        title="Price Category",
        scale=alt.Scale(scheme="tableau10")
    ),
    tooltip=[
        alt.Tooltip("transit_minutes:Q", bin=True, title="Transit Time Range"),
        alt.Tooltip("count():Q", title="Count"),
        alt.Tooltip("price_category:N", title="Price Category")
    ]
).properties(
    title=alt.TitleParams(
        text="Distribution of Transit Times to Boston Restaurants",
        subtitle="From university, grouped by price category",
        fontSize=16,
        subtitleFontSize=12
    ),
    width=600,
    height=350
).configure_axis(
    grid=False,
    labelFontSize=12,
    titleFontSize=13
).configure_legend(
    titleFontSize=12,
    labelFontSize=11
).configure_view(
    strokeWidth=0  # removes border around chart
)


chart.save("website_output/transit_histogram.html")