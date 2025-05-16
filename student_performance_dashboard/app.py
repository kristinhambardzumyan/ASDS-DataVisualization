from dash import Dash, html, page_container, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

COLOR_BG = "#FFFFFF"
COLOR_BLUE1 = "#034BE4"
COLOR_SIDEBAR_BG = "#F7FAFF"
COLOR_LINK_ACTIVE = COLOR_BLUE1
COLOR_LINK_INACTIVE = "#223355"

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server

app.layout = dbc.Container([
    dcc.Location(id="url"),
    dbc.NavbarSimple(
        brand="📊 Student Performance Dashboard",
        color=None,
        style={
            "backgroundColor": COLOR_BLUE1,
            "color": "white",
            "fontWeight": 600,
            "fontSize": "1.22rem",
            "borderRadius": "0 0 8px 8px",
            "boxShadow": "0 2px 8px 0 #B6CDFF44",
        },
        dark=True,
        fluid=True,
    ),
    dbc.Row([
        dbc.Col([
            html.Div(id="sidebar-nav")
        ], width=2, style={"minWidth": "180px"}),
        dbc.Col([
            page_container
        ], width=10)
    ])
], fluid=True, style={"backgroundColor": COLOR_BG})

@callback(
    Output("sidebar-nav", "children"),
    Input("url", "pathname"),
)
def update_sidebar(pathname):
    def nav_style(active):
        return {
            "color": COLOR_LINK_ACTIVE if active else COLOR_LINK_INACTIVE,
            "background": "#E8F0FE" if active else "transparent",
            "fontWeight": 700 if active else 500,
            "marginBottom": "0.5em",
            "borderRadius": "8px",
            "padding": "0.7em 1em",
            "transition": "background 0.2s, color 0.2s"
        }

    return dbc.Nav([
        dbc.NavLink(
            "Overview", href="/", active="exact",
            style=nav_style(pathname == "/" or pathname == ""),
        ),
        dbc.NavLink(
            "Academic Insights", href="/academic", active="exact",
            style=nav_style(pathname == "/academic"),
        ),
    ], vertical=True, pills=False, style={
        "background": COLOR_SIDEBAR_BG,
        "padding": "1.5em 0.8em 1.5em 0.8em",
        "borderRadius": "12px",
        "boxShadow": "0 2px 6px 0 #E0EAFF22"
    })

from pages.overview import register_callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)