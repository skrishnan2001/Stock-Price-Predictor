# Stockify : The Stock Price Forecast App
ML based web-app that can predict the price of the stocks of a company for the next 4 years

## Project Overview
Investment firms, hedge funds and even individuals have been using financial models to better understand market behavior and make profitable investments and trades. A wealth of information is available in the form of historical stock prices and company performance data, suitable for machine learning algorithms to process.

Can we actually predict stock prices with machine learning? Investors make educated guesses by analyzing data. They'll read the news, study the company history, industry trends and other lots of data points that go into making a prediction. The prevailing theories is that stock prices are totally random and unpredictable but that raises the question why top investment banks and financial services hire quantitative analysts to build predictive models. We have this idea of a trading floor being filled with adrenaline infuse men with loose ties running around yelling something into a phone but these days they're more likely to see rows of machine learning experts quietly sitting in front of computer screens. In fact about 70% of all orders on Wall Street are now placed by software, we're now living in the age of the algorithm.

This web-app attempts to predict the stock prices of all the companies listed in `yahoo finance` for the next 4 years based on the data from Jan 2015 to the present date. I'm fetching the past stock information about a company using `Yfinance`, a python package that enables us to fetch historical market data from Yahoo Finance API in a Pythonic way. From this data, using Facebook's `fbprohet library`, I'm predicting the future stock prices and also displaying it graphically for the next 4 years.

## System Architecture Diagram
![Screenshot](https://github.com/skrishnan2001/Stock-Price-Predictor/blob/master/Workflow/SystemArchitecture.JPG)
