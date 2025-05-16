from dash import html, dcc, register_page, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLOR_BG = "#FFFFFF"
COLOR_DARK = "#062A74"
COLOR_GREY = "#707787"
COLOR_BLUE1 = "#034BE4"
COLOR_BLUE2 = "#428BF9"
COLOR_CYAN = "#B6CDFF"
COLOR_ORANGE = "#FF9705"
PALETTE_MAIN = [COLOR_ORANGE, COLOR_BLUE1, COLOR_BLUE2, COLOR_CYAN, COLOR_GREY]

register_page(__name__, path="/academic", name="Academic Insights")

df = pd.read_csv("data/student_data.csv")
df["final_grade"] = df[["G1", "G2", "G3"]].mean(axis=1)

def calculate_metrics(df_filtered):
    return {
        "total": len(df_filtered),
        "avg_grade": round(df_filtered["final_grade"].mean(), 1),
        "gp_pct": round((df_filtered["school"] == "GP").mean() * 100),
        "ms_pct": 100 - round((df_filtered["school"] == "GP").mean() * 100),
        "activities_pct": round((df_filtered["activities"] == "yes").mean() * 100),
        "avg_absences": round(df_filtered["absences"].mean()),
        "avg_health": round(df_filtered["health"].mean(), 1),
        "avg_freetime": round(df_filtered["freetime"].mean(), 1)
    }

def card(title, val, icon="📊", highlight=False):
    style = {
        "flex": "0 0 auto",
        "width": "100%",
        "minWidth": "150px",
        "maxWidth": "200px",
        "backgroundColor": COLOR_BG,
        "color": COLOR_DARK,
       "border": f"2px solid {COLOR_BLUE1}",
        "borderRadius": "12px",
        "boxShadow": "0 2px 6px 0 #E0EAFF66",
        "padding": "10px 12px",
        "margin": "0"
    }

    safe_val = str(val) if val is not None else "-"
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div(icon, style={
                    "fontSize": "1.2rem",
                    "background": COLOR_BLUE2,
                    "borderRadius": "50%",
                    "padding": "0.3em",
                    "color": COLOR_DARK,
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "marginRight": "0.5em",
                    "height": "2.2em",
                    "width": "2.2em"
                }),
                html.Div(title, style={
                    "fontSize": "0.88em",
                    "fontWeight": 500,
                    "color": COLOR_GREY,
                    "wordBreak": "break-word"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "marginBottom": "0.6em"
            }),

            html.Div(safe_val, style={
                "color": COLOR_BLUE1,
                "fontWeight": 700,
                "fontSize": "1.15rem",
                "lineHeight": "1.35",
                "wordBreak": "break-word",
                "whiteSpace": "normal"
            })
        ])
    ], style=style)

def plot_grade_by_factor(data, factor, chart_type="box"):
    binary_factors = {"schoolsup", "famsup", "paid", "internet", "activities"}
    ALCOHOL_LEVELS = [1, 2, 3, 4, 5]
    ALCOHOL_COLORS = [COLOR_CYAN, COLOR_BLUE2, COLOR_BLUE1, COLOR_GREY, COLOR_ORANGE]

    if factor not in data.columns or data[factor].dropna().nunique() < 1:
        return go.Figure()

    order = sorted(data[factor].dropna().unique())
    color_seq = PALETTE_MAIN

    if factor in {"Dalc", "Walc"}:
        data = data.copy()
        data[factor] = data[factor].astype(str)
        order = [str(lvl) for lvl in ALCOHOL_LEVELS]
        color_seq = ALCOHOL_COLORS
    elif factor in binary_factors:
        order = ["yes", "no"]
        color_seq = [COLOR_BLUE1, COLOR_ORANGE]

    if chart_type == "strip":
        fig = px.strip(data, x=factor, y="final_grade",
                       category_orders={factor: order},
                       color=factor,
                       color_discrete_sequence=color_seq)
    elif chart_type == "bar":
        agg = (
            data.groupby(factor, observed=True)["final_grade"]
            .mean()
            .reindex(order, fill_value=None)
            .reset_index()
        )
        fig = px.bar(agg, x=factor, y="final_grade", color=factor,
                     category_orders={factor: order},
                     color_discrete_sequence=color_seq)
    elif chart_type == "violin":
        fig = px.violin(data, x=factor, y="final_grade", box=True, points="all",
                        category_orders={factor: order},
                        color=factor,
                        color_discrete_sequence=color_seq)
    else:
        fig = px.box(data, x=factor, y="final_grade",
                     category_orders={factor: order},
                     color=factor,
                     color_discrete_sequence=color_seq)

    fig.update_layout(
        template="simple_white",
        height=320,
        showlegend=True,
        xaxis_title=factor.replace("_", " ").title(),
        yaxis=dict(range=[0, 20], tick0=0, dtick=5, title="Final Grade", color=COLOR_DARK),
        plot_bgcolor=COLOR_BG,
        paper_bgcolor=COLOR_BG,
        font=dict(color=COLOR_DARK)
    )
    return fig

def plot_grade_trend(data):
    avg = data[["G1", "G2", "G3"]].mean().reset_index()
    avg.columns = ["Term", "Average"]

    fig = go.Figure(go.Scatter(
        x=avg["Term"], y=avg["Average"], mode="lines+markers",
        line=dict(color=COLOR_BLUE2, width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        template="simple_white",
        height=300,
        margin=dict(t=40, b=40, l=40, r=40),
        title=dict(
            text="",
            x=0.5,
            xanchor='center',
            font=dict(size=16, color=COLOR_BLUE1)
        ),
        xaxis=dict(
            title="Term",
            tickmode="array",
            tickvals=["G1", "G2", "G3"],
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Average Grade",
            range=[0, 20],
            title_font=dict(size=14),
            tickfont=dict(size=12),
            color=COLOR_DARK
        ),
        plot_bgcolor=COLOR_BG,
        paper_bgcolor=COLOR_BG,
        font=dict(color=COLOR_DARK)
    )
    return fig

layout = dbc.Container([
    html.Br(),
    html.H2("Academic Insights", style={"color": COLOR_BLUE1}),
    dbc.Row([
        dbc.Col([
            html.Label("Filter by School:", style={"color": COLOR_DARK}),
            dcc.Dropdown(
                id="academic-school-filter",
                options=[{"label": "All", "value": "All"}] +
                        [{"label": s, "value": s} for s in sorted(df["school"].unique())],
                value="All", clearable=False,
                style={"backgroundColor": COLOR_BG}
            )
        ], width=3)
    ]),
    html.Br(),
    html.H4("Key Metrics", style={"color": COLOR_BLUE1}),
    html.Div(
        id="academic-metrics-row",
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(160px, 1fr))",
            "gap": "12px",
            "padding": "12px 6px",
            "alignItems": "stretch"
        }
    ),
    html.Hr(),
    html.H4("Support & Lifestyle Factors vs Grades", style={"color": COLOR_BLUE1}),
    dbc.Row([
        dbc.Col([
            html.Label("", style={"color": COLOR_DARK}),
            dcc.Dropdown(
                id="support-factor",
                options=[
                    {"label": "School Support", "value": "schoolsup"},
                    {"label": "Family Support", "value": "famsup"},
                    {"label": "Paid Classes", "value": "paid"},
                    {"label": "Internet Access", "value": "internet"},
                ],
                value="schoolsup", clearable=False,
                style={"backgroundColor": COLOR_BG}
            ),
            dcc.Graph(id="support-plot")
        ], width=6),
        dbc.Col([
            html.Label("", style={"color": COLOR_DARK}),
            dcc.Dropdown(
                id="lifestyle-factor",
                options=[
                    {"label": "Free Time", "value": "freetime"},
                    {"label": "Going Out", "value": "goout"},
                    {"label": "Study Time", "value": "studytime"},
                    {"label": "Activities", "value": "activities"},
                ],
                value="studytime", clearable=False,
                style={"backgroundColor": COLOR_BG}
            ),
            dcc.Graph(id="lifestyle-plot")
        ], width=6),
    ]),
    html.Hr(),
    html.H4("Health and Personal Factors vs Grades", style={"color": COLOR_BLUE1}),
    dbc.Row([
        dbc.Col([
            html.Label("", style={"color": COLOR_DARK}),
            dcc.Dropdown(
                id="personal-factor",
                options=[
                    {"label": "Weekday Alcohol", "value": "Dalc"},
                    {"label": "Weekend Alcohol", "value": "Walc"},
                    {"label": "Absences", "value": "absences"},
                    {"label": "Health Rating", "value": "health"},
                ],
                value="Walc", clearable=False,
                style={"backgroundColor": COLOR_BG}
            ),
            dcc.Graph(id="personal-plot")
        ])
    ]),
    html.Hr(),
    html.H4("Grade Progression Over Time", style={"color": COLOR_BLUE1}),
    dbc.Row([dbc.Col(dcc.Graph(id="academic-trend-fig"), width=12)])
], fluid=True, style={"backgroundColor": COLOR_BG, "color": COLOR_DARK})

@callback(
    Output("academic-metrics-row", "children"),
    Output("support-plot", "figure"),
    Output("lifestyle-plot", "figure"),
    Output("personal-plot", "figure"),
    Output("academic-trend-fig", "figure"),
    Input("academic-school-filter", "value"),
    Input("support-factor", "value"),
    Input("lifestyle-factor", "value"),
    Input("personal-factor", "value")
)
def update_academic_dashboard(school, support, lifestyle, personal):
    dff = df if school == "All" else df[df["school"] == school]
    m = calculate_metrics(dff)
    ratio = f"GP: {m['gp_pct']}% · MS: {m['ms_pct']}%" if school == "All" else f"{school}: {round((len(dff)/len(df))*100)}%"
    metrics_cards = [
        card("Total Students", m["total"], "👥"),
        card("School Ratio", ratio, "🏫"),
        card("Avg Final Grade", f"{m['avg_grade']} / 20", "📊", highlight=True),
        card("Absences / Student", f"{int(m['avg_absences'])} / yr", "📅"),
        card("Activities", f"{m['activities_pct']}%", "🎯", highlight=True),
        card("Free Time Rating", f"{m['avg_freetime']} / 5", "🕒"),
        card("Health Rating", f"{m['avg_health']} / 5", "💪"),
    ]
    lifestyle_chart = "violin"
    personal_chart = "strip" if personal == "absences" else ("bar" if personal in ["Walc", "Dalc"] else "box")
    return (
        metrics_cards,
        plot_grade_by_factor(dff, support, chart_type="box"),
        plot_grade_by_factor(dff, lifestyle, chart_type=lifestyle_chart),
        plot_grade_by_factor(dff, personal, chart_type=personal_chart),
        plot_grade_trend(dff)
    )