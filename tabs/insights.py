# from dash import html
# from styles import *

# title = 'Market Insights'
# desc = 'Actionable takeaways from the data.'
# layout = html.Div([
#     html.Div([
#         html.H2(title, style={"fontSize": "1.8rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY}),
#         html.Div(desc, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "marginTop": "4px"})
#     ], style={"marginBottom": "2rem"}),
    
#     html.Div(style={**CARD_STYLE, "minHeight": "400px", "display": "flex", "alignItems": "center", "justifyContent": "center"}, children=[
#         html.Div("Module currently under construction", style={"color": TEXT_SECONDARY, "fontSize": "0.95rem"})
#     ])
# ])

import json
import math

# Trigger dash auto-reloader
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html
from plotly.subplots import make_subplots

# Import layout constants directly from your centralized style sheet
from styles import (
    BG_SURFACE,
    CARD_STYLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "games.csv"
JSON_PATH = Path(__file__).resolve().parents[1] / "data" / "insights_precomputed.json"

title = "Market Insights"
desc = "Actionable takeaways from the data."

BLUE = '#636EFA'
RED = '#EF553B'
GREEN = '#00CC96'
PURPLE = '#AB63FA'

def _load_insights_data() -> pd.DataFrame:
    usecols = [
        "AppID", "Name", "Price", "Genres", "Tags", "Positive", "Peak CCU",
        "Estimated owners", "Average playtime forever", "Achievements", "DLC count",
        "Owner midpoint", "Estimated_Income", "Positive_Pct"
    ]
    frame = pd.read_csv(DATA_PATH, usecols=usecols, low_memory=False)
    frame['Tag_List'] = frame['Tags'].fillna('').astype(str).str.split(',')
    return frame

GAMES = _load_insights_data()

try:
    with open(JSON_PATH, 'r') as f:
        PRECOMPUTED = json.load(f)
except FileNotFoundError:
    PRECOMPUTED = {}

if PRECOMPUTED:
    GENRE_OPTIONS = sorted(list(PRECOMPUTED.keys()))
else:
    GENRE_OPTIONS = sorted(list(set([
        g.strip() for sublist in GAMES['Genres'].dropna().astype(str).str.split(',') for g in sublist if g.strip()
    ])))


def _build_treemap(genre_data, selected_genre):
    treemap = genre_data.get('treemap', {})
    if not treemap or not treemap.get('Tag_List'):
        return go.Figure()

    df = pd.DataFrame(treemap)
    
    # 1. THE MATH: Create a tiny offset below your real data
    min_income = df['Estimated_Income_Median'].min()
    max_income = df['Estimated_Income_Median'].max()
    
    # Create a 1% gap below your lowest actual income
    offset = (max_income - min_income) * 0.01 if max_income > min_income else 100
    root_value = min_income - offset
    
    fig = px.treemap(
        df,
        path=['Tag_List'],
        values='Game_Count',
        color='Estimated_Income_Median',
        
        # 2. THE SCALE: 0.0 is White. 0.01 starts your Gray and sweeps up to Blue.
        color_continuous_scale=[
            [0.0, 'white'], 
            [0.01, '#E5E7EB'], 
            [1.0, BLUE] # Assuming BLUE is defined globally in your script
        ],
        # Lock the colorbar engine to our new extended range
        range_color=[root_value, max_income],
        labels={'Estimated_Income_Median': 'Median of<br>Estimated Income'},
    )
    
    # 3. THE HIJACK: Push the hidden root node down into the white pocket
    ids = list(fig.data[0].ids)
    if '(?)' in ids:
        root_idx = ids.index('(?)')
        colors = list(fig.data[0].marker.colors)
        colors[root_idx] = root_value
        fig.data[0].marker.colors = colors

    fig.update_traces(
        hovertemplate="<b>Tag: %{label}</b><br>Total Games: %{value:,}<br>Median Income: $%{color:,.0f}<extra></extra>",
        pathbar=dict(visible=False),
        tiling=dict(pad=0), 
        marker=dict(line=dict(color="white", width=3)),
        textfont=dict(family="Inter, sans-serif", size=14),
        hoverlabel=dict(bgcolor="rgba(17, 24, 39, 0.95)", font_size=13, font_family="Inter, sans-serif", font_color="white")
    )
    
    fig.update_layout(
        title=dict(text=f"<b>Market Opportunity Analysis: Tag Frequency & Median Earnings ({selected_genre})</b>", x=0.02, xanchor="left"),
        margin=dict(l=0, r=0, t=52, b=70),
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY),
        paper_bgcolor=BG_SURFACE, 
        plot_bgcolor=BG_SURFACE, 
        
        coloraxis_colorbar=dict(
            title="",
            orientation="h",
            yanchor="top",
            y=-0.02,
            xanchor="center",
            x=0.5,
            thickness=10,
            len=0.6,
            outlinewidth=0,
            tickformat="$,.0s",
        ),
    )
    return fig

def _build_heatmap(genre_data, selected_genre):
    heatmap = genre_data.get('heatmap', {})
    tags = heatmap.get('tags', [])
    matrix = heatmap.get('matrix', [])
    
    if not tags or not matrix:
        return go.Figure()

    fig = px.imshow(
        matrix,
        x=tags,
        y=tags,
        color_continuous_scale='Viridis',
        labels=dict(x="Primary Tag", y="Secondary Tag", color="Average Positive<br>Reviews (%)")
    )
    
    fig.update_traces(
        hovertemplate="Primary Tag: %{x}<br>Secondary Tag: %{y}<br>Average Positive Reviews: %{z:.1f}%<extra></extra>"
    )
    
    fig.update_layout(
        title=dict(text=f"<b>Genre Co-occurrence & Player Satisfaction Matrix ({selected_genre})</b>", x=0.02, xanchor="left"),
        xaxis_tickangle=-45, 
        xaxis_title="", 
        yaxis_title="", 
        margin=dict(l=50, r=20, t=52, b=50),
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    
    return fig

def _build_violins(df_target, selected_genre):

    df_violin = df_target[df_target['Average playtime forever'] > 0].copy()
    df_violin['Playtime_Hours'] = df_violin['Average playtime forever'] / 60
    if not df_violin.empty:
        df_violin = df_violin[df_violin['Playtime_Hours'] <= df_violin['Playtime_Hours'].quantile(0.95)]
    
    q40 = df_violin['Price'].quantile(0.40)
    q80 = df_violin['Price'].quantile(0.80)
    if q40 == q80:
        q40 = df_violin['Price'].median() * 0.7
        q80 = df_violin['Price'].median() * 1.3

    def tier_assigner(price):
        if price == 0: return "Free"
        elif price <= q40: return f"Budget<br>(Under ${q40:.2f})"
        elif price <= q80: return f"Mid-tier<br>(${q40:.2f} - ${q80:.2f})"
        else: return f"Premium<br>(Above ${q80:.2f})"

    df_violin['Price_Tier'] = df_violin['Price'].apply(tier_assigner)
    global_order = ["Free", f"Budget<br>(Under ${q40:.2f})", f"Mid-tier<br>(${q40:.2f} - ${q80:.2f})", f"Premium<br>(Above ${q80:.2f})"]

    # --- Violin Chart A: Playtime Engagement ---
    fig_playtime = px.violin(
        df_violin, x='Price_Tier', y='Playtime_Hours', points=False, box=True, color='Price_Tier', color_discrete_sequence=[PURPLE,BLUE,RED,GREEN],
        category_orders={'Price_Tier': global_order},
        labels={'Playtime_Hours': 'Playtime (Hours)', 'Price_Tier': 'Market Tier'}
    )
    for trace in fig_playtime.data:
        tier_name = trace.name
        sub_df = df_violin[df_violin['Price_Tier'] == tier_name]
        if not sub_df.empty:
            min_val = sub_df['Playtime_Hours'].min()
            q1_val = sub_df['Playtime_Hours'].quantile(0.25)
            median_val = sub_df['Playtime_Hours'].median()
            mean_val = sub_df['Playtime_Hours'].mean()
            q3_val = sub_df['Playtime_Hours'].quantile(0.75)
            max_val = sub_df['Playtime_Hours'].max()
            
            tier_display = tier_name.replace("<br>", " ")
            hover_text = (
                f"<b>{tier_display}</b><br>"
                f"Max: {max_val:.1f} hrs<br>"
                f"Q3: {q3_val:.1f} hrs<br>"
                f"Median: {median_val:.1f} hrs<br>"
                f"Mean: {mean_val:.1f} hrs<br>"
                f"Q1: {q1_val:.1f} hrs<br>"
                f"Min: {min_val:.1f} hrs<extra></extra>"
            )
            trace.hovertemplate = hover_text
        trace.hoveron = 'violins'
        if hasattr(trace, 'marker') and getattr(trace.marker, 'color', None):
            trace.hoverlabel = dict(
                bgcolor=trace.marker.color,
                bordercolor=trace.marker.color,
                font=dict(family="Inter, sans-serif", size=13, color="white")
            )

    fig_playtime.update_layout(
        title=dict(text=f"<b>Player Engagement & Playtime Distribution by Pricing Tier ({selected_genre})</b>", x=0.02, xanchor="left"),
        showlegend=False, 
        margin=dict(l=50, r=20, t=52, b=50),
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
    )
    fig_playtime.update_xaxes(showspikes=False)
    fig_playtime.update_yaxes(showspikes=False)

    # --- Violin Chart B: Estimated Income ---
    df_income = df_target[df_target['Estimated_Income'] > 0].copy()
    if not df_income.empty:
        df_income = df_income[df_income['Estimated_Income'] <= df_income['Estimated_Income'].quantile(0.95)]
    
    df_income['Price_Tier'] = df_income['Price'].apply(tier_assigner)

    income_order = [tier for tier in global_order if tier != "Free"]
    
    fig_income = px.violin(
        df_income, x='Price_Tier', y='Estimated_Income', points=False, log_y=True, color='Price_Tier',
        color_discrete_sequence=[BLUE, RED, GREEN],
        category_orders={'Price_Tier': income_order}, box=True,
        labels={'Estimated_Income': 'Estimated Income (USD)', 'Price_Tier': 'Market Tier'}
    )
    for trace in fig_income.data:
        tier_name = trace.name
        sub_df = df_income[df_income['Price_Tier'] == tier_name]
        if not sub_df.empty:
            min_val = sub_df['Estimated_Income'].min()
            q1_val = sub_df['Estimated_Income'].quantile(0.25)
            median_val = sub_df['Estimated_Income'].median()
            mean_val = sub_df['Estimated_Income'].mean()
            q3_val = sub_df['Estimated_Income'].quantile(0.75)
            max_val = sub_df['Estimated_Income'].max()
            
            tier_display = tier_name.replace("<br>", " ")
            hover_text = (
                f"<b>{tier_display}</b><br>"
                f"Max: ${max_val:,.0f}<br>"
                f"Q3: ${q3_val:,.0f}<br>"
                f"Median: ${median_val:,.0f}<br>"
                f"Mean: ${mean_val:,.0f}<br>"
                f"Q1: ${q1_val:,.0f}<br>"
                f"Min: ${min_val:,.0f}<extra></extra>"
            )
            trace.hovertemplate = hover_text
        trace.hoveron = 'violins'
        if hasattr(trace, 'marker') and getattr(trace.marker, 'color', None):
            trace.hoverlabel = dict(
                bgcolor=trace.marker.color,
                bordercolor=trace.marker.color,
                font=dict(family="Inter, sans-serif", size=13, color="white")
            )

    fig_income.update_layout(
        title=dict(text=f"<b>Revenue Performance and Distribution Analysis by Pricing Tier ({selected_genre})</b>", x=0.02, xanchor="left"),
        showlegend=False, 
        margin=dict(l=50, r=20, t=52, b=50),
        yaxis=dict(tickformat="$,", tickvals=[5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000]),
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
    )
    fig_income.update_xaxes(showspikes=False)
    fig_income.update_yaxes(showspikes=False)

    return fig_playtime, fig_income

def _build_radar(df_target, selected_genre):
    radar_metrics = ['Price', 'Positive_Pct', 'DLC count', 'Achievements', 'Average playtime forever']
    
    df_percentiles = pd.DataFrame()
    for col in radar_metrics:
        df_percentiles[col] = df_target[col].rank(pct=True, method='max') * 100

    df_percentiles['Peak CCU'] = pd.to_numeric(df_target['Peak CCU'], errors='coerce').fillna(0).values
    df_percentiles['Estimated_Income'] = pd.to_numeric(df_target['Estimated_Income'], errors='coerce').fillna(0).values

    niche_median_profile = df_percentiles[radar_metrics].median()
    
    top_cutoff_marker1 = df_percentiles['Peak CCU'].quantile(0.90)
    leaderboard_profile1 = df_percentiles[df_percentiles['Peak CCU'] >= top_cutoff_marker1][radar_metrics].median()

    top_cutoff_marker2 = df_percentiles['Estimated_Income'].quantile(0.90)
    leaderboard_profile2 = df_percentiles[df_percentiles['Estimated_Income'] >= top_cutoff_marker2][radar_metrics].median()

    metrics_closed = radar_metrics + [radar_metrics[0]]
    niche_values = niche_median_profile.tolist() + [niche_median_profile.tolist()[0]]
    leader_values1 = leaderboard_profile1.tolist() + [leaderboard_profile1.tolist()[0]]
    leader_values2 = leaderboard_profile2.tolist() + [leaderboard_profile2.tolist()[0]]

    COLOR_MEDIAN = BLUE
    COLOR_CCU = RED
    COLOR_INCOME = GREEN

    fig = make_subplots(rows=2, cols=1, specs=[[{'type': 'polar'}], [{'type': 'polar'}]])

    fig.add_trace(go.Scatterpolar(
        r=niche_values, theta=metrics_closed, fill='toself', name='Genre Baseline Median',
        legendgroup='median', showlegend=True, line=dict(color=COLOR_MEDIAN)
    ), row=1, col=1)

    fig.add_trace(go.Scatterpolar(
        r=leader_values1, theta=metrics_closed, fill='toself', name='Top 10% Leaders (by CCU)',
        line=dict(color=COLOR_CCU)
    ), row=1, col=1)

    fig.add_trace(go.Scatterpolar(
        r=niche_values, theta=metrics_closed, fill='toself', name='Genre Baseline Median',
        legendgroup='median', showlegend=False, line=dict(color=COLOR_MEDIAN)
    ), row=2, col=1)

    fig.add_trace(go.Scatterpolar(
        r=leader_values2, theta=metrics_closed, fill='toself', name='Top 10% Leaders (by Income)',
        line=dict(color=COLOR_INCOME)
    ), row=2, col=1)

    fig.update_layout(
        polar1=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%", angle=45)),
        polar2=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%", angle=45)),
        title=dict(text=f"<b>Competitive Performance Benchmarking: Baseline vs. Market Leaders ({selected_genre})</b>", x=0.02, xanchor="left"),
        showlegend=True, 
        legend=dict(yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=50, r=20, t=52, b=50),
        font=dict(family="Inter, sans-serif", color=TEXT_PRIMARY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


layout = html.Div([
    # Page Heading Info Block
    html.Div([
        html.H2(title, style={"fontSize": "1.8rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY}),
        html.Div(desc, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "marginTop": "4px"}),
    ], style={"marginBottom": "1.5rem"}),
    
    # Global Control Filter Card Panel
    html.Div(
        children=[
            html.Label(
                "Genre",
                style={
                    "color": TEXT_SECONDARY,
                    "fontSize": "0.75rem",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                    "marginBottom": "6px",
                    "display": "block",
                },
            ),
            dcc.Dropdown(
                id="insights-global-genre-dropdown",
                options=[{"label": g, "value": g} for g in GENRE_OPTIONS],
                value="Indie",
                clearable=False,
                style={"maxWidth": "340px"}
            )
        ], style={"marginBottom": "1.25rem"}
    ),

    # UPPER SECTION: Flex Row Split (Left Column Stack vs Right Column Tall Card)
    html.Div([
        
        # Left Sub-Column: Treemap on top of Heatmap
        html.Div([
            html.Div(style={**CARD_STYLE, "border": "none", "marginBottom": "1.5rem"}, children=[
                dcc.Graph(id="insights-treemap-graph", config={"responsive": True}, style={"height": "650px"})
            ]),
            html.Div(style={**CARD_STYLE, "border": "none"}, children=[
                dcc.Graph(id="insights-heatmap-graph", config={"responsive": True}, style={"height": "500px"})
            ])
        ], style={"flex": "1.1", "display": "flex", "flexDirection": "column"}),
        
        # Right Column: Holds the full double-stacked Radar Subplots together
        html.Div(style={**CARD_STYLE, "border": "none", "flex": "0.9", "display": "flex", "flexDirection": "column"}, children=[
            dcc.Graph(id="insights-radar-subplots-graph", config={"responsive": True}, style={"flex": "1", "height": "980px"})
        ])
        
    ], style={"display": "flex", "gap": "1.5rem", "marginBottom": "1.5rem"}),

    # LOWER SECTION: Wide Full-Width Stacked Violin Charts
    html.Div(style={**CARD_STYLE, "border": "none", "marginBottom": "1.5rem"}, children=[
        dcc.Graph(id="insights-income-violin-graph", config={"responsive": True})
    ]),
    
    html.Div(style={**CARD_STYLE, "border": "none"}, children=[
        dcc.Graph(id="insights-playtime-violin-graph", config={"responsive": True})
    ])
])


def register_callbacks(app):
    @app.callback(
        Output("insights-treemap-graph", "figure"),
        Output("insights-heatmap-graph", "figure"),
        Output("insights-playtime-violin-graph", "figure"),
        Output("insights-income-violin-graph", "figure"),
        Output("insights-radar-subplots-graph", "figure"),
        Input("insights-global-genre-dropdown", "value")
    )
    def update_insights_dashboard(selected_genre):
        
        genre_data = PRECOMPUTED.get(selected_genre, {})
        
        # We use regex=False for a massive speedup on string searching
        df_target = GAMES[GAMES['Genres'].fillna('').astype(str).str.contains(selected_genre, case=False, regex=False)].copy()
        
        fig_treemap = _build_treemap(genre_data, selected_genre)
        fig_heatmap = _build_heatmap(genre_data, selected_genre)
        fig_playtime, fig_income = _build_violins(df_target, selected_genre)
        fig_radar = _build_radar(df_target, selected_genre)
        
        return fig_treemap, fig_heatmap, fig_playtime, fig_income, fig_radar