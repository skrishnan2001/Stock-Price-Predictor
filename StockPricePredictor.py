import streamlit as st
from datetime import date
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import pandas as pd
from plotly import graph_objs as go


def isLeapYear(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def sideBarHelper(text):
    st.sidebar.text(text)


def populateSideBar():
    st.sidebar.image(selection.info["logo_url"])
    st.sidebar.header(selection.info['shortName'])
    sideBarHelper("Sector: " + selection.info['sector'])
    sideBarHelper("Financial Currency: " + selection.info['financialCurrency'])
    sideBarHelper("Exchange: " + selection.info['exchange'])
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
    col1.metric(label="Current Price, Change w.r.t Opening Price", value=selection.info['currentPrice'],
                delta='%.2f' % priceChangeToday)

    priceChangeYesterday = data['Close'][len(data) - 1] - data['Close'][len(data) - 2] if len(data) >= 2 else 0
    col2.metric(label="Previous Closing, Previous Day Change", value=selection.info['currentPrice'],
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

    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)

    # Showing and plotting the forecast
    st.subheader('Forecast data')
    st.write(forecast)

    st.write(f'Forecast plot for {n_years} years')
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)

    st.write("Forecast components - Yearly, Daily and Monthly Trends")
    fig2 = m.plot_components(forecast)
    st.write(fig2)


# Driver
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
year = int(TODAY[: 4])

st.title('STOCK FORECAST APP')

try:
    option = st.sidebar.selectbox("Which Dashboard?", ('Past Trends', 'Predict Stock Price'), 0)
    stock = st.sidebar.text_input("Symbol", value='GOOG')
    # selected_stock = st.selectbox('Select dataset for prediction', stocks)
    # stocks = listOfStockSymbols()
    selected_stock = stock

    data = load_data(selected_stock)

    selection = yf.Ticker(selected_stock)
    company_name = selection.info['longName']
    st.subheader(company_name + "'s Stocks")

    populateSideBar()

    if option == 'Past Trends':
        pastTrends()
        plot_raw_data()

    if option == 'Predict Stock Price':
        # Predicting the forecast with Prophet.
        predictingTheStockPrices()
except KeyError:
    st.error('This company is not listed !')

except FileNotFoundError:
    st.error('No data is available about this stock !')

except ValueError:
    st.error('Symbol cannot be empty !')
