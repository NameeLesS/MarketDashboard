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

from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Input, Output, dcc, html

# Import layout constants directly from your centralized style sheet
from styles import (
    CARD_STYLE,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "games.csv"

title = "Market Insights"
desc = "Actionable takeaways from the data."

BLUE = '#636EFA'
RED = '#EF553B'
GREEN = '#00CC96'
PURPLE = '#AB63FA'

def _calculate_owners_midpoint(estimated_owners):
    if pd.isna(estimated_owners):
        return np.nan
    owners_range = str(estimated_owners).split(' - ')
    if len(owners_range) != 2:
        return np.nan
    try:
        return (int(owners_range[0]) + int(owners_range[1])) // 2
    except ValueError:
        return np.nan

def _load_insights_data() -> pd.DataFrame:
    usecols = [
        "AppID", "Name", "Price", "Genres", "Tags", "Positive", "Peak CCU",
        "Estimated owners", "Average playtime forever", "Achievements", "DLC count"
    ]
    frame = pd.read_csv(DATA_PATH, usecols=usecols, low_memory=False)
    
    frame['Price'] = pd.to_numeric(frame['Price'], errors='coerce').fillna(0)
    frame['Peak CCU'] = pd.to_numeric(frame['Peak CCU'], errors='coerce').fillna(0)
    frame['Positive'] = pd.to_numeric(frame['Positive'], errors='coerce').fillna(0)
    frame['Average playtime forever'] = pd.to_numeric(frame['Average playtime forever'], errors='coerce').fillna(0)
    frame['Achievements'] = pd.to_numeric(frame['Achievements'], errors='coerce').fillna(0)
    frame['DLC count'] = pd.to_numeric(frame['DLC count'], errors='coerce').fillna(0)
    
    frame['Positive_Pct'] = frame['Positive'] * 100
    frame['Owners_Midpoint'] = frame['Estimated owners'].apply(_calculate_owners_midpoint)
    frame['Estimated_Income'] = frame['Owners_Midpoint'] * frame['Price']
    
    return frame

GAMES = _load_insights_data()

GENRE_OPTIONS = sorted(list(set([
    g.strip() for sublist in GAMES['Genres'].dropna().str.split(',') for g in sublist if g.strip()
])))


def _build_treemap(df_target, selected_genre):
    df_target_tags = df_target.dropna(subset=['Tags']).copy()
    df_target_tags['Tag_List'] = df_target_tags['Tags'].apply(lambda x: [t.strip() for t in str(x).split(',') if t.strip()])
    df_exploded = df_target_tags.explode('Tag_List')
    
    tag_summary = df_exploded.groupby('Tag_List').agg(
        Game_Count=('Name', 'count'), 
        Estimated_Income_Median=('Estimated_Income', 'median')
    ).reset_index()
    
    tag_summary = tag_summary[tag_summary['Tag_List'].str.lower() != selected_genre.lower()]
    top_30_tags = tag_summary.sort_values(by='Game_Count', ascending=False).head(30)
    
    if top_30_tags.empty:
        return go.Figure()

    fig = px.treemap(
        top_30_tags,
        path=['Tag_List'],
        values='Game_Count',
        color='Estimated_Income_Median',
        color_continuous_scale='Blues',
        title=f'Sub-Tag Strategic Matrix for {selected_genre} Games',
        labels={'Estimated_Income_Median': 'Median of<br>Estimated Income'},
        template='plotly_white'
    )
    fig.update_traces(
        hovertemplate="<b>Tag: %{label}</b><br>Total Games: %{value:,}<br>Median Income: $%{color:,.0f}<extra></extra>"
    )
    fig.update_layout(title_x=0.5, margin=dict(t=50, b=10, l=10, r=10))
    return fig

def _build_heatmap(df_target, selected_genre):
    df_target_tags = df_target.dropna(subset=['Tags']).copy()
    df_target_tags['Tag_List'] = df_target_tags['Tags'].apply(lambda x: [t.strip() for t in str(x).split(',') if t.strip()])
    df_exploded = df_target_tags.explode('Tag_List')
    
    top_15_subtags = df_exploded[df_exploded['Tag_List'].str.lower() != selected_genre.lower()]['Tag_List'].value_counts().head(15).index.tolist()
    
    if not top_15_subtags:
        return go.Figure()
        
    df_matrix_filtered = df_exploded[df_exploded['Tag_List'].isin(top_15_subtags)]
    tag_pairs = df_matrix_filtered.merge(df_matrix_filtered, on='AppID', suffixes=('_A', '_B'))
    tag_pairs = tag_pairs[tag_pairs['Tag_List_A'] != tag_pairs['Tag_List_B']]
    
    if tag_pairs.empty:
        return go.Figure()

    fig = px.density_heatmap(
        tag_pairs, 
        x='Tag_List_A', 
        y='Tag_List_B', 
        z='Positive_Pct_A', 
        histfunc='avg',
        title=f'Sub-Tag Synergy Heatmap Matrix for {selected_genre} Games',
        color_continuous_scale='Viridis',
        category_orders={"Tag_List_A": top_15_subtags, "Tag_List_B": top_15_subtags},
        template='plotly_white'
    )
    fig.update_traces(
        hovertemplate="Primary Tag: %{x}<br>Secondary Tag: %{y}<br>Average Positive Reviews: %{z:.1f}%<extra></extra>"
    )
    fig.update_coloraxes(colorbar_title="Average Positive<br>Reviews (%)")
    fig.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="", title_x=0.5, margin=dict(t=50, b=0, l=0, r=0))
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
        title=f'Player Engagement across Pricing Levels for {selected_genre} Games',
        labels={'Playtime_Hours': 'Playtime (Hours)', 'Price_Tier': 'Market Tier'},
        template='plotly_white'
    )
    fig_playtime.update_traces(hovertemplate="<b>%{x}</b><br>Playtime: %{y:.1f} hours<extra></extra>")
    fig_playtime.update_layout(title_x=0.5, showlegend=False, margin=dict(t=50, b=10, l=10, r=10))

    # --- Violin Chart B: Estimated Income ---
    df_income = df_target[df_target['Estimated_Income'] > 0].copy()
    if not df_income.empty:
        df_income = df_income[df_income['Estimated_Income'] <= df_income['Estimated_Income'].quantile(0.95)]
    
    df_income['Price_Tier'] = df_income['Price'].apply(tier_assigner)

    income_order = [tier for tier in global_order if tier != "Free"]
    
    fig_income = px.violin(
        df_income, x='Price_Tier', y='Estimated_Income', points=False, log_y=True, color='Price_Tier',
        category_orders={'Price_Tier': income_order}, box=True,
        title=f'Estimated Income Potential across Pricing Levels for {selected_genre} Games',
        labels={'Estimated_Income': 'Estimated Income (USD)', 'Price_Tier': 'Market Tier'},
        template='plotly_white'
    )
    fig_income.update_traces(hovertemplate="<b>%{x}</b><br>Estimated Income: %{y:.1f}<extra></extra>")
    fig_income.update_layout(
        title_x=0.5, showlegend=False, margin=dict(t=50, b=10, l=10, r=10),
        yaxis=dict(tickformat="$,", tickvals=[5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000, 2000000])
    )

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
        title=f'Percentile-Ranked Competitive Benchmarks for {selected_genre} Games',
        showlegend=True, title_x=0.5, template='plotly_white',
        legend=dict(yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=80, b=80, l=20, r=20)
    )
    return fig


layout = html.Div([
    # Page Heading Info Block
    html.Div([
        html.H2(title, style={"fontSize": "1.8rem", "fontWeight": "600", "margin": "0", "color": TEXT_PRIMARY}),
        html.Div(desc, style={"color": TEXT_SECONDARY, "fontSize": "0.95rem", "marginTop": "4px"}),
    ], style={"marginBottom": "1.5rem"}),
    
    # Global Control Filter Card Panel
    html.Div(style={**CARD_STYLE, "marginBottom": "1.5rem"}, children=[
        html.Div([
            html.Label("Target Analytical Genre Vertical:", style={"fontWeight": "600", "fontSize": "0.85rem", "color": TEXT_PRIMARY, "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="insights-global-genre-dropdown",
                options=[{"label": g, "value": g} for g in GENRE_OPTIONS],
                value="Indie",
                clearable=False,
                style={"width": "100%", "minWidth": "280px"}
            )
        ], style={"maxWidth": "400px"})
    ]),

    # UPPER SECTION: Flex Row Split (Left Column Stack vs Right Column Tall Card)
    html.Div([
        
        # Left Sub-Column: Treemap on top of Heatmap
        html.Div([
            html.Div(style={**CARD_STYLE, "marginBottom": "1.5rem"}, children=[
                dcc.Graph(id="insights-treemap-graph", config={"responsive": True}, style={"height": "400px"})
            ]),
            html.Div(style=CARD_STYLE, children=[
                dcc.Graph(id="insights-heatmap-graph", config={"responsive": True}, style={"height": "500px"})
            ])
        ], style={"flex": "1.1", "display": "flex", "flexDirection": "column"}),
        
        # Right Column: Holds the full double-stacked Radar Subplots together
        html.Div(style={**CARD_STYLE, "flex": "0.9", "display": "flex", "flexDirection": "column"}, children=[
            dcc.Graph(id="insights-radar-subplots-graph", config={"responsive": True}, style={"flex": "1", "height": "980px"})
        ])
        
    ], style={"display": "flex", "gap": "1.5rem", "marginBottom": "1.5rem"}),

    # LOWER SECTION: Wide Full-Width Stacked Violin Charts
    html.Div(style={**CARD_STYLE, "marginBottom": "1.5rem"}, children=[
        dcc.Graph(id="insights-income-violin-graph", config={"responsive": True})
    ]),
    
    html.Div(style=CARD_STYLE, children=[
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
        
        df_target = GAMES[GAMES['Genres'].fillna('').str.contains(selected_genre, case=False)].copy()
        
        fig_treemap = _build_treemap(df_target, selected_genre)
        fig_heatmap = _build_heatmap(df_target, selected_genre)
        fig_playtime, fig_income = _build_violins(df_target, selected_genre)
        fig_radar = _build_radar(df_target, selected_genre)
        
        return fig_treemap, fig_heatmap, fig_playtime, fig_income, fig_radar