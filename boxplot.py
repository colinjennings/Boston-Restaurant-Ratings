import pandas as pd
import altair as alt

df = pd.read_csv("collect_data/boston_restaurants.csv")

# Keep the top 15 neighborhoods by restaurant counts
top = (
    df["neighborhood"].dropna()
    .loc[lambda s: s.str.strip() != ""]
    .value_counts()
    .head(15)
    .index.tolist()
)
df = df[df["neighborhood"].isin(top)]

# --- sort by descending restaurants
sort_order = top

# --- Selection ---
click_select = alt.selection_point(fields=["neighborhood"], on="click", empty="none")

# --- Invisible hit target ---
hit_target = alt.Chart(df).mark_rect(opacity=0, tooltip=False).encode(
    alt.X("neighborhood:N", sort=sort_order),
)

# --- Box plot layer ---
boxes = alt.Chart(df).mark_boxplot(size=40, outliers=False).encode(
    alt.X("neighborhood:N", title="Click a Neighborhood's Box", sort=sort_order,
          axis=alt.Axis(labelAngle=-35)),
    alt.Y("rating:Q", title="Rating", scale=alt.Scale(domain=[3.0, 5.0])),
    alt.Color("mean(price_level):Q", title="Mean Price Level",
              scale=alt.Scale(scheme="goldred")),
    opacity=alt.condition(click_select, alt.value(1.0), alt.value(0.3)),
    tooltip=alt.Tooltip("count():Q")
)

boxplot = alt.layer(hit_target, boxes).add_params(
    click_select
).properties(
    width="container",
    height=350
)


# --- Heat map panel: price level (bin) vs rating (bin), count of restaurants ---
heatmap = alt.Chart(df).mark_rect().encode(
    alt.X(
        "price_display:O",
        title="Price Level",
        axis=alt.Axis(labelAngle=0),
        scale=alt.Scale(domain=[1, 2, 3, 4])
    ),
    alt.Y(
        "rating_bin:O",
        title="Rating",
        sort="ascending",
        scale=alt.Scale(domain=["4.75", "4.50", "4.25", "4.00", "3.75", "3.50"])
    ),
    alt.Color(
        "count():Q",
        title="# Restaurants",
        scale=alt.Scale(scheme="tealblues", domainMin=0, domainMax=20),
        legend=alt.Legend(orient="right", title="# Restaurants")
    ),
    tooltip=[
        alt.Tooltip("price_display:O",  title="Price Level"),
        alt.Tooltip("rating_bin:O",     title="Rating (bin)"),
        alt.Tooltip("count():Q",        title="# Restaurants"),
    ]
).transform_filter(
    "datum.rating > 3.5 && datum.price_level != null && datum.price_level > 0"
).transform_calculate(
    price_display="datum.price_level",
).transform_bin(
    "rating_bin", field="rating", bin=alt.Bin(step=0.25, extent=[3.5,5.0])
).transform_calculate(
    rating_bin="format(datum.rating_bin, '.2f')"
).transform_filter(
    f"length(data('{click_select.name}_store')) > 0"
).transform_filter(
    click_select
).properties(
    title=alt.TitleParams(text="Price vs. Rating Heat Map in Selected Neighborhood", fontSize=16),
    width="container",
    height=300
)

# --- Stack vertically ---
chart = alt.vconcat(
    boxplot,
    heatmap
).resolve_scale(
    color="independent"
).configure_axis(
    grid=False,
    labelFontSize=14,
    titleFontSize=16
).configure_view(strokeWidth=0)

chart.save("website_output/boxplot.html", embed_options={'actions': False})