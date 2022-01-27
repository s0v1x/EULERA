<div align="center">
  <hr />
  <p>
      <img width="200" src="assets\logo.png" alt="EULERA" />
      

  </p>
  <b>an easy and intuitive way to get a quick feel of what’s happening on the world’s market !</b>
  
  <br />
</div>

---

[![Language](https://img.shields.io/badge/Language-Python-green?style)](https://github.com/s0v1x)
[![framework](https://img.shields.io/badge/Framework-FastAPI-blue?style)](https://fastapi.tiangolo.com/)
[![framework](https://img.shields.io/badge/Framework-Dash-blue?style)](https://dash.plotly.com/)
[![Star Badge](https://img.shields.io/static/v1?label=%F0%9F%8C%9F&message=If%20Useful&style=style=flatcolor=BC4E99)](https://github.com/s0v1x/EULERA)
[![Heroku](https://pyheroku-badge.herokuapp.com/?app=eulera&style=flat)](https://eulera.herokuapp.com)
[![GitHub license](https://img.shields.io/github/license/s0v1x/EULERA)](https://github.com/s0v1x/EULERA/blob/master/LICENSE)


# EULERA in simple words

## What is EULERA ?

EULERA is a Machine Learning-based web app, dedicated for Stock Market Prediction. The app gives a precise forecasting of the stock price of the following day for any given stock under NASDAQ stock exchange.

That means you get to choose your favorite company, and get in return the forecast for its stock price for the following day.

Eulera uses AI based algorithmic forecasting solutions for the capital markets to uncover the best investment opportunities.

Beside predicitons, EULERA gives the opportunity to visualize technical indicators, financial ratios (for different time ranges), and also some metrics that showcases the performance of the company chosen. In addition, the latest news related to the company of choice are gathered in one place.

## How is this all possible ?

EULERA app is made from scratch using Dash framework, FastAPI, and the technical skills of the authors.

## Project using 

### Setup environment

You should create a virtual environment and activate it:

```bash
python -m venv venv/
```

```bash
source venv/bin/activate
```

And then install the development dependencies:

```bash
pip install -r requirements.txt
```
or using ```pipenv``` in the root of the folder:


```bash
pipenv install
```
### Run Dash

To run the app 

```bash
py app.py
```

## Important files description

**app.py**: As the name indicates, it contains the code for creating EULERA

**charts.py**: Creation of charts of the App using Plotly.

**technical_indicators.py** computes different technical and financial indicators (RSI, SMA, EMA, TSI, ...etc) for the company of choice.

## License 

This project is licensed under the terms of the [MIT License](https://github.com/s0v1x/EULERA/blob/master/LICENSE).
