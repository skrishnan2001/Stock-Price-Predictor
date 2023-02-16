import streamlit as st
from datetime import date
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import pandas as pd
from plotly import graph_objs as go
import requests
#import config
import constants
import json

API_KEY = st.secrets["NEWS_API_KEY"]
countries = constants.countries


def business_news_feed():
    select_country = st.sidebar.selectbox("Select Country: ", countries.keys())
    st.header('NEWS FEED')
    r = requests.get('https://newsapi.org/v2/top-headlines?country=' + countries[
        select_country] + '&category=business&apikey=' + API_KEY)
    data_news = json.loads(r.content)
    length = min(15, len(data_news['articles']))
    for i in range(length):
        news = data_news['articles'][i]['title']
        st.subheader(news)

        image = data_news['articles'][i]['urlToImage']
        try:
            st.image(image)
        except:
            pass
        else:
            pass

        content = data_news['articles'][i]['content']
        st.write(content)

        url = data_news['articles'][i]['url']
        st.write(url)


def isLeapYear(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def sideBarHelper(text):
    st.sidebar.text(text)


def populateSideBar():
    st.sidebar.image(selection.info["logo_url"])
    st.sidebar.header(selection.info['shortName'])
    sideBarHelper("Sector: " + selection.info['sector'])
    sideBarHelper("Financial Currency: " + selection.info['financialCurrency'])
    #sideBarHelper("Exchange: " + selection.info['exchange'])
    sideBarHelper("Timezone: " + selection.info['exchangeTimezoneName'])


def stockPricesToday():
    today_data = {'Current Price': [selection.info['currentPrice']],
                  'Previous Close': [selection.info['previousClose']],
                  'Open': [selection.info['open']],
                  'Day Low': [selection.info['dayLow']],
                  'Day High': [selection.info['dayHigh']]
                  }

    df = pd.DataFrame(today_data)
    # priceChangeToday = selection.info['currentPrice'] - data['Close'][len(data) - 1]  # Current Price - Previous Closing
    col1, col2 = st.columns(2)
    priceChangeToday = selection.info['currentPrice'] - selection.info['open']  # Current Price - Previous Closing
    col1.metric(label="Current Price, Change w.r.t Opening Price", value='%.2f' % selection.info['currentPrice'],
                delta='%.2f' % priceChangeToday)

    priceChangeYesterday = data['Close'][len(data) - 1] - data['Close'][len(data) - 2] if len(data) >= 2 else 0
    col2.metric(label="Previous Closing, Previous Day Change", value='%.2f' % data['Close'][len(data) - 1],
                delta='%.2f' % priceChangeYesterday)

    st.dataframe(df)


@st.cache
def load_data(ticker):
    historicData = yf.download(ticker, START, TODAY)
    historicData.reset_index(inplace=True)
    return historicData


def plot_raw_data():
    # Plotting the raw data
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

    fig = go.Figure()
    lastFiveDays = data.tail(10)
    fig.add_trace(go.Candlestick(x=lastFiveDays['Date'], open=lastFiveDays['Open'], high=lastFiveDays['High'],
                                 low=lastFiveDays['Low'],
                                 close=lastFiveDays['Close']))
    fig.layout.update(title_text='Candle Stick Chart - Last 10 Days Trend', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


def pastTrends():
    st.info(selection.info['longBusinessSummary'])
    st.subheader('Today')
    stockPricesToday()

    st.subheader('Last 5 Days Trend')
    st.write(data.tail())


def predictingTheStockPrices():
    period = 0
    n_years = st.slider('Years of prediction:', 1, 4)

    for i in range(0, n_years):
        if isLeapYear(year + i):
            period += 366
        else:
            period += 365
                
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
    
    df_train['ds'] = df_train['ds'].dt.tz_convert(None)

    model_param = {
        "daily_seasonality": False,
        "weekly_seasonality": False,
        "yearly_seasonality": True,
        "seasonality_mode": "multiplicative",
        "growth": "logistic"
    }

    m = Prophet(**model_param)

    m = m.add_seasonality(name="monthly", period=30, fourier_order=10)
    m = m.add_seasonality(name="quarterly", period=92.25, fourier_order=10)

    df_train['cap'] = df_train["y"].max() + df_train["y"].std() * 0.05
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    future['cap'] = df_train['cap'].max()
    forecast = m.predict(future)

    # Showing and plotting the forecast
    st.subheader('Forecast data')
    st.write(forecast)

    st.write(f'Forecast plot for {n_years} years')
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)

    st.write("Forecast components - Yearly, Monthly and Quarterly Trends")
    fig2 = m.plot_components(forecast)
    st.write(fig2)


# Driver
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
year = int(TODAY[: 4])

st.title('STOCK FORECAST APP')

try:
    option = st.sidebar.selectbox("Which Dashboard?", ('Past Trends', 'Predict Stock Price', 'Trending Business News'),
                                  0)
    stock = st.sidebar.text_input("Symbol", value='GOOG')
    # selected_stock = st.selectbox('Select dataset for prediction', stocks)
    # stocks = listOfStockSymbols()
    selected_stock = stock

    data = load_data(selected_stock)

    selection = yf.Ticker(selected_stock)

    if option == 'Past Trends':
        company_name = selection.info['longName']
        st.subheader(company_name + "'s Stocks")
        populateSideBar()
        pastTrends()
        plot_raw_data()

    if option == 'Predict Stock Price':
        # Predicting the forecast with Prophet.
        company_name = selection.info['longName']
        st.subheader(company_name + "'s Stocks")
        populateSideBar()
        predictingTheStockPrices()

    if option == 'Trending Business News':
        business_news_feed()

except KeyError:
    st.error('This company is not listed !')

except FileNotFoundError:
    st.error('No data is available about this stock !')

# except TypeError:
#     st.error('No data is available about this stock !')

except ValueError:
    st.error('Symbol cannot be empty !')

except ConnectionError:
    st.error('Could not connect to the internet :(')
