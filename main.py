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
from typing import Union, List
import nethog_iner as neti
# ---------- Helper UI Components ----------

def create_program_row(name, sent, recv, total_bytes, index=0):
    """Creates a single row for a program in the stats table with alternating row colors."""
    bg_color = ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if index % 2 == 0 else None
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(name, expand=True),
                ft.Text(f"{sent:.2f} KBps", width=80, text_align=ft.TextAlign.RIGHT),
                ft.Text(f"{recv:.2f} KBps", width=80, text_align=ft.TextAlign.RIGHT),
                ft.Text(f"{total_bytes / 1024:.2f} KB", width=100, text_align=ft.TextAlign.RIGHT),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        ),
        padding=8,
        bgcolor=bg_color,
        border_radius=6,
    )

def error_screen(
    short_error: str,
    detailed_error: Union[str, List[str]]
) -> ft.Control:
    
    # Normalize detailed error to text
    if isinstance(detailed_error, list):
        detailed_text = "\n".join(str(line) for line in detailed_error)
    else:
        detailed_text = str(detailed_error)

    details_visible = False

    details_text = ft.Text(
        detailed_text,
        selectable=True,
        size=13,
        font_family="monospace",
        visible=False,
    )

    details_container = ft.Container(
        content=details_text,
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        visible=False,
    )

    def toggle_details(e):
        nonlocal details_visible
        details_visible = not details_visible
        details_text.visible = details_visible
        details_container.visible = details_visible
        e.control.text = "Hide full error" if details_visible else "See full error"
        e.control.update()
        # copy_row.visible = details_visible
        # copy_row.update()
        details_text.update()
        details_container.update()

    async def copy_error(e:ft.Event):
        # print()
        await e.page.clipboard.set(detailed_text)

    return ft.Container(
        alignment=ft.alignment.Alignment.CENTER,
        expand=True,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.RED),
                ft.Text(
                    short_error,
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.TextButton(
                    "See full error",
                    on_click=toggle_details,
                ),
                details_container,
                ft.Row(
                    [
                        ft.Button(
                            "Copy error",
                            icon=ft.Icons.COPY,
                            on_click=copy_error,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    visible=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
    )

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
    vni_interface_options,err = vni.get_vnstat_interfaces()
    if(vni_interface_options == None):
        page.controls.clear()
        page.controls.append(error_screen("Failed to get Interface list",detailed_error=err))
        page.update()
        return
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

    header = ft.Row(
    [
        ft.Text("Program", weight="bold", expand=True),
        ft.Text("Sent KBps", weight="bold", width=80, text_align=ft.TextAlign.RIGHT),
        ft.Text("Recv KBps", weight="bold", width=80, text_align=ft.TextAlign.RIGHT),
        ft.Text("Total KB", weight="bold", width=100, text_align=ft.TextAlign.RIGHT),
    ],
    spacing=10,
    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    program_container = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        spacing=5,
        expand=True,
    )


    # ---------- Chart Data ----------
    # bar_groups: list[BarChartGroup] = []
    # bar_graph_timestamps = []

    # chart = BarChart(
    #     groups=bar_groups,
    #     max_y=1,
    #     expand=True,
        
    # )
    # nethhog_output_data = ft.List
    # nethhog_output_data_container = ft.Container


    # chart_container = ft.Container(
    #     content=chart,
    #     padding=20,
    #     border_radius=12,
    #     bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
    #     expand=True,
    # )

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
        ret,err  = vni.set_interface(new_interface)
        if(ret == -2):
            page.controls.clear()
            page.controls.append(error_screen("Failed to set interface",detailed_error=err))
            page.update()
            return
        if(ret != 0):
            
            dropdown.error_text = f"{err} is no longer a valid option"
    

    async def update_nethog_ui_task():
        print("UPDATING")
        async for totals in neti.nethogs_tracker():
            # Clear previous rows
            program_container.controls.clear()

            # Add rows with alternating colors
            for i, (name, data) in enumerate(totals.items()):
                program_container.controls.append(
                    create_program_row(name, data['sent_kbps'], data['recv_kbps'], data['total_bytes'], index=i)
                )
                print(name, data['sent_kbps'], data['recv_kbps'], data['total_bytes'])

            # Refresh the UI
            page.update()
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
            # await update_nethog_ui()
            # await update_nethog_ui(page,container=program_container)
            # add_graph_point(month_timestamp,month_up, month_down)

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
                # chart_container,
                year_stats,
                header,
                program_container
            ],
            spacing=24,
            expand=True,
        )
    )

    asyncio.create_task(update_all_stats_periodically())
    asyncio.create_task(update_nethog_ui_task())

# ---------- Run ----------
ft.run(main=main)
