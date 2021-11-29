import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from pytz import timezone
from yahoo_fin import news
from yahoo_fin import stock_info as si
from yahooquery import Ticker
from datetime import datetime
import dash_daq as daq
from dash.exceptions import PreventUpdate
from bs4 import BeautifulSoup
import json
from utilities import *
from charts import *


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://pro.fontawesome.com/releases/v5.10.0/css/all.css",
    ],
    external_scripts=["https://pro.fontawesome.com/releases/v5.10.0/js/all.js"],
    update_title=None,
)
app.title = "Eulera Dashboard"
server = app.server


conf_graph = {
    "scrollZoom": True,
    "displaylogo": False,
    "displayModeBar": "hover",
    "responsive": True,
    "modeBarButtonsToRemove": ["zoom", "toImage", "resetScale", "select2d", "lasso2d"],
    "modeBarButtonsToAdd": ["drawline", "eraseshape"],
}


def update_news(company):
    list_news = news.get_yf_rss(company)
    df = pd.DataFrame(list_news)[["title", "link"]]
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-news", children="Headlines"),
            html.P(
                className="p-news float-right",
                children="Last update : " + datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=df.iloc[i]["title"],
                                        href=df.iloc[i]["link"],
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(min(len(df), max_rows))
                ],
            ),
            html.Span(
                [
                    "*the news are from ",
                    html.A(
                        "Yahoo Finance",
                        href="https://finance.yahoo.com/",
                    ),
                ],
                className="note-ratios",
            ),
        ]
    )


def get_top_bar_cell(cellTitle, cellValue):
    if cellValue is None:
        cellValue = "--"
    else:
        cellValue = "%.4f" % cellValue
    return html.Div(
        className="two-col",
        children=[
            html.P(
                className="p-top-bar",
                children=[cellTitle, html.Span("*", className="star")],
            ),
            html.P(id=cellTitle, className="display-none", children=cellValue),
            html.P(children=cellValue, className="f-ratios"),
        ],
    )


def get_top_bar(company):
    headers = {"User-Agent": rand_agent("assets/user-agents.txt")}
    url = (
        "https://financialmodelingprep.com/api/v3/ratios-ttm/"
        + company
        + "?apikey=fdcb26b779c637247be2e6d28d760cee"
    )
    ratios_requests = requests.get(url, headers=headers)
    json_data = ratios_requests.json()[0]

    return [
        get_top_bar_cell("Quick Ratio", json_data["quickRatioTTM"]),
        get_top_bar_cell("Price to earnings", json_data["priceEarningsRatioTTM"]),
        get_top_bar_cell("Debt-to-equity", json_data["debtEquityRatioTTM"]),
        get_top_bar_cell("Gross Margin", json_data["grossProfitMarginTTM"]),
        get_top_bar_cell("Net Profit Margin", json_data["netProfitMarginTTM"]),
        get_top_bar_cell("Inventory Turnover", json_data["inventoryTurnoverTTM"]),
    ]


def market_status():
    try:
        dt = datetime.now(timezone("America/New_York"))
        dt = dt.replace(tzinfo=None)
        r_time = datetime.strptime(dt.strftime("%H:%M:%S"), "%H:%M:%S")
        open_time = datetime.strptime("09:31:00", "%H:%M:%S")
        close_time = datetime.strptime("16:01:00", "%H:%M:%S")
        stat = si.get_market_status()

        if stat == "CLOSED":
            return html.P(
                ["Market Status : Closed"],
                className="ind-mark ind-anim",
                style={"color": "red", "margin-bottom": "3rem"},
            )

        elif stat == "PRE":
            intrv = open_time - r_time
            stat = ["Market Status : Pre-Market"]
            if (intrv.seconds // 3600) <= 2:
                stat.append(
                    html.P(["markets open in ", str_time(intrv)], className="h-status")
                )
            return html.P(
                stat, className="ind-mark ind-anim", style={"color": "yellow"}
            )

        elif stat == "POST" or stat == "POSTPOST":
            return html.P(
                ["Market Status : Post-Market"],
                className="ind-mark ind-anim",
                style={"color": "yellow", "margin-bottom": "3rem"},
            )

        else:
            intrv = close_time - r_time
            stat = ["Market Status : Open"]
            if (intrv.seconds // 3600) <= 2:
                stat.append(
                    html.P(["markets close in ", str_time(intrv)], className="h-status")
                )
            return html.P(stat, className="ind-mark ind-anim", style={"color": "green"})

    except Exception as e:
        return html.P(
            ["Market Status : --"],
            className="ind-mark ind-anim",
            style={"color": "yellow"},
        )


def get_company_infos(company):
    info = [
        {
            "logo": "logos/apple.png",
            "title": "Apple, Inc.",
            "coord": [
                "One Apple Park Way, Cupertino, CA 95014, United States",
                html.Br(),
                "408-996-1010",
                html.Br(),
                html.A("www.apple.com", href="http://www.apple.com"),
            ],
            "summary": "Apple, Inc. engages in the design, manufacture, and sale of smartphones, personal computers, tablets, wearables and accessories, and other variety of related services. It operates through the following geographical segments: Americas, Europe, Greater China, Japan, and Rest of Asia Pacific. The Americas segment includes North and South America. The Europe segment consists of European countries, as well as India, the Middle East, and Africa. The Greater China segment comprises of China, Hong Kong, and Taiwan. The Rest of Asia Pacific segment includes Australia and Asian countries. Its products and services include iPhone, Mac, iPad, AirPods, Apple TV, Apple Watch, Beats products, Apple Care, iCloud, digital content stores, streaming, and licensing services.",
        },
        {
            "logo": "logos/tesla.png",
            "title": "Tesla, Inc.",
            "coord": [
                "3500 Deer Creek Road, Palo Alto, CA 94304, United States",
                html.Br(),
                "650-681-5000",
                html.Br(),
                html.A("www.tesla.com", href="http://www.tesla.com"),
            ],
            "summary": "Tesla, Inc. engages in the design, development, manufacture, and sale of fully electric vehicles, energy generation and storage systems. It also provides vehicle service centers, supercharger station, and self-driving capability. The company operates through the following segments: Automotive and Energy Generation and Storage. The Automotive segment includes the design, development, manufacture and sale of electric vehicles. The Energy Generation and Storage segment includes the design, manufacture, installation, sale, and lease of stationary energy storage products and solar energy systems, and sale of electricity generated by its solar energy systems to customers. It develops energy storage products for use in homes, commercial facilities and utility sites.",
        },
        {
            "logo": "logos/fb.png",
            "title": "Facebook, Inc.",
            "coord": [
                "1601 Willow Road, Menlo Park, CA 94025, United States",
                html.Br(),
                "650-543-4800",
                html.Br(),
                html.A("investor.fb.com", href="http://investor.fb.com"),
            ],
            "summary": "Facebook, Inc. operates as a social networking company worldwide. The company engages in the development of social media applications for people to connect through mobile devices, personal computers, and other surfaces. It enables users to share opinions, ideas, photos, videos, and other activities online. The firm's products include Facebook, Instagram, Messenger, WhatsApp, and Oculus. The company was founded by Mark Elliot Zuckerberg, Dustin Moskovitz, Chris R. Hughes, Andrew McCollum, and Eduardo P. Saverin on February 4, 2004 and is headquartered in Menlo Park, CA.",
        },
        {
            "logo": "logos/amzn.png",
            "title": "Amazon, Inc.",
            "coord": [
                "410 Terry Avenue North, Seattle, WA 98109-5210, United States",
                html.Br(),
                "206-266-1000",
                html.Br(),
                html.A("www.amazon.com", href="http://www.amazon.com"),
            ],
            "summary": "Amazon.com, Inc. engages in the provision of online retail shopping services. It operates through the following business segments: North America, International, and Amazon Web Services (AWS). The North America segment includes retail sales of consumer products and subscriptions through North America-focused websites such as www.amazon.com and www.amazon.ca. The International segment offers retail sales of consumer products and subscriptions through internationally-focused websites. The Amazon Web Services segment involves in the global sales of compute, storage, database, and AWS service offerings for start-ups, enterprises, government agencies, and academic institutions. The company was founded by Jeffrey P. Bezos in July 1994 and is headquartered in Seattle, WA.",
        },
        {
            "logo": "logos/goog.png",
            "title": "Google, Inc.",
            "coord": [
                "1600 Amphitheatre Parkway, Mountain View, CA 94043, United States",
                html.Br(),
                "650-253-0000",
                html.Br(),
                html.A("http://www.abc.xyz", href="http://www.abc.xyz"),
            ],
            "summary": "Alphabet, Inc. is a holding company, which engages in the business of acquisition and operation of different companies. It operates through the Google and Other Bets segments. The Google segment includes its main Internet products such as ads, Android, Chrome, hardware, Google Cloud, Google Maps, Google Play, Search, and YouTube. The Other Bets segment consists of businesses such as Access, Calico, CapitalG, GV, Verily, Waymo, and X. The company was founded by Lawrence E. Page and Sergey Mikhaylovich Brin on October 2, 2015 and is headquartered in Mountain View, CA.",
        },
        {
            "logo": "logos/tw.png",
            "title": "Twitter, Inc.",
            "coord": [
                "1355 Market Street, Suite 900, San Francisco, CA 94103, United States",
                html.Br(),
                "415-222-9670",
                html.Br(),
                html.A("http://www.twitter.com", href="http://www.twitter.com"),
            ],
            "summary": "Twitter, Inc. is a global platform for public self-expression and conversation in real time. It provides a network that connects users to people, information, ideas, opinions and news. The company's services include live commentary, live connections and live conversations. Its application provides social networking services and micro-blogging services through mobile devices and the Internet. The company can also be used as a marketing tool for businesses. Its products and services include Promoted Tweets, Promoted Accounts and Promoted Trends. Twitter was founded by Jack Dorsey, Christopher Isaac Stone, Noah E. Glass, Jeremy LaTrasse and Evan Williams on March 21, 2006 and is headquartered in San Francisco, CA.",
        },
        {
            "logo": "logos/nflx.png",
            "title": "Netflix, Inc.",
            "coord": [
                "100 Winchester Circle, Los Gatos, CA 95032, United States",
                html.Br(),
                "408-540-3700",
                html.Br(),
                html.A("http://www.netflix.com", href="http://www.netflix.com"),
            ],
            "summary": "Netflix, Inc. operates as a streaming entertainment service company. The firm provides subscription service streaming movies and television episodes over the Internet and sending DVDs by mail. It operates through the following segments: Domestic Streaming, International Streaming and Domestic DVD. The Domestic Streaming segment derives revenues from monthly membership fees for services consisting of streaming content to its members in the United States. The International Streaming segment includes fees from members outside the United States. The Domestic DVD segment covers revenues from services consisting of DVD-by-mail. The company was founded by Marc Randolph and Wilmot Reed Hastings Jr. on August 29, 1997 and is headquartered in Los Gatos, CA.",
        },
    ]
    info_dict = {
        "AAPL": info[0],
        "TSLA": info[1],
        "FB": info[2],
        "AMZN": info[3],
        "GOOG": info[4],
        "TWTR": info[5],
        "NFLX": info[6],
    }
    return [
        html.Div(
            children=html.Img(
                className="lg", src=app.get_asset_url(info_dict[company]["logo"])
            ),
            className="fff",
        ),
        html.Div(
            children=[
                html.H2(info_dict[company]["title"]),
                html.P(
                    info_dict[company]["coord"],
                    className="p1",
                ),
                html.P(
                    info_dict[company]["summary"],
                    className="p2",
                ),
            ],
            className="sss",
        ),
    ]


f_elements = [
    "regularMarketPreviousClose",
    "regularMarketOpen",
    "regularMarketVolume",
    "averageDailyVolume3Month",
    "regularMarketDayRange",
    "ask",
    "askSize",
    "bid",
    "bidSize",
    "marketCap",
    "trailingPE",
    "epsTrailingTwelveMonths",
    "fiftyTwoWeekLow",
    "fiftyTwoWeekHigh",
    "earningsTimestampStart",
    "earningsTimestampEnd",
]


def get_finance_infos(company):
    data_infos = Ticker(company).quotes[company]
    for e in f_elements:
        if e not in data_infos.keys():
            data_infos[e] = "--"
    if not isinstance(data_infos["earningsTimestampStart"], str):
        data_infos["earningsTimestampStart"] = datetime.fromtimestamp(
            int(data_infos["earningsTimestampStart"])
        ).strftime("%d %b %Y")
        data_infos["earningsTimestampEnd"] = datetime.fromtimestamp(
            int(data_infos["earningsTimestampEnd"])
        ).strftime("%d %b %Y")
    return [
        html.Div(
            children=[
                html.P(
                    [
                        "Previous Close",
                        html.Span(
                            data_infos["regularMarketPreviousClose"],
                            className="price-inf-num",
                            id="pc",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "Open",
                        html.Span(
                            data_infos["regularMarketOpen"],
                            className="price-inf-num",
                            id="op",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "Volume",
                        html.Span(
                            "{:,}".format(int(data_infos["regularMarketVolume"])),
                            className="price-inf-num",
                            id="vl",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "Avg. Volume",
                        html.Span(
                            "{:,}".format(int(data_infos["averageDailyVolume3Month"])),
                            className="price-inf-num",
                            id="av",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "Day's Range",
                        html.Span(
                            data_infos["regularMarketDayRange"],
                            className="price-inf-num",
                            id="dr",
                        ),
                    ],
                    className="price-inf",
                ),
            ],
            className="ff",
        ),
        html.Div(
            children=[
                html.P("Ask", className="ask"),
                html.P(
                    [
                        data_infos["ask"],
                        html.Span(
                            ["x", int(data_infos["askSize"]) * 100],
                            className="ask-bid-size",
                        ),
                    ],
                    className="ask-bid-num",
                ),
                html.P("Bid", className="bid"),
                html.P(
                    [
                        data_infos["bid"],
                        html.Span(
                            ["x", int(data_infos["bidSize"]) * 100],
                            className="ask-bid-size",
                        ),
                    ],
                    className="ask-bid-num",
                ),
            ],
            className="ss",
            id="ask_bid",
        ),
        html.Div(
            children=[
                html.P(
                    [
                        "Market Cap",
                        html.Span(
                            human_format(int(data_infos["marketCap"])),
                            className="price-inf-num",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "PE Ratio (TTM)",
                        html.Span(
                            data_infos["trailingPE"],
                            className="price-inf-num",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "EPS (TTM)",
                        html.Span(
                            data_infos["epsTrailingTwelveMonths"],
                            className="price-inf-num",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "52 Week Range",
                        html.Span(
                            [
                                data_infos["fiftyTwoWeekLow"],
                                " - ",
                                data_infos["fiftyTwoWeekHigh"],
                            ],
                            className="price-inf-num",
                        ),
                    ],
                    className="price-inf",
                ),
                html.P(
                    [
                        "Earnings Date",
                        html.Span(
                            [
                                data_infos["earningsTimestampStart"],
                                " - ",
                                data_infos["earningsTimestampEnd"],
                            ],
                            className="price-inf-num",
                        ),
                    ],
                    className="price-inf",
                ),
            ],
            className="tt",
        ),
    ]


def get_esg_score(company):
    try:
        esg_data = Ticker(company).esg_scores[company]
        return [
            html.Div(
                children=html.P(
                    [
                        "{:.1f}".format(esg_data["totalEsg"]),
                        html.Span(" | ", className="percentile"),
                        html.Span(
                            ["{:.0f}".format(esg_data["percentile"]), "th percentile"],
                            style=dict(fontSize="1.2rem"),
                        ),
                    ],
                    className="esg-score",
                ),
            ),
            html.Div(
                className="threescores",
                children=[
                    html.Div(
                        children=[
                            html.P(
                                "Environment Risk Score", className="other-scores-p"
                            ),
                            html.P(
                                "{:.1f}".format(esg_data["environmentScore"]),
                                style=dict(fontWeight="200"),
                            ),
                        ],
                        className="other-scores",
                    ),
                    html.Div(className="other-scores-deco"),
                    html.Div(
                        children=[
                            html.P("Social Risk Score", className="other-scores-p"),
                            html.P(
                                "{:.1f}".format(esg_data["socialScore"]),
                                style=dict(fontWeight="200"),
                            ),
                        ],
                        className="other-scores",
                    ),
                    html.Div(className="other-scores-deco"),
                    html.Div(
                        children=[
                            html.P("Governance Risk Score", className="other-scores-p"),
                            html.P(
                                "{:.1f}".format(esg_data["governanceScore"]),
                                style=dict(fontWeight="200"),
                            ),
                        ],
                        className="other-scores",
                    ),
                ],
                style={
                    "display": "flex",
                    "flex-direction": "row",
                    "justify-content": "space-between",
                },
            ),
        ]
    except Exception:
        return html.P("feature not available", className="f-notav2")


def get_currencies():
    try:
        data = si.get_currencies()
        items = []
        for i in range(4):
            d = data[i * 6 : 6 * (i + 1)]
            d.reset_index(inplace=True)
            alt = []
            for j in range(6):
                alt.append(str(d["Name"][j]) + " " + str(d["% Change"][j]))
            items.append({"key": str(i + 1), "alt": "  —  ".join(alt)})
        return items
    except Exception:
        return [
            {"key": "1", "alt": "feature not available"},
            {"key": "2", "alt": "feature not available"},
            {"key": "3", "alt": "feature not available"},
        ]


def get_recomm_rating(company):
    try:
        headers = {"User-Agent": rand_agent("assets/user-agents.txt")}
        url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + company
        rating_requests = requests.get(url, headers=headers)
        str_rating = rating_requests.json()["quoteResponse"]["result"][0][
            "averageAnalystRating"
        ]
        return daq.Slider(
            min=1,
            max=5,
            value=float(str_rating.split(" - ")[0]),
            step=0.1,
            marks={
                1: {"label": "Strong Buy", "style": {"color": "#008f88"}},
                2: {"label": "Buy", "style": {"color": "#00c073"}},
                3: {"label": "Hold", "style": {"color": "#ffdc48"}},
                4: {"label": "Under-perform", "style": {"color": "#ffa33e"}},
                5: {"label": "Sell", "style": {"color": "#ff333a"}},
            },
            labelPosition="top",
            handleLabel={
                "showCurrentValue": True,
                "label": " ",
                "color": "red",
                "style": {"fontSize": "1rem"},
            },
            included=False,
            disabled=True,
            size=275,
        )
    except KeyError:
        return html.P("feature not available", className="f-notav1")


def get_pre_post_post(company):
    try:
        status = si.get_market_status()
        url = "https://finance.yahoo.com/quote/" + company + "?p=" + company
        headers = {"User-Agent": rand_agent("assets/user-agents.txt")}
        resp = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(resp.text, "lxml")
        if status == "PRE" or status == "POSTPOST" or status == "POST":

            div = soup.find("span", {"class": "C($primaryColor) Fz(24px) Fw(b)"})
            price = float(div.text.replace(",", ""))
            prev = Ticker(company).history(
                period="1d", interval="1d", adj_timezone=False
            )
            prev = prev.loc[company]
            prev = prev.iloc[-1].close
        else:
            div = soup.find(
                "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}
            )
            price = float(div.text.replace(",", ""))
            prev = Ticker(company).quotes[company]["regularMarketPreviousClose"]
    except AttributeError:
        price = None
        prev = None

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
                        "color": "#acacad",
                        "size": 25,
                        "family": "Trebuchet MS, sans-serif",
                    },
                },
            )
        ]
    )
    fig.update_layout(
        width=100,
        height=60,
        margin={"t": 10, "l": 10, "b": 10, "r": 10},
        autosize=True,
        paper_bgcolor="#22252b",
        plot_bgcolor="#22252b",
        hoverlabel={
            "align": "auto",
            "font": {"color": "#ededed", "size": 8},
        },
    )
    return dcc.Graph(
        id="pre_post_price",
        style={"display": "inline-flex"},
        figure=fig,
        config={
            "scrollZoom": True,
            "displaylogo": False,
            "displayModeBar": False,
            "responsive": True,
        },
    )


df = pd.read_csv("history.csv", index_col=0)

app.layout = html.Div(
    className="rrow",
    children=[
        dcc.Interval(id="i_news", interval=300000),  # 5min
        dcc.Interval(id="i_price_infos", interval=30000),  # 30sec
        dcc.Interval(id="i_stat_curren", interval=20000),  # 20sec
        dcc.Interval(id="i_rtchart", interval=40000),  # 40s
        dcc.Interval(id="i_mainchart", interval=400 * 100000),  # 11.11h
        dcc.Interval(id="i_update_model", interval=1000),  # 1s
        dcc.Interval(id="i_pre_post", interval=3000),  # 5s
        html.Div(
            className="three columns div-left-panel",
            children=[
                html.Div(
                    className="div-info",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src=app.get_asset_url("logo.png"),
                            ),
                            href="/",
                        ),
                        html.P(
                            "Eulera Dashboard is an easy and intuitive way to get a quick feel of what’s happening on the world’s market",
                            style={
                                "font-size": "1rem",
                                "text-align": "justify",
                                "margin": "5%",
                            },
                        ),
                        html.Div(
                            [
                                html.Div(
                                    children=[
                                        html.Div(
                                            html.A("Contact Us", href="#"),
                                            id="open",
                                            n_clicks=0,
                                            className="link",
                                        ),
                                        html.Div(html.Span("|")),
                                        html.Div(
                                            html.A(
                                                "Source Code",
                                                href="https://github.com/s0v1x/EULERA",
                                            ),
                                            className="link",
                                        ),
                                    ],
                                    className="s-contact",
                                ),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(
                                            dbc.Button(
                                                html.I(
                                                    className="fas fa-times",
                                                ),
                                                id="close",
                                                className="ml-auto",
                                                n_clicks=0,
                                            )
                                        ),
                                        dbc.ModalBody(
                                            children=[
                                                html.Img(
                                                    className="lg",
                                                    src=app.get_asset_url("logo.png"),
                                                ),
                                                html.P(
                                                    "Eulera dashboard is a tool allows you to monitor historical data, assist users in their decision-making process by showcasing selected technical indicators, use past data to have more information for your seasonal trading analysis and view current real-time news headlines for any thicker you choose. Eulera uses AI based algorithmic forecasting solutions for the capital markets to uncover the best investment opportunities.",
                                                    className="txt-modal mt-4",
                                                ),
                                                html.P(
                                                    "Eulera does not provide personal investment or financial advice to individuals, or act as personal financial, legal, or institutional investment advisors, or individually advocate the purchase or sale of any security or investment or the use of any particular financial strategy. All investing, stock forecasts and investment strategies include the risk of loss for some or even all of your capital. Before pursuing any financial strategies discussed on this website, you should always consult with a licensed financial advisor.",
                                                    className="txt-modal mt-4",
                                                    style={"font-size": ".7rem"},
                                                ),
                                            ]
                                        ),
                                        dbc.ModalFooter(
                                            className="footermodal",
                                            children=[
                                                html.Div(
                                                    className="contributor",
                                                    children=[
                                                        html.Span(
                                                            "LABIAD Salah Eddine",
                                                            className="h3",
                                                        ),
                                                        html.Div(
                                                            className="socials",
                                                            children=[
                                                                html.A(
                                                                    children=[
                                                                        html.I(
                                                                            className="fab fa-github fa-2x"
                                                                        ),
                                                                    ],
                                                                    href="https://github.com/s0v1x",
                                                                    style={
                                                                        "color": "#fea00a"
                                                                    },
                                                                    target="_blank",
                                                                ),
                                                                html.A(
                                                                    children=[
                                                                        html.I(
                                                                            className="fas fa-at fa-2x"
                                                                        )
                                                                    ],
                                                                    href="mailto:salaheddine.labiad@um6p.ma",
                                                                    style={
                                                                        "color": "#fea00a"
                                                                    },
                                                                ),
                                                                html.A(
                                                                    children=[
                                                                        html.I(
                                                                            className="fab fa-linkedin fa-2x"
                                                                        ),
                                                                    ],
                                                                    href="https://www.linkedin.com/in/salaheddinelabiad/",
                                                                    style={
                                                                        "color": "#fea00a"
                                                                    },
                                                                    target="_blank",
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                                html.Div(
                                                    className="contributor",
                                                    children=[
                                                        html.Span(
                                                            "ATERHI Mouad",
                                                            className="h3",
                                                        ),
                                                        html.Div(
                                                            className="socials",
                                                            children=[
                                                                html.A(
                                                                    children=[
                                                                        html.I(
                                                                            className="fab fa-github fa-2x"
                                                                        ),
                                                                    ],
                                                                    href="https://github.com/AterhiM",
                                                                    style={
                                                                        "color": "#fea00a"
                                                                    },
                                                                    target="_blank",
                                                                ),
                                                                html.A(
                                                                    children=[
                                                                        html.I(
                                                                            className="fas fa-at fa-2x"
                                                                        ),
                                                                    ],
                                                                    href="mailto:mouad.aterhi@um6p.ma",
                                                                    style={
                                                                        "color": "#fea00a"
                                                                    },
                                                                ),
                                                                html.A(
                                                                    children=[
                                                                        html.I(
                                                                            className="fab fa-linkedin fa-2x"
                                                                        ),
                                                                    ],
                                                                    href="https://www.linkedin.com/in/mouadaterhi/",
                                                                    style={
                                                                        "color": "#fea00a"
                                                                    },
                                                                    target="_blank",
                                                                ),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ],
                                    id="modal",
                                    is_open=True,
                                    backdrop=False,
                                    fade=True,
                                    size="xl",
                                    scrollable=False,
                                    centered=True,
                                ),
                            ],
                            className="d-contact",
                        ),
                    ],
                ),
                html.Div(
                    className="div-info",
                    children=[
                        html.Div(
                            children=[
                                html.Div(children=market_status(), id="market-status"),
                                html.Div(
                                    children=get_pre_post_post("AAPL"), id="pre_post_p"
                                ),
                                html.Div(id="test", style={"display": "none"}),
                                dbc.Button(
                                    "Forecast Price",
                                    color="primary",
                                    className="mt-6 btn-lg btn-block btn-outline-warning",
                                    outline=True,
                                    id="open_price",
                                    style={"margin-top": "1rem"},
                                ),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader(
                                            dbc.Button(
                                                html.I(
                                                    className="fas fa-times",
                                                ),
                                                id="close_price",
                                                className="ml-auto",
                                                n_clicks=0,
                                            )
                                        ),
                                        dbc.ModalBody(
                                            [
                                                html.Div(
                                                    [
                                                        html.Img(
                                                            className="img-model",
                                                            src=app.get_asset_url(
                                                                "favicon.ico"
                                                            ),
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    id="null",
                                                    style={"font-size": "2rem"},
                                                ),
                                                html.Div(
                                                    children=[
                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [
                                                                        html.P(
                                                                            [
                                                                                "The close price for the upcoming day",
                                                                                html.Br(),
                                                                                dcc.Graph(
                                                                                    id="price_indicator",
                                                                                    style={
                                                                                        "display": "inline-flex"
                                                                                    },
                                                                                    figure=indc_price(
                                                                                        0,
                                                                                        "AAPL",
                                                                                    ),
                                                                                    config={
                                                                                        "scrollZoom": True,
                                                                                        "displaylogo": False,
                                                                                        "displayModeBar": False,
                                                                                        "responsive": True,
                                                                                    },
                                                                                ),
                                                                            ]
                                                                        ),
                                                                    ],
                                                                    className="price-txt",
                                                                ),
                                                                html.P(
                                                                    """We use Auto Regressive Integrated Moving Average (ARIMA) based approach 
                                                                                    of  forecasting  in  this  method.  For  the  purpose  of  building  the  ARIMA  model. Based onthe real-time data 
                                                                                    , we compute the three parameters of the ARIMA model, 
                                                                                    i.e. the Auto Regression parameter (p), the Difference parameter (d), and the Moving Average 
                                                                                    parameter (q). The values of the three parameters are used to develop the ARIMA model for the 
                                                                                    purpose of forecasting.""",
                                                                    className="model-txt",
                                                                ),
                                                            ],
                                                            style={
                                                                "float": "left",
                                                                "width": "60%",
                                                                "margin-top": "5%",
                                                            },
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.P(
                                                                    "The history of forecasting",
                                                                    className="price-txt",
                                                                ),
                                                                dcc.Graph(
                                                                    id="history_chart",
                                                                    className="chart-graph",
                                                                    figure=model_chart(
                                                                        "AAPL", df
                                                                    ),
                                                                    config={
                                                                        "scrollZoom": True,
                                                                        "displaylogo": False,
                                                                        "displayModeBar": False,
                                                                        "responsive": True,
                                                                    },
                                                                ),
                                                                html.P(
                                                                    "*MP: Market Price, *FP: Forecasted Price",
                                                                    className="chart-note",
                                                                ),
                                                            ],
                                                            style={
                                                                "float": "right",
                                                                "width": "50%",
                                                            },
                                                        ),
                                                    ],
                                                    className="div-modal",
                                                    id="div_modal",
                                                    style={},
                                                ),
                                            ]
                                        ),
                                    ],
                                    id="modal_price",
                                    is_open=False,
                                    backdrop=False,
                                    fade=True,
                                    size="xl",
                                    scrollable=False,
                                    centered=True,
                                ),
                            ],
                            id="price-info",
                        ),
                        html.Div(
                            className="",
                            children=[
                                html.P("Choose a company :", className="tex4"),
                                dcc.Dropdown(
                                    className="",
                                    id="dropdown_corp",
                                    options=[
                                        {"label": "Apple, Inc", "value": "AAPL"},
                                        {"label": "Facebook, Inc", "value": "FB"},
                                        {"label": "Tesla, Inc", "value": "TSLA"},
                                        {"label": "Amazon, Inc", "value": "AMZN"},
                                        {"label": "Google, Inc", "value": "GOOG"},
                                        {"label": "Twitter, Inc", "value": "TWTR"},
                                        {"label": "Netflix, Inc", "value": "NFLX"},
                                    ],
                                    value="AAPL",
                                    clearable=False,
                                    searchable=False,
                                    style={"min-width": "80%"},
                                ),
                            ],
                            style={
                                "display": "flex",
                                "flex-direction": "column",
                                "align-items": "center",
                                "margin-top": "10%",
                            },
                        ),
                    ],
                ),
                html.Div(
                    className="div-news",
                    children=[
                        html.Div(
                            id="news",
                            children=update_news("AAPL"),
                            className="alignnews",
                            style={
                                "display": "flex",
                                "flex-direction": "column",
                                "align-items": "center",
                            },
                        )
                    ],
                ),
            ],
        ),
        html.Div(
            className="nine columns div-right-panel",
            children=[
                html.Div(
                    id="top_bar",
                    className="row div-top-bar",
                    children=get_top_bar("AAPL"),
                ),
                html.Div(
                    style=dict(float="right"),
                    className="row ratiostxt1",
                    children=html.Span(
                        [
                            "*the ratios are in TTM from ",
                            html.A(
                                "Financial Modeling Prep",
                                href="https://financialmodelingprep.com/",
                            ),
                        ],
                        className="note-ratios",
                    ),
                ),
                html.Div(
                    className="wrapper",
                    children=[
                        html.Div(
                            className="leftit",
                            children=[
                                html.Div(
                                    children=[
                                        html.Div(
                                            className="btns1",
                                            children=[
                                                html.Div(
                                                    id="collapse-buttonn",
                                                    children=[
                                                        dbc.RadioItems(
                                                            className="btn-group active",
                                                            labelClassName="btn btn-secondary rad-r",
                                                            options=[
                                                                {
                                                                    "label": "Add Studies",
                                                                    "value": "",
                                                                },
                                                            ],
                                                            value="",
                                                            style={
                                                                "border-top-right-radius": "0px",
                                                                "border-bottom-right-radius": "0px",
                                                            },
                                                        )
                                                    ],
                                                    n_clicks=0,
                                                    className="radio-group",
                                                ),
                                                html.Div(
                                                    id="collapse-button",
                                                    children=[
                                                        dbc.RadioItems(
                                                            className="btn-group active",
                                                            labelClassName="btn btn-secondary rad-l",
                                                            options=[
                                                                {
                                                                    "label": "Change Style",
                                                                    "value": "",
                                                                },
                                                            ],
                                                            value="",
                                                            style={
                                                                "border-top-left-radius": "0px",
                                                                "border-bottom-left-radius": "0px",
                                                            },
                                                        )
                                                    ],
                                                    n_clicks=0,
                                                    className="radio-group",
                                                ),
                                            ],
                                        ),
                                        html.Div(
                                            children=[
                                                dbc.RadioItems(
                                                    id="duration",
                                                    className="btn-group active",
                                                    labelClassName="btn btn-secondary",
                                                    options=[
                                                        {
                                                            "label": "1 Week",
                                                            "value": "7d",
                                                        },
                                                        {
                                                            "label": "1 Month",
                                                            "value": "1mo",
                                                        },
                                                        {
                                                            "label": "3 Month",
                                                            "value": "3mo",
                                                        },
                                                        {
                                                            "label": "1 Year",
                                                            "value": "1y",
                                                        },
                                                        {
                                                            "label": "5 Year",
                                                            "value": "5y",
                                                        },
                                                    ],
                                                    value="1mo",
                                                ),
                                            ],
                                            className="radio-group",
                                        ),
                                    ],
                                    className="buttons",
                                ),
                                dbc.Collapse(
                                    dbc.Card(
                                        dcc.Checklist(
                                            id="studies",
                                            options=[
                                                {
                                                    "label": "RSI",
                                                    "value": "RSI_trace",
                                                },
                                                {"label": "ROC", "value": "ROC_trace"},
                                                {
                                                    "label": "MACD",
                                                    "value": "MACD_trace",
                                                },
                                                {"label": "OBV", "value": "OBV_trace"},
                                                {
                                                    "label": "ATR",
                                                    "value": "ATR_trace",
                                                },
                                                {
                                                    "label": "TSI",
                                                    "value": "TSI_trace",
                                                },
                                                {
                                                    "label": "CCI",
                                                    "value": "CCI_trace",
                                                },
                                                {
                                                    "label": "BOLLINGER",
                                                    "value": "BOLLINGER_trace",
                                                },
                                                {
                                                    "label": "EMA",
                                                    "value": "EMA_trace",
                                                },
                                                {
                                                    "label": "SMA",
                                                    "value": "SMA_trace",
                                                },
                                            ],
                                            value=[],
                                        )
                                    ),
                                    id="collapsee",
                                    is_open=False,
                                ),
                                dbc.Collapse(
                                    dbc.Card(
                                        dcc.RadioItems(
                                            id="styles",
                                            options=[
                                                {
                                                    "label": "OHLC Chart",
                                                    "value": "ohlc_trace",
                                                },
                                                {
                                                    "label": "Candlestick Chart",
                                                    "value": "candle_trace",
                                                },
                                                {
                                                    "label": "Line Chart",
                                                    "value": "line_trace",
                                                },
                                            ],
                                            value="ohlc_trace",
                                        )
                                    ),
                                    id="collapse",
                                    is_open=False,
                                ),
                            ],
                        )
                    ],
                ),
                html.Div(
                    dcc.Graph(
                        id="charts",
                        className="chart-graph",
                        figure=main_chart("AAPL", [], "1mo", "ohlc_trace"),
                        config=conf_graph,
                    ),
                    className="ohlc",
                ),
                html.Div(
                    dbc.Carousel(
                        items=get_currencies(),
                        controls=False,
                        indicators=False,
                        interval=5000,
                        ride="carousel",
                        slide=True,
                        id="currencies",
                    ),
                    className="fnews",
                ),
                html.Div(
                    children=get_finance_infos("AAPL"),
                    className="cc",
                    id="finance_info",
                ),
                html.Div(
                    dcc.Graph(
                        id="realtime_chart",
                        className="rt",
                        figure=rt_chart("AAPL"),
                        config=conf_graph,
                    ),
                    className="cc_",
                ),
                html.Div(
                    children=[
                        html.Div(
                            [
                                html.P("Recommendation Rating", className="tit_div"),
                                html.Div(
                                    children=get_recomm_rating("AAPL"),
                                    className="rating",
                                    id="recomm_rating",
                                    style={
                                        "display": "flex",
                                        "justify-content": "center",
                                        "flex-direction": "row",
                                    },
                                ),
                            ],
                            className="lside",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=html.P(
                                        "Total ESG Risk score", className="tit_div"
                                    ),
                                    className="",
                                ),
                                html.Div(
                                    children=get_esg_score("AAPL"),
                                    className="div-scores",
                                    id="esg_scores",
                                ),
                            ],
                            className="rside",
                        ),
                    ],
                    className="cont",
                ),
                html.Div(
                    children=get_company_infos("AAPL"),
                    className="ccc",
                    id="info-company",
                ),
            ],
            style={"margin": "auto", "margin-left": "1rem"},
        ),
    ],
)


@app.callback(
    Output("news", "children"),
    [Input("i_news", "n_intervals"), Input("dropdown_corp", "value")],
)
def update__news__rating(n, dropdown_corp):
    return update_news(dropdown_corp)


@app.callback(
    Output("charts", "figure"),
    [
        Input("i_mainchart", "n_intervals"),
        Input("dropdown_corp", "value"),
        Input("studies", "value"),
        Input("duration", "value"),
        Input("styles", "value"),
    ],
)
def update_mainchart(n, dropdown_corp, studies, duration, styles):
    return main_chart(dropdown_corp, studies, duration, styles)


# CALLBACK TOP BAR - ESG RISK SCORES - COMPANY COORDS - RECOMMENDATION RATING


@app.callback(
    [
        Output("top_bar", "children"),
        Output("esg_scores", "children"),
        Output("info-company", "children"),
        Output("recomm_rating", "children"),
    ],
    [
        Input("dropdown_corp", "value"),
    ],
)
def update__topbar__esg__infos(dropdown_corp):
    return [
        get_top_bar(dropdown_corp),
        get_esg_score(dropdown_corp),
        get_company_infos(dropdown_corp),
        get_recomm_rating(dropdown_corp),
    ]


@app.callback(
    Output("collapsee", "is_open"),
    [Input("collapse-buttonn", "n_clicks")],
    [State("collapsee", "is_open")],
)
def toggle_collapsee(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("realtime_chart", "figure"),
    [Input("i_rtchart", "n_intervals"), Input("dropdown_corp", "value")],
)
def update__rtchart(n, dropdown_corp):

    status = si.get_market_status()
    data = Ticker(dropdown_corp).history(period="1d", interval="1m", adj_timezone=False)
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if (
        isinstance(data, dict)
        or status == "PRE"
        or status == "CLOSED"
        or status == "POSTPOST"
        or status == "POST"
    ) and input_id == "i_rtchart":
        raise PreventUpdate
    else:
        return rt_chart(dropdown_corp)


@app.callback(
    [Output("market-status", "children"), Output("currencies", "items")],
    [
        Input("i_stat_curren", "n_intervals"),
    ],
)
def update__status__currencies(n):

    return [market_status(), get_currencies()]


@app.callback(
    Output("finance_info", "children"),
    [Input("i_price_infos", "n_intervals"), Input("dropdown_corp", "value")],
)
def update__finfo(n, dropdown_corp):
    status = si.get_market_status()
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if (
        status == "PRE"
        or status == "CLOSED"
        or status == "POSTPOST"
        or status == "POST"
    ) and input_id == "i_price_infos":
        raise PreventUpdate
    else:
        return get_finance_infos(dropdown_corp)


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(open, close, is_open):

    if open or close:
        return not is_open
    return is_open


@app.callback(
    Output("modal_price", "is_open"),
    [Input("open_price", "n_clicks"), Input("close_price", "n_clicks")],
    [State("modal_price", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


model_history = pd.DataFrame(columns=["date", "min_conf", "max_conf", "f_price"])


@app.callback(
    [
        Output("price_indicator", "figure"),
        Output("history_chart", "figure"),
        Output("null", "children"),
        Output("div_modal", "style"),
    ],
    [Input("dropdown_corp", "value"), Input("modal_price", "is_open")],
)
def update_forecast(dropdown_corp, is_open):
    df = pd.read_csv("history.csv", index_col=0)
    response = requests.post(
            "http://euleraapi.herokuapp.com/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(dict(ticker=dropdown_corp)),
        )

    if is_open and dropdown_corp == "AAPL" and response.status_code == 200:

        res = response.json()
        dd = datetime.strptime(df.index[-1], "%Y-%m-%d")
        td = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        if dd != td and (td.weekday() != 5 and td.weekday() != 6):
            data = (
                td.strftime("%Y-%m-%d")
                + ","
                + str(res["CI"]["min"])
                + ","
                + str(res["CI"]["max"])
                + ","
                + str(res["forecast"])
                + "\n"
            )
            with open("hist.csv", "a") as f:
                f.write(data)

        return [
            indc_price(res["forecast"], dropdown_corp),
            model_chart(dropdown_corp, df),
            "",
            {},
        ]
    else:
        df = pd.DataFrame(columns=['f_price', 'min_conf', 'max_conf'])
        return [
            indc_price(0, "AAPL"),
            model_chart("AAPL", df),
            "Forecasting is not availabale for " + dropdown_corp + "...",
            {"filter": "blur(6px)", "margin": "-5%"},
        ]


@app.callback(
    Output("test", "children"),
    [Input("i_update_model", "n_intervals")],
)
def update_modelt(n):
    dt = datetime.now(timezone("America/New_York"))
    dt = dt.replace(tzinfo=None)
    dt = datetime.strptime(dt.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    update_time = datetime.strptime("16:01:00", "%H:%M:%S")
    if (
        dt.hour == update_time.hour
        and dt.minute == update_time.minute
        and dt.second == update_time.second
    ):
        status = si.get_market_status()
        if status == "POSTPOST" or status == "POST":
            response = requests.post(
                "http://euleraapi.herokuapp.com/update",
                headers={"Content-Type": "application/json"},
                data=json.dumps(dict(ticker="AAPL")),
            )
            # print(dt,'\t',response.text, 'MODEL UPDATED \t AAPL')
    else:
        raise PreventUpdate


@app.callback(
    Output("pre_post_p", "children"),
    [Input("i_pre_post", "n_intervals"), Input("dropdown_corp", "value")],
)
def update_pre_post_price(n, dropdown_corp):
    return get_pre_post_post(dropdown_corp)


if __name__ == "__main__":
    app.run_server(debug=False)
