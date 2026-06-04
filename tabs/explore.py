from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, ctx, dash_table, dcc, html

from styles import (
    ACCENT_COLOR,
    DEFAULT_TABLE_COLUMNS,
    EXPLORE_BODY_STYLE,
    EXPLORE_GRAPH_STYLE,
    FIELD_STYLE,
    FILTER_INPUT_STYLE,
    HELP_TEXT_STYLE,
    HINT_PILL_STYLE,
    HISTOGRAM_CARD_STYLE,
    LABEL_STYLE,
    PANEL_STYLE,
    RIGHT_COLUMN_STYLE,
    SECTION_TITLE_STYLE,
    TABLE_AVAILABLE_COLUMNS,
    TABLE_BLOCK_STYLE,
    TABLE_CARD_STYLE,
    TABLE_CELL_STYLE,
    TABLE_HEADER_STYLE,
    TABLE_STYLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "games.csv"

title = "Explore Data"
desc = "Dive deeper into the Game Market data and explore interesting patterns."


def _tokenize(value: str) -> tuple[str, ...]:
    if not value:
        return ()
    tokens = [part.strip().lower() for part in value.split(",")]
    return tuple(token for token in tokens if token)


def _multi_options(values: pd.Series) -> list[dict[str, str]]:
    unique_values = sorted({str(value).strip() for value in values.dropna() if str(value).strip()})
    return [{"label": value, "value": value.lower()} for value in unique_values]


def _load_games() -> pd.DataFrame:
    usecols = [
        "Name",
        "Release date",
        "Estimated owners",
        "Peak CCU",
        "Price",
        "Metacritic score",
        "User score",
        "Positive",
        "Categories",
        "Genres",
        "Tags",
    ]
    frame = pd.read_csv(DATA_PATH, usecols=usecols, low_memory=False)
    frame["Release date"] = pd.to_datetime(frame["Release date"], errors="coerce")
    for column in ["Peak CCU", "Price", "Metacritic score", "User score", "Positive"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    owner_bounds = frame["Estimated owners"].fillna("").astype(str).str.extract(r"(?P<lower>\d+)\s*-\s*(?P<upper>\d+)")
    frame["Owners lower"] = pd.to_numeric(owner_bounds["lower"], errors="coerce")
    frame["Owners upper"] = pd.to_numeric(owner_bounds["upper"], errors="coerce")

    for column in ["Genres", "Categories", "Tags"]:
        frame[f"_{column.lower().replace(' ', '_')}_tokens"] = frame[column].fillna("").astype(str).map(_tokenize)

    frame["Positive ratings"] = frame["Positive"] * 100
    return frame


GAMES = _load_games()

GENRE_OPTIONS = _multi_options(GAMES["Genres"].dropna().astype(str).str.split(",").explode())
CATEGORY_OPTIONS = _multi_options(GAMES["Categories"].dropna().astype(str).str.split(",").explode())
TAG_OPTIONS = _multi_options(GAMES["Tags"].dropna().astype(str).str.split(",").explode())

RELEASE_MIN = GAMES["Release date"].min()
RELEASE_MAX = GAMES["Release date"].max()
PRICE_MIN = float(GAMES["Price"].min()) if not GAMES["Price"].dropna().empty else 0.0
PRICE_MAX = float(GAMES["Price"].max()) if not GAMES["Price"].dropna().empty else 0.0
OWNERS_MIN = int(GAMES["Owners lower"].min()) if not GAMES["Owners lower"].dropna().empty else 0
OWNERS_MAX = int(GAMES["Owners upper"].max()) if not GAMES["Owners upper"].dropna().empty else 0
USER_SCORE_MAX = 100
METACRITIC_MAX = int(GAMES["Metacritic score"].max()) if not GAMES["Metacritic score"].dropna().empty else 100
POSITIVE_MAX = 100.0


def _date_value(value: pd.Timestamp | None) -> str:
    if pd.isna(value):
        return ""
    return value.strftime("%Y-%m-%d")


def _build_range_inputs(prefix: str, minimum: float, maximum: float, step: str | float = "any") -> html.Div:
    return html.Div(
        [
            dcc.Input(
                id=f"{prefix}-min",
                type="number",
                value=minimum,
                min=minimum,
                max=maximum,
                step=step,
                debounce=True,
                style=FILTER_INPUT_STYLE,
            ),
            dcc.Input(
                id=f"{prefix}-max",
                type="number",
                value=maximum,
                min=minimum,
                max=maximum,
                step=step,
                debounce=True,
                style=FILTER_INPUT_STYLE,
            ),
        ],
        style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "0.65rem"},
    )


def _field(label: str, control, help_text: str | None = None) -> html.Div:
    children = [html.Div(label, style=LABEL_STYLE), control]
    if help_text:
        children.append(html.Div(help_text, style=HELP_TEXT_STYLE))
    return html.Div(children, style=FIELD_STYLE)


def _empty_figure(message: str) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin={"l": 42, "r": 18, "t": 18, "b": 42},
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "showarrow": False,
                "font": {"size": 15, "color": TEXT_SECONDARY},
            }
        ],
    )
    return figure


def _apply_token_filter(frame: pd.DataFrame, column: str, selected_values: list[str] | None) -> pd.DataFrame:
    selected = {value.strip().lower() for value in (selected_values or []) if value and value.strip()}
    if not selected:
        return frame
    token_column = f"_{column.lower().replace(' ', '_')}_tokens"
    return frame[frame[token_column].map(lambda tokens: bool(selected.intersection(tokens)))]


def _filter_games(
    genre_values,
    price_min,
    price_max,
    owners_min,
    owners_max,
    category_values,
    release_min,
    release_max,
    tag_values,
    user_score_min,
    user_score_max,
    metacritic_min,
    metacritic_max,
    positive_min,
    positive_max,
) -> pd.DataFrame:
    frame = GAMES

    if price_min is not None:
        frame = frame[frame["Price"].ge(price_min)]
    if price_max is not None:
        frame = frame[frame["Price"].le(price_max)]

    if owners_min is not None:
        frame = frame[frame["Owners upper"].ge(owners_min)]
    if owners_max is not None:
        frame = frame[frame["Owners lower"].le(owners_max)]

    if release_min:
        release_min_ts = pd.to_datetime(release_min, errors="coerce")
        frame = frame[frame["Release date"].ge(release_min_ts)]
    if release_max:
        release_max_ts = pd.to_datetime(release_max, errors="coerce")
        frame = frame[frame["Release date"].le(release_max_ts)]

    if user_score_min is not None:
        frame = frame[frame["User score"].ge(user_score_min)]
    if user_score_max is not None:
        frame = frame[frame["User score"].le(user_score_max)]

    if metacritic_min is not None:
        frame = frame[frame["Metacritic score"].ge(metacritic_min)]
    if metacritic_max is not None:
        frame = frame[frame["Metacritic score"].le(metacritic_max)]

    if positive_min is not None:
        frame = frame[frame["Positive ratings"].ge(positive_min)]
    if positive_max is not None:
        frame = frame[frame["Positive ratings"].le(positive_max)]

    frame = _apply_token_filter(frame, "Genres", genre_values)
    frame = _apply_token_filter(frame, "Categories", category_values)

    tag_selection = {value.strip().lower() for value in (tag_values or []) if value and value.strip()}
    if tag_selection:
        frame = frame[frame["_tags_tokens"].map(lambda tokens: bool(tag_selection.intersection(tokens)))]

    return frame


def _histogram_figure(frame: pd.DataFrame, filter_signature: str) -> go.Figure:
    values = frame["Peak CCU"].dropna()
    if values.empty:
        return _empty_figure("No games match the current filters.")

    values_min = float(values.min())
    values_max = float(values.max())
    full_span = max(values_max - values_min, 1.0)
    baseline_bin_count = 40
    baseline_bin_width = full_span / baseline_bin_count

    zoom_min = frame.attrs.get("zoom_min")
    zoom_max = frame.attrs.get("zoom_max")
    if zoom_min is not None and zoom_max is not None:
        visible_min = max(min(float(zoom_min), float(zoom_max)), values_min)
        visible_max = min(max(float(zoom_min), float(zoom_max)), values_max)
        if visible_max <= visible_min:
            visible_min, visible_max = values_min, values_max
    else:
        visible_min, visible_max = values_min, values_max

    visible_span = max(visible_max - visible_min, baseline_bin_width)
    dynamic_bins = max(8, min(120, int(round(visible_span / baseline_bin_width))))
    bin_size = max(visible_span / dynamic_bins, 1e-9)
    y_axis_revision = f"{filter_signature}|{visible_min:.6f}|{visible_max:.6f}|{dynamic_bins}"

    figure = go.Figure(
        data=[
            go.Histogram(
                x=values,
                autobinx=False,
                xbins={"start": visible_min, "end": visible_max, "size": bin_size},
                marker={"color": ACCENT_COLOR, "line": {"color": "#1d4ed8", "width": 0.5}},
                hovertemplate="Peak CCU: %{x}<br>Count: %{y}<extra></extra>",
            )
        ]
    )
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin={"l": 42, "r": 18, "t": 26, "b": 42},
        title={"text": "Peak CCU Histogram", "x": 0, "xanchor": "left", "font": {"size": 18, "color": TEXT_PRIMARY}},
        xaxis={"title": "Peak CCU", "uirevision": filter_signature},
        yaxis={"title": "Games", "autorange": True, "uirevision": y_axis_revision},
        bargap=0.05,
        uirevision=filter_signature,
        dragmode="zoom",
        hovermode="x",
        legend={"orientation": "h"},
    )
    return figure


def _extract_zoom_range(relayout_data):
    if not isinstance(relayout_data, dict) or relayout_data.get("xaxis.autorange"):
        return None, None

    axis_range = relayout_data.get("xaxis.range")
    if isinstance(axis_range, (list, tuple)) and len(axis_range) >= 2:
        x0, x1 = axis_range[0], axis_range[1]
    else:
        x0 = relayout_data.get("xaxis.range[0]")
        x1 = relayout_data.get("xaxis.range[1]")

    try:
        return float(x0), float(x1)
    except (TypeError, ValueError):
        return None, None


def _table_frame(frame: pd.DataFrame) -> pd.DataFrame:
    table = frame.copy()
    table["Release date"] = table["Release date"].dt.strftime("%Y-%m-%d").fillna("")
    table["Price"] = table["Price"].map(lambda value: "" if pd.isna(value) else f"{value:.2f}")
    table["User score"] = table["User score"].map(lambda value: "" if pd.isna(value) else f"{value:.0f}")
    table["Metacritic score"] = table["Metacritic score"].map(lambda value: "" if pd.isna(value) else f"{value:.0f}")
    table["Positive ratings"] = table["Positive ratings"].map(lambda value: "" if pd.isna(value) else f"{value:.1f}")
    table["Peak CCU"] = table["Peak CCU"].map(lambda value: "" if pd.isna(value) else f"{int(value):,}")
    table["Estimated owners"] = table["Estimated owners"].fillna("")
    table["Genres"] = table["Genres"].fillna("")
    table["Categories"] = table["Categories"].fillna("")
    table["Tags"] = table["Tags"].fillna("")
    return table[
        [
            "Name",
            "Release date",
            "Estimated owners",
            "Peak CCU",
            "Price",
            "Genres",
            "Categories",
            "Tags",
            "User score",
            "Metacritic score",
            "Positive ratings",
        ]
    ]


def _table_style(active_cell) -> list[dict]:
    base = [
        {"if": {"row_index": "odd"}, "backgroundColor": "#fafcff"},
        {"if": {"state": "active"}, "backgroundColor": "inherit", "border": "1px solid rgba(0, 0, 0, 0)"},
    ]
    if isinstance(active_cell, dict) and active_cell.get("row") is not None:
        base.append({"if": {"row_index": active_cell["row"]}, "backgroundColor": "#dbeafe", "color": TEXT_PRIMARY})
    return base


layout = html.Div(
    [
        html.Div(
            [
                html.H2(title, style={"fontSize": "1.8rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY}),
                html.Div(desc, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "marginTop": "4px"}),
            ],
            style={"marginBottom": "0.75rem"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Filters", style=SECTION_TITLE_STYLE),
                        html.Div(
                            "Use the controls below to narrow the dataset before exploring the CCU distribution.",
                            style=HELP_TEXT_STYLE,
                        ),
                        html.Div("Linked table follows the histogram zoom range.", style=HINT_PILL_STYLE),
                        _field(
                            "Genres",
                            dcc.Dropdown(
                                id="explore-genres",
                                options=GENRE_OPTIONS,
                                value=[],
                                multi=True,
                                placeholder="Select one or more genres",
                            ),
                        ),
                        _field(
                            "Price",
                            _build_range_inputs("explore-price", PRICE_MIN, PRICE_MAX),
                            "Lower and upper price bounds.",
                        ),
                        _field(
                            "Owners",
                            _build_range_inputs("explore-owners", OWNERS_MIN, OWNERS_MAX, step=1),
                            "Matches games whose estimated owner range overlaps the selected interval.",
                        ),
                        _field(
                            "Categories",
                            dcc.Dropdown(
                                id="explore-categories",
                                options=CATEGORY_OPTIONS,
                                value=[],
                                multi=True,
                                placeholder="Select one or more categories",
                            ),
                        ),
                        _field(
                            "Release date",
                            html.Div(
                                [
                                    dcc.Input(
                                        id="explore-release-min",
                                        type="number",
                                        value=_date_value(RELEASE_MIN),
                                        min=_date_value(RELEASE_MIN),
                                        max=_date_value(RELEASE_MAX),
                                        debounce=True,
                                        style=FILTER_INPUT_STYLE,
                                    ),
                                    dcc.Input(
                                        id="explore-release-max",
                                        type="number",
                                        value=_date_value(RELEASE_MAX),
                                        min=_date_value(RELEASE_MIN),
                                        max=_date_value(RELEASE_MAX),
                                        debounce=True,
                                        style=FILTER_INPUT_STYLE,
                                    ),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "repeat(2, minmax(0, 1fr))", "gap": "0.65rem"},
                            ),
                            "Use the calendar inputs to constrain the release window.",
                        ),
                        _field(
                            "Tags",
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="explore-tags",
                                        options=TAG_OPTIONS,
                                        value=[],
                                        multi=True,
                                        placeholder="Select one or more tags",
                                    ),
                                ],
                                style={"display": "flex", "flexDirection": "column", "gap": "0.65rem"},
                            ),
                            "Select one or many tags.",
                        ),
                        _field(
                            "User score",
                            _build_range_inputs("explore-user-score", 0, USER_SCORE_MAX, step=1),
                            "Score is constrained to the 0-100 range.",
                        ),
                        _field(
                            "Metacritic score",
                            _build_range_inputs("explore-metacritic", 0, METACRITIC_MAX, step=1),
                            "Lower and upper Metacritic score bounds.",
                        ),
                        _field(
                            "Positive ratings",
                            _build_range_inputs("explore-positive", 0, POSITIVE_MAX, step=0.1),
                            "Values are shown as percentages from 0 to 100.",
                        ),
                    ],
                    style=PANEL_STYLE,
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id="explore-peak-ccu-histogram",
                                    figure=_empty_figure("Apply filters to see the peak CCU distribution."),
                                    style=EXPLORE_GRAPH_STYLE,
                                    config={"displayModeBar": True, "responsive": True, "scrollZoom": True},
                                ),
                            ],
                            style=HISTOGRAM_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("Matching Games", style=SECTION_TITLE_STYLE),
                                        dcc.Dropdown(
                                            id="explore-table-columns",
                                            options=[{"label": column, "value": column} for column in TABLE_AVAILABLE_COLUMNS],
                                            value=DEFAULT_TABLE_COLUMNS,
                                            multi=True,
                                            clearable=False,
                                            placeholder="Select columns to display",
                                            style={"minWidth": "320px", "maxWidth": "520px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "flex-start",
                                        "justifyContent": "space-between",
                                        "gap": "1rem",
                                        "flexWrap": "wrap",
                                    },
                                ),
                                html.Div(
                                    dash_table.DataTable(
                                        id="explore-matches-table",
                                        columns=[{"name": column, "id": column} for column in DEFAULT_TABLE_COLUMNS],
                                        data=[],
                                        page_action="custom",
                                        page_current=0,
                                        page_size=15,
                                        page_count=1,
                                        sort_action="custom",
                                        sort_mode="single",
                                        sort_by=[],
                                        filter_action="none",
                                        style_table=TABLE_STYLE,
                                        style_cell=TABLE_CELL_STYLE,
                                        style_header=TABLE_HEADER_STYLE,
                                        style_data_conditional=_table_style(None),
                                        fixed_rows={"headers": True},
                                    ),
                                    style={"flex": "1 1 0", "minHeight": 0},
                                ),
                            ],
                            style={**TABLE_CARD_STYLE, **TABLE_BLOCK_STYLE},
                        ),
                    ],
                    style=RIGHT_COLUMN_STYLE,
                ),
            ],
            style=EXPLORE_BODY_STYLE,
        ),
    ]
)


def register_callbacks(app):
    @app.callback(
        Output("explore-peak-ccu-histogram", "figure"),
        Output("explore-matches-table", "columns"),
        Output("explore-matches-table", "data"),
        Output("explore-matches-table", "page_count"),
        Output("explore-matches-table", "page_current"),
        Output("explore-matches-table", "style_data_conditional"),
        Input("explore-genres", "value"),
        Input("explore-price-min", "value"),
        Input("explore-price-max", "value"),
        Input("explore-owners-min", "value"),
        Input("explore-owners-max", "value"),
        Input("explore-categories", "value"),
        Input("explore-release-min", "value"),
        Input("explore-release-max", "value"),
        Input("explore-tags", "value"),
        Input("explore-user-score-min", "value"),
        Input("explore-user-score-max", "value"),
        Input("explore-metacritic-min", "value"),
        Input("explore-metacritic-max", "value"),
        Input("explore-positive-min", "value"),
        Input("explore-positive-max", "value"),
        Input("explore-table-columns", "value"),
        Input("explore-matches-table", "sort_by"),
        Input("explore-peak-ccu-histogram", "relayoutData"),
        Input("explore-matches-table", "active_cell"),
        Input("explore-matches-table", "page_current"),
        Input("explore-matches-table", "page_size"),
    )
    def update_explore(
        genre_values,
        price_min,
        price_max,
        owners_min,
        owners_max,
        category_values,
        release_min,
        release_max,
        tag_values,
        user_score_min,
        user_score_max,
        metacritic_min,
        metacritic_max,
        positive_min,
        positive_max,
        selected_table_columns,
        sort_by,
        relayout_data,
        active_cell,
        page_current,
        page_size,
    ):
        filtered = _filter_games(
            genre_values,
            price_min,
            price_max,
            owners_min,
            owners_max,
            category_values,
            release_min,
            release_max,
            tag_values,
            user_score_min,
            user_score_max,
            metacritic_min,
            metacritic_max,
            positive_min,
            positive_max,
        )

        filter_signature = "|".join(
            [
                str(sorted((genre_values or []))),
                str(price_min),
                str(price_max),
                str(owners_min),
                str(owners_max),
                str(sorted((category_values or []))),
                str(release_min),
                str(release_max),
                str(sorted((tag_values or []))),
                str(user_score_min),
                str(user_score_max),
                str(metacritic_min),
                str(metacritic_max),
                str(positive_min),
                str(positive_max),
            ]
        )

        x_min, x_max = _extract_zoom_range(relayout_data)
        filtered_for_hist = filtered.copy()
        filtered_for_hist.attrs["zoom_min"] = x_min
        filtered_for_hist.attrs["zoom_max"] = x_max
        histogram_figure = _histogram_figure(filtered_for_hist, filter_signature)

        visible_columns = [column for column in (selected_table_columns or DEFAULT_TABLE_COLUMNS) if column in TABLE_AVAILABLE_COLUMNS]
        if not visible_columns:
            visible_columns = DEFAULT_TABLE_COLUMNS
        table_columns = [{"name": column, "id": column} for column in visible_columns]

        table_frame = filtered
        if x_min is not None and x_max is not None:
            table_frame = table_frame[table_frame["Peak CCU"].between(x_min, x_max, inclusive="both")]

        if sort_by:
            sort_column = sort_by[0].get("column_id")
            sort_direction = sort_by[0].get("direction", "desc")
            if sort_column in table_frame.columns:
                table_frame = table_frame.sort_values(
                    by=sort_column,
                    ascending=(sort_direction == "asc"),
                    kind="mergesort",
                    na_position="last",
                )

        page_size = int(page_size or 15)
        page_current = int(page_current or 0)
        triggered_props = {trigger.get("prop_id", "") for trigger in ctx.triggered}
        pagination_triggered = any(
            prop.startswith("explore-matches-table.page_current") or prop.startswith("explore-matches-table.page_size")
            for prop in triggered_props
        )
        current_page = page_current if pagination_triggered else 0

        total_rows = len(table_frame)
        page_count = max(1, math.ceil(total_rows / page_size))
        current_page = max(0, min(current_page, page_count - 1))
        start = current_page * page_size
        end = start + page_size
        page_data = _table_frame(table_frame.iloc[start:end])[visible_columns].to_dict("records")

        return histogram_figure, table_columns, page_data, page_count, current_page, _table_style(active_cell)
        
