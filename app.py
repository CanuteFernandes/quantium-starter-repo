from pathlib import Path

import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "output.csv"
PRICE_CHANGE_DATE = pd.Timestamp("2021-01-15")


def load_daily_sales() -> pd.DataFrame:
    sales = pd.read_csv(OUTPUT_FILE)
    sales["Date"] = pd.to_datetime(sales["Date"])

    daily_sales = (
        sales.groupby("Date", as_index=False)["Sales"]
        .sum()
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return daily_sales


def build_figure(daily_sales: pd.DataFrame):
    figure = px.line(
        daily_sales,
        x="Date",
        y="Sales",
        title="Total Pink Morsel Sales Over Time",
        labels={"Date": "Date", "Sales": "Sales ($)"},
    )

    figure.update_traces(line=dict(width=3))
    figure.add_vline(
        x=PRICE_CHANGE_DATE,
        line_dash="dash",
        line_color="red",
        annotation_text="Price increase: 2021-01-15",
        annotation_position="top left",
    )
    figure.update_layout(margin=dict(l=30, r=30, t=60, b=30))

    return figure


def build_summary_text(daily_sales: pd.DataFrame) -> str:
    before = daily_sales[daily_sales["Date"] < PRICE_CHANGE_DATE]["Sales"].mean()
    after = daily_sales[daily_sales["Date"] >= PRICE_CHANGE_DATE]["Sales"].mean()

    return (
        f"Average daily sales before 2021-01-15: ${before:,.2f} | "
        f"after: ${after:,.2f}"
    )


daily_sales_df = load_daily_sales()
figure = build_figure(daily_sales_df)
summary_text = build_summary_text(daily_sales_df)

app = dash.Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div(
    [
        html.H1("Soul Foods Pink Morsel Sales Visualiser"),
        html.P(
            "Daily total sales for Pink Morsels, with the 2021-01-15 price increase marked."
        ),
        html.P(summary_text),
        dcc.Graph(id="sales-line-chart", figure=figure),
    ],
    style={"maxWidth": "1100px", "margin": "0 auto", "padding": "24px"},
)


if __name__ == "__main__":
    app.run(debug=True)
