from dash import Dash, Input, Output, dcc, html

from styles import (
    APP_STYLE,
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
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.title = "Game Market Analyzer"
overview.register_callbacks(app)

app.layout = html.Div([
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
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '2.5rem', 'padding': '0 24px'}),
        
        dcc.Tabs(
            id='sidebar-tabs', 
            value='tab-summary', 
            vertical=True,
            parent_style={"width": "100%", "display": "flex", "flexDirection": "column"},
            style={'border': 'none', 'borderBottom': 'none'},
            colors={"border": "transparent", "primary": "transparent", "background": "transparent"},
            children=[
                dcc.Tab(label=html.Div([html.I(className="fa-solid fa-layer-group", style={"width": "20px"}), html.Span("Overview")]), value='tab-summary', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                dcc.Tab(label=html.Div([html.I(className="fa-solid fa-compass", style={"width": "20px"}), html.Span("Explore")]), value='tab-explore', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                dcc.Tab(label=html.Div([html.I(className="fa-solid fa-lightbulb", style={"width": "20px"}), html.Span("Insights")]), value='tab-insights', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                dcc.Tab(label=html.Div([html.I(className="fa-solid fa-circle-info", style={"width": "20px"}), html.Span("About")]), value='tab-about', style=TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
            ]
        )
    ], style=SIDEBAR_STYLE),

    html.Div(id='tab-content', style=CONTENT_STYLE)
], style=APP_STYLE)

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

if __name__ == '__main__':
    app.run(debug=True)
