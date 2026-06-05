import json
from pathlib import Path

import pandas as pd
from dash import Input, Output, ctx, dcc, html, no_update

from styles import (
    ACCENT_COLOR,
    BUTTON_ACTIVE_STYLE,
    BUTTON_BASE_STYLE,
    BUTTON_ROW_STYLE,
    CARD_CHANGE_STYLE,
    CARD_COMPARISON_STYLE,
    CARD_VALUE_STYLE,
    CHART_CARD_STYLE,
    CHART_ROW_STYLE,
    CHART_STYLE,
    GENRE_PALETTE,
    METRIC_CARD_STYLE,
    METRIC_GRID_STYLE,
    PIE_CARD_STYLE,
    PIE_GRAPH_STYLE,
    PIE_ROW_STYLE,
    RANGE_ROW_STYLE,
    SECTION_STYLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def _load_precomputed():
    path = Path(__file__).resolve().parents[1] / "data" / "overview_precomputed.json"
    with open(path, "r") as f:
        return json.load(f)

PRECOMPUTED = _load_precomputed()
genre_values = sorted([g for g in PRECOMPUTED["metrics"].keys() if g != "All genres"])

title = 'Overview'
desc = 'A high-level view of the gaming market.'

END_RANGE = pd.to_datetime("2026-01-31")
DEFAULT_GENRE = "All genres"
DEFAULT_PERIOD = "year"
DEFAULT_RANGE = "last-6-years"

GENRE_DROPDOWN_ID = "overview-genre-dropdown"
PERIOD_STORE_ID = "overview-period-store"
RANGE_STORE_ID = "overview-range-store"
MONTH_BUTTON_ID = "overview-period-month"
QUARTER_BUTTON_ID = "overview-period-quarter"
YEAR_BUTTON_ID = "overview-period-year"
RANGE_6M_BUTTON_ID = "overview-range-6m"
RANGE_1Y_BUTTON_ID = "overview-range-1y"
RANGE_3Y_BUTTON_ID = "overview-range-3y"
RANGE_6Y_BUTTON_ID = "overview-range-6y"
RANGE_10Y_BUTTON_ID = "overview-range-10y"
RANGE_ALL_BUTTON_ID = "overview-range-all"
GAMES_VALUE_ID = "overview-games-released-value"
GAMES_CHANGE_ID = "overview-games-released-value-change"
GAMES_COMPARISON_ID = "overview-games-released-value-comparison"
MARKET_VALUE_ID = "overview-market-value-value"
MARKET_CHANGE_ID = "overview-market-value-value-change"
MARKET_COMPARISON_ID = "overview-market-value-value-comparison"
PURCHASED_VALUE_ID = "overview-purchased-copies-value"
PURCHASED_CHANGE_ID = "overview-purchased-copies-value-change"
PURCHASED_COMPARISON_ID = "overview-purchased-copies-value-comparison"
PLAYTIME_VALUE_ID = "overview-average-playtime-value"
PLAYTIME_CHANGE_ID = "overview-average-playtime-value-change"
PLAYTIME_COMPARISON_ID = "overview-average-playtime-value-comparison"
PEAK_CCU_VALUE_ID = "overview-peak-ccu-value"
PEAK_CCU_CHANGE_ID = "overview-peak-ccu-value-change"
PEAK_CCU_COMPARISON_ID = "overview-peak-ccu-value-comparison"

MARKET_VALUE_CHART_ID = "overview-estimated-market-value-chart"
RELATIVE_MARKET_CHART_ID = "overview-relative-market-value-chart"
PURCHASED_VALUE_CHART_ID = "overview-estimated-purchased-copies-chart"
RELATIVE_PURCHASED_CHART_ID = "overview-relative-purchased-copies-chart"
GAME_TYPE_PIE_ID = "overview-game-type-pie-chart"
PLATFORM_PIE_ID = "overview-platform-pie-chart"
CONTROLLER_PIE_ID = "overview-controller-pie-chart"
VR_PIE_ID = "overview-vr-pie-chart"


genre_options = [{"label": DEFAULT_GENRE, "value": DEFAULT_GENRE}] + [
    {"label": genre, "value": genre} for genre in genre_values
]


def _period_window(period, end_date):
    if period == "quarter":
        current_quarter = pd.Period(end_date, freq='Q')
        if current_quarter.end_time == end_date:
            return current_quarter - 1, end_date
        return (current_quarter - 1).start_time, (current_quarter - 1).end_time
    elif period == "year":
        current_year = pd.Period(end_date, freq='Y')
        if current_year.end_time == end_date:
            return current_year - 1, end_date
        return (current_year - 1).start_time, (current_year - 1).end_time
    elif period == "month":
        current_month = pd.Period(end_date, freq='M')
        if current_month.end_time == end_date:
            return current_month - 1, end_date
        return (current_month - 1).start_time, (current_month - 1).end_time
    else:
        raise ValueError(f"Unknown period: {period}")


def _comparison_label(period):
    return {
        "month": "Last month",
        "quarter": "Last quarter",
        "year": "Last year",
    }[period]


def _relative_change(current_value, previous_value):
    if pd.isna(previous_value) or previous_value == 0:
        return "No prior period", TEXT_SECONDARY

    change = ((current_value - previous_value) / previous_value) * 100
    if change > 0:
        return f"▲ {change:.1f}%", "#15803d"
    if change < 0:
        return f"▼ {abs(change):.1f}%", "#b91c1c"
    return "• 0.0%", TEXT_SECONDARY


def _comparison_text(period, value, formatter):
    label = _comparison_label(period)
    formatted_value = formatter(value) if pd.notna(value) else "N/A"
    return f"{label}: {formatted_value}"


def _period_frequency(period):
    return {
        "month": "M",
        "quarter": "Q",
        "year": "Y",
    }[period]


def _period_axis_label(period):
    return {
        "month": "Month",
        "quarter": "Quarter",
        "year": "Year",
    }[period]


def _period_tick_format(period):
    return {
        "month": "%B %Y",
        "quarter": "%Y",
        "year": "%Y",
    }[period]


def _period_tick_labels(period, timestamps):
    if period == "month":
        return [timestamp.strftime("%B %Y") for timestamp in timestamps]
    if period == "quarter":
        return [f"Q{((timestamp.month - 1) // 3) + 1} {timestamp.year}" for timestamp in timestamps]
    return [timestamp.strftime("%Y") for timestamp in timestamps]


def _period_tickformatstops(period):
    if period == "month":
        return [
            {"dtickrange": [None, "M1"], "value": "%Y"},
            {"dtickrange": ["M1", "M12"], "value": "%B %Y"},
            {"dtickrange": ["M12", None], "value": "%Y"},
        ]
    if period == "quarter":
        return [
            {"dtickrange": [None, "M3"], "value": "%Y"},
            {"dtickrange": ["M3", "M12"], "value": "Q%q %Y"},
            {"dtickrange": ["M12", None], "value": "%Y"},
        ]
    return [
        {"dtickrange": [None, "M12"], "value": "%Y"},
        {"dtickrange": ["M12", None], "value": "%Y"},
    ]


def _range_start_date(range_key):
    history_start = pd.to_datetime("1997-06-26")
    end_date = END_RANGE.normalize()
    if range_key == "last-6-months":
        return (end_date - pd.DateOffset(months=6)).normalize()
    if range_key == "last-year":
        return (end_date - pd.DateOffset(years=1)).normalize()
    if range_key == "last-3-years":
        return (end_date - pd.DateOffset(years=3)).normalize()
    if range_key == "last-6-years":
        return (end_date - pd.DateOffset(years=6)).normalize()
    if range_key == "last-10-years":
        return (end_date - pd.DateOffset(years=10)).normalize()
    if range_key == "all-data":
        return history_start
    raise ValueError(f"Unknown range: {range_key}")


def _range_label(range_key):
    return {
        "last-6-months": "Last 6 Months",
        "last-year": "Last Year",
        "last-3-years": "Last 3 Years",
        "last-6-years": "Last 6 Years",
        "last-10-years": "Last 10 Years",
        "all-data": "All Data",
    }[range_key]


def _bucket_market_value(selected_genre, period, start_date, end_date):
    data = PRECOMPUTED["timeseries"][period].get(selected_genre, {"Release date": [], "Market value": []})
    df = pd.DataFrame(data)
    if not df.empty:
        df["Release date"] = pd.to_datetime(df["Release date"])
        df = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)]
    return df


def _bucket_purchased_copies(selected_genre, period, start_date, end_date):
    data = PRECOMPUTED["timeseries"][period].get(selected_genre, {"Release date": [], "Purchased copies": []})
    df = pd.DataFrame(data)
    if not df.empty:
        df["Release date"] = pd.to_datetime(df["Release date"])
        df = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)]
    return df


def _category_items(value):
    return {item.strip().lower() for item in str(value).split(",") if item.strip()}


def _has_any_category(value, terms):
    normalized = _category_items(value)
    return any(term.strip().lower() in normalized for term in terms)


def _get_xaxis_ticks(x_values, period, selected_range):
    if not x_values:
        return [], []
        
    if period == "year":
        return x_values, [t.strftime("%Y") for t in x_values]
        
    if period == "quarter":
        if selected_range in ["last-6-months", "last-year"]:
            tick_text = []
            for t in x_values:
                q = ((t.month - 1) // 3) + 1
                tick_text.append(f"Q{q} {t.strftime('%y')}")
            return x_values, tick_text
        else:
            tickvals = [t for t in x_values if t.month == 1]
            if not tickvals:
                tickvals = [x_values[0]]
            return tickvals, [t.strftime("%Y") for t in tickvals]
            
    if period == "month":
        if selected_range in ["last-6-months", "last-year"]:
            return x_values, [t.strftime("%b") for t in x_values]
        else:
            tickvals = [t for t in x_values if t.month == 1]
            if not tickvals:
                years_seen = set()
                tickvals = []
                for t in x_values:
                    if t.year not in years_seen:
                        tickvals.append(t)
                        years_seen.add(t.year)
            return tickvals, [t.strftime("%Y") for t in tickvals]
            
    return x_values, [t.strftime("%Y-%m-%d") for t in x_values]


def _build_pie_figure(labels, values, title, colors):
    """Build a filled pie chart figure with no native legend (legend rendered as custom HTML)."""
    return {
        "data": [
            {
                "type": "pie",
                "labels": labels,
                "values": values,
                "marker": {"colors": colors},
                "textinfo": "none",
                "sort": False,
                "direction": "clockwise",
                "hole": 0,
                "hovertemplate": "%{label}<br>%{value:,}<br>%{percent}<extra></extra>",
            }
        ],
        "layout": {
            "title": {"text": f"<b>{title}</b>", "x": 0.02, "xanchor": "left", "font": {"size": 15}},
            "margin": {"l": 8, "r": 8, "t": 36, "b": 8},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "showlegend": False,
            "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY},
        },
    }


def _legend_labels_with_percentages(labels, values):
    total = sum(values)
    if total <= 0:
        return [f"{label} (0.0%)" for label in labels]

    return [f"{label} ({(value / total) * 100:.1f}%)" for label, value in zip(labels, values)]


def _build_pie_legend(labels, values, colors):
    """Render a compact horizontal legend with filled circle swatches below a pie chart."""
    total = sum(values)
    items = []
    for label, value, color in zip(labels, values, colors):
        pct = f"{(value / total * 100):.1f}%" if total > 0 else "0.0%"
        items.append(
            html.Div(
                [
                    html.Span(
                        style={
                            "display": "inline-block",
                            "width": "10px",
                            "height": "10px",
                            "borderRadius": "50%",
                            "backgroundColor": color,
                            "flexShrink": "0",
                            "marginTop": "2px",
                        }
                    ),
                    html.Span(
                        f"{label} {pct}",
                        style={
                            "fontSize": "0.73rem",
                            "color": TEXT_SECONDARY,
                            "lineHeight": "1.3",
                            "fontFamily": "Inter, sans-serif",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "flex-start",
                    "gap": "5px",
                },
            )
        )
    return html.Div(
        items,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "6px 12px",
            "justifyContent": "center",
            "padding": "6px 8px 8px",
        },
    )


def _build_game_type_pie_figure(selected_genre, year):
    pies = PRECOMPUTED["pies"].get(selected_genre, {}).get(str(year), {})
    values = pies.get("game_type", [0, 0, 0])
    labels = ["Singleplayer", "Multiplayer", "Co-op"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "Game Type",
        ["#3b82f6", "#10b981", "#f59e0b"],
    )


def _build_platform_pie_figure(selected_genre, year):
    pies = PRECOMPUTED["pies"].get(selected_genre, {}).get(str(year), {})
    values = pies.get("platform", [0, 0, 0, 0])
    labels = ["Windows only", "Windows + Linux + Mac", "Windows + Linux", "Windows + Mac"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "Supported Platforms",
        ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"],
    )


def _build_controller_support_pie_figure(selected_genre, year):
    pies = PRECOMPUTED["pies"].get(selected_genre, {}).get(str(year), {})
    values = pies.get("controller", [0, 0])
    labels = ["Yes", "No"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "Controller Support",
        ["#3b82f6", "#10b981"],
    )


def _build_vr_support_pie_figure(selected_genre, year):
    pies = PRECOMPUTED["pies"].get(selected_genre, {}).get(str(year), {})
    values = pies.get("vr", [0, 0])
    labels = ["Yes", "No"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "VR Support",
        ["#3b82f6", "#10b981"],
    )


def _genre_market_value_buckets(selected_period, start_date, end_date):
    rows = []
    for genre, data in PRECOMPUTED["timeseries"][selected_period].items():
        if genre == "All genres": continue
        for d, v in zip(data["Release date"], data["Market value"]):
            if v > 0: rows.append({"Release date": d, "Genre": genre, "Market value": v})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Release date"] = pd.to_datetime(df["Release date"])
        df = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)]
    return df


def _genre_purchased_copies_buckets(selected_period, start_date, end_date):
    rows = []
    for genre, data in PRECOMPUTED["timeseries"][selected_period].items():
        if genre == "All genres": continue
        for d, v in zip(data["Release date"], data["Purchased copies"]):
            if v > 0: rows.append({"Release date": d, "Genre": genre, "Purchased copies": v})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Release date"] = pd.to_datetime(df["Release date"])
        df = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)]
    return df


def _build_market_value_figure(selected_genre, period, selected_range, start_date, end_date):
    grouped = _bucket_market_value(selected_genre, period, start_date, end_date)
    return timeseries_line_figure(
        grouped,
        period=period,
        selected_range=selected_range,
        y_col="Market value",
        title="Estimated Market Value",
        yaxis_title="Market value",
        hover_template="%{x|%b %d, %Y}<br>Market value: $%{y:,.0f}<extra></extra>",
        currency=True,
    )


def _build_purchased_copies_figure(selected_genre, period, selected_range, start_date, end_date):
    grouped = _bucket_purchased_copies(selected_genre, period, start_date, end_date)
    return timeseries_line_figure(
        grouped,
        period=period,
        selected_range=selected_range,
        y_col="Purchased copies",
        title="Estimated Purchased Copies",
        yaxis_title="Purchased copies",
        hover_template="%{x|%b %d, %Y}<br>Purchased copies: %{y:,.0f}<extra></extra>",
        currency=False,
    )


def timeseries_line_figure(grouped, period, selected_range, y_col, title, yaxis_title, hover_template, currency=False):
    """Build a line figure from a grouped dataframe with a datetime 'Release date' index and a numeric y_col."""
    if not grouped.empty:
        index = pd.period_range(
            start=grouped["Release date"].min().to_period(_period_frequency(period)),
            end=grouped["Release date"].max().to_period(_period_frequency(period)),
            freq=_period_frequency(period),
        ).to_timestamp()
        grouped = grouped.set_index("Release date").reindex(index, fill_value=0).reset_index()
        grouped.rename(columns={"index": "Release date"}, inplace=True)
    x_values = grouped["Release date"].dt.to_pydatetime().tolist() if not grouped.empty else []
    y_values = grouped[y_col].tolist() if not grouped.empty else []

    yaxis = {"title": yaxis_title, "separatethousands": True, "showgrid": True}
    if currency:
        yaxis.update({"tickprefix": "$", "separatethousands": True})

    tickvals, ticktext = _get_xaxis_ticks(x_values, period, selected_range)

    return {
        "data": [
            {
                "type": "scatter",
                "mode": "lines+markers",
                "x": x_values,
                "y": y_values,
                "line": {"color": ACCENT_COLOR, "width": 3},
                "marker": {"color": ACCENT_COLOR, "size": 7},
                "hovertemplate": hover_template,
                "name": title,
            }
        ],
        "layout": {
            "title": {"text": f"<b>{title}</b>", "x": 0.02, "xanchor": "left"},
            "margin": {"l": 50, "r": 20, "t": 52, "b": 50},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "hovermode": "x unified",
            "xaxis": {
                "title": _period_axis_label(period),
                "type": "date",
                "showgrid": False,
                "tickvals": tickvals,
                "ticktext": ticktext,
            },
            "yaxis": yaxis,
            "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY},
        },
    }


def _build_relative_market_value_figure(period, selected_genre, selected_range, start_date, end_date):
    grouped = _genre_market_value_buckets(period, start_date, end_date)
    return relative_barchart_figure(
        grouped,
        period=period,
        selected_range=selected_range,
        value_col="Market value",
        title="Relative Market Value",
        yaxis_title="Market value",
        hover_label="Market value",
        currency=True,
        selected_genre=selected_genre,
    )


def _build_relative_purchased_copies_figure(period, selected_genre, selected_range, start_date, end_date):
    grouped = _genre_purchased_copies_buckets(period, start_date, end_date)
    return relative_barchart_figure(
        grouped,
        period=period,
        selected_range=selected_range,
        value_col="Purchased copies",
        title="Relative Purchased Copies",
        yaxis_title="Purchased copies",
        hover_label="Purchased copies",
        currency=False,
        selected_genre=selected_genre,
    )


def relative_barchart_figure(grouped, period, selected_range, value_col, title, yaxis_title, hover_label, currency=False, selected_genre=None):
    """Build a per-column-sorted stacked bar chart using explicit base arrays.

    For every time-period column, genres are sorted independently by their value in that column
    (largest at the bottom, smallest at the top). This uses barmode='overlay' with a per-bar
    `base` array rather than Plotly's built-in stack ordering, which only supports a global trace order.
    Colours are stable (same genre always gets the same hue) regardless of the current selection.
    When a genre is highlighted it is pinned at the very bottom of every bar.
    """
    selected_is_all = not selected_genre or selected_genre == DEFAULT_GENRE
    highlighted_genre = None if selected_is_all else selected_genre

    if not grouped.empty:
        x_index = pd.period_range(
            start=grouped["Release date"].min().to_period(_period_frequency(period)),
            end=grouped["Release date"].max().to_period(_period_frequency(period)),
            freq=_period_frequency(period),
        ).to_timestamp()
    else:
        x_index = pd.DatetimeIndex([])
    x_values = x_index.to_pydatetime().tolist()
    n_x = len(x_values)

    all_genres_in_data = grouped["Genre"].dropna().unique().tolist() if not grouped.empty else []

    pivot_data = {}
    for genre in all_genres_in_data:
        if n_x > 0:
            gf = grouped[grouped["Genre"] == genre]
            series = (
                gf.set_index("Release date")
                .reindex(x_index)       
                [value_col]
                .fillna(0)               
                .astype(float)
            )
            pivot_data[genre] = series.tolist()
        else:
            pivot_data[genre] = []

    overall_totals = {genre: sum(vals) for genre, vals in pivot_data.items()}
    sorted_genres_overall = sorted(overall_totals, key=lambda g: overall_totals[g], reverse=True)

    genre_color_map = {
        genre: GENRE_PALETTE[i % len(GENRE_PALETTE)]
        for i, genre in enumerate(sorted_genres_overall)
    }

    base_dict = {genre: [0.0] * n_x for genre in sorted_genres_overall}

    for i in range(n_x):
        row = {g: pivot_data[g][i] for g in sorted_genres_overall if g in pivot_data}

        if highlighted_genre:
            base_dict.setdefault(highlighted_genre, [0.0] * n_x)
            base_dict[highlighted_genre][i] = 0.0
            highlighted_val = row.get(highlighted_genre, 0.0)

            others = [g for g in sorted_genres_overall if g != highlighted_genre]
            sorted_others = sorted(
                others,
                key=lambda g: (row.get(g, 0.0), overall_totals.get(g, 0.0)),
                reverse=True,
            )
            cumbase = highlighted_val
            for genre in sorted_others:
                base_dict[genre][i] = cumbase
                cumbase += row.get(genre, 0.0)
        else:
            sorted_at_i = sorted(
                sorted_genres_overall,
                key=lambda g: (row.get(g, 0.0), overall_totals.get(g, 0.0)),
                reverse=True,
            )
            cumbase = 0.0
            for genre in sorted_at_i:
                base_dict[genre][i] = cumbase
                cumbase += row.get(genre, 0.0)

    bar_traces = []
    line_traces = []

    for genre in sorted_genres_overall:
        if genre not in pivot_data:
            continue
        y_arr = pivot_data[genre]
        base_arr = base_dict[genre]
        is_highlighted = genre == highlighted_genre
        color = ACCENT_COLOR if is_highlighted else genre_color_map.get(genre, GENRE_PALETTE[0])

        hoverfmt = f"{genre}<br>%{{x|%b %d, %Y}}<br>{hover_label}: %{{customdata:,.0f}}<extra></extra>"
        if currency:
            hoverfmt = f"{genre}<br>%{{x|%b %d, %Y}}<br>{hover_label}: $%{{customdata:,.0f}}<extra></extra>"

        bar_traces.append({
            "type": "bar",
            "name": genre,
            "x": x_values,
            "y": y_arr,
            "base": base_arr,
            "customdata": y_arr,
            "marker": {
                "color": color,
                "line": {"color": "#0f172a" if is_highlighted else color, "width": 1.4 if is_highlighted else 0.5},
                "opacity": 0.96 if is_highlighted else 0.72,
            },
            "hovertemplate": hoverfmt,
            "showlegend": False,
        })

        if is_highlighted:
            midpoint_values = [v / 2 for v in y_arr]
            line_traces.append({
                "type": "scatter",
                "mode": "lines+markers",
                "name": f"{genre} trend",
                "x": x_values,
                "y": midpoint_values,
                "line": {"color": "#0f172a", "width": 3},
                "marker": {"color": "#0f172a", "size": 6},
                "hoverinfo": "skip",
                "showlegend": False,
            })

    traces = bar_traces + line_traces

    yaxis = {"title": yaxis_title, "separatethousands": True, "showgrid": True}
    if currency:
        yaxis.update({"tickprefix": "$", "separatethousands": True})

    tickvals, ticktext = _get_xaxis_ticks(x_values, period, selected_range)

    return {
        "data": traces,
        "layout": {
            "title": {"text": f"<b>{title}</b>", "x": 0.02, "xanchor": "left"},
            "margin": {"l": 50, "r": 20, "t": 52, "b": 50},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            # barmode='overlay' + explicit per-bar `base` arrays = per-column sorted stacking
            "barmode": "overlay",
            "hovermode": "closest",
            "xaxis": {
                "title": _period_axis_label(period),
                "type": "date",
                "showgrid": False,
                "tickvals": tickvals,
                "ticktext": ticktext,
            },
            "yaxis": yaxis,
            "showlegend": False,
            "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY},
        },
    }





def _format_number(value):
    if value > 1_000_000:
        return f"{value / 1_000_000:.1f} Milions"
    elif value > 1_000_000_000:
        return f"{value / 1_000_000_000:.1f} Bilions"
    else:
        return f"{int(round(value)):,}"


def _format_currency(value):
    if value > 1_000_000:
        return f"${value / 1_000_000:.1f} Milions"
    elif value > 1_000_000_000:
        return f"${value / 1_000_000_000:.1f} Bilions"
    else:
        return f"${value:,.2f}"


def _format_playtime(value):
    return f"{value:,.1f} min"


def _build_metric_card(label, value_id, default_value):
    return html.Div(
        style=METRIC_CARD_STYLE,
        children=[
            html.Div(
                label,
                style={
                    "color": TEXT_SECONDARY,
                    "fontSize": "0.85rem",
                    "fontWeight": "600",
                    "marginBottom": "0.75rem",
                },
            ),
            html.Div(
                default_value,
                id=value_id,
                style=CARD_VALUE_STYLE,
            ),
            html.Div(
                "No prior period",
                id=f"{value_id}-change",
                style={**CARD_CHANGE_STYLE, "color": TEXT_SECONDARY},
            ),
            html.Div(
                f"{_comparison_label(DEFAULT_PERIOD)}: {default_value}",
                id=f"{value_id}-comparison",
                style=CARD_COMPARISON_STYLE,
            ),
        ],
    )




# TODO: Change this in the future because now this does not make, it should use the full data range and not thte part of it
DEFAULT_PIE_YEAR = int(END_RANGE.year)

history_start_date = pd.to_datetime("1997-06-26")
default_range_start_date = _range_start_date(DEFAULT_RANGE)

default_market_value_figure = _build_market_value_figure(
    DEFAULT_GENRE, DEFAULT_PERIOD, DEFAULT_RANGE, default_range_start_date, END_RANGE
)
default_relative_market_value_figure = _build_relative_market_value_figure(
    DEFAULT_PERIOD, DEFAULT_GENRE, DEFAULT_RANGE, default_range_start_date, END_RANGE
)
default_purchased_copies_figure = _build_purchased_copies_figure(
    DEFAULT_GENRE, DEFAULT_PERIOD, DEFAULT_RANGE, default_range_start_date, END_RANGE
)
default_relative_purchased_copies_figure = _build_relative_purchased_copies_figure(
    DEFAULT_PERIOD, DEFAULT_GENRE, DEFAULT_RANGE, default_range_start_date, END_RANGE
)

default_game_type_pie_figure = _build_game_type_pie_figure(DEFAULT_GENRE, DEFAULT_PIE_YEAR)
default_platform_pie_figure = _build_platform_pie_figure(DEFAULT_GENRE, DEFAULT_PIE_YEAR)
default_controller_pie_figure = _build_controller_support_pie_figure(DEFAULT_GENRE, DEFAULT_PIE_YEAR)
default_vr_pie_figure = _build_vr_support_pie_figure(DEFAULT_GENRE, DEFAULT_PIE_YEAR)
# END TODO



layout = html.Div(
    [
        dcc.Store(id=PERIOD_STORE_ID, data=DEFAULT_PERIOD),
        dcc.Store(id=RANGE_STORE_ID, data=DEFAULT_RANGE),
        html.Div(
            [
                html.H2(
                    title,
                    style={"fontSize": "1.8rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY},
                ),
                html.Div(desc, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "marginTop": "4px"}),
            ],
            style={"marginBottom": "1.5rem"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "Genre",
                            style={
                                "color": TEXT_SECONDARY,
                                "fontSize": "0.75rem",
                                "fontWeight": "600",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.06em",
                                "marginBottom": "6px",
                            },
                        ),
                        dcc.Dropdown(
                            id=GENRE_DROPDOWN_ID,
                            options=genre_options,
                            value=DEFAULT_GENRE,
                            clearable=False,
                            searchable=True,
                            style={"maxWidth": "340px"},
                        ),
                    ]
                ),
            ],
            style={"marginBottom": "1.25rem"},
        ),
        html.Div(
            [
                html.Div(
                    "Market Size And Trends",
                    style={"fontSize": "1.25rem", "fontWeight": "700", "color": TEXT_PRIMARY},
                ),
                html.Div(
                    id="overview-period-buttons",
                    children=[
                        html.Button("Month", id=MONTH_BUTTON_ID, n_clicks=0, style=BUTTON_ACTIVE_STYLE),
                        html.Button("Quarter", id=QUARTER_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                        html.Button("Year", id=YEAR_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                    ],
                    style=BUTTON_ROW_STYLE,
                ),
                html.Div(
                    [
                        _build_metric_card("Games released", GAMES_VALUE_ID, "0"),
                        _build_metric_card("Market value", MARKET_VALUE_ID, "$0.00"),
                        _build_metric_card("Number of purchased copies", PURCHASED_VALUE_ID, "0"),
                        _build_metric_card("Average playtime", PLAYTIME_VALUE_ID, "0.0 min"),
                        _build_metric_card("Max peak ccu", PEAK_CCU_VALUE_ID, "0"),
                    ],
                    style=METRIC_GRID_STYLE,
                ),
                html.Div(
                    id="overview-range-buttons",
                    children=[
                        html.Button("Last 6 Months", id=RANGE_6M_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                        html.Button("Last Year", id=RANGE_1Y_BUTTON_ID, n_clicks=0, style=BUTTON_ACTIVE_STYLE),
                        html.Button("Last 3 Years", id=RANGE_3Y_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                        html.Button("Last 6 Years", id=RANGE_6Y_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                        html.Button("Last 10 Years", id=RANGE_10Y_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                        html.Button("All Data", id=RANGE_ALL_BUTTON_ID, n_clicks=0, style=BUTTON_BASE_STYLE),
                    ],
                    style=RANGE_ROW_STYLE,
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id=MARKET_VALUE_CHART_ID,
                                    figure=default_market_value_figure,
                                    style=CHART_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                )
                            ],
                            style=CHART_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id=RELATIVE_MARKET_CHART_ID,
                                    figure=default_relative_market_value_figure,
                                    style=CHART_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                )
                            ],
                            style=CHART_CARD_STYLE,
                        ),
                    ],
                    style=CHART_ROW_STYLE,
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id=PURCHASED_VALUE_CHART_ID,
                                    figure=default_purchased_copies_figure,
                                    style=CHART_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                )
                            ],
                            style=CHART_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id=RELATIVE_PURCHASED_CHART_ID,
                                    figure=default_relative_purchased_copies_figure,
                                    style=CHART_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                )
                            ],
                            style=CHART_CARD_STYLE,
                        ),
                    ],
                    style=CHART_ROW_STYLE,
                ),
                html.Div(
                    [
                        html.Div("Game Characteristics", style={"fontSize": "1.25rem", "fontWeight": "700", "color": TEXT_PRIMARY}),
                        html.Div(
                            [
                                html.Div(
                                    "Year",
                                    style={
                                        "color": TEXT_SECONDARY,
                                        "fontSize": "0.75rem",
                                        "fontWeight": "600",
                                        "textTransform": "uppercase",
                                        "letterSpacing": "0.06em",
                                        "marginBottom": "6px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="overview-pie-year-dropdown",
                                    options=[{"label": str(y), "value": y} for y in range(2026, 1996, -1)],
                                    value=DEFAULT_PIE_YEAR,
                                    clearable=False,
                                    searchable=False,
                                    style={"width": "110px"},
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "column", "alignItems": "flex-end"}
                        )
                    ],
                    style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-end", "marginTop": "1.5rem", "marginBottom": "1rem", "flexWrap": "wrap", "gap": "0.5rem"}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id=GAME_TYPE_PIE_ID,
                                    figure=default_game_type_pie_figure,
                                    style=PIE_GRAPH_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                html.Div(
                                    id="overview-game-type-pie-legend",
                                    children=_build_pie_legend(
                                        ["Singleplayer", "Multiplayer", "Co-op"],
                                        [1, 1, 1],
                                        ["#3b82f6", "#10b981", "#f59e0b"],
                                    ),
                                ),
                            ],
                            style=PIE_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id=PLATFORM_PIE_ID,
                                    figure=default_platform_pie_figure,
                                    style=PIE_GRAPH_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                html.Div(
                                    id="overview-platform-pie-legend",
                                    children=_build_pie_legend(
                                        ["Win only", "Win+Lin+Mac", "Win+Linux", "Win+Mac"],
                                        [1, 1, 1, 1],
                                        ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"],
                                    ),
                                ),
                            ],
                            style=PIE_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id=CONTROLLER_PIE_ID,
                                    figure=default_controller_pie_figure,
                                    style=PIE_GRAPH_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                html.Div(
                                    id="overview-controller-pie-legend",
                                    children=_build_pie_legend(
                                        ["Yes", "No"],
                                        [1, 1],
                                        ["#3b82f6", "#10b981"],
                                    ),
                                ),
                            ],
                            style=PIE_CARD_STYLE,
                        ),
                        # VR Support pie
                        html.Div(
                            [
                                dcc.Graph(
                                    id=VR_PIE_ID,
                                    figure=default_vr_pie_figure,
                                    style=PIE_GRAPH_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                                html.Div(
                                    id="overview-vr-pie-legend",
                                    children=_build_pie_legend(
                                        ["Yes", "No"],
                                        [1, 1],
                                        ["#3b82f6", "#10b981"],
                                    ),
                                ),
                            ],
                            style=PIE_CARD_STYLE,
                        ),
                    ],
                    style=PIE_ROW_STYLE,
                ),
            ],
            style=SECTION_STYLE,
        ),
    ]
)


def register_callbacks(app):
    @app.callback(
        Output(PERIOD_STORE_ID, "data"),
        Input(MONTH_BUTTON_ID, "n_clicks"),
        Input(QUARTER_BUTTON_ID, "n_clicks"),
        Input(YEAR_BUTTON_ID, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_period(_, __, ___):
        triggered = ctx.triggered_id
        if triggered == MONTH_BUTTON_ID:
            return "month"
        if triggered == QUARTER_BUTTON_ID:
            return "quarter"
        if triggered == YEAR_BUTTON_ID:
            return "year"
        return no_update

    @app.callback(
        Output(RANGE_STORE_ID, "data"),
        Input(RANGE_6M_BUTTON_ID, "n_clicks"),
        Input(RANGE_1Y_BUTTON_ID, "n_clicks"),
        Input(RANGE_3Y_BUTTON_ID, "n_clicks"),
        Input(RANGE_6Y_BUTTON_ID, "n_clicks"),
        Input(RANGE_10Y_BUTTON_ID, "n_clicks"),
        Input(RANGE_ALL_BUTTON_ID, "n_clicks"),
        prevent_initial_call=True,
    )
    def set_range(_, __, ___, ____, _____, ______):
        triggered = ctx.triggered_id
        if triggered == RANGE_6M_BUTTON_ID:
            return "last-6-months"
        if triggered == RANGE_1Y_BUTTON_ID:
            return "last-year"
        if triggered == RANGE_3Y_BUTTON_ID:
            return "last-3-years"
        if triggered == RANGE_6Y_BUTTON_ID:
            return "last-6-years"
        if triggered == RANGE_10Y_BUTTON_ID:
            return "last-10-years"
        if triggered == RANGE_ALL_BUTTON_ID:
            return "all-data"
        return no_update

    @app.callback(
        Output(GAMES_VALUE_ID, "children"),
        Output(MARKET_VALUE_ID, "children"),
        Output(PURCHASED_VALUE_ID, "children"),
        Output(PLAYTIME_VALUE_ID, "children"),
        Output(PEAK_CCU_VALUE_ID, "children"),
        Output(MARKET_VALUE_CHART_ID, "figure"),
        Output(RELATIVE_MARKET_CHART_ID, "figure"),
        Output(PURCHASED_VALUE_CHART_ID, "figure"),
        Output(RELATIVE_PURCHASED_CHART_ID, "figure"),
        Output(GAME_TYPE_PIE_ID, "figure"),
        Output(PLATFORM_PIE_ID, "figure"),
        Output(CONTROLLER_PIE_ID, "figure"),
        Output(VR_PIE_ID, "figure"),
        Output("overview-game-type-pie-legend", "children"),
        Output("overview-platform-pie-legend", "children"),
        Output("overview-controller-pie-legend", "children"),
        Output("overview-vr-pie-legend", "children"),
        Output(GAMES_CHANGE_ID, "children"),
        Output(MARKET_CHANGE_ID, "children"),
        Output(PURCHASED_CHANGE_ID, "children"),
        Output(PLAYTIME_CHANGE_ID, "children"),
        Output(PEAK_CCU_CHANGE_ID, "children"),
        Output(GAMES_CHANGE_ID, "style"),
        Output(MARKET_CHANGE_ID, "style"),
        Output(PURCHASED_CHANGE_ID, "style"),
        Output(PLAYTIME_CHANGE_ID, "style"),
        Output(PEAK_CCU_CHANGE_ID, "style"),
        Output(GAMES_COMPARISON_ID, "children"),
        Output(MARKET_COMPARISON_ID, "children"),
        Output(PURCHASED_COMPARISON_ID, "children"),
        Output(PLAYTIME_COMPARISON_ID, "children"),
        Output(PEAK_CCU_COMPARISON_ID, "children"),
        Output(MONTH_BUTTON_ID, "style"),
        Output(QUARTER_BUTTON_ID, "style"),
        Output(YEAR_BUTTON_ID, "style"),
        Output(RANGE_6M_BUTTON_ID, "style"),
        Output(RANGE_1Y_BUTTON_ID, "style"),
        Output(RANGE_3Y_BUTTON_ID, "style"),
        Output(RANGE_6Y_BUTTON_ID, "style"),
        Output(RANGE_10Y_BUTTON_ID, "style"),
        Output(RANGE_ALL_BUTTON_ID, "style"),
        Input(GENRE_DROPDOWN_ID, "value"),
        Input(PERIOD_STORE_ID, "data"),
        Input(RANGE_STORE_ID, "data"),
        Input("overview-pie-year-dropdown", "value"),
    )
    def update_metrics(selected_genre, selected_period, selected_range, selected_pie_year):
        range_start_date = _range_start_date(selected_range)

        market_value_figure = _build_market_value_figure(
            selected_genre, selected_period, selected_range, range_start_date, END_RANGE
        )
        relative_market_value_figure = _build_relative_market_value_figure(
            selected_period, selected_genre, selected_range, range_start_date, END_RANGE
        )
        purchased_copies_figure = _build_purchased_copies_figure(
            selected_genre, selected_period, selected_range, range_start_date, END_RANGE
        )
        relative_purchased_copies_figure = _build_relative_purchased_copies_figure(
            selected_period, selected_genre, selected_range, range_start_date, END_RANGE
        )

        game_type_pie_figure = _build_game_type_pie_figure(selected_genre, selected_pie_year)
        platform_pie_figure = _build_platform_pie_figure(selected_genre, selected_pie_year)
        controller_pie_figure = _build_controller_support_pie_figure(selected_genre, selected_pie_year)
        vr_pie_figure = _build_vr_support_pie_figure(selected_genre, selected_pie_year)

        pies = PRECOMPUTED["pies"].get(selected_genre, {}).get(str(selected_pie_year), {})
        game_type_values = pies.get("game_type", [0, 0, 0])
        game_type_legend = _build_pie_legend(
            ["Singleplayer", "Multiplayer", "Co-op"],
            game_type_values,
            ["#3b82f6", "#10b981", "#f59e0b"],
        )

        platform_values = pies.get("platform", [0, 0, 0, 0])
        platform_legend = _build_pie_legend(
            ["Win only", "Win+Lin+Mac", "Win+Linux", "Win+Mac"],
            platform_values,
            ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"],
        )

        controller_values = pies.get("controller", [0, 0])
        controller_legend = _build_pie_legend(
            ["Yes", "No"], controller_values, ["#3b82f6", "#10b981"]
        )

        vr_values = pies.get("vr", [0, 0])
        vr_legend = _build_pie_legend(
            ["Yes", "No"], vr_values, ["#3b82f6", "#10b981"]
        )

        metrics = PRECOMPUTED["metrics"].get(selected_genre, {}).get(selected_period, {})
        current = metrics.get("current_period", {"games_released": 0, "market_value": 0, "purchased_copies": 0, "average_playtime": 0, "peak_ccu": 0})
        previous = metrics.get("previous_period", {"games_released": 0, "market_value": 0, "purchased_copies": 0, "average_playtime": 0, "peak_ccu": 0})

        games_released = _format_number(current["games_released"])
        market_value_text = _format_currency(current["market_value"])
        purchased_copies_text = _format_number(current["purchased_copies"])
        playtime_text = _format_playtime(current["average_playtime"])
        peak_ccu_text = _format_number(current["peak_ccu"])

        games_change_text, games_change_color = _relative_change(current["games_released"], previous["games_released"])
        market_change_text, market_change_color = _relative_change(current["market_value"], previous["market_value"])
        purchased_change_text, purchased_change_color = _relative_change(current["purchased_copies"], previous["purchased_copies"])
        playtime_change_text, playtime_change_color = _relative_change(current["average_playtime"], previous["average_playtime"])
        peak_change_text, peak_change_color = _relative_change(current["peak_ccu"], previous["peak_ccu"])

        games_comparison_text = _comparison_text(selected_period, previous["games_released"], _format_number)
        market_comparison_text = _comparison_text(selected_period, previous["market_value"], _format_currency)
        purchased_comparison_text = _comparison_text(selected_period, previous["purchased_copies"], _format_number)
        playtime_comparison_text = _comparison_text(selected_period, previous["average_playtime"], _format_playtime)
        peak_comparison_text = _comparison_text(selected_period, previous["peak_ccu"], _format_number)


        return (
            games_released,
            market_value_text,
            purchased_copies_text,
            playtime_text,
            peak_ccu_text,
            market_value_figure,
            relative_market_value_figure,
            purchased_copies_figure,
            relative_purchased_copies_figure,
            game_type_pie_figure,
            platform_pie_figure,
            controller_pie_figure,
            vr_pie_figure,
            game_type_legend,
            platform_legend,
            controller_legend,
            vr_legend,
            games_change_text,
            market_change_text,
            purchased_change_text,
            playtime_change_text,
            peak_change_text,
            {**CARD_CHANGE_STYLE, "color": games_change_color},
            {**CARD_CHANGE_STYLE, "color": market_change_color},
            {**CARD_CHANGE_STYLE, "color": purchased_change_color},
            {**CARD_CHANGE_STYLE, "color": playtime_change_color},
            {**CARD_CHANGE_STYLE, "color": peak_change_color},
            games_comparison_text,
            market_comparison_text,
            purchased_comparison_text,
            playtime_comparison_text,
            peak_comparison_text,
            BUTTON_ACTIVE_STYLE if selected_period == "month" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_period == "quarter" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_period == "year" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_range == "last-6-months" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_range == "last-year" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_range == "last-3-years" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_range == "last-6-years" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_range == "last-10-years" else BUTTON_BASE_STYLE,
            BUTTON_ACTIVE_STYLE if selected_range == "all-data" else BUTTON_BASE_STYLE,
        )