import pandas as pd
import plotly.express as px
from dash_extensions import EventSource
from dash_extensions.enrich import html, dcc, Output, Input, DashProxy
from dash import dash_table, ClientsideFunction

"""
A Stock Visualizer that shows Live and Historical stock data for the 5 given stocks.
"""

HISTORICAL = pd.read_csv('src/data/stocks.csv')
# covert the date to datetime then to string
HISTORICAL['DATE'] = pd.to_datetime(HISTORICAL['DATE'], format="%m%d%Y").dt.strftime('%Y-%m-%d')
HISTORICAL = HISTORICAL.sort_values('DATE')
HISTORICAL = HISTORICAL.round(2)


app = DashProxy(__name__, suppress_callback_exceptions=True)
app.layout = html.Div([
    html.H1('Stock Visualizer'),
    dcc.Tabs(id="stocks-tabs", value='tab-2-historical', children=[
        dcc.Tab(label='Live', value='tab-1-live', children=[
            EventSource(id="sse", url="http://127.0.0.1:5000/stocks_data"),
            dcc.Graph(id="live-graph")
        ]),
        dcc.Tab(label='Historical', value='tab-2-historical', children=[
            dcc.Graph(id="historical-graph"),
            dash_table.DataTable(
                id='historical-table',
                style_cell={'textAlign': 'left'},
                style_table={ 'minWidth': '100%'},
                fixed_columns={'headers': True, 'data': 1}
            )
        ]),
    ]),
])


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_graph'
    ), Output("live-graph", "figure"), Input("sse", "message"))


@app.callback(Output('historical-graph', 'figure'), Input('stocks-tabs', 'value'))
def generate_historical_graph(value):
    global HISTORICAL
    if value != 'tab-2-historical' or HISTORICAL.empty:
        return {}
    
    historical_data = HISTORICAL
    historical_data = historical_data.drop_duplicates(subset='DATE')

    non_date_columns = historical_data.columns[historical_data.columns != 'DATE']
    
    fig = px.line(historical_data, x='DATE', y=non_date_columns)
    fig.update_traces(hovertemplate='$%{y}')
    fig.update_layout(hovermode='x unified', legend_title_text=None, xaxis_title=None, yaxis_title=None)

    return fig


@app.callback(
    Output('historical-table', 'data'), 
    Input('stocks-tabs', 'value'))
def generate_historical_table(value):
    global HISTORICAL
    if value != 'tab-2-historical' or HISTORICAL.empty:
        return ()
    
    historical_data = HISTORICAL
    historical_data = historical_data.drop_duplicates(subset='DATE')
        
    # transpose
    date_header_df = historical_data.set_index('DATE').T
    data = date_header_df.reset_index().rename(columns={'index': 'Ticker'}).to_dict('records')

    return data


if __name__ == "__main__":
    app.run_server(debug=True)
