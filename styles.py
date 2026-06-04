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
    "display": "flex"
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
    "zIndex": 1000
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
    "margin": "0 16px 4px 16px" 
}

SELECTED_TAB_STYLE = {
    **TAB_STYLE,
    "color": "#1d4ed8",
    "backgroundColor": "#eff6ff", 
    "fontWeight": "500"
}

CARD_STYLE = {
    "backgroundColor": BG_SURFACE,
    "borderRadius": "12px",
    "padding": "1.5rem 2rem",
    "border": f"1px solid {BORDER_COLOR}",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"
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

SECTION_STYLE = {
    **CARD_STYLE,
    "padding": "1.75rem",
    "display": "flex",
    "flexDirection": "column",
    "gap": "1.25rem",
}

BUTTON_ROW_STYLE = {
    "display": "flex",
    "gap": "0.75rem",
    "flexWrap": "wrap",
}

METRIC_GRID_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
    "gap": "1rem",
}

METRIC_CARD_STYLE = {
    **CARD_STYLE,
    "padding": "1.25rem 1.4rem",
    "minHeight": "112px",
}

CARD_VALUE_STYLE = {"fontSize": "1.75rem", "fontWeight": "700", "color": TEXT_PRIMARY}
CARD_CHANGE_STYLE = {"fontSize": "0.82rem", "fontWeight": "600", "marginTop": "0.55rem"}
CARD_COMPARISON_STYLE = {"fontSize": "0.78rem", "fontWeight": "500", "marginTop": "0.25rem", "color": TEXT_SECONDARY}

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

PIE_CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "borderRadius": "12px",
    "padding": "0.75rem 0.8rem 0.35rem",
    "border": "1px solid #e2e8f0",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
    "minHeight": "320px",
}

PIE_GRAPH_STYLE = {"height": "240px"}


RANGE_ROW_STYLE = {
    "display": "flex",
    "flexWrap": "wrap",
    "gap": "0.75rem",
}

CHART_CARD_STYLE = {
    "backgroundColor": "#ffffff",
    "borderRadius": "12px",
    "padding": "1rem 1rem 0.5rem",
    "border": "1px solid #e2e8f0",
    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
    "minHeight": "460px",
}

CHART_STYLE = {"height": "380px"}

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

FIELD_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "0.45rem",
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

INPUT_STYLE = {
    "width": "100%",
    "padding": "0.7rem 0.8rem",
    "borderRadius": "10px",
    "border": "1px solid #dbe4f0",
    "backgroundColor": "#ffffff",
    "color": TEXT_PRIMARY,
    "fontSize": "0.92rem",
}

SECTION_TITLE_STYLE = {
    "fontSize": "1.05rem",
    "fontWeight": "700",
    "color": TEXT_PRIMARY,
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
    "flex": "1 1 0",
    "overflow": "hidden",
    "boxSizing": "border-box",
}

TABLE_STYLE = {
    "overflowX": "auto",
    "overflowY": "auto",
    "height": "100%",
    "minHeight": 0,
}

TABLE_CELL_STYLE = {
    "fontSize": "0.86rem",
    "padding": "0.65rem 0.6rem",
    "whiteSpace": "normal",
    "height": "auto",
    "border": "none",
    "textAlign": "left",
}

TABLE_HEADER_STYLE = {
    "backgroundColor": "#f8fbff",
    "fontWeight": "700",
    "color": TEXT_PRIMARY,
    "borderBottom": "1px solid #dbe4f0",
}


EXPLORE_GRAPH_STYLE = {
    "height": "100%",
    "minHeight": 0,
    "flex": "1 1 0",
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

TABLE_BLOCK_STYLE = {
    "display": "flex",
    "flexDirection": "column",
    "gap": "0.65rem",
    "minHeight": 0,
    "flex": "1 1 0",
}

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

FILTER_INPUT_STYLE = {
    **INPUT_STYLE,
    "height": "44px",
    "padding": "0 0.85rem",
    "boxSizing": "border-box",
    "lineHeight": "44px",
}
