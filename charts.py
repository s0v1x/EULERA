import plotly.graph_objs as go
from technical_indicators import *
from utilities import *
from yahooquery import Ticker
import numpy as np
import pandas as pd
from plotly.subplots import make_subplots
from pytz import timezone
from datetime import datetime
from yahoo_fin import stock_info as si


def ohlc_trace(df):
    return go.Ohlc(
        x=df.date,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="OHLC",
        line=dict(width=1),
        customdata=df.vol,
        hoverinfo="x+y+text",
    )


def candle_trace(df):
    return go.Candlestick(
        x=df.date,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candlestick",
        line=dict(width=1),
        hoverinfo="x+y+text",
    )


def line_trace(df):

    return go.Scatter(
        x=df.date,
        y=df["close"],
        mode="lines",
        name="Prices",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        customdata=np.stack(
            (df["open"], df["high"], df["low"], df["close"], df["vol"], df["date"])
        ).T,
        hovertemplate="<b>%{customdata[5]|%B %d, %Y}</b><br>Open: %{customdata[0]:.3f} <br>High: %{customdata[1]:.3f} <br>Low: %{customdata[2]:.3f} <br>Close: %{customdata[3]:.3f} <br>Volume: %{customdata[4]} <extra></extra>",
    )


dic_studies = {
    "RSI_trace": RSI_trace,
    "ROC_trace": ROC_trace,
    "MACD_trace": MACD_trace,
    "OBV_trace": OBV_trace,
    "TSI_trace": TSI_trace,
    "ATR_trace": ATR_trace,
    "CCI_trace": CCI_trace,
    "EMA_trace": EMA_trace,
    "SMA_trace": SMA_trace,
    "BOLLINGER_trace": BOLLINGER_trace,
}
dic_styles = {
    "ohlc_trace": ohlc_trace,
    "candle_trace": candle_trace,
    "line_trace": line_trace,
}


def main_chart(company, list_charts, duration, styles):

    data = Ticker(company).history(period=duration, interval="1d", adj_timezone=True)
    data = data.loc[company]
    data["vol"] = data.volume.apply(human_format)
    data["date"] = pd.to_datetime(data.index).strftime("%Y-%m-%d")
    data.index = np.arange(0, len(data))

    appended_studies = ["SMA_trace", "EMA_trace", "BOLLINGER_trace"]
    tmp_studies = []
    for idx, i in enumerate(list_charts):
        if i in appended_studies:
            tmp_studies.append(i)

    final_charts = [chart for chart in list_charts if chart not in tmp_studies]

    fig = make_subplots(
        rows=len(final_charts) + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
    )

    fig.add_trace(dic_styles[styles](data), row=1, col=1)

    for i in tmp_studies:
        if i == "BOLLINGER_trace":
            dic_studies[i](data, fig)
        else:
            fig.add_trace(dic_studies[i](data), row=1, col=1)

    for idx, i in enumerate(final_charts):
        fig.add_trace(dic_studies[i](data), row=idx + 2, col=1)

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin={"t": 30, "l": 20, "b": 25, "r": 10},
        autosize=True,
        paper_bgcolor="#22252b",
        plot_bgcolor="#22252b",
        height=480,
        hovermode="x",  # x
        hoverlabel={
            "align": "auto",
            "font": {"color": "#ededed", "size": 9},
        },
        legend={
            "font": {"color": "#b2b2b2", "size": 9},
            "itemsizing": "trace",
            "orientation": "v",
        },
    )

    fig.update_traces(xaxis="x")

    fig.update_xaxes(
        gridcolor="#3E3F40",
        gridwidth=1,
        zeroline=False,
        tickfont={
            "color": "#b2b2b2",
            "size": 8,
        },
        showspikes=True,
        spikecolor="#6c757d",
        spikemode="across+marker",
        spikesnap="hovered data",
        spikethickness=1,
        spikedash="dot",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#3E3F40",
        gridwidth=1,
        zeroline=False,
        tickfont={
            "color": "#b2b2b2",
            "size": 8,
        },
        showspikes=True,
        spikecolor="#6c757d",
        spikemode="across+marker",
        spikesnap="hovered data",
        spikethickness=1,
        spikedash="dot",
    )
    return fig


def rt_chart(company):

    data = Ticker(company).history(period="1d", interval="1m", adj_timezone=False)
    if len(data) > 3:
        data = data.loc[company].asfreq("60s", method="ffill")
    else:
        data = data.loc[company]
    data["date"] = pd.to_datetime(data.index).strftime("%Y-%m-%d %H:%M:%S")
    data.index = np.arange(0, len(data))

    prev_close = Ticker(company).quotes[company]["regularMarketPreviousClose"]
    rt_close = si.get_live_price(company)
    change = rt_close - prev_close
    if change > 0:
        line_color = "green"
    else:
        line_color = "red"

    dt = datetime.now(timezone("America/New_York"))
    dt = dt.replace(tzinfo=None)
    dt = dt.replace(hour=20, minute=1)
    r_time = datetime.strptime(dt.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    intrv = r_time - datetime.strptime(data.date.iloc[0], "%Y-%m-%d %H:%M:%S")
    if intrv.days >= 1:
        intrv = data.date.iloc[-1]
    else:
        intrv = dt
    fig = go.Figure(
        data=[
            go.Scatter(
                x=data.date,
                y=data["close"],
                mode="lines",
                name="Line",
                customdata=np.stack(
                    (
                        data["open"],
                        data["high"],
                        data["low"],
                        data["close"],
                        data["volume"],
                    )
                ).T,
                line=dict(
                    width=1, color=line_color, shape="linear", dash="solid", smoothing=0
                ),
                hovertemplate="<b>%{x|%m/%d %H:%M}</b><br>Open: %{customdata[0]:.3f} <br>High: %{customdata[1]:.3f} <br>Low: %{customdata[2]:.3f} <br>Close: %{customdata[3]:.3f} <br>Volume: %{customdata[4]}<extra></extra>",
            )
        ]
    )

    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=rt_close,
            delta={
                "reference": prev_close,
                "valueformat": ".2f",
                "position": "bottom",
                "font": {
                    "color": "#b2b2b2",
                    "size": 25,
                    "family": "Trebuchet MS, sans-serif",
                },
            },
            title={
                "text": "Close Price",
                "align": "center",
                "font": {
                    "color": "#797979",
                    "size": 20,
                    "family": "Trebuchet MS, sans-serif",
                },
            },
            align="center",
            number={
                "valueformat": ".2f",
                "font": {
                    "color": "#797979",
                    "size": 40,
                    "family": "Trebuchet MS, sans-serif",
                },
            },
        )
    )

    fig.update_layout(
        margin={"t": 30, "l": 30, "b": 30, "r": 20},
        autosize=True,
        paper_bgcolor="#22252b",
        plot_bgcolor="#22252b",
        hoverlabel={
            "align": "auto",
            "font": {"color": "#ededed", "size": 8},
        },
    )
    fig.update_xaxes(
        range=[data.date.iloc[0], intrv],
        gridcolor="#3E3F40",
        gridwidth=1,
        tickfont={
            "color": "#b2b2b2",
            "size": 8,
        },
        showspikes=True,
        spikecolor="#6c757d",
        spikemode="across+marker",
        spikesnap="hovered data",
        spikethickness=1,
        spikedash="dot",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#3E3F40",
        gridwidth=1,
        tickfont={
            "color": "#b2b2b2",
            "size": 8,
        },
        showspikes=True,
        spikecolor="#6c757d",
        spikemode="across+marker",
        spikesnap="hovered data",
        spikethickness=1,
        spikedash="dot",
    )

    return fig

def model_chart(company, hist):
    status = si.get_market_status()
    data = Ticker(company).history(period="ytd", interval="1d", adj_timezone=False)
    data = data.loc[company]
    if status == 'REGULAR':
        data = data.iloc[len(data) - len(hist) +1 : -1]
    else:
        data = data.iloc[len(data) - len(hist) +1 : ]
    data["date"] = pd.to_datetime(data.index).strftime("%Y-%m-%d %H:%M:%S")
    data.index = np.arange(0, len(data))

    fig = go.Figure(
        data=[
            go.Scatter(
                x=data.date,
                y=data.close,
                mode="lines+markers",
                name="MP",
                hovertemplate="MP: %{y:.4f}",
                line=dict(width=1, shape="linear", dash="solid", smoothing=0),
            ),
        ]
    )
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist.f_price,
            mode="lines+markers",
            name="FP",
            hovertemplate="MP: %{y:.4f}",
            line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist.min_conf,
            mode="lines",
            marker=dict(color="#444"),
            line=dict(
                width=1, shape="spline", dash="longdash", smoothing=0.5, color="gray"
            ),
            showlegend=False,
            hovertemplate="Min Confidence: %{y:.4f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=hist.index,
            y=hist.max_conf,
            marker=dict(color="#444"),
            line=dict(
                width=1, shape="spline", dash="longdash", smoothing=0.5, color="gray"
            ),
            mode="lines",
            fill="tonexty",
            showlegend=False,
            hovertemplate="Max Confidence: %{y:.4f}<extra></extra>",
        )
    )

    fig.update_layout(
        width=500,
        height=300,
        margin={"t": 10, "l": 10, "b": 10, "r": 10},
        autosize=True,
        paper_bgcolor="#1d1e22",
        plot_bgcolor="#1d1e22",
        hovermode="x",
        hoverlabel={
            "align": "auto",
            "font": {"color": "#ededed", "size": 8},
        },
        legend={
            "font": {"color": "#b2b2b2", "size": 8},
            "itemsizing": "trace",
            "orientation": "v",
        },
    )

    fig.update_traces(xaxis="x")

    fig.update_xaxes(
        gridcolor="#3E3F40",
        gridwidth=1,
        zerolinecolor="#3E3F40",
        zerolinewidth=1,
        tickfont={
            "color": "#b2b2b2",
            "size": 8,
        },
        showspikes=True,
        spikecolor="#6c757d",
        spikemode="across+marker",
        spikesnap="hovered data",
        spikethickness=1,
        spikedash="dot",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#3E3F40",
        gridwidth=1,
        zerolinecolor="#3E3F40",
        zerolinewidth=1.5,
        tickfont={
            "color": "#b2b2b2",
            "size": 8,
        },
        showspikes=True,
        spikecolor="#6c757d",
        spikemode="across+marker",
        spikesnap="hovered data",
        spikethickness=1,
        spikedash="dot",
    )

    return fig


def indc_price(price, company):
    status = si.get_market_status()
    data = Ticker(company).history(period="1d", interval="1d", adj_timezone=False)
    data = data.loc[company]
    dd = datetime.strptime(str(data.index[-1]), "%Y-%m-%d")
    td = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    if td > dd:
        prev = Ticker('AAPL').quotes['AAPL']["regularMarketPreviousClose"]
    else:
        prev = data.iloc[-1].close
    print(prev)
    print(price, "-------------------")
    print(type(price), "-------------------")
    fig = go.Figure(
        data=[
            go.Indicator(
                mode="number+delta",
                value=price,
                delta={
                    "reference": prev,
                    "valueformat": ".2f",
                    "position": "bottom",
                    "font": {
                        "color": "#b2b2b2",
                        "size": 15,
                        "family": "Trebuchet MS, sans-serif",
                    },
                },
                align="center",
                number={
                    "valueformat": ".3f",
                    "font": {
                        "color": "#797979",
                        "size": 30,
                        "family": "Trebuchet MS, sans-serif",
                    },
                },
            )
        ]
    )

    fig.update_layout(
        width=120,
        height=80,
        margin={"t": 30, "l": 30, "b": 30, "r": 20},
        autosize=True,
        paper_bgcolor="#1d1e22",
        plot_bgcolor="#1d1e22",
        hoverlabel={
            "align": "auto",
            "font": {"color": "#ededed", "size": 8},
        },
    )

    return fig
