from pathlib import Path

import pandas as pd
from dash import Input, Output, ctx, dcc, html, no_update

from styles import (
    BUTTON_ACTIVE_STYLE,
    BUTTON_BASE_STYLE,
    BUTTON_ROW_STYLE,
    CARD_CHANGE_STYLE,
    CARD_COMPARISON_STYLE,
    CARD_VALUE_STYLE,
    METRIC_CARD_STYLE,
    METRIC_GRID_STYLE,
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

GENRE_DROPDOWN_ID = "overview-genre-dropdown"
PERIOD_STORE_ID = "overview-period-store"
MONTH_BUTTON_ID = "overview-period-month"
QUARTER_BUTTON_ID = "overview-period-quarter"
YEAR_BUTTON_ID = "overview-period-year"
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


layout = html.Div(
    [
        dcc.Store(id=PERIOD_STORE_ID, data=DEFAULT_PERIOD),
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
        Output(GAMES_VALUE_ID, "children"),
        Output(MARKET_VALUE_ID, "children"),
        Output(PURCHASED_VALUE_ID, "children"),
        Output(PLAYTIME_VALUE_ID, "children"),
        Output(PEAK_CCU_VALUE_ID, "children"),
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
        Input(GENRE_DROPDOWN_ID, "value"),
        Input(PERIOD_STORE_ID, "data"),
    )
    def update_metrics(selected_genre, selected_period):
        start_date, end_date = _period_window(selected_period, END_RANGE)
        filtered = _filter_games(games, selected_genre, start_date, end_date)
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
        )