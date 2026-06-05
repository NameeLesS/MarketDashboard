BG_BASE = "#f8fafc"
BG_SURFACE = "#ffffff"
BORDER_COLOR = "#e2e8f0"
TEXT_PRIMARY = "#0f172a"
TEXT_SECONDARY = "#64748b"
ACCENT_COLOR = "#3b82f6"


APP_STYLE = {
    "backgroundColor": BG_BASE,
    "minHeight": "100vh",
    "fontFamily": "'Inter', sans-serif",
    "color": TEXT_PRIMARY,
    "display": "flex",
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "240px",
    "backgroundColor": BG_SURFACE,
    "borderRight": f"1px solid {BORDER_COLOR}",
    "display": "flex",
    "flexDirection": "column",
    "padding": "2rem 0",
    "zIndex": 1000,
}

CONTENT_STYLE = {
    "marginLeft": "240px",
    "flex": "1",
    "padding": "3rem 4rem",
    "minHeight": "100vh",
}


TAB_STYLE = {
    "padding": "10px 16px",
    "color": TEXT_SECONDARY,
    "backgroundColor": "transparent",
    "border": "none",
    "marginBottom": "4px",
    "cursor": "pointer",
    "fontSize": "14px",
    "fontWeight": "500",
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "flex-start",
    "gap": "12px",
    "transition": "all 0.2s ease",
    "borderRadius": "8px",
    "margin": "0 16px 4px 16px",
}

SELECTED_TAB_STYLE = {
    **TAB_STYLE,
    "color": "#1d4ed8",
    "backgroundColor": "#eff6ff",
    "fontWeight": "500",
}


CARD_STYLE = {
    "backgroundColor": BG_SURFACE,
    "borderRadius": "12px",
    "padding": "1.5rem 2rem",
    "border": f"1px solid {BORDER_COLOR}",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
}

SECTION_STYLE = {
    **CARD_STYLE,
    "padding": "1.75rem",
    "display": "flex",
    "flexDirection": "column",
    "gap": "1.25rem",
}

METRIC_CARD_STYLE = {
    **CARD_STYLE,
    "padding": "1.25rem 1.4rem",
    "minHeight": "112px",
}

CHART_CARD_STYLE = {
    "backgroundColor": BG_SURFACE,
    "borderRadius": "12px",
    "padding": "1rem 1rem 0.5rem",
    "border": f"1px solid {BORDER_COLOR}",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
    "minHeight": "460px",
}

PIE_CARD_STYLE = {
    "backgroundColor": BG_SURFACE,
    "borderRadius": "12px",
    "padding": "0.6rem 0.6rem 0.5rem",
    "border": f"1px solid {BORDER_COLOR}",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
    # Fixed total height so all four cards are identical
    "height": "310px",
    "display": "flex",
    "flexDirection": "column",
}

BUTTON_BASE_STYLE = {
    "padding": "0.7rem 1rem",
    "borderRadius": "999px",
    "border": f"1px solid {BORDER_COLOR}",
    "backgroundColor": BG_SURFACE,
    "color": TEXT_SECONDARY,
    "fontSize": "0.9rem",
    "fontWeight": "600",
    "cursor": "pointer",
    "transition": "all 0.2s ease",
}

BUTTON_ACTIVE_STYLE = {
    **BUTTON_BASE_STYLE,
    "backgroundColor": TEXT_PRIMARY,
    "border": f"1px solid {TEXT_PRIMARY}",
    "color": BG_SURFACE,
}

SORT_BUTTON_SMALL_BASE_STYLE = {
    **BUTTON_BASE_STYLE,
    "fontSize": "0.78rem",
    "padding": "0.3rem 0.7rem",
}

SORT_BUTTON_SMALL_ACTIVE_STYLE = {
    **BUTTON_ACTIVE_STYLE,
    "fontSize": "0.78rem",
    "padding": "0.3rem 0.7rem",
}

BUTTON_ROW_STYLE = {
    "display": "flex",
    "gap": "0.75rem",
    "flexWrap": "wrap",
}


SECTION_TITLE_STYLE = {
    "fontSize": "1.05rem",
    "fontWeight": "700",
    "color": TEXT_PRIMARY,
}

LABEL_STYLE = {
    "fontSize": "0.9rem",
    "fontWeight": "600",
    "color": TEXT_PRIMARY,
}

HELP_TEXT_STYLE = {
    "fontSize": "0.78rem",
    "color": TEXT_SECONDARY,
    "lineHeight": "1.35",
}

HINT_PILL_STYLE = {
    "display": "inline-flex",
    "alignItems": "center",
    "gap": "0.4rem",
    "padding": "0.45rem 0.7rem",
    "borderRadius": "999px",
    "backgroundColor": "#eff6ff",
    "color": "#1d4ed8",
    "fontSize": "0.8rem",
    "fontWeight": "600",
}

CARD_VALUE_STYLE = {
    "fontSize": "1.75rem",
    "fontWeight": "700",
    "color": TEXT_PRIMARY,
}

CARD_CHANGE_STYLE = {
    "fontSize": "0.82rem",
    "fontWeight": "600",
    "marginTop": "0.55rem",
}

CARD_COMPARISON_STYLE = {
    "fontSize": "0.78rem",
    "fontWeight": "500",
    "marginTop": "0.25rem",
    "color": TEXT_SECONDARY,
}

INPUT_STYLE = {
    "width": "100%",
    "padding": "0.7rem 0.8rem",
    "borderRadius": "10px",
    "border": "1px solid #dbe4f0",
    "backgroundColor": BG_SURFACE,
    "color": TEXT_PRIMARY,
    "fontSize": "0.92rem",
}

FILTER_INPUT_STYLE = {
    **INPUT_STYLE,
    "height": "44px",
    "padding": "0 0.85rem",
    "boxSizing": "border-box",
    "lineHeight": "44px",
}

METRIC_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
    "gap": "1rem",
}

CHART_ROW_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))",
    "gap": "1rem",
}

PIE_ROW_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(4, minmax(0, 1fr))",
    "gap": "0.75rem",
}

RANGE_INPUT_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(2, minmax(0, 1fr))",
    "gap": "0.65rem",
}


EXPLORE_PAGE_HEADER_STYLE = {"marginBottom": "0.75rem"}

EXPLORE_PAGE_TITLE_STYLE = {
    "fontSize": "1.8rem",
    "fontWeight": "600",
    "margin": "0",
    "color": TEXT_PRIMARY,
}

EXPLORE_PAGE_SUBTITLE_STYLE = {
    "color": TEXT_SECONDARY,
    "fontSize": "0.95rem",
    "marginTop": "4px",
}

EXPLORE_BODY_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "minmax(320px, 360px) minmax(0, 1fr)",
    "gap": "1.25rem",
    "alignItems": "stretch",
    "minHeight": 0,
    "flex": "1 1 0",
    "width": "100%",
    "boxSizing": "border-box",
}

PANEL_STYLE = {
    **CARD_STYLE,
    "padding": "1.5rem",
    "display": "flex",
    "flexDirection": "column",
    "gap": "1.1rem",
    "width": "100%",
    "boxSizing": "border-box",
    "position": "sticky",
    "top": "1.5rem",
    "alignSelf": "flex-start",
    "maxHeight": "calc(100vh - 9rem)",
    "overflowY": "auto",
}

RIGHT_COLUMN_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "1rem",
    "minWidth": 0,
    "flex": "1 1 0",
    "minHeight": 0,
    "width": "100%",
    "boxSizing": "border-box",
}

FIELD_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "0.45rem",
}



EXPLORE_GRAPH_STYLE = {
    "height": "100%",
    "minHeight": 0,
    "flex": "1 1 0",
}

HISTOGRAM_CARD_STYLE = {
    **CHART_CARD_STYLE,
    "display": "flex",
    "flexDirection": "column",
    "minHeight": 0,
    "flex": "1 1 0",
    "overflow": "hidden",
    "boxSizing": "border-box",
}


TABLE_CARD_STYLE = {
    **CHART_CARD_STYLE,
    "display": "flex",
    "flexDirection": "column",
    "minHeight": 0,
    "minWidth": 0,
    "flex": "1 1 0",
    "overflow": "visible",
    "boxSizing": "border-box",
    "padding": "1.5rem 1.75rem",
}

TABLE_BLOCK_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "0.65rem",
    "minHeight": 0,
    "flex": "1 1 0",
}

TABLE_COLUMN_PICKER_STYLE = {
    "display": "flex",
    "alignItems": "flex-start",
    "justifyContent": "space-between",
    "gap": "1rem",
    "flexWrap": "wrap",
}

TABLE_COLUMN_PICKER_DROPDOWN_STYLE = {
    "minWidth": "320px",
    "maxWidth": "520px",
}

TABLE_WRAPPER_STYLE = {
    "flex": "1 1 0",
    "minHeight": 0,
    "overflowY": "auto",
}

TABLE_STYLE = {
    "overflowX": "auto",
    "borderCollapse": "separate",
    "borderSpacing": 0,
}

TABLE_CELL_STYLE = {
    "fontSize": "0.84rem",
    "padding": "0.75rem 1rem",
    "whiteSpace": "normal",
    "height": "auto",
    "border": "none",
    "borderBottom": f"1px solid {BORDER_COLOR}",
    "textAlign": "left",
    "color": TEXT_PRIMARY,
    "fontFamily": "'Inter', sans-serif",
    "backgroundColor": "transparent",
}

TABLE_HEADER_STYLE = {
    "backgroundColor": BG_BASE,
    "fontWeight": "600",
    "fontSize": "0.78rem",
    "textTransform": "uppercase",
    "letterSpacing": "0.05em",
    "color": TEXT_SECONDARY,
    "borderBottom": f"2px solid {BORDER_COLOR}",
    "border": "none",
    "padding": "0.7rem 1rem",
}

SCATTER_CARD_STYLE = {
    **CHART_CARD_STYLE,
    "width": "100%",
    "marginTop": "1.5rem",
    "boxSizing": "border-box",
    "minHeight": 0,
}

CHART_PLOTS_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(3, minmax(0, 1fr))",
    "gap": "1rem",
    "width": "100%",
    "marginTop": "1.5rem",
    "boxSizing": "border-box",
}

PLOT_CARD_STYLE = {
    **CARD_STYLE,
    "boxSizing": "border-box",
    "overflow": "hidden",
}

PLOT_CARD_HEADER_STYLE = {
    "display": "flex",
    "justifyContent": "space-between",
    "alignItems": "center",
}

SORT_BUTTON_GROUP_STYLE = {
    "display": "flex",
    "gap": "0.4rem",
}

PLOT_CHART_WRAPPER_STYLE = {
    "height": "400px",
    "overflow": "hidden",
    "marginTop": "1rem",
}

PLOT_CHART_STYLE = {
    "height": "100%",
    "width": "100%",
}

PIE_GRAPH_STYLE = {"height": "210px", "flex": "1 1 0", "minHeight": 0}
CHART_STYLE = {"height": "380px"}
RANGE_ROW_STYLE = {"display": "flex", "flexWrap": "wrap", "gap": "0.75rem"}

GENRE_PALETTE = [
    "#3b82f6",
    "#06b6d4",
    "#10b981",
    "#f59e0b",
    "#ef4444",
    "#8b5cf6",
    "#14b8a6",
    "#f97316",
    "#84cc16",
    "#ec4899",
]

TABLE_AVAILABLE_COLUMNS = [
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
    "Negative ratings",
    "Positive (raw)",
    "Negative (raw)",
]

DEFAULT_TABLE_COLUMNS = [
    "Name",
    "Release date",
    "Estimated owners",
    "Peak CCU",
    "Price",
    "User score",
    "Metacritic score",
    "Positive ratings",
]
