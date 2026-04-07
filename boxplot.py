import pandas as pd
import altair as alt

# Load your dataset
df = pd.read_csv("collect_data/boston_restaurants.csv")

# Filter out missing neighborhoods, keep top 15 by restaurant count
top = (
    df["neighborhood"].dropna()
    .loc[lambda s: s.str.strip() != ""]
    .value_counts()
    .head(15)
    .index.tolist()
)
df = df[df["neighborhood"].isin(top)]

# --- Sort order: by descending restaurant count ---
sort_order = top  # value_counts() already returns descending order

# --- Selection ---
click_select = alt.selection_point(fields=["neighborhood"], on="click", empty="none")

# --- Invisible hit target ---
hit_target = alt.Chart(df).mark_rect(opacity=0, tooltip=False).encode(
    alt.X("neighborhood:N", sort=sort_order),
)

# --- Box plot layer ---
boxes = alt.Chart(df).mark_boxplot(size=40, outliers=False).encode(
    alt.X("neighborhood:N", title="Neighborhood", sort=sort_order,
          axis=alt.Axis(labelAngle=-35)),
    alt.Y("rating:Q", title="Rating", scale=alt.Scale(domain=[3.0, 5.0])),
    alt.Color("mean(price_level):Q", title="Mean Price Level",
              scale=alt.Scale(scheme="goldred")),
    opacity=alt.condition(click_select, alt.value(1.0), alt.value(0.3)),
    tooltip=alt.Tooltip("count():Q")
)

boxplot = alt.layer(hit_target, boxes).add_params(
    click_select
).properties(width=650, height=350)

# --- Scatter plot panel: price level vs rating ---
scatter = alt.Chart(df).mark_point(filled=True, size=80).encode(
    alt.X("jittered_price:Q", title="Price Level", scale=alt.Scale(domain=[-0.5, 4.5]),
          axis=alt.Axis(values=[0, 1, 2, 3, 4], labelExpr="datum.value === 0 ? 'N/A' : datum.value")),
    alt.Y("rating:Q", title="Rating", scale=alt.Scale(domain=[3.0, 5.0])),
    alt.Color("neighborhood:N", legend=None, scale=alt.Scale(scheme="tableau10")),
    tooltip=[
        alt.Tooltip("name:N",        title="Restaurant"),
        alt.Tooltip("rating:Q",      title="Rating"),
        alt.Tooltip("price_level:Q", title="Price Level"),
        alt.Tooltip("review_count:Q", title="# Reviews"),
    ]
).transform_filter(
    "datum.rating > 3"
).transform_calculate(
    price_display="datum.price_level == null ? 0 : datum.price_level",
    jittered_price="(datum.price_level == null ? 0 : datum.price_level) + (random() - 0.5) * 0.45"
).transform_filter(
    click_select
).properties(
    title=alt.TitleParams(text="Price vs. Rating in Selected Neighborhood", fontSize=13),
    width=650,
    height=250
)

# --- Stack vertically ---
chart = alt.vconcat(
    boxplot,
    scatter
).properties(
    title=alt.TitleParams(
        text="Restaurant Ratings by Neighborhood",
        subtitle="Sorted by restaurant count — click a box to see price vs. rating",
        fontSize=16,
        subtitleFontSize=12
    )
).configure_axis(
    grid=False,
    labelFontSize=11,
    titleFontSize=13
).configure_view(strokeWidth=0)

chart.save("website_output/boxplot.html")