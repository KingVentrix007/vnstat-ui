import flet as ft
from flet_charts import LineChart
from datetime import datetime, timedelta
import vnstat_interface
# from flet_timer.flet_timer import Timer
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
    
    # ---------- Day Stats (NEW BLOCK) ----------
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
    top_stats = ft.Row(
        [
            stat_box("DATA UP", up_text),
            stat_box("DATA DOWN", down_text),
            stat_box("TOTAL", total_text),
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
    up_data: list[tuple[datetime, float]] = []
    down_data: list[tuple[datetime, float]] = []

    chart = LineChart(
        data_series=[
            {
                "data": up_data,
                "color": ft.Colors.BLUE_400,
                "stroke_width": 3,
                "label": "Upload",
            },
            {
                "data": down_data,
                "color": ft.Colors.RED_400,
                "stroke_width": 3,
                "label": "Download",
            },
        ],
        min_y=0,
        expand=True,
        vertical_grid_lines=True
    )

    chart_container = ft.Container(
        content=chart,
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        expand=True,
    )

    # ---------- Update Functions ----------

    def update_current_stats(up_mb: float, down_mb: float):
        total = up_mb + down_mb
        up_text.value = f"{up_mb:.2f} MB"
        down_text.value = f"{down_mb:.2f} MB"
        total_text.value = f"{total:.2f} MB"
        page.update()

    def update_day_stats(up_mb: float, down_mb: float):
        total = up_mb + down_mb
        day_up_text.value = f"{up_mb:.2f} MB"
        day_down_text.value = f"{down_mb:.2f} MB"
        day_total_text.value = f"{total:.2f} MB"
        page.update()

    def update_year_stats(up_gb: float, down_gb: float):
        total = up_gb + down_gb
        year_up_text.value = f"{up_gb:.2f} GB"
        year_down_text.value = f"{down_gb:.2f} GB"
        year_total_text.value = f"{total:.2f} GB"
        page.update()

    def add_graph_point(date: datetime, up_mb: float, down_mb: float):
        up_data.append((date, up_mb))
        down_data.append((date, down_mb))
        chart.update()
    def update_all_stats_periodically():
        """
        This function will be called periodically.
        Replace the random values below with your real data.
        # """
        # # --- Provide your actual values here ---
        current_up = random.uniform(50, 150)
        current_down = random.uniform(80, 300)
        # day_up = random.uniform(5, 50)
        # day_down = random.uniform(10, 100)
        # year_up = random.uniform(20, 100)
        # year_down = random.uniform(50, 200)
        # new_point_date = datetime.now()

        # # --- Update all stats ---
        # update_current_stats(current_up, current_down)
        # update_day_stats(day_up, day_down)
        # update_year_stats(year_up, year_down)
        # add_graph_point(new_point_date, current_up, current_down)

        page.update()
    # ---------- Layout ----------
    page.add(
        ft.Column(
            [
                day_stats,        # <-- Day stats added here
                top_stats,
                
                chart_container,
                year_stats,
            ],
            spacing=24,
            expand=True,
        )
    )

    # page.add_timer(1, update_all_stats_periodically)  # 1 second interval

    # page.timer.start()
    # page.add(timer)
    # ---------- Demo Data ----------
    # update_current_stats(120.5, 340.2)
    # update_day_stats(20.3, 50.7)
    # update_year_stats(32.4, 88.1)

    # base_date = datetime.now() - timedelta(days=6)
    # for i in range(7):
    #     add_graph_point(
    #         base_date + timedelta(days=i),
    #         50 + i * 10,
    #         80 + i * 15,
    #     )

# ---------- Run ----------
ft.app(target=main)
