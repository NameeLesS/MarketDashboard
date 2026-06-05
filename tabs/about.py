from dash import dcc, html

from styles import *

title = 'About'
desc = 'Learn more about the Game Market Analyzer.'

def _build_section(icon, title_text, description_text, items=None):
    children = [
        html.Div([
            html.H3(title_text, style={"fontSize": "1.2rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
        html.Div(description_text, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "lineHeight": "1.6", "marginBottom": "12px" if items else "0"})
    ]
    
    if items:
        ul_items = [html.Li(item, style={"marginBottom": "10px", "color": TEXT_SECONDARY, "fontSize": "0.95rem", "lineHeight": "1.5"}) for item in items]
        children.append(html.Ul(ul_items, style={"margin": "0", "paddingLeft": "24px", "listStyleType": "disc"}))
        
    return html.Div(children, style={"marginBottom": "40px"})

layout = html.Div([
    html.Div([
        html.H2(title, style={"fontSize": "1.8rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY}),
        html.Div(desc, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "marginTop": "4px"})
    ], style={"marginBottom": "2rem"}),
    
    html.Div([
        _build_section(
            "fa-solid fa-chart-line",
            "Project Overview",
            "Game Market Analyzer is a powerful analytics dashboard designed to help you analyze the game market and gain crucial insights. Whether you're an indie developer or an established studio, this tool provides the data-driven perspectives you need to create better games and make informed business decisions in the future."
        ),
        
        _build_section(
            "fa-solid fa-map",
            "Dashboard Sections",
            "The dashboard is divided into three main analytical sections, each serving a distinct purpose:",
            [
                html.Span([html.Strong("Overview: ", style={"color": TEXT_PRIMARY}), "Gives you a high-level view of the market. Explore general information such as market size, trends, and seasonality. Use interactive filters to aggregate data by different periods and limit data ranges."]),
                html.Span([html.Strong("Explore: ", style={"color": TEXT_PRIMARY}), "Dive deep into specific market segments. Discover similarities and characteristics of games that interest you using interactive filters, data tables, and advanced Multidimensional Scaling (MDS) scatter plots."]),
                html.Span([html.Strong("Insights: ", style={"color": TEXT_PRIMARY}), "Derive actionable business intelligence. Analyze what features maximize revenue, compare genre leaders against average competitors using radar charts, and determine the optimal pricing strategy using our tier-based distribution plots."])
            ]
        ),
        
        _build_section(
            "fa-solid fa-server",
            "Technical Information & Methodology",
            "This dashboard leverages advanced data processing techniques and machine learning models to provide deep market insights.",
            [
                html.Span([html.Strong("Dataset Time Range: ", style={"color": TEXT_PRIMARY}), "The historical data spans over two decades, covering games released from June 1997 to January 2026."]),
                html.Span([
                    html.Strong("Game Similarity Graph: ", style={"color": TEXT_PRIMARY}), "The Game Similarity scatter plot in the Explore section maps complex relationships between thousands of games. First, game attributes and descriptions were unified into text and processed through the Qwen3-Embedding-0.6B model to generate high-dimensional embeddings. These embeddings were then projected into a 2D space using a custom Neural Network designed to mimic the Multidimensional Scaling (MDS) algorithm, ensuring that both local and global similarities are accurately visualized."
                ])
            ]
        ),
        
        html.Div([
            html.Div([
                html.H3("Authors", style={"fontSize": "1.2rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY})
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "16px"}),
            
            html.Div([
                html.Div([
                    html.Div("- Marcin Dzióbkowski", style={"fontWeight": "500", "color": TEXT_PRIMARY, "fontSize": "1rem"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "16px"}),
                
                html.Div([
                    html.Div("- Tomasz Białecki", style={"fontWeight": "500", "color": TEXT_PRIMARY, "fontSize": "1rem"})
                ], style={"display": "flex", "alignItems": "center"})
            ], style={"marginBottom": "32px"}),
            
            html.Div(style={"height": "1px", "backgroundColor": BORDER_COLOR, "marginBottom": "24px"}),
            
            html.Div([
                html.Div([
                    html.Div("Repository", style={"fontSize": "0.8rem", "color": TEXT_SECONDARY, "marginBottom": "2px"}),
                    html.A("tomciolowsky/DataVisualization2", href="https://github.com/tomciolowsky/DataVisualization2", target="_blank", style={"color": ACCENT_COLOR, "textDecoration": "none", "fontWeight": "500", "fontSize": "1rem"})
                ], style={"display": "flex", "flexDirection": "column"})
            ], style={"display": "flex", "alignItems": "center"}),
            
        ], style={"marginBottom": "12px"})
        
    ], style={**CARD_STYLE, "width": "100%"})
])