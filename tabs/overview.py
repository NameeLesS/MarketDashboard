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


def _parse_owner_midpoint(value):
    if pd.isna(value):
        return pd.NA

    end_points = [float(val.strip()) for val in value.split(" - ")]
    return sum(end_points) / 2


def _load_games() -> pd.DataFrame:
    DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "games.csv"
    games = pd.read_csv(DATA_PATH, index_col=0)
    games["Release date"] = pd.to_datetime(games["Release date"], errors="coerce")
    for column in ["Price", "Peak CCU", "Average playtime forever"]:
        games[column] = pd.to_numeric(games[column], errors="coerce")
    games["Owner midpoint"] = games["Estimated owners"].apply(_parse_owner_midpoint)
    return games


games = _load_games()

genre_values = sorted(
    {
        genre.strip()
        for genres in games["Genres"].dropna().astype(str)
        for genre in genres.split(",")
        if genre.strip()
    }
)


title = 'Overview'
desc = 'A high-level view of the gaming market.'

END_RANGE = games['Release date'].max()
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
    history_start = games["Release date"].min().normalize()
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


def _bucket_market_value(df, period, start_date, end_date):
    if df.empty:
        return pd.DataFrame(columns=["Release date", "Market value"])

    working = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)]
    working["Market value"] = working["Owner midpoint"].fillna(0) * working["Price"].fillna(0)
    working["Release date"] = working["Release date"].dt.to_period(_period_frequency(period)).dt.to_timestamp()
    grouped = (
        working.groupby("Release date")
        ["Market value"]
        .sum()
        .reset_index()
    )
    return grouped[grouped["Market value"] > 0]


def _bucket_purchased_copies(df, period, start_date, end_date):
    if df.empty:
        return pd.DataFrame(columns=["Release date", "Purchased copies"])

    working = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)].copy()
    working["Purchased copies"] = working["Owner midpoint"].fillna(0)
    working["Release date"] = working["Release date"].dt.to_period(_period_frequency(period)).dt.to_timestamp()
    grouped = working.groupby("Release date")["Purchased copies"].sum().reset_index()
    return grouped[grouped["Purchased copies"] > 0]


def _category_items(value):
    return {item.strip().lower() for item in str(value).split(",") if item.strip()}


def _has_any_category(value, terms):
    normalized = _category_items(value)
    return any(term.strip().lower() in normalized for term in terms)


def _build_pie_figure(labels, values, title, colors):
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
                "hole": 0.34,
                "hovertemplate": "%{label}<br>%{value:,}<br>%{percent}<extra></extra>",
            }
        ],
        "layout": {
            "title": {"text": title, "x": 0.02, "xanchor": "left", "font": {"size": 16}},
            "margin": {"l": 12, "r": 140, "t": 40, "b": 12},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "showlegend": True,
            "legend": {
                "x": 1.01,
                "y": 1,
                "xanchor": "left",
                "yanchor": "top",
                "orientation": "v",
                "font": {"size": 11},
            },
            "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY},
        },
    }


def _legend_labels_with_percentages(labels, values):
    total = sum(values)
    if total <= 0:
        return [f"{label} (0.0%)" for label in labels]

    return [f"{label} ({(value / total) * 100:.1f}%)" for label, value in zip(labels, values)]


def _build_game_type_pie_figure(df):
    category_series = df["Categories"].fillna("").astype(str)
    singleplayer_terms = {"Single-player"}
    multiplayer_terms = {
        "Multi-player",
        "PvP",
        "Online PvP",
        "Remote Play Together",
        "Cross-Platform Multiplayer",
        "MMO",
        "LAN PvP",
    }
    coop_terms = {
        "Co-op",
        "Remote Play Together",
        "Online Co-op",
        "Shared/Split Screen Co-op",
        "LAN Co-op",
    }

    values = [
        int(category_series.apply(lambda value: _has_any_category(value, singleplayer_terms)).sum()),
        int(category_series.apply(lambda value: _has_any_category(value, multiplayer_terms)).sum()),
        int(category_series.apply(lambda value: _has_any_category(value, coop_terms)).sum()),
    ]
    labels = ["Singleplayer", "Multiplayer", "Co-op"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "Game Type",
        ["#2563eb", "#f59e0b", "#10b981"],
    )


def _build_platform_pie_figure(df):
    windows = df["Windows"].fillna(False).astype(bool)
    linux = df["Linux"].fillna(False).astype(bool)
    mac = df["Mac"].fillna(False).astype(bool)

    values = [
        int((windows & ~linux & ~mac).sum()),
        int((windows & linux & mac).sum()),
        int((windows & linux & ~mac).sum()),
        int((windows & ~linux & mac).sum()),
    ]
    labels = ["Windows only", "Windows + Linux + Mac", "Windows + Linux", "Windows + Mac"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "Supported Platforms",
        ["#3b82f6", "#8b5cf6", "#22c55e", "#f97316"],
    )


def _build_controller_support_pie_figure(df):
    supported_terms = {
        "Full controller support",
        "Partial controller support",
        "Tracked Controller Support",
    }
    supported = df["Categories"].fillna("").astype(str).apply(lambda value: _has_any_category(value, supported_terms))
    values = [int(supported.sum()), int((~supported).sum())]
    labels = ["Yes", "No"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "Controller Support",
        ["#14b8a6", "#ef4444"],
    )


def _build_vr_support_pie_figure(df):
    supported_terms = {"VR Only", "VR Supported", "VR Support", "SteamVR Collectibles"}
    supported = df["Categories"].fillna("").astype(str).apply(lambda value: _has_any_category(value, supported_terms))
    values = [int(supported.sum()), int((~supported).sum())]
    labels = ["Yes", "No"]
    return _build_pie_figure(
        _legend_labels_with_percentages(labels, values),
        values,
        "VR Support",
        ["#a855f7", "#64748b"],
    )


def _genre_market_value_buckets(df, period, start_date, end_date):
    if df.empty:
        return pd.DataFrame(columns=["Release date", "Genre", "Market value"])

    working = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)]
    genre_lists = working["Genres"].fillna("").astype(str).apply(
        lambda value: [genre.strip() for genre in value.split(",") if genre.strip()]
    )
    working["Genre list"] = genre_lists
    working["Genre count"] = genre_lists.apply(len)
    working = working[working["Genre count"] > 0].explode("Genre list")
    working["Release date"] = working["Release date"].dt.to_period(_period_frequency(period)).dt.to_timestamp()
    working["Market value"] = (
        working["Owner midpoint"].fillna(0) * working["Price"].fillna(0) / working["Genre count"]
    )
    grouped = working.groupby(["Release date", "Genre list"])["Market value"].sum().reset_index()
    grouped.rename(columns={"Genre list": "Genre"}, inplace=True)
    return grouped[grouped["Market value"] > 0]


def _genre_purchased_copies_buckets(df, period, start_date, end_date):
    if df.empty:
        return pd.DataFrame(columns=["Release date", "Genre", "Purchased copies"])

    working = df[(df["Release date"] >= start_date) & (df["Release date"] < end_date)].copy()
    genre_lists = working["Genres"].fillna("").astype(str).apply(
        lambda value: [genre.strip() for genre in value.split(",") if genre.strip()]
    )
    working["Genre list"] = genre_lists
    working["Genre count"] = genre_lists.apply(len)
    working = working[working["Genre count"] > 0].explode("Genre list")
    working["Release date"] = working["Release date"].dt.to_period(_period_frequency(period)).dt.to_timestamp()
    working["Purchased copies"] = working["Owner midpoint"].fillna(0) / working["Genre count"]
    grouped = working.groupby(["Release date", "Genre list"])["Purchased copies"].sum().reset_index()
    grouped.rename(columns={"Genre list": "Genre"}, inplace=True)
    return grouped[grouped["Purchased copies"] > 0]


def _build_market_value_figure(df, period, start_date, end_date):
    grouped = _bucket_market_value(df, period, start_date, end_date)
    return timeseries_line_figure(
        grouped,
        period=period,
        y_col="Market value",
        title="Estimated Market Value",
        yaxis_title="Market value",
        hover_template="%{x|%b %d, %Y}<br>Market value: $%{y:,.0f}<extra></extra>",
        currency=True,
    )


def _build_purchased_copies_figure(df, period, start_date, end_date):
    grouped = _bucket_purchased_copies(df, period, start_date, end_date)
    return timeseries_line_figure(
        grouped,
        period=period,
        y_col="Purchased copies",
        title="Estimated Purchased Copies",
        yaxis_title="Purchased copies",
        hover_template="%{x|%b %d, %Y}<br>Purchased copies: %{y:,.0f}<extra></extra>",
        currency=False,
    )


def timeseries_line_figure(grouped, period, y_col, title, yaxis_title, hover_template, currency=False):
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
            "title": {"text": title, "x": 0.02, "xanchor": "left"},
            "margin": {"l": 50, "r": 20, "t": 52, "b": 50},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "hovermode": "x unified",
            "xaxis": {
                "title": _period_axis_label(period),
                "type": "date",
                "showgrid": False,
                "tickformatstops": _period_tickformatstops(period),
            },
            "yaxis": yaxis,
            "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY},
        },
    }


def _build_relative_market_value_figure(df, period, selected_genre, start_date, end_date):
    grouped = _genre_market_value_buckets(df, period, start_date, end_date)
    return relative_barchart_figure(
        grouped,
        period=period,
        value_col="Market value",
        title="Relative Market Value",
        yaxis_title="Market value",
        hover_label="Market value",
        currency=True,
        selected_genre=selected_genre,
    )


def _build_relative_purchased_copies_figure(df, period, selected_genre, start_date, end_date):
    grouped = _genre_purchased_copies_buckets(df, period, start_date, end_date)
    return relative_barchart_figure(
        grouped,
        period=period,
        value_col="Purchased copies",
        title="Relative Purchased Copies",
        yaxis_title="Purchased copies",
        hover_label="Purchased copies",
        currency=False,
        selected_genre=selected_genre,
    )


def relative_barchart_figure(grouped, period, value_col, title, yaxis_title, hover_label, currency=False, selected_genre=None):
    """Build a stacked relative bar chart with optional highlighted genre and midpoint trend."""
    selected_is_all = not selected_genre or selected_genre == DEFAULT_GENRE
    if selected_is_all:
        genre_totals = grouped.groupby("Genre")[value_col].sum().sort_values(ascending=False)
        ordered_genres = genre_totals.index.tolist()
        highlighted_genre = None
    else:
        highlighted_genre = selected_genre
        genre_totals = grouped.groupby("Genre")[value_col].sum().sort_values(ascending=False)
        ordered_genres = [selected_genre] + [genre for genre in genre_totals.index.tolist() if genre != selected_genre]

    traces = []
    if not grouped.empty:
        x_index = pd.period_range(
            start=grouped["Release date"].min().to_period(_period_frequency(period)),
            end=grouped["Release date"].max().to_period(_period_frequency(period)),
            freq=_period_frequency(period),
        ).to_timestamp()
    else:
        x_index = pd.DatetimeIndex([])
    x_values = x_index.to_pydatetime().tolist()

    for index, genre in enumerate(ordered_genres):
        genre_frame = grouped[grouped["Genre"] == genre]
        if genre_frame.empty and genre != highlighted_genre:
            continue
        if len(x_index) > 0:
            genre_frame = genre_frame.set_index("Release date").reindex(x_index, fill_value=pd.NA).reset_index()
            genre_frame.rename(columns={"index": "Release date"}, inplace=True)
        else:
            genre_frame = pd.DataFrame({"Release date": [], value_col: []})
        values = genre_frame[value_col].fillna(0).tolist()
        is_highlighted = genre == highlighted_genre
        color = ACCENT_COLOR if is_highlighted else GENRE_PALETTE[index % len(GENRE_PALETTE)]

        hoverfmt = f"{genre}<br>%{{x|%b %d, %Y}}<br>{hover_label}: %{{y:,.0f}}<extra></extra>"
        if currency:
            hoverfmt = f"{genre}<br>%{{x|%b %d, %Y}}<br>{hover_label}: $%{{y:,.0f}}<extra></extra>"

        traces.append(
            {
                "type": "bar",
                "name": genre,
                "x": x_values,
                "y": values,
                "marker": {
                    "color": color,
                    "line": {"color": "#0f172a" if is_highlighted else color, "width": 1.4 if is_highlighted else 0.5},
                    "opacity": 0.96 if is_highlighted else 0.68,
                },
                "hovertemplate": hoverfmt,
            }
        )

        if is_highlighted:
            midpoint_values = [value / 2 for value in values]
            traces.append(
                {
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": f"{genre} trend",
                    "x": x_values,
                    "y": midpoint_values,
                    "line": {"color": "#0f172a", "width": 3},
                    "marker": {"color": "#0f172a", "size": 6},
                    "hoverinfo": "skip",
                }
            )

    yaxis = {"title": yaxis_title, "separatethousands": True, "showgrid": True}
    if currency:
        yaxis.update({"tickprefix": "$", "separatethousands": True})

    return {
        "data": traces,
        "layout": {
            "title": {"text": title, "x": 0.02, "xanchor": "left"},
            "margin": {"l": 50, "r": 20, "t": 52, "b": 50},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "barmode": "stack",
            "hovermode": "closest",
            "xaxis": {
                "title": _period_axis_label(period),
                "type": "date",
                "showgrid": False,
                "tickformatstops": _period_tickformatstops(period),
            },
            "yaxis": yaxis,
            "showlegend": False,
            "font": {"family": "Inter, sans-serif", "color": TEXT_PRIMARY},
        },
    }


def _filter_games(df, genre, start_date, end_date):
    filtered = df
    if genre and genre != DEFAULT_GENRE:
        filtered = df[df["Genres"].fillna("").str.contains(genre, case=False, na=False)]

    filtered = filtered[(filtered["Release date"] >= start_date) & (filtered["Release date"] < end_date)]
    return filtered



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
default_start_date, default_end_date = _period_window(DEFAULT_PERIOD, END_RANGE)
default_period_games = _filter_games(games, DEFAULT_GENRE, default_start_date, default_end_date)
history_start_date = games["Release date"].min().normalize()
default_range_start_date = _range_start_date(DEFAULT_RANGE)
default_market_value_figure = _build_market_value_figure(
    _filter_games(games, DEFAULT_GENRE, default_range_start_date, END_RANGE),
    DEFAULT_PERIOD,
    default_range_start_date,
    END_RANGE,
)
default_relative_market_value_figure = _build_relative_market_value_figure(
    _filter_games(games, DEFAULT_GENRE, default_range_start_date, END_RANGE),
    DEFAULT_PERIOD,
    DEFAULT_GENRE,
    default_range_start_date,
    END_RANGE,
)
default_purchased_copies_figure = _build_purchased_copies_figure(
    _filter_games(games, DEFAULT_GENRE, default_range_start_date, END_RANGE),
    DEFAULT_PERIOD,
    default_range_start_date,
    END_RANGE,
)
default_relative_purchased_copies_figure = _build_relative_purchased_copies_figure(
    _filter_games(games, DEFAULT_GENRE, default_range_start_date, END_RANGE),
    DEFAULT_PERIOD,
    DEFAULT_GENRE,
    default_range_start_date,
    END_RANGE,
)
default_game_type_pie_figure = _build_game_type_pie_figure(default_period_games)
default_platform_pie_figure = _build_platform_pie_figure(default_period_games)
default_controller_pie_figure = _build_controller_support_pie_figure(default_period_games)
default_vr_pie_figure = _build_vr_support_pie_figure(default_period_games)
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
                                "fontSize": "0.85rem",
                                "fontWeight": "600",
                                "marginBottom": "0.5rem",
                            },
                        ),
                        dcc.Dropdown(
                            id=GENRE_DROPDOWN_ID,
                            options=genre_options,
                            value=DEFAULT_GENRE,
                            clearable=False,
                            searchable=True,
                            style={"color": TEXT_PRIMARY},
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
                    [
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
                    [
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
                    "Game Characteristics",
                    style={"fontSize": "1.25rem", "fontWeight": "700", "color": TEXT_PRIMARY, "marginTop": "0.5rem"},
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
                                )
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
                                )
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
                                )
                            ],
                            style=PIE_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id=VR_PIE_ID,
                                    figure=default_vr_pie_figure,
                                    style=PIE_GRAPH_STYLE,
                                    config={"displayModeBar": False, "responsive": True},
                                )
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
    )
    def update_metrics(selected_genre, selected_period, selected_range):
        start_date, end_date = _period_window(selected_period, END_RANGE)
        filtered = _filter_games(games, selected_genre, start_date, end_date)
        range_start_date = _range_start_date(selected_range)
        market_value_figure = _build_market_value_figure(
            _filter_games(games, selected_genre, range_start_date, END_RANGE),
            selected_period,
            range_start_date,
            END_RANGE,
        )
        relative_market_value_figure = _build_relative_market_value_figure(
            _filter_games(games, DEFAULT_GENRE, range_start_date, END_RANGE),
            selected_period,
            selected_genre,
            range_start_date,
            END_RANGE,
        )
        purchased_copies_figure = _build_purchased_copies_figure(
            _filter_games(games, selected_genre, range_start_date, END_RANGE),
            selected_period,
            range_start_date,
            END_RANGE,
        )
        relative_purchased_copies_figure = _build_relative_purchased_copies_figure(
            _filter_games(games, DEFAULT_GENRE, range_start_date, END_RANGE),
            selected_period,
            selected_genre,
            range_start_date,
            END_RANGE,
        )
        filtered_for_pies = _filter_games(games, selected_genre, range_start_date, END_RANGE)
        game_type_pie_figure = _build_game_type_pie_figure(filtered_for_pies)
        platform_pie_figure = _build_platform_pie_figure(filtered_for_pies)
        controller_pie_figure = _build_controller_support_pie_figure(filtered_for_pies)
        vr_pie_figure = _build_vr_support_pie_figure(filtered_for_pies)
        previous_start, previous_end = _period_window(selected_period, start_date)
        previous_filtered = _filter_games(games, selected_genre, previous_start, previous_end)

        owners = filtered["Owner midpoint"].fillna(0)
        prices = filtered["Price"].fillna(0)
        market_value = (owners * prices).sum()
        purchased_copies = owners.sum()
        average_playtime = filtered["Average playtime forever"].mean(skipna=True)
        peak_ccu = filtered["Peak CCU"].max(skipna=True)

        previous_owners = previous_filtered["Owner midpoint"].fillna(0)
        previous_prices = previous_filtered["Price"].fillna(0)
        previous_market_value = (previous_owners * previous_prices).sum()
        previous_purchased_copies = previous_owners.sum()
        previous_average_playtime = previous_filtered["Average playtime forever"].mean(skipna=True)
        previous_peak_ccu = previous_filtered["Peak CCU"].max(skipna=True)

        games_released = _format_number(len(filtered))
        market_value_text = _format_currency(market_value)
        purchased_copies_text = _format_number(purchased_copies)
        playtime_text = _format_playtime(0 if pd.isna(average_playtime) else average_playtime)
        peak_ccu_text = _format_number(0 if pd.isna(peak_ccu) else peak_ccu)

        games_change_text, games_change_color = _relative_change(len(filtered), len(previous_filtered))
        market_change_text, market_change_color = _relative_change(market_value, previous_market_value)
        purchased_change_text, purchased_change_color = _relative_change(purchased_copies, previous_purchased_copies)
        playtime_change_text, playtime_change_color = _relative_change(
            0 if pd.isna(average_playtime) else average_playtime,
            0 if pd.isna(previous_average_playtime) else previous_average_playtime,
        )
        peak_change_text, peak_change_color = _relative_change(
            0 if pd.isna(peak_ccu) else peak_ccu,
            0 if pd.isna(previous_peak_ccu) else previous_peak_ccu,
        )

        games_comparison_text = _comparison_text(selected_period, len(previous_filtered), _format_number)
        market_comparison_text = _comparison_text(selected_period, previous_market_value, _format_currency)
        purchased_comparison_text = _comparison_text(selected_period, previous_purchased_copies, _format_number)
        playtime_comparison_text = _comparison_text(selected_period, previous_average_playtime, _format_playtime)
        peak_comparison_text = _comparison_text(selected_period, previous_peak_ccu, _format_number)


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