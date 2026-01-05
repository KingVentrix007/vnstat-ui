import flet as ft
def main(page: ft.Page):
    page.title = "Flet Line Chart Example"
    
    # Define the data points for the chart
    data_points_1 = [
        ft.LineChartDataPoint(1, 1),
        ft.LineChartDataPoint(3, 1.5),
        ft.LineChartDataPoint(5, 1.4),
        ft.LineChartDataPoint(7, 3.4),
        ft.LineChartDataPoint(10, 2),
        ft.LineChartDataPoint(12, 2.2),
        ft.LineChartDataPoint(13, 1.8),
    ]

    # Create the line chart data series
    line_chart_data = [
        ft.LineChartData(
            data_points=data_points_1,
            stroke_width=4,
            color=ft.colors.LIGHT_GREEN,
            curved=True,
            stroke_cap_round=True,
        ),
    ]

    # Create the LineChart control
    chart = ft.LineChart(
        data_series=line_chart_data,
        border=ft.border.all(1, ft.colors.GREY),
        horizontal_grid_lines=ft.ChartGridLines(color=ft.colors.GREY, width=0.5),
        vertical_grid_lines=ft.ChartGridLines(color=ft.colors.GREY, width=0.5),
        left_axis=ft.ChartAxis(labels_size=40),
        bottom_axis=ft.ChartAxis(labels_size=40),
        tooltip_bgcolor=ft.colors.BLUE_GREY_100,
        expand=True,
    )

    # Add the chart to the page
    page.add(chart)

ft.app(target=main)
