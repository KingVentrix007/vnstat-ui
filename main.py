import flet as ft
from flet_charts import (
    BarChart,
    BarChartGroup,
    BarChartRod,
    BarChartTooltip,BarChartRodTooltip
)

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
    vni_interface_options = vni.get_vnstat_interfaces()

    dropdown = ft.Dropdown(
        value=vni_interface_options[0] if vni_interface_options else None,
        options=[
            ft.dropdown.Option(i) for i in vni_interface_options
        ],
        expand=True,
        
    )

    controls = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [dropdown],
                    spacing=4,
                ),
                padding=16,
                border_radius=12,
                expand=True,
            ),
        ]
    )
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
    bar_groups: list[BarChartGroup] = []
    bar_graph_timestamps = []

    chart = BarChart(
        groups=bar_groups,
        max_y=1,
        expand=True,
        
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
    def update_vni_interface():
        new_interface = dropdown.value
        ret  = vni.set_interface(new_interface)
        if(ret != 0):
            dropdown.error_text = "Error"

    def add_graph_point(timestamp: int, up_mb: float, down_mb: float):
        x = len(bar_groups)
        if(timestamp in bar_graph_timestamps):
            return
        bar_graph_timestamps.append(timestamp)
            
        group = BarChartGroup(
            x=x,
            rods=[
                BarChartRod(
                    
                    from_y=0,
                    to_y=up_mb,
                    width=10,
                    color=ft.Colors.BLUE_400,
                    tooltip=BarChartRodTooltip(text=f"Upload {up_mb}"),
                    
                ),
                BarChartRod(
                    from_y=0,
                    to_y=down_mb,
                    width=10,
                    color=ft.Colors.RED_400,
                    tooltip=BarChartRodTooltip(text=f"Download {down_mb}"),
                    
                ),
            ],
        
            
        )

        bar_groups.append(group)

        # Limit to last N bars
        N = 20
        if len(bar_groups) > N:
            bar_groups[:] = bar_groups[-N:]

        # Auto-scale Y axis
        chart.max_y = max(
            max(up_mb, down_mb),
            chart.max_y+30 or 0,
        )

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
            add_graph_point(month_timestamp,month_up, month_down)

            page.update()
            await asyncio.sleep(1)

    # ---------- Layout ----------
    dropdown.on_select=update_vni_interface
    page.add(
        ft.Column(
            [
                controls,
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
