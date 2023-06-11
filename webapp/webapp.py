import dash
from dash import dcc, html
import pandas as pd
import numpy as np
import plotly.express as px
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from pymongo import MongoClient
import yfinance as yf
from datetime import datetime, timedelta
from dash import ctx

cluster = "mongodb://localhost:27017/"
mongo_client = MongoClient(cluster)

db_sentiment = mongo_client.tweets
db_news = mongo_client.news

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Stock Sentiment Tracker", style={'color': '#4caf50'}),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.H3('Select Stock', style={'color': '#4caf50'}),
                    dcc.Dropdown(id='stock_dd',
                                 # Set the available options with noted labels and values
                                 options=[
                                     {'label': '$TSLA', 'value': 'Tesla'},
                                     {'label': '$AAPL', 'value': 'Apple'},
                                     {'label': '$BTC', 'value': 'Bitcoin'},
                                     {'label': '$GME', 'value': 'GameStop'}],
                                 style={'width': '200px', 'margin': '0 auto', 'box-shadow': '0 0 10px #ddd', 'border-radius': '5px', 'height': '35px', 'outline': 'none'}),
                ],
                style={'width': 'auto', 'height': 'auto', 'display': 'inline-block', 'vertical-align': 'top',
                       'border': '1px solid black', 'padding': '20px', 'box-sizing': 'border-box'}),
            html.Div(children=[
                dcc.Graph(id='sentiment_graph', style={'height': '500px', 'display': 'inline-block', 'box-shadow': '0 0 10px #ddd', 'margin': '15px', 'background': '#fff'}),
                dcc.Graph(id='stock_graph', style={'display': 'inline-block', 'height': '500px', 'box-shadow': '0 0 10px #ddd', 'margin': '15px', 'background': '#fff'}),
            ],),
            dcc.Graph(id='news_sentiment_graph', style={'width': '1400px', 'height': '500px', 'display': 'inline-block',
                                                        'box-shadow': '0 0 10px #ddd', 'margin': '15px',
                                                        'background': '#fff'}),
        ])],
    style={'text-align': 'center', 'display': 'inline-block', 'width': '100%', 'box-sizing': 'border-box'}
)

@app.callback(
    # Set the input and output of the callback to link the dropdown to the graph
    Output(component_id='news_sentiment_graph', component_property='figure'),
    Input(component_id='stock_dd', component_property='value')
)
def update_news_sentiment(input_stock):
    stock_default = 'Apple'
    smoothing_value_int = 0.01
    sentiment_collection = db_news.AAPL
    df_tweets = pd.DataFrame()
    df_tweets = df_tweets.append(list(sentiment_collection.find({})))
    df_tweets.sort_values(by='date', inplace=True)
    tweets = df_tweets.copy(deep=True)

    if input_stock:
        stock_default = input_stock
        if input_stock == "GameStop":
            sentiment_collection = db_news.GME
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='date', inplace=True)
            tweets = df_tweets.copy(deep=True)
        if input_stock == "Apple":
            sentiment_collection = db_news.AAPL
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='date', inplace=True)
            tweets = df_tweets.copy(deep=True)
        if input_stock == "Tesla":
            sentiment_collection = db_news.TSLA
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='date', inplace=True)
            tweets = df_tweets.copy(deep=True)
        if input_stock == "Bitcoin":
            sentiment_collection = db_news.BTC
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='date', inplace=True)
            tweets = df_tweets.copy(deep=True)

    graph_array = []
    sentiment_dict = {'positive': 1, 'neutral': 0, 'negative': -1}
    for tweet in range(len(tweets)):
        graph_array.append(sentiment_dict[tweets['sentiment'][tweet][0]['label']])
    exponential_model = SimpleExpSmoothing(graph_array)
    #exponential_model._index = pd.to_datetime(tweets.index)
    fit = exponential_model.fit(smoothing_level=smoothing_value_int)

    line_fig_tweets_news = px.line(
        title=f'News sentiment change of {stock_default}', data_frame=tweets, x=tweets.date, y=fit.fittedvalues, range_y=[-0.3, 0.3])

    fin_buttons = [
        {'count': 7, 'label': "1W", 'step': 'day', 'stepmode': "backward"},
        {'count': 14, 'label': "2W", 'step': 'day', 'stepmode': "backward"},
        {'count': 1, 'label': "1M", 'step': 'month', 'stepmode': "backward"},
        {'count': 6, 'label': "6M", 'step': "month", 'stepmode': "backward"},
        {'count': 1, 'label': "1Y", 'step': "year", 'stepmode': "backward"},
        {'label': "MAX", 'step': "all"}
    ]

    line_fig_tweets_news.update_layout(
        {'xaxis': {"rangeselector": {'buttons': fin_buttons}}},
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="grey",
        legend_title_font_color="green",
        xaxis_title=" ",
        yaxis_title="Sentiment score",
    )

    return line_fig_tweets_news


@app.callback(
    # Set the input and output of the callback to link the dropdown to the graph
    Output(component_id='sentiment_graph', component_property='figure'),
    Input(component_id='stock_dd', component_property='value')
)
def update_sentiment(input_stock):
    stock_default = 'Apple'
    smoothing_value_int = 0.01
    #df_tweets = pd.read_csv('D:/anaconda_environment/dipterv 1/TWTR.csv')
    #tweets = df_tweets.copy(deep=True)
    #tweets = sentiment_collection_start.copy(deep=True)
    sentiment_collection = db_sentiment.AAPL
    df_tweets = pd.DataFrame()
    df_tweets = df_tweets.append(list(sentiment_collection.find({})))
    df_tweets.sort_values(by='created_at', inplace=True)
    tweets = df_tweets.copy(deep=True)

    if input_stock:
        stock_default = input_stock
        if input_stock == "GameStop":
            sentiment_collection = db_sentiment.GME
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='created_at', inplace=True)
            tweets = df_tweets.copy(deep=True)
        if input_stock == "Apple":
            sentiment_collection = db_sentiment.AAPL
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='created_at', inplace=True)
            tweets = df_tweets.copy(deep=True)
        if input_stock == "Tesla":
            sentiment_collection = db_sentiment.TSLA
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='created_at', inplace=True)
            tweets = df_tweets.copy(deep=True)
        if input_stock == "Bitcoin":
            sentiment_collection = db_sentiment.BTC
            df_tweets = pd.DataFrame()
            df_tweets = df_tweets.append(list(sentiment_collection.find({})))
            df_tweets.sort_values(by='created_at', inplace=True)
            tweets = df_tweets.copy(deep=True)

    graph_array = []
    sentiment_dict = {'positive': 1, 'neutral': 0, 'negative': -1}
    for tweet in range(len(tweets)):
        graph_array.append(sentiment_dict[tweets['sentiment'][tweet][0]['label']])
    exponential_model = SimpleExpSmoothing(graph_array)
    #exponential_model._index = pd.to_datetime(tweets.index)
    fit = exponential_model.fit(smoothing_level=smoothing_value_int)

    line_fig_tweets = px.line(
        title=f'Sentiment change of {stock_default}', data_frame=tweets, x=tweets.created_at, y=fit.fittedvalues, range_y=[-1, 1])

    # Loop through the states
    for step in np.arange(0.01, 0.2, 0.01):
        fit = exponential_model.fit(smoothing_level=step)
        line_fig_tweets.add_trace(
            go.Scatter(
                visible=False,
                x=tweets.created_at,
                y=fit.fittedvalues))

    # Create the slider elements
    steps = []
    for i in range(len(line_fig_tweets.data)):
        step = dict(
            label=f"{(i+1)*0.01}",
            method="update",
            args=[{"visible": [False] * len(line_fig_tweets.data)}],  # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Exponential Smoothing: "},
        pad={"t": 30},
        steps=steps
    )]

    fin_buttons = [
        {'count': 1, 'label': "1H", 'step': 'hour', 'stepmode': "backward"},
        {'count': 3, 'label': "3H", 'step': 'hour', 'stepmode': "backward"},
        {'count': 12, 'label': "12H", 'step': 'hour', 'stepmode': "backward"},
        {'count': 1, 'label': "1D", 'step': "day", 'stepmode': "backward"},
        {'count': 7, 'label': "1W", 'step': 'day', 'stepmode': "backward"},
        {'count': 6, 'label': "6M", 'step': "month", 'stepmode': "backward"},
        {'count': 1, 'label': "1Y", 'step': "year", 'stepmode': "backward"},
        {'label': "MAX", 'step': "all"}
    ]

    line_fig_tweets.update_layout(
        {'xaxis': {"rangeselector": {'buttons': fin_buttons}}, 'sliders': sliders},
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="grey",
        legend_title_font_color="green",
        xaxis_title=" ",
        yaxis_title="Sentiment score",
    )

    return line_fig_tweets

@app.callback(
    # Set the input and output of the callback to link the dropdown to the graph
    Output(component_id='stock_graph', component_property='figure'),
    Input(component_id='stock_dd', component_property='value')
)
def update_stock(input_stock):
    stock_default = 'Apple'
    #df_stocks = pd.read_csv('D:/anaconda_environment/dipterv 1/TSLA_stock.csv')
    #stocks = df_stocks.copy(deep=True)
    ticker = yf.Ticker('AAPL')
    now = datetime.now()
    now_and_one_day = now + timedelta(days=1)
    delta_week = now - timedelta(days=7)
    dt_string_now = now_and_one_day.strftime("%Y-%m-%d")
    dt_string_delta_week = delta_week.strftime("%Y-%m-%d")
    stock_week_historical = ticker.history(start=dt_string_delta_week, end=dt_string_now, interval="2m",
                                           prepost=True,
                                           actions=False)
    stock_historical = ticker.history(start="2023-01-01", end=dt_string_delta_week, actions=False)
    stock_historical = stock_historical.append(stock_week_historical)

    if input_stock:
        stock_default = input_stock
        if input_stock == "GameStop":
            ticker = yf.Ticker('GME')
            now = datetime.now()
            now_and_one_day = now + timedelta(days=1)
            delta_week = now - timedelta(days=7)
            dt_string_now = now_and_one_day.strftime("%Y-%m-%d")
            dt_string_delta_week = delta_week.strftime("%Y-%m-%d")
            stock_week_historical = ticker.history(start=dt_string_delta_week, end=dt_string_now, interval="2m",
                                                   prepost=True,
                                                   actions=False)
            stock_historical = ticker.history(start="2023-01-01", end=dt_string_delta_week, actions=False)
            stock_historical = stock_historical.append(stock_week_historical)
        if input_stock == "Apple":
            ticker = yf.Ticker('AAPL')
            now = datetime.now()
            now_and_one_day = now + timedelta(days=1)
            delta_week = now - timedelta(days=7)
            dt_string_now = now_and_one_day.strftime("%Y-%m-%d")
            dt_string_delta_week = delta_week.strftime("%Y-%m-%d")
            stock_week_historical = ticker.history(start=dt_string_delta_week, end=dt_string_now, interval="2m",
                                                   prepost=True,
                                                   actions=False)
            stock_historical = ticker.history(start="2023-01-01", end=dt_string_delta_week, actions=False)
            stock_historical = stock_historical.append(stock_week_historical)
        if input_stock == "Tesla":
            ticker = yf.Ticker('TSLA')
            now = datetime.now()
            now_and_one_day = now + timedelta(days=1)
            delta_week = now - timedelta(days=7)
            dt_string_now = now_and_one_day.strftime("%Y-%m-%d")
            dt_string_delta_week = delta_week.strftime("%Y-%m-%d")
            stock_week_historical = ticker.history(start=dt_string_delta_week, end=dt_string_now, interval="2m",
                                                   prepost=True,
                                                   actions=False)
            stock_historical = ticker.history(start="2023-01-01", end=dt_string_delta_week, actions=False)
            stock_historical = stock_historical.append(stock_week_historical)
        if input_stock == "Bitcoin":
            ticker = yf.Ticker('BTC-USD')
            now = datetime.now()
            now_and_one_day = now + timedelta(days=1)
            delta_week = now - timedelta(days=7)
            dt_string_now = now_and_one_day.strftime("%Y-%m-%d")
            dt_string_delta_week = delta_week.strftime("%Y-%m-%d")
            stock_week_historical = ticker.history(start=dt_string_delta_week, end=dt_string_now, interval="2m",
                                                   prepost=True,
                                                   actions=False)
            stock_historical = ticker.history(start="2023-01-01", end=dt_string_delta_week, actions=False)
            stock_historical = stock_historical.append(stock_week_historical)


    line_fig_tweets = px.line(
        title=f'Stock price change of {stock_default}', data_frame=stock_historical, x=stock_historical.index, y=stock_historical["Open"])


    fin_buttons = [
        {'count': 1, 'label': "1H", 'step': 'hour', 'stepmode': "backward"},
        {'count': 3, 'label': "3H", 'step': 'hour', 'stepmode': "backward"},
        {'count': 12, 'label': "12H", 'step': 'hour', 'stepmode': "backward"},
        {'count': 1, 'label': "1D", 'step': "day", 'stepmode': "backward"},
        {'count': 7, 'label': "1W", 'step': 'day', 'stepmode': "backward"},
        {'count': 6, 'label': "6M", 'step': "month", 'stepmode': "backward"},
        {'count': 1, 'label': "1Y", 'step': "year", 'stepmode': "backward"},
        {'label': "MAX", 'step': "all"}
    ]

    line_fig_tweets.update_layout(
        {'xaxis': {"rangeselector": {'buttons': fin_buttons}}},
        font_family="Courier New",
        font_color="blue",
        title_font_family="Times New Roman",
        title_font_color="grey",
        legend_title_font_color="green",
        xaxis_title=" ",
        yaxis_title="Stock price",
    )

    return line_fig_tweets


# Set the app to run in development mode
if __name__ == '__main__':
    app.run_server(debug=True)
