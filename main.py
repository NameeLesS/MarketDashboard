from dash import Dash, Input, Output, State, ctx, dcc, html

from styles import (
    APP_STYLE,
    BORDER_COLOR,
    CONTENT_STYLE,
    SELECTED_TAB_STYLE,
    SIDEBAR_STYLE,
    TAB_STYLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from tabs import about, explore, insights, overview

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    "https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.css"
]

external_scripts = [
    "https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.js.iife.js"
]

app = Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts, suppress_callback_exceptions=True)
app.title = "Game Market Analyzer"
overview.register_callbacks(app)
explore.register_callbacks(app)
insights.register_callbacks(app)

app.layout = html.Div([
    dcc.Store(id="sidebar-state-store", data={"visible": True}),
    
    html.Button(
        html.I(className="fa-solid fa-bars"),
        id="sidebar-show-btn",
        n_clicks=0,
        style={
            "position": "fixed",
            "left": "16px",
            "top": "32px",
            "zIndex": 1100,
            "display": "none",
            "alignItems": "center",
            "justifyContent": "center",
            "width": "40px",
            "height": "40px",
            "borderRadius": "8px",
            "backgroundColor": "#ffffff",
            "border": f"1px solid {BORDER_COLOR}",
            "cursor": "pointer",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "color": TEXT_PRIMARY,
            "transition": "all 0.2s"
        }
    ),

    html.Div([
        html.Div([
            html.Div([
                html.Img(
                    src='/assets/pp_znak_konturowy_RGB.png', 
                    style={'width': '32px', 'height': 'auto', 'marginRight': '12px'}
                ),
                html.Div([
                    html.Div("Game Market", style={'fontWeight': '600', 'fontSize': '1.1rem', 'color': TEXT_PRIMARY}),
                    html.Div("Analyzer", style={'fontWeight': '400', 'fontSize': '0.85rem', 'color': TEXT_SECONDARY})
                ], style={'lineHeight': '1.2'})
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Button(
                html.I(className="fa-solid fa-chevron-left"),
                id="sidebar-hide-btn",
                n_clicks=0,
                style={
                    "border": "none",
                    "backgroundColor": "transparent",
                    "color": TEXT_SECONDARY,
                    "cursor": "pointer",
                    "fontSize": "1.1rem",
                    "padding": "8px",
                    "borderRadius": "6px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "transition": "all 0.2s"
                }
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'marginBottom': '2.5rem', 'padding': '0 16px 0 24px'}),
        
        dcc.Tabs(
            id='sidebar-tabs', 
            value='tab-summary', 
            vertical=True,
            parent_style={"width": "100%", "display": "flex", "flexDirection": "column"},
            style={'border': 'none', 'borderBottom': 'none'},
            colors={"border": "transparent", "primary": "transparent", "background": "transparent"},
            children=[
                dcc.Tab(id='sidebar-overview-tab', label=html.Div([html.I(className="fa-solid fa-layer-group", style={"width": "20px"}), html.Span("Overview")]), value='tab-summary', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                dcc.Tab(id='sidebar-explore-tab', label=html.Div([html.I(className="fa-solid fa-compass", style={"width": "20px"}), html.Span("Explore")]), value='tab-explore', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                dcc.Tab(id='sidebar-insights-tab', label=html.Div([html.I(className="fa-solid fa-lightbulb", style={"width": "20px"}), html.Span("Insights")]), value='tab-insights', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                dcc.Tab(id='sidebar-about-tab', label=html.Div([html.I(className="fa-solid fa-circle-info", style={"width": "20px"}), html.Span("About")]), value='tab-about', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
            ]
        ),
        html.Div([
            html.Button([
                html.I(className="fa-solid fa-route", style={"marginRight": "8px"}),
                "Start Tour"
            ], id="start-tour-btn", n_clicks=0, style={
                "marginTop": "auto", "width": "100%", "padding": "12px", "borderRadius": "8px",
                "backgroundColor": "#3b82f6", "color": "white", "border": "none", "cursor": "pointer",
                "fontWeight": "600", "fontSize": "0.95rem"
            })
        ], style={"marginTop": "auto", "padding": "0 24px"}),
        html.Div(id="tour-dummy-output", style={"display": "none"})
    ], id="sidebar-container", style=SIDEBAR_STYLE),

    html.Div(id='tab-content', style=CONTENT_STYLE)
], style=APP_STYLE)

app.clientside_callback(
    """
    function(n_clicks) {
        if(n_clicks > 0 && window.startTour) {
            window.startTour();
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("tour-dummy-output", "children"),
    Input("start-tour-btn", "n_clicks")
)

@app.callback(
    Output('tab-content', 'children'),
    Input('sidebar-tabs', 'value')
)
def render_content(tab):
    if tab == 'tab-summary':
        return overview.layout
    elif tab == 'tab-explore':
        return explore.layout
    elif tab == 'tab-insights':
        return insights.layout
    elif tab == 'tab-about':
        return about.layout

@app.callback(
    Output("sidebar-container", "style"),
    Output("tab-content", "style"),
    Output("sidebar-show-btn", "style"),
    Output("sidebar-state-store", "data"),
    Input("sidebar-hide-btn", "n_clicks"),
    Input("sidebar-show-btn", "n_clicks"),
    Input("start-tour-btn", "n_clicks"),
    State("sidebar-state-store", "data"),
    prevent_initial_call=False
)
def toggle_sidebar(hide_clicks, show_clicks, tour_clicks, state_data):
    if state_data is None:
        state_data = {"visible": True}
        
    triggered_id = ctx.triggered_id
    if triggered_id == "sidebar-hide-btn":
        state_data["visible"] = False
    elif triggered_id == "sidebar-show-btn":
        state_data["visible"] = True
    elif triggered_id == "start-tour-btn" and tour_clicks > 0:
        state_data["visible"] = True
        
    if state_data["visible"]:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
        show_btn_style = {
            "position": "fixed",
            "left": "16px",
            "top": "32px",
            "zIndex": 1100,
            "display": "none",
            "alignItems": "center",
            "justifyContent": "center",
            "width": "40px",
            "height": "40px",
            "borderRadius": "8px",
            "backgroundColor": "#ffffff",
            "border": f"1px solid {BORDER_COLOR}",
            "cursor": "pointer",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "color": TEXT_PRIMARY,
            "transition": "all 0.2s"
        }
    else:
        sidebar_style = {**SIDEBAR_STYLE, "display": "none"}
        content_style = {**CONTENT_STYLE, "marginLeft": "0px"}
        show_btn_style = {
            "position": "fixed",
            "left": "16px",
            "top": "32px",
            "zIndex": 1100,
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "width": "40px",
            "height": "40px",
            "borderRadius": "8px",
            "backgroundColor": "#ffffff",
            "border": f"1px solid {BORDER_COLOR}",
            "cursor": "pointer",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "color": TEXT_PRIMARY,
            "transition": "all 0.2s"
        }
        
    return sidebar_style, content_style, show_btn_style, state_data

if __name__ == '__main__':
    app.run(debug=True)
