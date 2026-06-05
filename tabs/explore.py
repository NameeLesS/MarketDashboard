from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, ctx, dash_table, dcc, html, no_update

from styles import (
    ACCENT_COLOR,
    BUTTON_ACTIVE_STYLE,
    BUTTON_BASE_STYLE,
    CARD_CHANGE_STYLE,
    CARD_STYLE,
    CHART_CARD_STYLE,
    CHART_PLOTS_GRID_STYLE,
    DEFAULT_TABLE_COLUMNS,
    EXPLORE_BODY_STYLE,
    EXPLORE_GRAPH_STYLE,
    EXPLORE_PAGE_HEADER_STYLE,
    EXPLORE_PAGE_SUBTITLE_STYLE,
    EXPLORE_PAGE_TITLE_STYLE,
    FIELD_STYLE,
    FILTER_INPUT_STYLE,
    HELP_TEXT_STYLE,
    HINT_PILL_STYLE,
    HISTOGRAM_CARD_STYLE,
    LABEL_STYLE,
    PANEL_STYLE,
    PLOT_CARD_HEADER_STYLE,
    PLOT_CARD_STYLE,
    PLOT_CHART_STYLE,
    PLOT_CHART_WRAPPER_STYLE,
    RANGE_INPUT_GRID_STYLE,
    RIGHT_COLUMN_STYLE,
    SCATTER_CARD_STYLE,
    SECTION_TITLE_STYLE,
    SORT_BUTTON_GROUP_STYLE,
    SORT_BUTTON_SMALL_ACTIVE_STYLE,
    SORT_BUTTON_SMALL_BASE_STYLE,
    TABLE_AVAILABLE_COLUMNS,
    TABLE_BLOCK_STYLE,
    TABLE_CARD_STYLE,
    TABLE_CELL_STYLE,
    TABLE_COLUMN_PICKER_DROPDOWN_STYLE,
    TABLE_COLUMN_PICKER_STYLE,
    TABLE_HEADER_STYLE,
    TABLE_STYLE,
    TABLE_WRAPPER_STYLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "games.csv"

title = "Explore Data"
desc = "Dive deeper into the Game Market data and explore interesting patterns."

COLOR_USER_SCORE = "#3b82f6"
COLOR_META_SCORE = "#10b981"
COLOR_POSITIVE = "#3b82f6"
COLOR_NEGATIVE = "#ef4444"
COLOR_DIVERGE_DEFAULT = "#0f172a"
COLOR_SELECTED = "#ea580c"

CHART_HEIGHT = 380
TOP_N_GAMES = 50


def _tokenize(value: str) -> tuple[str, ...]:
    """Split a comma-separated string into a lowercase token tuple."""
    if not value:
        return ()
    return tuple(part.strip().lower() for part in value.split(",") if part.strip())


def _multi_options(values: pd.Series) -> list[dict[str, str]]:
    """Build a sorted list of {label, value} dicts for a Dash Dropdown."""
    unique = sorted({str(v).strip() for v in values.dropna() if str(v).strip()})
    return [{"label": v, "value": v.lower()} for v in unique]


def _load_games() -> pd.DataFrame:
    parquet_path = Path(__file__).resolve().parents[1] / "data" / "explore_optimized.parquet"
    frame = pd.read_parquet(parquet_path)
    return frame


GAMES = _load_games()


def _build_available_columns() -> list[str]:
    base_cols = [
        "Name", "Release date", "Estimated owners", "Peak CCU", "Price",
        "Genres", "Categories", "Tags", "User score", "Metacritic score",
        "Positive ratings", "Negative ratings", "Positive (raw)", "Negative (raw)"
    ]
    other_cols = []
    for c in GAMES.columns:
        if c not in base_cols and not c.startswith("_"):
            other_cols.append(c)
    other_cols.sort()
    return base_cols + other_cols


TABLE_AVAILABLE_COLUMNS = _build_available_columns()


def _get_robust_color_values(series: pd.Series) -> tuple[pd.Series, float, float]:
    """Clip upper outliers to a robust range (e.g. 95th percentile) for heatmap coloring."""
    numeric_series = pd.to_numeric(series, errors="coerce").fillna(0)
    if numeric_series.empty:
        return numeric_series, 0.0, 0.0
    val_min = float(numeric_series.min())
    val_max = float(numeric_series.max())
    if val_min == val_max:
        return numeric_series, val_min, val_max

    p95 = numeric_series.quantile(0.95)
    if p95 <= val_min:
        p95 = numeric_series.quantile(0.99)
    if p95 <= val_min:
        p95 = val_max

    return numeric_series.clip(upper=p95), val_min, float(p95)


def _extract_scatter_zoom_range(relayout_data) -> tuple[float | None, float | None, float | None, float | None]:
    """Parse scatter plot relayoutData into (x_min, x_max, y_min, y_max) zoom range."""
    if not isinstance(relayout_data, dict):
        return None, None, None, None

    if any(k.endswith("autorange") or k == "autosize" for k in relayout_data):
        return None, None, None, None

    x0, x1, y0, y1 = None, None, None, None

    if "xaxis.range" in relayout_data:
        x_range = relayout_data["xaxis.range"]
        if isinstance(x_range, (list, tuple)) and len(x_range) >= 2:
            x0, x1 = x_range[0], x_range[1]
    else:
        x0 = relayout_data.get("xaxis.range[0]")
        x1 = relayout_data.get("xaxis.range[1]")

    if "yaxis.range" in relayout_data:
        y_range = relayout_data["yaxis.range"]
        if isinstance(y_range, (list, tuple)) and len(y_range) >= 2:
            y0, y1 = y_range[0], y_range[1]
    else:
        y0 = relayout_data.get("yaxis.range[0]")
        y1 = relayout_data.get("yaxis.range[1]")

    try:
        return (
            float(x0) if x0 is not None else None,
            float(x1) if x1 is not None else None,
            float(y0) if y0 is not None else None,
            float(y1) if y1 is not None else None,
        )
    except (TypeError, ValueError):
        return None, None, None, None


COLOR_COLUMN_MAP = {
    "Price": "Price",
    "Required age": "Required age",
    "Estimated owners": "Owner midpoint",
    "Peak CCU": "Peak CCU",
    "Discount": "Discount",
    "DLC count": "DLC count",
    "Income": "Income",
    "User score": "User score",
    "Metacritic score": "Metacritic score",
    "Achievements": "Achievements",
    "Recommendations": "Recommendations",
    "Average playtime forever": "Average playtime forever",
    "Average playtime two weeks": "Average playtime two weeks",
    "Median playtime forever": "Median playtime forever",
    "Median playtime two weeks": "Median playtime two weeks",
}

GENRE_OPTIONS    = _multi_options(GAMES["Genres"].dropna().astype(str).str.split(",").explode())
CATEGORY_OPTIONS = _multi_options(GAMES["Categories"].dropna().astype(str).str.split(",").explode())
TAG_OPTIONS      = _multi_options(GAMES["Tags"].dropna().astype(str).str.split(",").explode())

RELEASE_MIN   = GAMES["Release date"].min()
RELEASE_MAX   = GAMES["Release date"].max()
PRICE_MIN     = float(GAMES["Price"].min())         if not GAMES["Price"].dropna().empty         else 0.0
PRICE_MAX     = float(GAMES["Price"].max())         if not GAMES["Price"].dropna().empty         else 0.0
OWNERS_MIN    = int(GAMES["Owners lower"].min())    if not GAMES["Owners lower"].dropna().empty  else 0
OWNERS_MAX    = int(GAMES["Owners upper"].max())    if not GAMES["Owners upper"].dropna().empty  else 0
USER_SCORE_MAX = 100
METACRITIC_MAX = int(GAMES["Metacritic score"].max()) if not GAMES["Metacritic score"].dropna().empty else 100
POSITIVE_MAX   = 100.0


def _date_str(value: pd.Timestamp | None) -> str:
    return "" if pd.isna(value) else value.strftime("%Y-%m-%d")


def _apply_token_filter(
    frame: pd.DataFrame,
    column: str,
    selected_values: list[str] | None,
) -> pd.DataFrame:
    """Keep rows whose tokenised `column` overlaps any of `selected_values`."""
    selected = {v.strip().lower() for v in (selected_values or []) if v and v.strip()}
    if not selected:
        return frame
    token_col = f"_{column.lower()}_tokens"
    return frame[frame[token_col].map(lambda tokens: bool(selected.intersection(tokens)))]


def _filter_games(
    genre_values, price_min, price_max,
    owners_min, owners_max, category_values,
    release_min, release_max, tag_values,
    user_score_min, user_score_max,
    metacritic_min, metacritic_max,
    positive_min, positive_max,
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
        frame = frame[frame["Release date"].ge(pd.to_datetime(release_min, errors="coerce"))]
    if release_max:
        frame = frame[frame["Release date"].le(pd.to_datetime(release_max, errors="coerce"))]

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

    tag_sel = {v.strip().lower() for v in (tag_values or []) if v and v.strip()}
    if tag_sel:
        frame = frame[frame["_tags_tokens"].map(lambda t: bool(tag_sel.intersection(t)))]

    return frame


def _extract_zoom_range(relayout_data) -> tuple[float | None, float | None]:
    """Parse histogram relayoutData into an (x_min, x_max) zoom range."""
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


def _fmt(value, fmt: str, fallback: str = "") -> str:
    return fallback if pd.isna(value) else format(value, fmt)


def _table_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Format a raw dataframe slice into display-ready strings for the DataTable."""
    t = frame.copy()
    
    if "Positive" in t.columns and "Positive (raw)" not in t.columns:
        t["Positive (raw)"] = t["Positive"].map(lambda v: _fmt(v, ".4f"))
    if "Negative" in t.columns and "Negative (raw)" not in t.columns:
        t["Negative (raw)"] = t["Negative"].map(lambda v: _fmt(v, ".4f"))

    if "Release date" in t.columns:
        t["Release date"] = t["Release date"].dt.strftime("%Y-%m-%d").fillna("")
    if "Price" in t.columns:
        t["Price"] = t["Price"].map(lambda v: _fmt(v, ".2f"))
    if "User score" in t.columns:
        t["User score"] = t["User score"].map(lambda v: _fmt(v, ".0f"))
    if "Metacritic score" in t.columns:
        t["Metacritic score"] = t["Metacritic score"].map(lambda v: _fmt(v, ".0f"))
    if "Positive ratings" in t.columns:
        t["Positive ratings"] = t["Positive ratings"].map(lambda v: _fmt(v, ".1f"))
    if "Negative ratings" in t.columns:
        t["Negative ratings"] = t["Negative ratings"].map(lambda v: _fmt(v, ".1f"))
    if "Peak CCU" in t.columns:
        t["Peak CCU"] = t["Peak CCU"].map(lambda v: "" if pd.isna(v) else f"{int(v):,}")
    
    formatted_cols = {"Release date", "Price", "User score", "Metacritic score", "Positive ratings", "Negative ratings", "Peak CCU", "Positive (raw)", "Negative (raw)"}
    
    for col in t.columns:
        if col in formatted_cols:
            continue
        
        if pd.api.types.is_numeric_dtype(t[col]):
            t[col] = t[col].map(lambda v: "" if pd.isna(v) else (f"{int(v)}" if float(v).is_integer() else f"{v}"))
        else:
            t[col] = t[col].fillna("")
            
    cols_to_return = [c for c in TABLE_AVAILABLE_COLUMNS if c in t.columns]
    return t[cols_to_return]


def _table_style(active_cell, selected_game_name: str | None = None, page_data: list[dict] | None = None) -> list[dict]:
    """
    Build the style_data_conditional list for the DataTable.

    Highlights the row corresponding to the selected game (by name) if present in page_data.
    Otherwise falls back to highlighting the active cell's row.
    """
    styles = [
        {"if": {"row_index": "odd"},  "backgroundColor": "#f8fafc"},
        {"if": {"row_index": "even"}, "backgroundColor": "#ffffff"},
        {"if": {"state": "active"},   "backgroundColor": "inherit", "border": "none", "outline": "none"},
        {"if": {"state": "selected"}, "backgroundColor": "inherit", "border": "none", "outline": "none"},
    ]

    highlighted_row = None
    if selected_game_name and page_data:
        for idx, row_dict in enumerate(page_data):
            if row_dict.get("Name") == selected_game_name:
                highlighted_row = idx
                break

    if highlighted_row is None and isinstance(active_cell, dict) and active_cell.get("row") is not None:
        highlighted_row = active_cell["row"]

    if highlighted_row is not None:
        styles.append({
            "if": {"row_index": highlighted_row},
            "backgroundColor": "#dbeafe",
            "color": "#1e40af",
            "borderBottom": "1px solid #93c5fd",
        })

    if isinstance(active_cell, dict) and active_cell.get("row") is not None:
        row = active_cell["row"]
        col = active_cell.get("column_id")
        if col:
            styles.append({
                "if": {"state": "active", "row_index": row, "column_id": col},
                "backgroundColor": "#dbeafe",
                "color": "#1e40af",
                "border": "none",
                "outline": "none",
            })

    return styles


def _empty_figure(message: str, height: int | None = None) -> go.Figure:
    layout: dict = {
        "template": "plotly_white",
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#ffffff",
        "margin": {"l": 42, "r": 18, "t": 18, "b": 42},
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [{
            "text": message,
            "xref": "paper", "yref": "paper",
            "x": 0.5, "y": 0.5,
            "showarrow": False,
            "font": {"size": 15, "color": TEXT_SECONDARY},
        }],
    }
    if height is not None:
        layout["height"] = height
    return go.Figure().update_layout(**layout)


def _bar_marker(names, selected_name, default_color: str) -> dict:
    """Return a Plotly marker dict that highlights the selected game in orange."""
    colors, line_colors, line_widths = [], [], []
    for name in names:
        if name == selected_name:
            colors.append(COLOR_SELECTED)
            line_colors.append("#000000")
            line_widths.append(1.5)
        else:
            colors.append(default_color)
            line_colors.append("rgba(0,0,0,0)")
            line_widths.append(0)
    return {"color": colors, "line": {"color": line_colors, "width": line_widths}}


def _shared_chart_xaxis(names: list[str]) -> dict:
    """Category x-axis with no labels — shared by all three linked charts."""
    return {
        "type": "category",
        "showticklabels": False,
        "title": "",
        "showgrid": False,
        "zeroline": False,
        "categoryorder": "array",
        "categoryarray": names,
    }


def _shared_chart_yaxis(title: str, tick_vals: list, tick_text: list) -> dict:
    return {
        "title": title,
        "range": [-105, 105],
        "zeroline": True,
        "zerolinecolor": "#475569",
        "zerolinewidth": 1.5,
        "tickvals": tick_vals,
        "ticktext": tick_text,
        "gridcolor": "#e2e8f0",
    }


def _shared_bar_layout_kwargs(uirevision: str) -> dict:
    """Common layout kwargs for the two mirrored bar charts."""
    return {
        "template": "plotly_white",
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#ffffff",
        "height": CHART_HEIGHT,
        "margin": {"l": 50, "r": 10, "t": 10, "b": 20},
        "barmode": "overlay",
        "bargap": 0.6,
        "uirevision": uirevision,
        "hovermode": "closest",
        "showlegend": True,
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
    }


def _build_score_figure(display_df: pd.DataFrame, selected_game: str | None) -> go.Figure:
    """User score (up) vs Metacritic score (down) mirrored bar chart."""
    names = display_df["Name"]
    traces = [
        go.Bar(
            x=names,
            y=display_df["User score"],
            marker=_bar_marker(names, selected_game, COLOR_USER_SCORE),
            name="User Score",
            hovertemplate="Game: %{x}<br>User Score: %{y:.0f}<extra></extra>",
        ),
        go.Bar(
            x=names,
            y=-display_df["Metacritic score"],
            marker=_bar_marker(names, selected_game, COLOR_META_SCORE),
            name="Metacritic Score",
            customdata=display_df["Metacritic score"],
            hovertemplate="Game: %{x}<br>Metacritic Score: %{customdata:.0f}<extra></extra>",
        ),
    ]
    tick_vals  = [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
    tick_text  = ["100", "80", "60", "40", "20", "0", "20", "40", "60", "80", "100"]
    fig = go.Figure(data=traces)
    fig.update_layout(
        **_shared_bar_layout_kwargs("score-plot"),
        xaxis=_shared_chart_xaxis(names.tolist()),
        yaxis=_shared_chart_yaxis("Score", tick_vals, tick_text),
    )
    return fig


def _build_diverge_figure(display_df: pd.DataFrame, selected_game: str | None) -> go.Figure:
    """Score divergence (User − Metacritic) lollipop chart."""
    df = display_df.copy()
    df["Divergence"] = df["User score"] - df["Metacritic score"]
    names = df["Name"].tolist()

    # Per-point marker appearance
    marker_colors, marker_line_colors, marker_line_widths, marker_sizes = [], [], [], []
    for name in names:
        if name == selected_game:
            marker_colors.append(COLOR_SELECTED)
            marker_line_colors.append("#000000")
            marker_line_widths.append(1.5)
            marker_sizes.append(10)
        else:
            marker_colors.append(COLOR_DIVERGE_DEFAULT)
            marker_line_colors.append("rgba(0,0,0,0)")
            marker_line_widths.append(0)
            marker_sizes.append(5)

    shapes = []
    for _, row in df.iterrows():
        if pd.isna(row["Divergence"]):
            continue
        is_selected = row["Name"] == selected_game
        shapes.append({
            "type": "line",
            "x0": row["Name"], "y0": 0,
            "x1": row["Name"], "y1": row["Divergence"],
            "xref": "x", "yref": "y",
            "line": {
                "color": COLOR_SELECTED if is_selected else COLOR_DIVERGE_DEFAULT,
                "width": 2.0 if is_selected else 1.0,
                "dash": "dash",
            },
        })

    tick_vals = [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
    tick_text = ["-100", "-80", "-60", "-40", "-20", "0", "+20", "+40", "+60", "+80", "+100"]

    fig = go.Figure(data=[
        go.Scatter(
            x=names,
            y=df["Divergence"],
            mode="markers",
            marker={
                "color": marker_colors,
                "size": marker_sizes,
                "line": {"color": marker_line_colors, "width": marker_line_widths},
            },
            name="Score Divergence",
            hovertemplate="Game: %{x}<br>Divergence (User − Meta): %{y:+.0f}<extra></extra>",
        )
    ])
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=CHART_HEIGHT,
        margin={"l": 50, "r": 10, "t": 10, "b": 20},
        uirevision="diverge-plot",
        xaxis=_shared_chart_xaxis(names),
        yaxis=_shared_chart_yaxis("Divergence", tick_vals, tick_text),
        shapes=shapes,
        hovermode="closest",
        showlegend=False,
    )
    return fig


def _build_ratings_figure(display_df: pd.DataFrame, selected_game: str | None) -> go.Figure:
    """Positive (up) vs Negative (down) ratings mirrored bar chart."""
    names = display_df["Name"]
    traces = [
        go.Bar(
            x=names,
            y=display_df["Positive ratings"],
            marker=_bar_marker(names, selected_game, COLOR_POSITIVE),
            name="Positive Ratings",
            hovertemplate="Game: %{x}<br>Positive Ratings: %{y:.1f}%<extra></extra>",
        ),
        go.Bar(
            x=names,
            y=-display_df["Negative ratings"],
            marker=_bar_marker(names, selected_game, COLOR_NEGATIVE),
            name="Negative Ratings",
            customdata=display_df["Negative ratings"],
            hovertemplate="Game: %{x}<br>Negative Ratings: %{customdata:.1f}%<extra></extra>",
        ),
    ]
    tick_vals = [-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100]
    tick_text = ["100%", "80%", "60%", "40%", "20%", "0%", "20%", "40%", "60%", "80%", "100%"]
    fig = go.Figure(data=traces)
    fig.update_layout(
        **_shared_bar_layout_kwargs("ratings-plot"),
        xaxis=_shared_chart_xaxis(names.tolist()),
        yaxis=_shared_chart_yaxis("Ratings (%)", tick_vals, tick_text),
    )
    return fig


def _histogram_figure(frame: pd.DataFrame, filter_signature: str) -> go.Figure:
    values = frame["Peak CCU"].dropna()
    if values.empty:
        return _empty_figure("No games match the current filters.")

    values_min = float(values.min())
    values_max = float(values.max())
    full_span   = max(values_max - values_min, 1.0)
    baseline_bin_width = full_span / 40

    zoom_min = frame.attrs.get("zoom_min")
    zoom_max = frame.attrs.get("zoom_max")
    if zoom_min is not None and zoom_max is not None:
        visible_min = max(min(float(zoom_min), float(zoom_max)), values_min)
        visible_max = min(max(float(zoom_min), float(zoom_max)), values_max)
        if visible_max <= visible_min:
            visible_min, visible_max = values_min, values_max
    else:
        visible_min, visible_max = values_min, values_max

    visible_span  = max(visible_max - visible_min, baseline_bin_width)
    dynamic_bins  = max(8, min(120, int(round(visible_span / baseline_bin_width))))
    bin_size      = max(visible_span / dynamic_bins, 1e-9)
    y_ui_revision = f"{filter_signature}|{visible_min:.6f}|{visible_max:.6f}|{dynamic_bins}"

    fig = go.Figure(data=[
        go.Histogram(
            x=values,
            autobinx=False,
            xbins={"start": visible_min, "end": visible_max, "size": bin_size},
            marker={"color": ACCENT_COLOR, "line": {"color": "#1d4ed8", "width": 0.5}},
            hovertemplate="Distribution Of Users Highest Activity: %{x}<br>Count: %{y}<extra></extra>",
        )
    ])
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin={"l": 42, "r": 18, "t": 10, "b": 42},
        xaxis={"title": "Distribution Of Users Highest Activity", "uirevision": filter_signature},
        yaxis={"title": "Games", "autorange": True, "uirevision": y_ui_revision},
        bargap=0.05,
        uirevision=filter_signature,
        dragmode="zoom",
        hovermode="x",
        legend={"orientation": "h"},
    )
    return fig


def _top_n_with_selection(
    df: pd.DataFrame,
    selected_name: str | None,
    n: int,
) -> pd.DataFrame:
    """
    Return the top-n rows of `df`.  If `selected_name` falls outside the top-n,
    swap it in for the last slot so it always appears in the chart.
    """
    if len(df) <= n:
        return df
    top = df.head(n)
    if selected_name is None or selected_name not in df["Name"].values:
        return top
    if selected_name in top["Name"].values:
        return top
    return pd.concat([df.head(n - 1), df[df["Name"] == selected_name].head(1)])


def _build_range_inputs(prefix: str, minimum: float, maximum: float, step: str | float = "any") -> html.Div:
    return html.Div(
        [
            dcc.Input(id=f"{prefix}-min", type="number", value=minimum,
                      min=minimum, max=maximum, step=step, debounce=True, style=FILTER_INPUT_STYLE),
            dcc.Input(id=f"{prefix}-max", type="number", value=maximum,
                      min=minimum, max=maximum, step=step, debounce=True, style=FILTER_INPUT_STYLE),
        ],
        style=RANGE_INPUT_GRID_STYLE,
    )


def _field(label: str, control, help_text: str | None = None) -> html.Div:
    children = [html.Div(label, style=LABEL_STYLE), control]
    if help_text:
        children.append(html.Div(help_text, style=HELP_TEXT_STYLE))
    return html.Div(children, style=FIELD_STYLE)


def _sort_button_pair(label_a: str, id_a: str, label_b: str, id_b: str) -> html.Div:
    """Two small toggle buttons for switching chart sort order."""
    return html.Div(
        [
            html.Button(label_a, id=id_a, n_clicks=0, style=SORT_BUTTON_SMALL_ACTIVE_STYLE),
            html.Button(label_b, id=id_b, n_clicks=0, style=SORT_BUTTON_SMALL_BASE_STYLE),
        ],
        style=SORT_BUTTON_GROUP_STYLE,
    )


def _chart_card(title_text: str, graph_id: str, sort_buttons: html.Div | None = None) -> html.Div:
    """A CARD_STYLE container holding an optional sort-button header and a fixed-height chart."""
    header_children = [html.Div(title_text, style=SECTION_TITLE_STYLE)]
    if sort_buttons:
        header_children.append(sort_buttons)

    return html.Div(
        [
            html.Div(header_children, style=PLOT_CARD_HEADER_STYLE),
            html.Div(
                dcc.Graph(
                    id=graph_id,
                    config={"displayModeBar": False, "responsive": True},
                    style=PLOT_CHART_STYLE,
                ),
                style=PLOT_CHART_WRAPPER_STYLE,
            ),
        ],
        style=PLOT_CARD_STYLE,
    )


layout = html.Div(
    [
        dcc.Store(id="explore-scatter-dist-method", data="euclidean"),
        dcc.Store(id="explore-selected-game", data=None),

        html.Div(
            [
                html.H2(title, style=EXPLORE_PAGE_TITLE_STYLE),
                html.Div(desc, style=EXPLORE_PAGE_SUBTITLE_STYLE),
            ],
            style=EXPLORE_PAGE_HEADER_STYLE,
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
                        _field("Genres",
                               dcc.Dropdown(id="explore-genres", options=GENRE_OPTIONS,
                                            value=[], multi=True, placeholder="Select one or more genres")),
                        _field("Price",
                               _build_range_inputs("explore-price", PRICE_MIN, PRICE_MAX),
                               "Lower and upper price bounds."),
                        _field("Owners",
                               _build_range_inputs("explore-owners", OWNERS_MIN, OWNERS_MAX, step=1),
                               "Matches games whose estimated owner range overlaps the selected interval."),
                        _field("Categories",
                               dcc.Dropdown(id="explore-categories", options=CATEGORY_OPTIONS,
                                            value=[], multi=True, placeholder="Select one or more categories")),
                        _field("Release date",
                               html.Div(
                                   [
                                       dcc.Input(id="explore-release-min", type="number",
                                                 value=_date_str(RELEASE_MIN),
                                                 min=_date_str(RELEASE_MIN), max=_date_str(RELEASE_MAX),
                                                 debounce=True, style=FILTER_INPUT_STYLE),
                                       dcc.Input(id="explore-release-max", type="number",
                                                 value=_date_str(RELEASE_MAX),
                                                 min=_date_str(RELEASE_MIN), max=_date_str(RELEASE_MAX),
                                                 debounce=True, style=FILTER_INPUT_STYLE),
                                   ],
                                   style=RANGE_INPUT_GRID_STYLE,
                               ),
                               "Use the calendar inputs to constrain the release window."),
                        _field("Tags",
                               dcc.Dropdown(id="explore-tags", options=TAG_OPTIONS,
                                            value=[], multi=True, placeholder="Select one or more tags"),
                               "Select one or many tags."),
                        _field("User score",
                               _build_range_inputs("explore-user-score", 0, USER_SCORE_MAX, step=1),
                               "Score is constrained to the 0–100 range."),
                        _field("Metacritic score",
                               _build_range_inputs("explore-metacritic", 0, METACRITIC_MAX, step=1),
                               "Lower and upper Metacritic score bounds."),
                        _field("Positive ratings",
                               _build_range_inputs("explore-positive", 0, POSITIVE_MAX, step=0.1),
                               "Values are shown as percentages from 0 to 100."),
                    ],
                    id="explore-filters-panel",
                    style=PANEL_STYLE,
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("Distribution Of Users Highest Activity", style=SECTION_TITLE_STYLE),
                                    ],
                                    style=PLOT_CARD_HEADER_STYLE,
                                ),
                                dcc.Graph(
                                    id="explore-peak-ccu-histogram",
                                    figure=_empty_figure("Apply filters to see the distribution of users highest activity."),
                                    style={**EXPLORE_GRAPH_STYLE, "marginTop": "1rem"},
                                    config={"displayModeBar": True, "responsive": True, "scrollZoom": True},
                                ),
                            ],
                            style=HISTOGRAM_CARD_STYLE,
                        ),

                        html.Div(
                            [
                                html.Div(
                                    id="explore-table-tour-target",
                                    children=[
                                        html.Div("Matching Games", style=SECTION_TITLE_STYLE),
                                        dcc.Dropdown(
                                            id="explore-table-columns",
                                            options=[{"label": c, "value": c} for c in TABLE_AVAILABLE_COLUMNS],
                                            value=DEFAULT_TABLE_COLUMNS,
                                            multi=True,
                                            clearable=False,
                                            placeholder="Select columns to display",
                                            style=TABLE_COLUMN_PICKER_DROPDOWN_STYLE,
                                        ),
                                    ],
                                    style=TABLE_COLUMN_PICKER_STYLE,
                                ),
                                html.Div(
                                    dash_table.DataTable(
                                        id="explore-matches-table",
                                        columns=[{"name": c, "id": c} for c in DEFAULT_TABLE_COLUMNS],
                                        data=[],
                                        page_action="custom",
                                        page_current=0,
                                        page_size=15,
                                        page_count=1,
                                        sort_action="custom",
                                        sort_mode="single",
                                        sort_by=[],
                                        filter_action="none",
                                        cell_selectable=True,
                                        style_table=TABLE_STYLE,
                                        style_cell=TABLE_CELL_STYLE,
                                        style_header=TABLE_HEADER_STYLE,
                                        style_data_conditional=_table_style(None),
                                        style_as_list_view=True,
                                    ),
                                    style=TABLE_WRAPPER_STYLE,
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

        html.Div(
            [
                html.Div(
                    [
                        html.Div("Game Similarity", style=SECTION_TITLE_STYLE),
                        html.Div(
                            id="explore-distance-buttons",
                            children=[
                                html.Span("Distance Method: ", style={**LABEL_STYLE, "marginRight": "8px"}),
                                html.Button("Euclidean", id="explore-scatter-dist-euclidean", n_clicks=0, style=BUTTON_ACTIVE_STYLE),
                                html.Button("Cosine similarity", id="explore-scatter-dist-cosine", n_clicks=0, style=BUTTON_BASE_STYLE),
                            ],
                            style={"display": "flex", "alignItems": "center", "gap": "6px"}
                        ),
                        html.Div(
                            [
                                html.Span("Color by: ", style={**LABEL_STYLE, "marginRight": "8px"}),
                                dcc.Dropdown(
                                    id="explore-scatter-color-by",
                                    options=[{"label": col, "value": col} for col in [
                                        "Price", "Required age", "Estimated owners", "Peak CCU", "Discount", "DLC count",
                                        "Income", "User score", "Metacritic score", "Achievements", "Recommendations",
                                        "Average playtime forever", "Average playtime two weeks", "Median playtime forever",
                                        "Median playtime two weeks"
                                    ]],
                                    value="Price",
                                    clearable=False,
                                    style={"width": "220px"}
                                )
                            ],
                            style={"display": "flex", "alignItems": "center"}
                        )
                    ],
                    style={**PLOT_CARD_HEADER_STYLE, "gap": "20px", "flexWrap": "wrap"}
                ),
                html.Div(
                    dcc.Graph(
                        id="explore-scatter-plot",
                        figure=_empty_figure("Game Similarity plot is empty for now.", height=600),
                        config={"displayModeBar": True, "responsive": True, "scrollZoom": True},
                        style=PLOT_CHART_STYLE,
                    ),
                    style=PLOT_CHART_WRAPPER_STYLE,
                ),
            ],
            style=SCATTER_CARD_STYLE,
        ),

        html.Div(
            [
                _chart_card(
                    "Score",
                    "explore-score-plot",
                    sort_buttons=_sort_button_pair(
                        "User score",      "explore-score-sort-user",
                        "Metacritic score","explore-score-sort-meta",
                    ),
                ),
                _chart_card("Score diverge", "explore-diverge-plot"),
                _chart_card(
                    "Ratings",
                    "explore-ratings-plot",
                    sort_buttons=_sort_button_pair(
                        "Positive", "explore-ratings-sort-pos",
                        "Negative", "explore-ratings-sort-neg",
                    ),
                ),
            ],
            id="explore-sentiment-graphs",
            style=CHART_PLOTS_GRID_STYLE,
        ),
    ]
)


def register_callbacks(app):
    @app.callback(
        Output("explore-scatter-dist-method", "data"),
        Input("explore-scatter-dist-euclidean", "n_clicks"),
        Input("explore-scatter-dist-cosine", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_scatter_dist_method(euclidean_clicks, cosine_clicks):
        triggered = ctx.triggered_id
        if triggered == "explore-scatter-dist-euclidean":
            return "euclidean"
        if triggered == "explore-scatter-dist-cosine":
            return "cosine"
        return no_update

    @app.callback(
        Output("explore-peak-ccu-histogram",      "figure"),
        Output("explore-matches-table",           "columns"),
        Output("explore-matches-table",           "data"),
        Output("explore-matches-table",           "page_count"),
        Output("explore-matches-table",           "page_current"),
        Output("explore-matches-table",           "style_data_conditional"),
        Output("explore-scatter-plot",            "figure"),
        Output("explore-score-plot",              "figure"),
        Output("explore-diverge-plot",            "figure"),
        Output("explore-ratings-plot",            "figure"),
        Output("explore-score-sort-user",         "style"),
        Output("explore-score-sort-meta",         "style"),
        Output("explore-ratings-sort-pos",        "style"),
        Output("explore-ratings-sort-neg",        "style"),
        Output("explore-selected-game",           "data"),
        Output("explore-scatter-dist-euclidean",  "style"),
        Output("explore-scatter-dist-cosine",     "style"),
        # Filter inputs
        Input("explore-genres",                   "value"),
        Input("explore-price-min",                "value"),
        Input("explore-price-max",                "value"),
        Input("explore-owners-min",               "value"),
        Input("explore-owners-max",               "value"),
        Input("explore-categories",               "value"),
        Input("explore-release-min",              "value"),
        Input("explore-release-max",              "value"),
        Input("explore-tags",                     "value"),
        Input("explore-user-score-min",           "value"),
        Input("explore-user-score-max",           "value"),
        Input("explore-metacritic-min",           "value"),
        Input("explore-metacritic-max",           "value"),
        Input("explore-positive-min",             "value"),
        Input("explore-positive-max",             "value"),
        # Table controls
        Input("explore-table-columns",            "value"),
        Input("explore-matches-table",            "sort_by"),
        Input("explore-peak-ccu-histogram",       "relayoutData"),
        Input("explore-matches-table",            "active_cell"),
        Input("explore-matches-table",            "page_current"),
        Input("explore-matches-table",            "page_size"),
        # Chart sort buttons
        Input("explore-score-sort-user",          "n_clicks"),
        Input("explore-score-sort-meta",          "n_clicks"),
        Input("explore-ratings-sort-pos",         "n_clicks"),
        Input("explore-ratings-sort-neg",         "n_clicks"),
        # Scatter Plot and Selection inputs
        Input("explore-scatter-plot",             "relayoutData"),
        Input("explore-scatter-plot",             "clickData"),
        Input("explore-scatter-dist-method",      "data"),
        Input("explore-scatter-color-by",         "value"),
        Input("explore-selected-game",            "data"),
    )
    def update_explore(
        genre_values, price_min, price_max,
        owners_min, owners_max, category_values,
        release_min, release_max, tag_values,
        user_score_min, user_score_max,
        metacritic_min, metacritic_max,
        positive_min, positive_max,
        selected_table_columns, sort_by, relayout_data,
        active_cell, page_current, page_size,
        score_sort_user_clicks, score_sort_meta_clicks,
        ratings_sort_pos_clicks, ratings_sort_neg_clicks,
        scatter_relayout_data, scatter_click_data,
        dist_method, color_by, stored_selected_game,
    ):
        score_sort_metric = (
            "Metacritic score"
            if (score_sort_meta_clicks or 0) > (score_sort_user_clicks or 0)
            else "User score"
        )
        ratings_sort_metric = (
            "Negative ratings"
            if (ratings_sort_neg_clicks or 0) > (ratings_sort_pos_clicks or 0)
            else "Positive ratings"
        )

        score_user_style    = SORT_BUTTON_SMALL_ACTIVE_STYLE if score_sort_metric   == "User score"       else SORT_BUTTON_SMALL_BASE_STYLE
        score_meta_style    = SORT_BUTTON_SMALL_ACTIVE_STYLE if score_sort_metric   == "Metacritic score"  else SORT_BUTTON_SMALL_BASE_STYLE
        ratings_pos_style   = SORT_BUTTON_SMALL_ACTIVE_STYLE if ratings_sort_metric == "Positive ratings"  else SORT_BUTTON_SMALL_BASE_STYLE
        ratings_neg_style   = SORT_BUTTON_SMALL_ACTIVE_STYLE if ratings_sort_metric == "Negative ratings"  else SORT_BUTTON_SMALL_BASE_STYLE

        euclidean_btn_style = BUTTON_ACTIVE_STYLE if dist_method == "euclidean" else BUTTON_BASE_STYLE
        cosine_btn_style    = BUTTON_ACTIVE_STYLE if dist_method == "cosine" else BUTTON_BASE_STYLE

        filtered = _filter_games(
            genre_values, price_min, price_max,
            owners_min, owners_max, category_values,
            release_min, release_max, tag_values,
            user_score_min, user_score_max,
            metacritic_min, metacritic_max,
            positive_min, positive_max,
        )
        filter_signature = "|".join([
            str(sorted(genre_values or [])),
            str(price_min), str(price_max),
            str(owners_min), str(owners_max),
            str(sorted(category_values or [])),
            str(release_min), str(release_max),
            str(sorted(tag_values or [])),
            str(user_score_min), str(user_score_max),
            str(metacritic_min), str(metacritic_max),
            str(positive_min), str(positive_max),
        ])

        x_col = "mds_x" if dist_method == "euclidean" else "mds_cosine_x"
        y_col = "mds_y" if dist_method == "euclidean" else "mds_cosine_y"

        scatter_x_min, scatter_x_max, scatter_y_min, scatter_y_max = _extract_scatter_zoom_range(scatter_relayout_data)

        df_filtered_by_scatter = filtered
        if scatter_x_min is not None and scatter_x_max is not None:
            df_filtered_by_scatter = df_filtered_by_scatter[df_filtered_by_scatter[x_col].between(scatter_x_min, scatter_x_max)]
        if scatter_y_min is not None and scatter_y_max is not None:
            df_filtered_by_scatter = df_filtered_by_scatter[df_filtered_by_scatter[y_col].between(scatter_y_min, scatter_y_max)]

        x_min, x_max = _extract_zoom_range(relayout_data)
        filtered_with_zoom = df_filtered_by_scatter.copy()
        filtered_with_zoom.attrs["zoom_min"] = x_min
        filtered_with_zoom.attrs["zoom_max"] = x_max
        histogram_figure = _histogram_figure(filtered_with_zoom, filter_signature)

        df_filtered_by_hist = filtered
        if x_min is not None and x_max is not None:
            df_filtered_by_hist = df_filtered_by_hist[df_filtered_by_hist["Peak CCU"].between(x_min, x_max, inclusive="both")]

        table_frame = df_filtered_by_scatter
        if x_min is not None and x_max is not None:
            table_frame = table_frame[table_frame["Peak CCU"].between(x_min, x_max, inclusive="both")]

        if sort_by:
            sort_col = sort_by[0].get("column_id")
            ascending = sort_by[0].get("direction", "desc") == "asc"
            if sort_col in table_frame.columns:
                table_frame = table_frame.sort_values(
                    by=sort_col, ascending=ascending, kind="mergesort", na_position="last"
                )

        page_size    = int(page_size or 15)
        page_current = int(page_current or 0)

        triggered = {t.get("prop_id", "") for t in ctx.triggered}
        pagination_triggered = any(
            p.startswith("explore-matches-table.page_current")
            or p.startswith("explore-matches-table.page_size")
            for p in triggered
        )
        current_page = page_current if pagination_triggered else 0
        page_count   = max(1, math.ceil(len(table_frame) / page_size))
        current_page = max(0, min(current_page, page_count - 1))
        start, end   = current_page * page_size, (current_page + 1) * page_size

        visible_columns = [c for c in (selected_table_columns or DEFAULT_TABLE_COLUMNS) if c in TABLE_AVAILABLE_COLUMNS] or DEFAULT_TABLE_COLUMNS
        table_columns   = [{"name": c, "id": c} for c in visible_columns]
        page_data       = _table_frame(table_frame.iloc[start:end])[visible_columns].to_dict("records")

        selected_game = stored_selected_game

        triggered_ids = [t.get("prop_id", "") for t in ctx.triggered]
        if any(p.startswith("explore-matches-table.active_cell") for p in triggered_ids):
            if active_cell and "row" in active_cell:
                row_idx = start + active_cell["row"]
                if row_idx < len(table_frame):
                    selected_game = table_frame.iloc[row_idx]["Name"]
        elif any(p.startswith("explore-scatter-plot.clickData") for p in triggered_ids):
            if scatter_click_data and "points" in scatter_click_data:
                point = scatter_click_data["points"][0]
                click_custom = point.get("customdata")
                if isinstance(click_custom, (list, tuple)) and len(click_custom) >= 2:
                    if isinstance(click_custom[0], str):
                        selected_game = click_custom[0]

        if selected_game and selected_game not in table_frame["Name"].values:
            selected_game = None

        plot_df = df_filtered_by_hist.dropna(subset=[x_col, y_col, "Name"]).copy()
        
        visible_df = plot_df
        if scatter_x_min is not None and scatter_x_max is not None:
            visible_df = visible_df[visible_df[x_col].between(scatter_x_min, scatter_x_max)]
        if scatter_y_min is not None and scatter_y_max is not None:
            visible_df = visible_df[visible_df[y_col].between(scatter_y_min, scatter_y_max)]

        num_visible = len(visible_df)

        if plot_df.empty:
            scatter_fig = _empty_figure("No games match the current filters.", height=600)
        else:
            color_col = COLOR_COLUMN_MAP.get(color_by, "Price")
            
            if color_by in ["Price", "Income"]:
                value_fmt = "$%{customdata[1]:,.2f}"
            elif color_by in ["Peak CCU", "Estimated owners", "Recommendations", "Achievements", "DLC count", "Discount", "Required age"]:
                value_fmt = "%{customdata[1]:,.0f}"
            elif color_by in ["User score", "Metacritic score", "Average playtime forever", "Average playtime two weeks", "Median playtime forever", "Median playtime two weeks"]:
                value_fmt = "%{customdata[1]:,.1f}"
            else:
                value_fmt = "%{customdata[1]}"

            scatter_fig = go.Figure()

            if num_visible > 2000:
                grid_size = 30
                
                x_min_val, x_max_val = visible_df[x_col].min(), visible_df[x_col].max()
                y_min_val, y_max_val = visible_df[y_col].min(), visible_df[y_col].max()
                
                if pd.isna(x_min_val) or pd.isna(x_max_val) or x_min_val == x_max_val:
                    x_min_val, x_max_val = 0.0, 1.0
                if pd.isna(y_min_val) or pd.isna(y_max_val) or y_min_val == y_max_val:
                    y_min_val, y_max_val = 0.0, 1.0

                x_edges = np.linspace(x_min_val, x_max_val, grid_size + 1)
                y_edges = np.linspace(y_min_val, y_max_val, grid_size + 1)
                x_centers = (x_edges[:-1] + x_edges[1:]) / 2
                y_centers = (y_edges[:-1] + y_edges[1:]) / 2

                bin_df = visible_df.copy()
                bin_df["x_bin"] = np.clip(np.digitize(bin_df[x_col], x_edges) - 1, 0, grid_size - 1)
                bin_df["y_bin"] = np.clip(np.digitize(bin_df[y_col], y_edges) - 1, 0, grid_size - 1)

                grouped = bin_df.groupby(["x_bin", "y_bin"]).agg(
                    count=("Name", "count"),
                    color_val=(color_col, "median"),
                ).reset_index()

                grouped["x_center"] = grouped["x_bin"].map(lambda idx: x_centers[idx])
                grouped["y_center"] = grouped["y_bin"].map(lambda idx: y_centers[idx])

                clipped_color, cmin, cmax = _get_robust_color_values(grouped["color_val"])

                log_counts = np.log1p(grouped["count"])
                min_log, max_log = log_counts.min(), log_counts.max()
                if max_log > min_log:
                    grouped["marker_size"] = 8 + 22 * (log_counts - min_log) / (max_log - min_log)
                else:
                    grouped["marker_size"] = 12

                hovertemplate = f"<b>Aggregated Region</b><br>Games Count: %{{customdata[0]:,}}<br>{color_by} (Median): {value_fmt}<extra></extra>"

                scatter_fig.add_trace(
                    go.Scatter(
                        x=grouped["x_center"],
                        y=grouped["y_center"],
                        mode="markers",
                        marker={
                            "color": clipped_color,
                            "colorscale": "Plasma",
                            "cmin": cmin,
                            "cmax": cmax,
                            "showscale": True,
                            "size": grouped["marker_size"],
                            "line": {"color": "rgba(255,255,255,0.6)", "width": 0.8},
                        },
                        customdata=np.stack([grouped["count"], grouped["color_val"].fillna(0)], axis=-1),
                        hovertemplate=hovertemplate,
                        name="Aggregated",
                    )
                )

                if selected_game:
                    selected_row = visible_df[visible_df["Name"] == selected_game]
                    if not selected_row.empty:
                        single_hover = f"<b>%{{text}} (Selected)</b><br>{color_by}: {value_fmt}<extra></extra>"
                        scatter_fig.add_trace(
                            go.Scatter(
                                x=selected_row[x_col],
                                y=selected_row[y_col],
                                mode="markers",
                                marker={
                                    "color": COLOR_SELECTED,
                                    "size": 12,
                                    "line": {"color": "#000000", "width": 2},
                                },
                                text=selected_row["Name"],
                                customdata=np.stack([selected_row["Name"], selected_row[color_col].fillna(0)], axis=-1),
                                hovertemplate=single_hover,
                                name="Selected",
                                showlegend=False,
                            )
                        )
            else:
                clipped_color, cmin, cmax = _get_robust_color_values(visible_df[color_col])
                hovertemplate = f"<b>%{{text}}</b><br>{color_by}: {value_fmt}<extra></extra>"

                scatter_fig.add_trace(
                    go.Scatter(
                        x=visible_df[x_col],
                        y=visible_df[y_col],
                        mode="markers",
                        marker={
                            "color": clipped_color,
                            "colorscale": "Plasma",
                            "cmin": cmin,
                            "cmax": cmax,
                            "showscale": True,
                            "size": 7,
                            "line": {"color": "rgba(255,255,255,0.4)", "width": 0.5},
                        },
                        text=visible_df["Name"],
                        customdata=np.stack([visible_df["Name"], visible_df[color_col].fillna(0)], axis=-1),
                        hovertemplate=hovertemplate,
                        name="Games",
                    )
                )

                if selected_game:
                    selected_row = visible_df[visible_df["Name"] == selected_game]
                    if not selected_row.empty:
                        scatter_fig.add_trace(
                            go.Scatter(
                                x=selected_row[x_col],
                                y=selected_row[y_col],
                                mode="markers",
                                marker={
                                    "color": COLOR_SELECTED,
                                    "size": 12,
                                    "line": {"color": "#000000", "width": 2},
                                },
                                text=selected_row["Name"],
                                customdata=np.stack([selected_row["Name"], selected_row[color_col].fillna(0)], axis=-1),
                                hovertemplate=hovertemplate,
                                name="Selected",
                                showlegend=False,
                            )
                        )

            scatter_fig.update_layout(
                template="plotly_white",
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                margin={"l": 40, "r": 20, "t": 20, "b": 40},
                height=600,
                xaxis={"title": "MDS X" if dist_method == "euclidean" else "MDS Cosine X", "gridcolor": "#e2e8f0"},
                yaxis={"title": "MDS Y" if dist_method == "euclidean" else "MDS Cosine Y", "gridcolor": "#e2e8f0"},
                uirevision="scatter-plot-revision",
                dragmode="zoom",
                hovermode="closest",
            )

        other_plot_df = table_frame.dropna(subset=["Name"]).copy()

        display_score   = _top_n_with_selection(
            other_plot_df.sort_values(by=score_sort_metric,   ascending=False, na_position="last"),
            selected_game, TOP_N_GAMES,
        ).sort_values(by=score_sort_metric, ascending=False, na_position="last")

        display_ratings = _top_n_with_selection(
            other_plot_df.sort_values(by=ratings_sort_metric, ascending=False, na_position="last"),
            selected_game, TOP_N_GAMES,
        ).sort_values(by=ratings_sort_metric, ascending=False, na_position="last")

        if display_score.empty:
            empty_msg  = "No games match the current filters."
            score_fig  = _empty_figure(empty_msg)
            diverge_fig= _empty_figure(empty_msg)
            ratings_fig= _empty_figure(empty_msg)
        else:
            score_fig   = _build_score_figure(display_score,   selected_game)
            diverge_fig = _build_diverge_figure(display_score, selected_game)
            ratings_fig = _build_ratings_figure(display_ratings, selected_game)

        return (
            histogram_figure,
            table_columns, page_data, page_count, current_page,
            _table_style(active_cell, selected_game, page_data),
            scatter_fig,
            score_fig, diverge_fig, ratings_fig,
            score_user_style, score_meta_style,
            ratings_pos_style, ratings_neg_style,
            selected_game,
            euclidean_btn_style,
            cosine_btn_style,
        )
