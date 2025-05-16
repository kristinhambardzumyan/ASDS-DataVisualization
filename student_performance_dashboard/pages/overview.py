from dash import html, dcc, register_page, Input, Output
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
COLOR_SOFT_ORANGE = "#FFD9B3"
PALETTE_MAIN = [COLOR_BLUE1, COLOR_BLUE2, COLOR_CYAN, COLOR_GREY, COLOR_SOFT_ORANGE]

register_page(__name__, path="/", name="Overview")

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
        "avg_freetime": round(df_filtered["freetime"].mean(), 1),
        "activities_pct": round((df_filtered["activities"] == "yes").mean() * 100),
    }
def card(title, val, icon="📊"):
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

def plot_categorical_bar(df, column, label, categories=None, display_labels=None):
    if categories is None:
        categories = sorted(df[column].dropna().unique())
    prop_data = (
        df[column].value_counts(normalize=True)
        .reindex(categories, fill_value=0)
        .reset_index()
    )
    prop_data.columns = ["label", "Proportion"]
    if display_labels:
        prop_data["label"] = [display_labels.get(val, val) for val in categories]
    else:
        prop_data["label"] = prop_data["label"].astype(str)
    palette = PALETTE_MAIN.copy()
    while len(palette) < len(categories):
        palette += palette
    color_seq = palette[:len(categories)]
    fig = px.bar(
        prop_data, x="label", y="Proportion",
        color="label",
        color_discrete_sequence=color_seq
    )
    fig.update_layout(
        title=label,
        title_x=0.5,
        height=300,
        yaxis=dict(range=[0, 1], title="", color=COLOR_DARK),
        xaxis_title="",
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor=COLOR_BG,
        paper_bgcolor=COLOR_BG,
        font=dict(color=COLOR_DARK),
        showlegend=False,
    )
    return fig

def plot_donut(title, yes_pct):
    fig = go.Figure([
        go.Pie(
            labels=["Yes", "No"],
            values=[yes_pct, 100 - yes_pct],
            hole=0.5,
            marker_colors=[COLOR_BLUE2, COLOR_GREY],
            textinfo="percent",
            textposition="outside",
            sort=False,
        )
    ])
    fig.update_layout(
        title_text=title,
        title_x=0.5,
        height=280,
        showlegend=True,
        legend=dict(orientation="h", y=-0.2, font=dict(color=COLOR_DARK)),
        plot_bgcolor=COLOR_BG,
        paper_bgcolor=COLOR_BG,
        font=dict(color=COLOR_DARK)
    )
    return fig

def plot_grade_distribution(df):
    fig = px.histogram(
        df, x="final_grade", nbins=20,
        color_discrete_sequence=[COLOR_BLUE1]
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white")))
    fig.update_layout(
        height=340,
        xaxis_title="Average Grade",
        yaxis_title="Number of Students",
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor=COLOR_BG,
        paper_bgcolor=COLOR_BG,
        font=dict(color=COLOR_DARK)
    )
    return fig

layout = dbc.Container([
    html.Br(),
    html.H2("Key Metrics", style={"color": COLOR_BLUE1}),
    dbc.Row([
        dbc.Col([
            html.Label("Filter by School:", style={"color": COLOR_DARK}),
            dcc.Dropdown(
                id="school-filter",
                options=[
                    {"label": "All", "value": "All"},
                    {"label": "GP", "value": "GP"},
                    {"label": "MS", "value": "MS"},
                ],
                value="All",
                clearable=False,
                style={"backgroundColor": COLOR_BG}
            ),
        ], width=3)
    ]),
    html.Br(),
    html.Div(id="metrics-row", style={
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(160px, 1fr))",
        "gap": "12px",
        "padding": "12px 6px"
    }),
    html.Hr(),
    html.H4("Demographics", style={"color": COLOR_BLUE1}),
    dbc.Row(id="demographics-row"),
    html.Hr(),
    html.H4("Support Access", style={"color": COLOR_BLUE1}),
    dbc.Row(id="support-row", className="mb-4"),
    html.Hr(),
    html.H4("Access and Aspirations", style={"color": COLOR_BLUE1}),
    dbc.Row(id="donut-row"),
    html.Hr(),
    html.H4("Grade Distribution", style={"color": COLOR_BLUE1}),
    dbc.Row([dbc.Col(dcc.Graph(id="grade-distribution"), width=12)]),
], fluid=True, style={"backgroundColor": COLOR_BG, "color": COLOR_DARK})

def register_callbacks(app):
    @app.callback(
        Output("metrics-row", "children"),
        Output("demographics-row", "children"),
        Output("support-row", "children"),
        Output("donut-row", "children"),
        Output("grade-distribution", "figure"),
        Input("school-filter", "value"),
    )
    def update_dashboard(school):
        dff = df if school == "All" else df[df["school"] == school]
        m = calculate_metrics(dff)
        ratio = f"GP: {m['gp_pct']}% · MS: {m['ms_pct']}%" if school == "All" else f"{school}: {round((len(dff)/len(df))*100)}%"
        cards = [
            card("Total Students", m["total"], "👥"),
            card("School Ratio", ratio, "🏫"),
            card("Avg Final Grade", f"{m['avg_grade']} / 20", "📊"),
            card("Absences / Student", f"{int(m['avg_absences'])} / yr", "📅"),
            card("Activities", f"{m['activities_pct']}%", "🎯"),
            card("Free Time Rating", f"{m['avg_freetime']} / 5", "🕒"),
            card("Health Rating", f"{m['avg_health']} / 5", "💪"),
        ]
        demo = [("sex", "Gender", ["F", "M"], {"F": "Female", "M": "Male"}),
                ("address", "Urban vs Rural", ["U", "R"], {"U": "Urban", "R": "Rural"}),
                ("famsize", "Family Size", ["LE3", "GT3"], {"LE3": "≤3", "GT3": ">3"})]
        demo_graphs = [dbc.Col(dcc.Graph(figure=plot_categorical_bar(dff, col, title, cats, labels)), width=4)
                       for col, title, cats, labels in demo]
        support = [("schoolsup", "School Support", ["no", "yes"], {"no": "No", "yes": "Yes"}),
                   ("famsup", "Family Support", ["no", "yes"], {"no": "No", "yes": "Yes"}),
                   ("paid", "Paid Classes", ["no", "yes"], {"no": "No", "yes": "Yes"})]
        support_graphs = [dbc.Col(dcc.Graph(figure=plot_categorical_bar(dff, col, title, cats, labels)), width=4)
                          for col, title, cats, labels in support]
        donut_row = [
            dbc.Col(dcc.Graph(figure=plot_donut("Has Internet Access", (dff["internet"]=="yes").mean()*100)), width=4),
            dbc.Col(dcc.Graph(figure=plot_donut("Wants Higher Education", (dff["higher"]=="yes").mean()*100)), width=4),
            dbc.Col(dcc.Graph(figure=plot_donut("Participates in Activities", m["activities_pct"])), width=4),
        ]
        return (
            cards,
            dbc.Row(demo_graphs),
            dbc.Row(support_graphs),
            dbc.Row(donut_row),
            plot_grade_distribution(dff)
        )
