import streamlit as st
from datetime import date
import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
import pandas as pd
from plotly import graph_objs as go


def listOfStockSymbols():
    yahooTickers = pd.read_csv('dataset/Yahoo Ticker Symbols.csv')
    symbols = yahooTickers['Ticker'].tolist()
    return symbols

def isLeapYear(y):
    if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
        return True
    return False

def sideBarHelper(text):
    st.sidebar.markdown(text)

def populateSideBar():
    st.sidebar.image(selection.info["logo_url"])
    st.sidebar.subheader(selection.info['shortName'])
    sideBarHelper("Sector: " + selection.info['sector'])
    sideBarHelper("Financial Currency: " + selection.info['financialCurrency'])
    sideBarHelper("Exchange: " + selection.info['exchange'])

    st.sidebar.json({
        "Exchange Time Zone" : selection.info['exchangeTimezoneName'],
        "Current Price" : selection.info['currentPrice'],
        "Previous Close" : selection.info['previousClose'],
        "Day Low" : selection.info['dayLow'],
        "Day High" : selection.info['dayHigh']
    })



START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")
year = int(TODAY[: 4])

st.title('Stock Forecast App')

# stocks = listOfStockSymbols()
stock = st.sidebar.text_input("Symbol", value='AAPL', max_chars=8)
# selected_stock = st.selectbox('Select dataset for prediction', stocks)

stockSymbols = listOfStockSymbols()

if stock not in stockSymbols:
    st.error('This company is not listed !')

else:
    selected_stock = stock

    selection = yf.Ticker(selected_stock)
    company_name = selection.info['longName']
    st.subheader(company_name + "'s Stocks")

    populateSideBar()

    period = 0
    n_years = st.slider('Years of prediction:', 1, 4)

    for i in range(0, n_years):
        if (isLeapYear(year + i)):
            period += 366
        else:
            period += 365


    @st.cache
    def load_data(ticker):
        data = yf.download(ticker, START, TODAY)
        data.reset_index(inplace=True)
        return data


    data_load_state = st.text('Loading data...')
    data = load_data(selected_stock)
    data_load_state.text('Loading data... done!')

    st.subheader('Raw data')
    st.write(data.tail())


    # Plotting the raw data
    def plot_raw_data():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
        fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)


    plot_raw_data()

    # Predicting the forecast with Prophet.
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

    st.write("Forecast components")
    fig2 = m.plot_components(forecast)
    st.write(fig2)
