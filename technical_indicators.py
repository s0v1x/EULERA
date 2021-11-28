from ta import momentum, trend, volatility, volume
import plotly.graph_objs as go


def RSI_trace(df, window=14):
    RSI_serie = momentum.rsi(df.close, window)
    trace = go.Scatter(
        x=df.date,
        y=RSI_serie,
        mode="lines",
        showlegend=True,
        name="RSI(14days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="RSI: %{y:.4f}<extra></extra>",
    )
    return trace


def ROC_trace(df, window=12):
    ROC_serie = momentum.roc(df.close, window)
    trace = go.Scatter(
        x=df.date,
        y=ROC_serie,
        mode="lines",
        showlegend=True,
        name="ROC(12days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="ROC: %{y:.4f}<extra></extra>",
    )
    return trace


def MACD_trace(df, window_s=26, window_f=12):
    MACD_serie = trend.macd(df.close, window_s, window_f)
    trace = go.Scatter(
        x=df.date,
        y=MACD_serie,
        mode="lines",
        showlegend=True,
        name="MACD(12days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="MACD: %{y:.4f}<extra></extra>",
    )
    return trace


def BOLLINGER_trace(df, fig, window=20, window_dev=2):
    BOLLINGER = volatility.BollingerBands(df.close, window, window_dev)
    hband = BOLLINGER.bollinger_hband()
    lband = BOLLINGER.bollinger_lband()
    mband = BOLLINGER.bollinger_mavg()
    trace_hband = go.Scatter(
        x=df.date,
        y=hband,
        mode="lines",
        showlegend=False,
        name="Bollinger High Band",
        line=dict(width=1, shape="linear", dash="longdash", smoothing=0, color="gray"),
        hovertemplate="High Band: %{y:.4f}<extra></extra>",
    )
    trace_lband = go.Scatter(
        x=df.date,
        y=lband,
        mode="lines",
        showlegend=False,
        name="Bollinger Low Band",
        line=dict(width=1, shape="linear", dash="longdash", smoothing=0, color="gray"),
        hovertemplate="Low Band: %{y:.4f}<extra></extra>",
        fill="tonexty",
    )
    trace_mband = go.Scatter(
        x=df.date,
        y=mband,
        mode="lines",
        showlegend=True,
        name="Bollinger Middle Band",
        line=dict(width=1, shape="linear", dash="dashdot", smoothing=0, color="gray"),
        hovertemplate="Middle Band: %{y:.4f}<extra></extra>",
    )
    fig.add_trace(trace_hband, row=1, col=1)
    fig.add_trace(trace_lband, row=1, col=1)
    fig.add_trace(trace_mband, row=1, col=1)

    return fig


def OBV_trace(df):
    OBV_serie = volume.on_balance_volume(df.close, df.volume)
    trace = go.Scatter(
        x=df.date,
        y=OBV_serie,
        mode="lines",
        showlegend=True,
        name="OBV",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="OBV: %{y:.4f}<extra></extra>",
    )
    return trace


def TSI_trace(df, window_s=25, window_f=13):
    TSI_serie = momentum.tsi(df.high, window_s, window_f)
    trace = go.Scatter(
        x=df.date,
        y=TSI_serie,
        mode="lines",
        showlegend=True,
        name="TSI",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="TSI: %{y:.4f}<extra></extra>",
    )
    return trace


def ATR_trace(df, window=14):
    ATR_serie = volatility.average_true_range(df.high, df.low, df.close, window)
    trace = go.Scatter(
        x=df.date,
        y=ATR_serie,
        mode="lines",
        showlegend=True,
        name="ATR(14days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="ATR: %{y:.4f}<extra></extra>",
    )
    return trace


def CCI_trace(df, window=14, constant=0.015):
    CCI_serie = trend.cci(df.high, df.low, df.close, window, constant)
    trace = go.Scatter(
        x=df.date,
        y=CCI_serie,
        mode="lines",
        showlegend=True,
        name="CCI(14days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="CCI: %{y:.4f}<extra></extra>",
    )
    return trace


def EMA_trace(df, window=12):
    EMA_serie = trend.ema_indicator(df.close, window)
    trace = go.Scatter(
        x=df.date,
        y=EMA_serie,
        mode="lines",
        showlegend=True,
        name="EMA(12days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="EMA: %{y:.4f}<extra></extra>",
    )
    return trace


def SMA_trace(df, window=12):
    SMA_serie = trend.sma_indicator(df.close, window)
    trace = go.Scatter(
        x=df.date,
        y=SMA_serie,
        mode="lines",
        showlegend=True,
        name="SMA(12days)",
        line=dict(width=1, shape="linear", dash="solid", smoothing=0),
        hovertemplate="SMA: %{y:.4f}<extra></extra>",
    )
    return trace
