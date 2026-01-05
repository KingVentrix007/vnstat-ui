import flet as ft
from flet_charts import LineChart, LineChartData, LineChartDataPoint

def main(page: ft.Page):
    page.title = "Test Chart"
    page.bgcolor = ft.Colors.BLACK
    page.theme_mode = ft.ThemeMode.DARK

    # Create chart data objects with points
    up_series = LineChartData(
        color=ft.Colors.BLUE_400,
        points=[
            LineChartDataPoint(x=0, y=1),
            LineChartDataPoint(x=1, y=2),
            LineChartDataPoint(x=2, y=3),
            LineChartDataPoint(x=3, y=4),
        ],
    )

    down_series = LineChartData(
        color=ft.Colors.RED_400,
        points=[
            LineChartDataPoint(x=0, y=2),
            LineChartDataPoint(x=1, y=1),
            LineChartDataPoint(x=2, y=4),
            LineChartDataPoint(x=3, y=3),
        ],
    )

    chart = LineChart(
        data_series=[up_series, down_series],
        min_y=0,
        expand=True,
    )

    page.add(chart)

ft.app(target=main)
