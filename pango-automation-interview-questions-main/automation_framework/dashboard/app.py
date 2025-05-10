import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os
from automation_framework.utilities.db_helpers import DbHelper

# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize database helper
db_helper = DbHelper()

def get_weather_data():
    """Fetch weather data from database and convert to DataFrame"""
    discrepancy_data = db_helper.get_discrepancy_report(threshold=0.0)
    return pd.DataFrame(discrepancy_data)

# Layout
app.layout = html.Div([
    html.H1('Weather Data Analysis Dashboard', style={'textAlign': 'center'}),
    
    # Summary Statistics Cards
    html.Div([
        html.Div([
            html.H3('Mean Difference'),
            html.H2(id='mean-diff')
        ], className='stat-card'),
        html.Div([
            html.H3('Max Difference'),
            html.H2(id='max-diff')
        ], className='stat-card'),
        html.Div([
            html.H3('Min Difference'),
            html.H2(id='min-diff')
        ], className='stat-card')
    ], className='stats-container'),
    
    # Temperature Comparison Scatter Plot
    html.Div([
        html.H2('Temperature Comparison: Web vs API'),
        dcc.Graph(id='temp-scatter')
    ], className='plot-container'),
    
    # Discrepancy Bar Chart
    html.Div([
        html.H2('Temperature Discrepancies by City'),
        dcc.Graph(id='discrepancy-bar')
    ], className='plot-container'),
    
    # Feels Like Comparison
    html.Div([
        html.H2('Feels Like Temperature Comparison'),
        dcc.Graph(id='feels-like-comparison')
    ], className='plot-container'),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # 5 minutes
        n_intervals=0
    )
])

# Callbacks
@app.callback(
    [Output('mean-diff', 'children'),
     Output('max-diff', 'children'),
     Output('min-diff', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_stats(n):
    stats = db_helper.get_summary_stats()
    return (
        f"{stats['mean_discrepancy']:.1f}°C",
        f"{stats['max_discrepancy']:.1f}°C",
        f"{stats['min_discrepancy']:.1f}°C"
    )

@app.callback(
    Output('temp-scatter', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_scatter(n):
    df = get_weather_data()
    fig = px.scatter(
        df,
        x='temperature_web',
        y='temperature_api',
        hover_name='city',
        title='Web vs API Temperature Comparison',
        labels={
            'temperature_web': 'Web Temperature (°C)',
            'temperature_api': 'API Temperature (°C)'
        }
    )
    
    # Add perfect correlation line
    fig.add_trace(
        go.Scatter(
            x=[df['temperature_web'].min(), df['temperature_web'].max()],
            y=[df['temperature_web'].min(), df['temperature_web'].max()],
            mode='lines',
            name='Perfect Correlation',
            line=dict(dash='dash', color='red')
        )
    )
    
    return fig

@app.callback(
    Output('discrepancy-bar', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_discrepancy_bar(n):
    df = get_weather_data()
    df['abs_discrepancy'] = df['discrepancy'].abs()
    df = df.sort_values('abs_discrepancy', ascending=False)
    
    fig = px.bar(
        df,
        x='city',
        y='abs_discrepancy',
        title='Temperature Discrepancies by City',
        labels={
            'city': 'City',
            'abs_discrepancy': 'Temperature Difference (°C)'
        }
    )
    
    return fig

@app.callback(
    Output('feels-like-comparison', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_feels_like(n):
    df = get_weather_data()
    if 'feels_like_web' in df.columns and 'feels_like_api' in df.columns:
        fig = px.scatter(
            df,
            x='feels_like_web',
            y='feels_like_api',
            hover_name='city',
            title='Feels Like Temperature Comparison',
            labels={
                'feels_like_web': 'Web Feels Like (°C)',
                'feels_like_api': 'API Feels Like (°C)'
            }
        )
        
        # Add perfect correlation line
        fig.add_trace(
            go.Scatter(
                x=[df['feels_like_web'].min(), df['feels_like_web'].max()],
                y=[df['feels_like_web'].min(), df['feels_like_web'].max()],
                mode='lines',
                name='Perfect Correlation',
                line=dict(dash='dash', color='red')
            )
        )
    else:
        fig = go.Figure()
        fig.add_annotation(
            text="Feels like temperature data not available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
    
    return fig

# Add CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Weather Data Analysis Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .stats-container {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
            }
            .stat-card {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                min-width: 200px;
            }
            .plot-container {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            body {
                background-color: #f0f2f5;
                font-family: Arial, sans-serif;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True) 