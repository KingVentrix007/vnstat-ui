import flet as ft
from flet_charts import LineChart, LineChartData, LineChartDataPoint
from datetime import datetime
import random
import asyncio
import vnstat_interface as vni

# ---------- Helper UI Components ----------
def stat_box(title: str, value_ref: ft.Text, bgcolor=None):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(title, size=12, color=ft.Colors.GREY_400),
                value_ref,
            ],
            spacing=4,
        ),
        padding=16,
        border_radius=12,
        bgcolor=bgcolor or ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        expand=True,
    )

# ---------- Main App ----------
def main(page: ft.Page):
    page.title = "Data Monitor"
    page.bgcolor = ft.Colors.BLACK
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK

    # ---------- Top Stats ----------
    up_text = ft.Text("0 MB", size=24, weight=ft.FontWeight.BOLD)
    down_text = ft.Text("0 MB", size=24, weight=ft.FontWeight.BOLD)
    total_text = ft.Text("0 MB", size=24, weight=ft.FontWeight.BOLD)
    
    # ---------- Day Stats ----------
    day_up_text = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD)
    day_down_text = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD)
    day_total_text = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD)

    day_stats = ft.Row(
        [
            stat_box("DAY UP", day_up_text, bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.CYAN)),
            stat_box("DAY DOWN", day_down_text, bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.CYAN)),
            stat_box("DAY TOTAL", day_total_text, bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.CYAN)),
        ],
        spacing=16,
    )
    
    month_stats = ft.Row(
        [
            stat_box("MONTH UP", up_text),
            stat_box("MONTH DOWN", down_text),
            stat_box("MONTH TOTAL", total_text),
        ],
        spacing=16,
    )

    # ---------- Year Stats ----------
    year_up_text = ft.Text("0 GB", size=22, weight=ft.FontWeight.BOLD)
    year_down_text = ft.Text("0 GB", size=22, weight=ft.FontWeight.BOLD)
    year_total_text = ft.Text("0 GB", size=22, weight=ft.FontWeight.BOLD)

    year_stats = ft.Row(
        [
            stat_box("YEAR UP", year_up_text),
            stat_box("YEAR DOWN", year_down_text),
            stat_box("YEAR TOTAL", year_total_text),
        ],
        spacing=16,
    )

    # ---------- Chart Data ----------
    chart_x_labels: list[str] = []  # timestamps
    chart_points_up: list[LineChartDataPoint] = [LineChartDataPoint(x=i, y=y) for i, y in enumerate([1,2,3,4])]
    chart_points_down: list[LineChartDataPoint] = [LineChartDataPoint(x=i, y=y) for i, y in enumerate([1,2,3,4])]

    up_series = LineChartData(points=chart_points_up, color=ft.Colors.BLUE_400)
    down_series = LineChartData(points=chart_points_down, color=ft.Colors.RED_400)

    chart = LineChart(
        data_series=[up_series, down_series],
        min_y=0,
        expand=True
    )

    chart_container = ft.Container(
        content=chart,
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
        expand=True,
    )

    # ---------- Update Functions ----------
    def update_month_stats(up_mb: float, down_mb: float):
        total = up_mb + down_mb
        up_text.value = f"{up_mb:.2f} MB"
        down_text.value = f"{down_mb:.2f} MB"
        total_text.value = f"{total:.2f} MB"

    def update_day_stats(up_mb: float, down_mb: float):
        total = up_mb + down_mb
        day_up_text.value = f"{up_mb:.2f} MB"
        day_down_text.value = f"{down_mb:.2f} MB"
        day_total_text.value = f"{total:.2f} MB"

    def update_year_stats(up_gb: float, down_gb: float):
        total = up_gb + down_gb
        year_up_text.value = f"{up_gb:.2f} GB"
        year_down_text.value = f"{down_gb:.2f} GB"
        year_total_text.value = f"{total:.2f} GB"

    def add_graph_point(up_mb: float, down_mb: float):
        x = len(up_series.points)
        up_series.points.append(LineChartDataPoint(x=x, y=up_mb))
        down_series.points.append(LineChartDataPoint(x=x, y=down_mb))

        # Limit to last N points
        N = 20
        up_series.points = up_series.points[-N:]
        down_series.points = down_series.points[-N:]

        chart.update()

    # ---------- Async Periodic Update ----------
    async def update_all_stats_periodically():
        while True:
            # Replace these with your actual data fetching
            month_timestamp, month_up, month_down = vni.get_month_output()
            day_stamp, day_up, day_down = vni.get_day_output()
            year_stamp, year_up, year_down = vni.get_year_output()

            # Update stats
            update_month_stats(month_up, month_down)
            update_day_stats(day_up, day_down)
            update_year_stats(year_up, year_down)
            add_graph_point(month_up, month_down)

            page.update()
            await asyncio.sleep(1)

    # ---------- Layout ----------
    page.add(
        ft.Column(
            [
                day_stats,
                month_stats,
                chart_container,
                year_stats,
            ],
            spacing=24,
            expand=True,
        )
    )

    asyncio.create_task(update_all_stats_periodically())

# ---------- Run ----------
ft.app(target=main)
