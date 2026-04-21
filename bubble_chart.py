import pandas as pd

df = pd.read_csv("collect_data/boston_restaurants.csv")

top = (
    df["neighborhood"].dropna()
    .loc[lambda s: s.str.strip() != ""]
    .value_counts()
    .head(15)
    .index.tolist()
)
df = df[df["neighborhood"].isin(top)]

agg = (
    df.groupby("neighborhood")
    .agg(
        avg_transit=("transit_minutes", "mean"),
        avg_reviews=("review_count", "mean"),
        count=("name", "count"),
    )
    .reset_index()
)

records = agg.to_dict(orient="records")

html = f"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    body {{
      font-family: "Segoe UI", sans-serif;
      background: #fafafa;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
    }}
    h2 {{
      margin-bottom: 4px;
      font-size: 18px;
      color: #222;
    }}
    p.subtitle {{
      font-size: 12px;
      color: #666;
      margin: 0 0 16px;
    }}
    .tooltip {{
      position: absolute;
      background: white;
      border: 1px solid #ccc;
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 13px;
      pointer-events: none;
      opacity: 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      line-height: 1.6;
    }}
    .axis-label {{
      font-size: 13px;
      fill: #000;
    }}
    circle:not(.legend-circle) {{
      stroke: white;
      stroke-width: 1.5;
      cursor: pointer;
      transition: opacity 0.2s;
    }}
    circle:not(.legend-circle):hover {{
      stroke: #333;
      stroke-width: 2;
    }}
    
  </style>
</head>
<body>
  
  <div class="tooltip" id="tooltip"></div>
  <svg id="chart"></svg>
  <script>
    const data = {records};

    // --- Dimensions ---------------------------------------------------------------------------
    const margin = {{ top: 40, right: 120, bottom: 60, left: 60 }};
    const W = window.innerWidth - 20;
    const H = window.innerHeight - 60;

    const w = W - margin.left - margin.right;
    const h = H - margin.top  - margin.bottom;

    const svg = d3.select("#chart")
      .attr("width",  W)
      .attr("height", H)
      .append("g")
      .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

    // --- Scales ------------------------------------------------------------------------------
    const xPad = 3;
    const xScale = d3.scaleLinear()
      .domain([
        d3.min(data, d => d.avg_transit) - xPad,
        d3.max(data, d => d.avg_transit) + xPad
      ])
      .range([0, w]);

    const yScale = d3.scaleLinear()
      .domain([325, d3.max(data, d => d.avg_reviews) ])
      .range([h, 0]);

    const rScale = d3.scaleSqrt()
      .domain([0, d3.max(data, d => d.count)])
      .range([8, 40]);

    const palette15 = [
      "#2f4f4f",
      "#8b4513",
      "#6b8e23",
      "#4b0082",
      "#ff0000",
      "#00ced1",
      "#ffa500",
      "#ffff00",
      "#00ff00",
      "#00fa9a",
      "#0000ff",
      "#d8bfd8",
      "#ff00ff",
      "#1e90ff",
      "#ff69b4",
    ];
    const color = d3.scaleOrdinal(palette15)
      .domain(data.map(d => d.neighborhood));

    // --- Gridlines ------------------------------------------------------------------------
    svg.append("g")
      .attr("class", "grid")
      .call(
        d3.axisLeft(yScale).tickSize(-w).tickFormat("")
      )
      .selectAll("line")
      .attr("stroke", "#e0e0e0");
    svg.selectAll(".grid .domain").remove();

    svg.append("g")
      .attr("class", "grid")
      .attr("transform", `translate(0,${{h}})`)
      .call(
        d3.axisBottom(xScale).tickSize(-h).tickFormat("")
      )
      .selectAll("line")
      .attr("stroke", "#e0e0e0");
    svg.selectAll(".grid .domain").remove();

    // --- Axes ------------------------------------------------------------------------
    svg.append("g")
      .attr("transform", `translate(0,${{h}})`)
      .call(d3.axisBottom(xScale).ticks(6).tickFormat(d => d + " min"));

    svg.append("g")
      .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => d3.format(",")(d)));

    // X label
    svg.append("text")
      .attr("class", "axis-label")
      .attr("x", w / 2)
      .attr("y", h + 48)
      .attr("text-anchor", "middle")
      .text("Average Transit Time (minutes)");

    // Y label
    svg.append("text")
      .attr("class", "axis-label")
      .attr("transform", "rotate(-90)")
      .attr("x", -h / 2)
      .attr("y", -48)
      .attr("text-anchor", "middle")
      .text("Average Review Count");

    // --- Tooltip ------------------------------------------------------------------
    const tooltip = d3.select("#tooltip");

    // --- Bubbles ------------------------------------------------------------------
    svg.selectAll("circle")
      .data(data)
      .join("circle")
        .attr("cx", d => xScale(d.avg_transit))
        .attr("cy", d => yScale(d.avg_reviews))
        .attr("r",  d => rScale(d.count))
        .attr("fill", d => color(d.neighborhood))
        .attr("opacity", 0.55)
      .on("mouseover", (event, d) => {{
        tooltip
          .style("opacity", 1)
          .html(`
            <strong>${{d.neighborhood}}</strong><br/>
            Avg. transit time: <b>${{d.avg_transit.toFixed(1)}} min</b><br/>
            Avg. review count: <b>${{d.avg_reviews.toFixed(0)}}</b><br/>
            Restaurant Count: <b>${{d.count}}</b>
          `);
      }})
      .on("mousemove", (event) => {{
        tooltip
          .style("left", (event.pageX + 14) + "px")
          .style("top",  (event.pageY - 28) + "px");
      }})
      .on("mouseout", () => tooltip.style("opacity", 0));

    // --- Labels ---------------------------------------------------------------
    svg.selectAll(".label")
      .data(data)
      .join("text")
        .attr("class", "label")
        .attr("x", d => xScale(d.avg_transit))
        .attr("y", d => yScale(d.avg_reviews)+4)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "black")
        .attr("font-weight", "bold")
        .attr("pointer-events", "none")
        .attr("transform", d => `rotate(20, ${{xScale(d.avg_transit)}}, ${{yScale(d.avg_reviews) + 4}})`)
        .text(d => d.neighborhood);

    // --- Size legend (50, 100, 200 restaurants displayed ) ---------------------
    const legendSizes = [50, 100, 200]; 
    const lx = w - 10, ly = 10; 

    svg.append("text")
      .attr("x", lx)
      .attr("y", ly - 8)
      .attr("text-anchor", "middle")
      .attr("font-size", "11px")
      .attr("fill", "#555")
      .text("# Restaurants");

    let offset = 0;
    legendSizes.forEach(s => {{
      const r = rScale(s);
      svg.append("circle")
        .attr("class", "legend-circle")
        .attr("cx", lx)
        .attr("cy", ly + offset + r)
        .attr("r", r)
        .attr("fill", "none")
        .attr("stroke", "#000");
        
      svg.append("text")
        .attr("x", lx + r + 6)
        .attr("y", ly + offset + r + 4)
        .attr("font-size", "10px")
        .attr("fill", "#666")
        .text(s);
      offset += r * 1.5 + 8;
    }});
  </script>
</body>
</html>
"""

# save the HTML file
with open("website_output/bubble_chart.html", "w", encoding="utf-8") as f:
    f.write(html)
