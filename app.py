from dash_extensions import EventSource
from dash_extensions.enrich import html, dcc, Output, Input, DashProxy
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table

"""
A Stock Visualizer that shows Live and Historical stock data for the 5 given stocks.
"""

HISTORICAL = pd.read_csv('stocks.csv')
# covert the date to datetime then to string
HISTORICAL['DATE'] = pd.to_datetime(HISTORICAL['DATE'], format="%m%d%Y").dt.strftime('%Y-%m-%d')
HISTORICAL = HISTORICAL.sort_values('DATE')
HISTORICAL = HISTORICAL.round(2)

update_graph = """function(msg) {
    if(!msg){return {};}  // no data, just return
    const data = JSON.parse(msg);  // read the data
    return {data: [{y: data, type: "scatter"}]};  // plot the data
}"""
app = DashProxy(__name__, suppress_callback_exceptions=True)
app.layout = html.Div([
    html.H1('Stock Visualizer'),
    dcc.Tabs(id="stocks-tabs", value='tab-2-historical', children=[
        dcc.Tab(label='Historical', value='tab-2-historical', children=[
            dcc.Graph(id="historical-graph"),
            dash_table.DataTable(
                id='historical-table',
                style_cell={'textAlign': 'left'},
                style_table={ 'minWidth': '100%'},
                fixed_columns={'headers': True, 'data': 1}
            )
        ]),
        dcc.Tab(label='Live', value='tab-1-live', children=[
            EventSource(id="sse", url="http://127.0.0.1:5000/stocks_data"),
            dcc.Graph(id="live-graph")
        ])
    ]),
    # html.Div(id='tabs-content-graph')
])
app.layout.children.append(html.Div(id='dummy-output'))
app.clientside_callback(update_graph, Output("live-graph", "figure"), Input("sse", "message"))


@app.callback(Output('dummy-output', 'children'), Input('tabs-content-graph', 'figure'))
def print_figure_data(figure):
    print(figure)
    return ''

@app.callback(Output('hover-data', 'children'), Input('historical-graph', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


# @app.callback(Output('live-graph', 'figure'), Input('stocks-tabs', 'value'))
# def generate_live_graph(value):
#     if value != 'tab-1-live':
#         return {}

@app.callback(Output('historical-graph', 'figure'), Input('stocks-tabs', 'value'))
def generate_historical_graph(value):
    if value != 'tab-2-historical':
        return {}
    
    global HISTORICAL
    historical_data = HISTORICAL
    historical_data = historical_data.drop_duplicates(subset='DATE')

    non_date_columns = historical_data.columns[historical_data.columns != 'DATE']
    
    fig = px.line(historical_data, x='DATE', y=non_date_columns)
    fig.update_traces(hovertemplate='$%{y}')
    fig.update_layout(hovermode='x unified', legend_title_text='Ticker')

    return fig


@app.callback(
    Output('historical-table', 'data'), 
    Output('historical-table', 'columns'), 
    Input('stocks-tabs', 'value'))
def generate_historical_table(value):
    if value != 'tab-2-historical':
        return (),[]
    
    global HISTORICAL
    historical_data = HISTORICAL
    historical_data = historical_data.drop_duplicates(subset='DATE')
        
    # transpose
    date_header_df = historical_data.set_index('DATE').T
    columns = [{"name": i, "id": i} for i in date_header_df.columns].append({'name': 'Ticker', 'id': 'Ticker'})
    data = date_header_df.reset_index().rename(columns={'index': 'Ticker'}).to_dict('records')
    return data, columns


if __name__ == "__main__":
    app.run_server(debug=True)
