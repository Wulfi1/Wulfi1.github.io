const fmt = d3.format(",");
const pct = d3.format(".1%");

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

const files = {
  summary: "data/summary.json",
  annual: "data/annual_reports.json",
  heatmap: "data/month_hour.json",
  shapes: "data/shape_counts.json",
  shapeDecades: "data/shape_by_decade.json",
  countries: "data/country_counts.json",
  states: "data/state_counts.json",
  cities: "data/city_counts.json",
  durationShapes: "data/duration_by_shape.json",
  durationEras: "data/duration_by_era_shape.json",
  area51: "data/area51_summary.json",
  hotspots: "data/hotspots.json",
  hexDecades: "data/hex_decade_bins.json",
  land: "data/land-110m.json"
};

const colors = {
  ink: "#17201d",
  muted: "#62706c",
  paper: "#f7f4ee",
  panel: "#fffdf8",
  line: "#d8d0c2",
  teal: "#117c78",
  coral: "#d65d47",
  gold: "#d99a2b",
  brown: "#8d6b2f",
  blue: "#3f6f9f",
  night: "#1c2430"
};

const plotConfig = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d"]
};

Promise.all(Object.values(files).map((path) => d3.json(path))).then((loaded) => {
  const data = Object.fromEntries(Object.keys(files).map((key, index) => [key, loaded[index]]));
  renderMetrics(data.summary);
  renderHeroMap(data.land, data.hotspots);
  renderShapeBars(data.shapes);
  renderShapeGroupStack(data.shapes);
  renderAnnualLine(data.annual);
  renderAnnotatedAnnual(data.annual);
  renderHeatmap(data.heatmap);
  renderStateSection(data.states);
  renderCityBars(data.cities);
  renderArea51(data.area51);
  renderDurationBars(data.durationShapes);
  renderDurationBoxplot(data.durationShapes);
  renderEraCards(data.durationEras);
  renderWords(data.summary.top_words);
  renderCountryBars(data.countries);
  renderHotspotMap(data.hexDecades, data.hotspots);
});

function baseLayout(selector, extra = {}) {
  const el = document.querySelector(selector);
  const height = Math.max(280, el?.clientHeight || 340);
  return {
    height,
    autosize: true,
    paper_bgcolor: colors.panel,
    plot_bgcolor: colors.panel,
    font: { family: "Inter, system-ui, sans-serif", color: colors.ink },
    margin: { t: 18, r: 20, b: 48, l: 78 },
    hoverlabel: {
      bgcolor: colors.ink,
      bordercolor: colors.ink,
      font: { color: "#fffdf6" }
    },
    ...extra
  };
}

function plot(selector, traces, layout, config = {}) {
  const el = document.querySelector(selector);
  if (!el || !window.Plotly) return;
  Plotly.react(el, traces, layout, { ...plotConfig, ...config });
}

function renderMetrics(summary) {
  const items = [
    { value: fmt(summary.clean_rows), label: "clean report rows" },
    { value: pct(summary.us_report_share), label: "of reports are coded as United States" },
    { value: `${summary.date_range.min_year}-${summary.date_range.max_year}`, label: "actual raw date range" },
    { value: summary.top_shape.shape, label: `${fmt(summary.top_shape.reports)} reports, most common shape` }
  ];

  d3.select("#summary-metrics")
    .selectAll(".metric")
    .data(items)
    .join("div")
    .attr("class", "metric")
    .html((d) => `<strong>${d.value}</strong><span>${d.label}</span>`);
}

function sizeSvg(selector) {
  const svg = d3.select(selector);
  const node = svg.node();
  const box = node.getBoundingClientRect();
  const width = Math.max(320, box.width || node.clientWidth || 800);
  const height = Math.max(300, box.height || parseInt(svg.style("min-height"), 10) || 360);
  svg.attr("viewBox", [0, 0, width, height]);
  return { svg, width, height };
}

function renderHeroMap(land, hotspots) {
  const { svg, width, height } = sizeSvg("#hero-map");
  const projection = d3.geoNaturalEarth1().fitSize([width, height], topojson.feature(land, land.objects.land));
  const path = d3.geoPath(projection);
  const max = d3.max(hotspots, (d) => d.total_reports);
  const radius = d3.scaleSqrt().domain([1, max]).range([1.5, 18]);

  svg.append("path")
    .datum({ type: "Sphere" })
    .attr("fill", "#202b38")
    .attr("d", path);

  svg.append("path")
    .datum(topojson.feature(land, land.objects.land))
    .attr("fill", "#314253")
    .attr("d", path);

  svg.append("g")
    .attr("opacity", 0.75)
    .selectAll("circle")
    .data(hotspots.slice(0, 520))
    .join("circle")
    .attr("cx", (d) => projection([d.lon, d.lat])?.[0])
    .attr("cy", (d) => projection([d.lon, d.lat])?.[1])
    .attr("r", (d) => radius(d.total_reports))
    .attr("fill", "#f2b24b")
    .attr("stroke", "#fff4d8")
    .attr("stroke-width", 0.5)
    .attr("fill-opacity", 0.42);
}

function shortDuration(seconds) {
  if (seconds >= 3600) return `${d3.format(".1f")(seconds / 3600)}h`;
  if (seconds >= 60) return `${d3.format(".0f")(seconds / 60)}m`;
  return `${d3.format(".0f")(seconds)}s`;
}

function renderShapeBars(data) {
  const top = data.slice(0, 10).reverse();
  plot("#shape-bars", [{
    type: "bar",
    orientation: "h",
    x: top.map((d) => d.reports),
    y: top.map((d) => d.shape),
    marker: { color: colors.teal },
    hovertemplate: "<b>%{y}</b><br>%{x:,} reports<extra></extra>"
  }], baseLayout("#shape-bars", {
    margin: { t: 8, r: 20, b: 42, l: 86 },
    xaxis: { title: "reports", tickformat: "~s", gridcolor: "#eee7da", zeroline: false },
    yaxis: { automargin: true }
  }));
}

function renderShapeGroupStack(shapes) {
  const groups = [
    { label: "lights / flashes", shapes: ["light", "fireball", "flash"], fill: colors.coral },
    { label: "round forms", shapes: ["circle", "sphere", "disk", "oval", "egg"], fill: colors.teal },
    { label: "uncertain labels", shapes: ["unknown", "other", "changing", "formation", "teardrop"], fill: colors.brown },
    { label: "structured forms", shapes: ["triangle", "rectangle", "diamond", "chevron", "cylinder", "cigar", "cross", "cone"], fill: colors.blue }
  ];
  const counts = new Map(shapes.map((d) => [d.shape, d.reports]));
  const total = d3.sum(shapes, (d) => d.reports);
  const rows = groups
    .map((group) => ({
      ...group,
      reports: d3.sum(group.shapes, (shape) => counts.get(shape) || 0)
    }))
    .sort((a, b) => b.reports - a.reports);

  plot("#shape-group-stack", rows.map((row) => ({
    type: "bar",
    orientation: "h",
    name: row.label,
    x: [row.reports],
    y: ["Grouped labels"],
    marker: { color: row.fill },
    customdata: [[pct(row.reports / total), row.shapes.join(", ")]],
    hovertemplate: `<b>${row.label}</b><br>%{x:,} reports<br>%{customdata[0]} of archive<br><span style="font-size:11px">%{customdata[1]}</span><extra></extra>`
  })), baseLayout("#shape-group-stack", {
    barmode: "stack",
    margin: { t: 6, r: 14, b: 44, l: 108 },
    xaxis: { title: "reports", tickformat: "~s", gridcolor: "#eee7da", zeroline: false },
    yaxis: { showgrid: false },
    legend: { orientation: "h", y: -0.22, x: 0 }
  }));
}

function renderLabeledBars(selector, data, options) {
  plot(selector, [{
    type: "bar",
    orientation: "h",
    x: data.map(options.value),
    y: data.map(options.label),
    text: data.map(options.valueLabel),
    textposition: "outside",
    cliponaxis: false,
    marker: { color: options.fill || colors.teal },
    customdata: data.map(options.customData || (() => [])),
    hovertemplate: options.hovertemplate || "<b>%{y}</b><br>%{x:,}<extra></extra>"
  }], baseLayout(selector, {
    margin: options.margin || { t: 8, r: 64, b: 42, l: 106 },
    xaxis: {
      title: options.xLabel || "",
      tickformat: options.tickFormat || "~s",
      gridcolor: "#eee7da",
      zeroline: false,
      ...(options.xAxis || {})
    },
    yaxis: { automargin: true },
    showlegend: false
  }));
}

function renderAnnualLine(data) {
  let mode = "linear";
  const buttons = d3.selectAll("[data-annual-scale]");
  buttons.on("click", function () {
    mode = this.dataset.annualScale;
    buttons.classed("active", function () { return this.dataset.annualScale === mode; });
    draw();
  });

  function draw() {
    const maxY = d3.max(data, (d) => d.reports) || 1;
    const y = mode === "log" ? data.map((d) => Math.max(1, d.reports)) : data.map((d) => d.reports);
    plot("#annual-line", [{
      type: "scatter",
      mode: "lines+markers",
      x: data.map((d) => d.year),
      y,
      customdata: data.map((d) => d.reports),
      line: { color: colors.coral, width: 3, shape: "spline" },
      marker: { color: colors.coral, size: 5 },
      hovertemplate: "<b>%{x}</b><br>%{customdata:,} reports<extra></extra>"
    }], baseLayout("#annual-line", {
      margin: { t: 18, r: 24, b: 48, l: 58 },
      xaxis: {
        title: "year",
        tickformat: "d",
        gridcolor: "#eee7da",
        zeroline: false
      },
      yaxis: {
        title: "reports",
        type: mode === "log" ? "log" : "linear",
        range: mode === "log" ? [0, Math.log10(maxY * 1.25)] : [0, maxY * 1.08],
        tickformat: "~s",
        gridcolor: "#eee7da",
        zeroline: false
      },
      shapes: [{
        type: "rect",
        xref: "x",
        yref: "paper",
        x0: 1995,
        x1: 2005,
        y0: 0,
        y1: 1,
        fillcolor: "#f2d49c",
        opacity: 0.45,
        line: { width: 0 },
        layer: "below"
      }],
      annotations: [{
        x: 1996,
        y: 0.96,
        xref: "x",
        yref: "paper",
        text: mode === "log" ? "online reporting era (log scale)" : "online reporting era",
        showarrow: false,
        xanchor: "left",
        font: { color: "#7a5d2a", size: 12 }
      }]
    }));
  }

  draw();
}

function renderAnnotatedAnnual(data) {
  const maxY = d3.max(data, (d) => d.reports) || 1;
  plot("#annual-annotated", [{
    type: "scatter",
    mode: "lines",
    x: data.map((d) => d.year),
    y: data.map((d) => d.reports),
    fill: "tozeroy",
    line: { color: colors.blue, width: 2.5, shape: "spline" },
    fillcolor: "rgba(63, 111, 159, 0.16)",
    hovertemplate: "<b>%{x}</b><br>%{y:,} reports<extra></extra>"
  }], baseLayout("#annual-annotated", {
    margin: { t: 16, r: 22, b: 48, l: 62 },
    xaxis: { title: "year", tickformat: "d", gridcolor: "#eee7da", zeroline: false },
    yaxis: { title: "reports", range: [0, maxY * 1.12], tickformat: "~s", gridcolor: "#eee7da", zeroline: false },
    shapes: [
      { type: "line", xref: "x", yref: "paper", x0: 1982, x1: 1982, y0: 0, y1: 0.55, line: { color: colors.gold, width: 2, dash: "dot" } },
      { type: "line", xref: "x", yref: "paper", x0: 1993.7, x1: 1993.7, y0: 0, y1: 1, line: { color: colors.ink, width: 2 } },
      { type: "line", xref: "x", yref: "paper", x0: 1995, x1: 1995, y0: 0, y1: 1, line: { color: colors.coral, width: 2, dash: "dash" } }
    ],
    annotations: [
      { x: 1982, y: 0.56, xref: "x", yref: "paper", text: "E.T.", showarrow: false, yanchor: "bottom", font: { color: colors.gold, size: 12 } },
      { x: 1993.7, y: 0.98, xref: "x", yref: "paper", text: "The X-Files premiere", showarrow: false, xanchor: "left", font: { color: colors.ink, size: 12 } },
      { x: 1995, y: 0.84, xref: "x", yref: "paper", text: "1995 reporting split", showarrow: false, xanchor: "left", font: { color: colors.coral, size: 12 } }
    ]
  }));
}

function renderHeatmap(data) {
  const byKey = new Map(data.map((d) => [`${d.month}:${d.hour}`, d.reports]));
  const z = d3.range(1, 13).map((month) => d3.range(24).map((hour) => byKey.get(`${month}:${hour}`) || 0));
  plot("#heatmap", [{
    type: "heatmap",
    x: d3.range(24),
    y: monthNames,
    z,
    colorscale: "YlOrRd",
    reversescale: true,
    colorbar: { title: "reports", tickformat: "~s" },
    hovertemplate: "<b>%{y}, %{x}:00</b><br>%{z:,} reports<extra></extra>"
  }], baseLayout("#heatmap", {
    margin: { t: 24, r: 76, b: 48, l: 48 },
    xaxis: { title: "hour of day", dtick: 3, gridcolor: "#eee7da" },
    yaxis: { title: "month", autorange: "reversed" }
  }));
}

function renderStateSection(states) {
  let mode = "reports";
  const buttons = d3.selectAll("[data-state-mode]");
  buttons.on("click", function () {
    mode = this.dataset.stateMode;
    buttons.classed("active", function () { return this.dataset.stateMode === mode; });
    draw();
  });

  function drawBars() {
    const top = [...states].sort((a, b) => d3.descending(a[mode], b[mode])).slice(0, 12).reverse();
    renderLabeledBars("#state-bars", top, {
      label: (d) => d.state,
      value: (d) => d[mode],
      valueLabel: (d) => mode === "reports" ? fmt(d.reports) : d3.format(".0f")(d.reports_per_million),
      fill: mode === "reports" ? colors.blue : colors.coral,
      margin: { t: 8, r: 58, b: 44, l: 54 },
      tickFormat: mode === "reports" ? "~s" : ".0f",
      xLabel: mode === "reports" ? "reports" : "reports per million",
      customData: (d) => [d.state_name, d.reports, d.reports_per_million],
      hovertemplate: "<b>%{customdata[0]}</b><br>%{customdata[1]:,} reports<br>%{customdata[2]:.0f} per million<extra></extra>"
    });
  }

  function drawMap() {
    const values = states.map((d) => d[mode]);
    plot("#state-map", [{
      type: "choropleth",
      locationmode: "USA-states",
      locations: states.map((d) => d.state),
      z: values,
      text: states.map((d) => d.state_name),
      customdata: states.map((d) => [d.reports, d.reports_per_million]),
      colorscale: mode === "reports" ? "Blues" : "OrRd",
      reversescale: true,
      marker: { line: { color: "#ffffff", width: 0.7 } },
      colorbar: { title: mode === "reports" ? "reports" : "per million", tickformat: "~s" },
      hovertemplate: mode === "reports"
        ? "<b>%{text}</b><br>%{customdata[0]:,} reports<extra></extra>"
        : "<b>%{text}</b><br>%{customdata[1]:.0f} reports per million<br>%{customdata[0]:,} reports<extra></extra>"
    }], baseLayout("#state-map", {
      margin: { t: 8, r: 6, b: 4, l: 6 },
      geo: {
        scope: "usa",
        bgcolor: colors.panel,
        lakecolor: colors.panel,
        landcolor: "#efeae0",
        showlakes: false
      }
    }));
  }

  function draw() {
    drawBars();
    drawMap();
  }

  draw();
}

function renderCityBars(cities) {
  const top = cities.slice(0, 12).reverse();
  renderLabeledBars("#city-bars", top, {
    label: (d) => `${d.city}, ${d.state}`,
    value: (d) => d.reports,
    valueLabel: (d) => fmt(d.reports),
    fill: colors.coral,
    margin: { t: 8, r: 58, b: 42, l: 128 },
    tickFormat: "~s",
    xLabel: "reports",
    customData: (d) => [d.top_shape, d.top_shape_count],
    hovertemplate: "<b>%{y}</b><br>%{x:,} reports<br>Top shape: %{customdata[0]} (%{customdata[1]:,})<extra></extra>"
  });
}

function renderArea51(area51) {
  const rows = [
    { label: "Area 51 region", reports: area51.nearby_reports, note: "nearby bounding region" },
    { label: "Las Vegas", reports: area51.las_vegas_reports, note: "city reports" },
    { label: "Nevada", reports: area51.nevada_reports, note: "all state reports" }
  ].reverse();

  renderLabeledBars("#area51-callout", rows, {
    label: (d) => d.label,
    value: (d) => d.reports,
    valueLabel: (d) => fmt(d.reports),
    fill: colors.gold,
    margin: { t: 8, r: 70, b: 42, l: 110 },
    tickFormat: "~s",
    xLabel: "reports",
    customData: (d) => [d.note],
    hovertemplate: "<b>%{y}</b><br>%{x:,} reports<br>%{customdata[0]}<extra></extra>"
  });
}

function renderDurationBars(durationShapes) {
  const rows = durationShapes.slice(0, 16).reverse();
  renderLabeledBars("#duration-bars", rows, {
    label: (d) => d.shape,
    value: (d) => d.median,
    valueLabel: (d) => shortDuration(d.median),
    fill: colors.brown,
    margin: { t: 8, r: 60, b: 44, l: 92 },
    tickFormat: "",
    xLabel: "median duration",
    xAxis: {
      tickvals: [30, 60, 180, 300, 600, 1200],
      ticktext: ["30s", "1m", "3m", "5m", "10m", "20m"]
    },
    customData: (d) => [shortDuration(d.median), d.count],
    hovertemplate: "<b>%{y}</b><br>Median: %{customdata[0]}<br>%{customdata[1]:,} duration records<extra></extra>"
  });
}

function renderDurationBoxplot(durationShapes) {
  const rows = durationShapes
    .filter((d) => d.p05 != null && d.p25 != null && d.median != null && d.p75 != null && d.p95 != null)
    .slice(0, 14)
    .reverse();

  plot("#duration-box", [{
    type: "box",
    orientation: "h",
    y: rows.map((d) => d.shape),
    q1: rows.map((d) => Math.max(1, +d.p25)),
    median: rows.map((d) => Math.max(1, +d.median)),
    q3: rows.map((d) => Math.max(1, +d.p75)),
    lowerfence: rows.map((d) => Math.max(1, +d.p05)),
    upperfence: rows.map((d) => Math.max(1, +d.p95)),
    boxpoints: false,
    marker: { color: colors.brown },
    line: { color: colors.brown },
    hovertemplate: "<b>%{y}</b><br>Duration quantiles on log scale<extra></extra>"
  }], baseLayout("#duration-box", {
    margin: { t: 24, r: 24, b: 48, l: 92 },
    xaxis: {
      title: "duration",
      type: "log",
      tickvals: [1, 10, 60, 600, 3600, 21600, 86400],
      ticktext: ["1s", "10s", "1m", "10m", "1h", "6h", "24h"],
      gridcolor: "#eee7da",
      zeroline: false
    },
    yaxis: { automargin: true },
    showlegend: false,
    annotations: [{
      x: 0,
      y: 1.08,
      xref: "paper",
      yref: "paper",
      text: "box = p25-p75, whiskers = p05-p95",
      showarrow: false,
      xanchor: "left",
      font: { color: colors.muted, size: 11 }
    }]
  }));
}

function renderEraCards(eras) {
  plot("#era-cards", [
    {
      type: "bar",
      name: "Reports",
      x: eras.map((d) => d.label),
      y: eras.map((d) => d.reports),
      marker: { color: colors.blue },
      customdata: eras.map((d) => [d.top_shape, pct(d.top_shape_share), pct(d.report_share), shortDuration(d.median)]),
      hovertemplate: "<b>%{x}</b><br>%{y:,} reports<br>Top shape: %{customdata[0]} (%{customdata[1]})<br>Archive share: %{customdata[2]}<extra></extra>"
    },
    {
      type: "bar",
      name: "Median duration",
      x: eras.map((d) => d.label),
      y: eras.map((d) => d.median / 60),
      yaxis: "y2",
      marker: { color: colors.coral },
      customdata: eras.map((d) => [shortDuration(d.median)]),
      hovertemplate: "<b>%{x}</b><br>Median duration: %{customdata[0]}<extra></extra>"
    }
  ], baseLayout("#era-cards", {
    barmode: "group",
    margin: { t: 8, r: 58, b: 72, l: 58 },
    xaxis: { tickangle: 0 },
    yaxis: { title: "reports", tickformat: "~s", gridcolor: "#eee7da", zeroline: false },
    yaxis2: {
      title: "minutes",
      overlaying: "y",
      side: "right",
      showgrid: false,
      zeroline: false
    },
    legend: { orientation: "h", y: -0.24, x: 0 }
  }));
}

function renderCountryBars(countries) {
  const rows = countries.slice(0, 6).reverse();
  renderLabeledBars("#country-bars", rows, {
    label: (d) => d.country,
    value: (d) => d.reports,
    valueLabel: (d) => fmt(d.reports),
    fill: colors.blue,
    margin: { t: 8, r: 76, b: 44, l: 132 },
    tickFormat: "~s",
    xLabel: "reports",
    customData: (d) => [d.country_code.toUpperCase()],
    hovertemplate: "<b>%{y}</b><br>%{x:,} reports<br>Code: %{customdata[0]}<extra></extra>"
  });
}

function renderWords(words) {
  const max = d3.max(words, (d) => d.count) || 1;
  const size = d3.scaleSqrt().domain([0, max]).range([16, 48]);
  const placed = words.slice(0, 28).map((d, i) => {
    const angle = i * 2.399963;
    const radius = Math.sqrt(i) * 0.18;
    return {
      ...d,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      size: size(d.count),
      color: d3.schemeTableau10[i % 10]
    };
  });

  plot("#word-cloud", [{
    type: "scatter",
    mode: "text",
    x: placed.map((d) => d.x),
    y: placed.map((d) => d.y),
    text: placed.map((d) => d.word),
    customdata: placed.map((d) => d.count),
    textfont: {
      size: placed.map((d) => d.size),
      color: placed.map((d) => d.color),
      family: "Inter, system-ui, sans-serif"
    },
    hovertemplate: "<b>%{text}</b><br>%{customdata:,} uses<extra></extra>"
  }], baseLayout("#word-cloud", {
    margin: { t: 4, r: 4, b: 4, l: 4 },
    xaxis: { visible: false, range: [-1.15, 1.15], fixedrange: false },
    yaxis: { visible: false, range: [-0.9, 0.9], fixedrange: false },
    showlegend: false
  }));
}

function renderHotspotMap(hexDecades, hotspots) {
  const slider = d3.select("#decade-slider");
  const label = d3.select("#decade-label");
  let mode = "reports";

  const byDecade = d3.group(hexDecades, (d) => +d.decade);
  const buttons = d3.selectAll("[data-map-mode]");

  buttons.on("click", function () {
    mode = this.dataset.mapMode;
    buttons.classed("active", function () { return this.dataset.mapMode === mode; });
    draw();
  });
  slider.on("input", draw);

  function markerSizes(rows, value) {
    const maxValue = d3.max(rows, value) || 1;
    return rows.map((d) => 5 + Math.sqrt(value(d) / maxValue) * 24);
  }

  function draw() {
    const decade = +slider.property("value");
    label.text(mode === "reports" ? decade : "all years");

    const rows = mode === "reports" ? (byDecade.get(decade) || []) : hotspots.slice(0, 600);
    const value = mode === "reports" ? (d) => d.reports : (d) => d.persistence_ratio;
    const sizeValue = mode === "reports" ? (d) => d.reports : (d) => d.total_reports;

    plot("#hotspot-map", [{
      type: "scattergeo",
      mode: "markers",
      lon: rows.map((d) => d.lon),
      lat: rows.map((d) => d.lat),
      text: rows.map((d) => d.top_shape),
      customdata: rows.map((d) => [
        d.reports,
        d.total_reports,
        d.active_years,
        d.active_decades,
        d.persistence_ratio
      ]),
      marker: {
        size: markerSizes(rows, sizeValue),
        color: rows.map(value),
        colorscale: mode === "reports" ? "OrRd" : "PuBuGn",
        reversescale: true,
        opacity: 0.76,
        line: { color: "#24322d", width: 0.35 },
        colorbar: { title: mode === "reports" ? "reports" : "persistence", tickformat: mode === "reports" ? "~s" : ".0%" }
      },
      hovertemplate: mode === "reports"
        ? "<b>%{customdata[0]:,} reports in selected decade</b><br>%{customdata[1]:,} total reports<br>%{customdata[2]} active years, %{customdata[3]} active decades<br>Top shape: %{text}<extra></extra>"
        : "<b>%{customdata[1]:,} total reports</b><br>%{customdata[2]} active years, %{customdata[3]} active decades<br>Persistence ratio: %{customdata[4]:.1%}<br>Top shape: %{text}<extra></extra>"
    }], baseLayout("#hotspot-map", {
      height: Math.max(460, document.querySelector("#hotspot-map")?.clientHeight || 620),
      margin: { t: 0, r: 0, b: 0, l: 0 },
      paper_bgcolor: "#e9f1ef",
      plot_bgcolor: "#e9f1ef",
      geo: {
        projection: { type: "natural earth" },
        showland: true,
        landcolor: "#d7dfd9",
        showocean: true,
        oceancolor: "#e9f1ef",
        lakecolor: "#e9f1ef",
        showcountries: false,
        bgcolor: "#e9f1ef"
      }
    }), { scrollZoom: true });
  }

  draw();
}
