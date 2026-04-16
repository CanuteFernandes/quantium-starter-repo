from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output
from dash import dcc, html


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "output.csv"
PRICE_CHANGE_DATE = pd.Timestamp("2021-01-15")
PRICE_CHANGE_DATE_LABEL = "2021-01-15"
REGIONS = ["all", "north", "east", "south", "west"]


def load_sales_data() -> pd.DataFrame:
    sales = pd.read_csv(OUTPUT_FILE)
    sales["Date"] = pd.to_datetime(sales["Date"])
    sales["Region"] = sales["Region"].str.lower()
    return sales


def build_daily_sales(sales: pd.DataFrame, selected_region: str) -> pd.DataFrame:
    filtered = sales if selected_region == "all" else sales[sales["Region"] == selected_region]
    daily_sales = (
        filtered.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return daily_sales


def build_figure(daily_sales: pd.DataFrame, selected_region: str):
    region_label = selected_region.capitalize() if selected_region != "all" else "All Regions"
    figure = px.line(
        daily_sales,
        x="Date",
        y="Sales",
        title=f"Pink Morsel Sales Over Time ({region_label})",
        labels={"Date": "Date", "Sales": "Sales ($)"},
    )

    figure.update_traces(line=dict(width=4, color="#ff6b35"))
    figure.add_vline(
        x=PRICE_CHANGE_DATE_LABEL,
        line_dash="dash",
        line_color="#183153",
    )
    figure.add_annotation(
        x=PRICE_CHANGE_DATE_LABEL,
        y=1.04,
        xref="x",
        yref="paper",
        text="Price increase: 2021-01-15",
        showarrow=False,
        font=dict(color="#183153", size=12),
    )
    figure.update_layout(
        margin=dict(l=30, r=30, t=70, b=30),
        paper_bgcolor="#fffdf8",
        plot_bgcolor="#fff7eb",
        font=dict(family="Space Grotesk, Segoe UI, sans-serif", color="#222222"),
        title_font=dict(size=24),
    )
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="#f0d8ba", zeroline=False)

    return figure


def build_summary_text(daily_sales: pd.DataFrame, selected_region: str) -> str:
    before = daily_sales[daily_sales["Date"] < PRICE_CHANGE_DATE]["Sales"].mean()
    after = daily_sales[daily_sales["Date"] >= PRICE_CHANGE_DATE]["Sales"].mean()
    region_label = selected_region.capitalize() if selected_region != "all" else "all regions"

    return (
        f"Average daily sales for {region_label} before 2021-01-15: ${before:,.2f} | "
        f"after: ${after:,.2f}"
    )


sales_df = load_sales_data()
daily_sales_df = build_daily_sales(sales_df, "all")
initial_figure = build_figure(daily_sales_df, "all")
initial_summary_text = build_summary_text(daily_sales_df, "all")

app = dash.Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div(
    [
        html.Div(
            [
                html.P("Soul Foods Analytics", className="eyebrow"),
                html.H1("Pink Morsel Sales Visualiser", className="title"),
                html.P(
                    "Explore daily sales trends and compare performance before and after the price change.",
                    className="subtitle",
                ),
            ],
            className="header-block",
        ),
        html.Div(
            [
                html.Label("Filter by region", className="filter-label"),
                dcc.RadioItems(
                    id="region-filter",
                    options=[{"label": region, "value": region} for region in REGIONS],
                    value="all",
                    inline=True,
                    className="radio-group",
                    labelClassName="radio-option",
                ),
            ],
            className="controls",
        ),
        html.P(id="summary-text", children=initial_summary_text, className="summary"),
        dcc.Graph(id="sales-line-chart", figure=initial_figure, className="chart-card"),
    ],
    className="app-shell",
)


@app.callback(
    Output("sales-line-chart", "figure"),
    Output("summary-text", "children"),
    Input("region-filter", "value"),
)
def update_chart(selected_region: str):
    daily_sales = build_daily_sales(sales_df, selected_region)
    figure = build_figure(daily_sales, selected_region)
    summary_text = build_summary_text(daily_sales, selected_region)
    return figure, summary_text


if __name__ == "__main__":
    app.run(debug=True)
