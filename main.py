import flet as ft
from flet_charts import (
    BarChart,
    BarChartGroup,
    BarChartRod,
    BarChartTooltip,BarChartRodTooltip
)
import flet.canvas as cv
from datetime import datetime
import random
import asyncio
import vnstat_interface as vni
from typing import Union, List
import nethog_iner as neti
import socket
from pathlib import Path
import json
import math
SOCKET_PATH = "/tmp/nethogs_service.sock"
CONFIG_PATH = "vnstat_ui_config.json"
#sorting

def quick_sort_simple(arr: list[float], arr_display: list[ft.Control]):
    if len(arr) <= 1:
        return arr, arr_display

    pivot_val = arr[0]
    pivot_ctrl = arr_display[0]

    left_vals, left_ctrls = [], []
    right_vals, right_ctrls = [], []

    for val, ctrl in zip(arr[1:], arr_display[1:]):
        if val < pivot_val:
            left_vals.append(val)
            left_ctrls.append(ctrl)
        else:
            right_vals.append(val)
            right_ctrls.append(ctrl)

    sorted_left_vals, sorted_left_ctrls = quick_sort_simple(left_vals, left_ctrls)
    sorted_right_vals, sorted_right_ctrls = quick_sort_simple(right_vals, right_ctrls)

    return (
        sorted_left_vals + [pivot_val] + sorted_right_vals,
        sorted_left_ctrls + [pivot_ctrl] + sorted_right_ctrls
    )
# Example Usage:
#----------- Network Helpers---------------
async def fetch_nethogs_data():
    """
    Connect to the nethogs service via UNIX socket and return the latest totals.
    """
    if not Path(SOCKET_PATH).exists():
        return {}

    loop = asyncio.get_running_loop()

    # Run the blocking socket code in a thread to avoid blocking the event loop
    def socket_query():
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(SOCKET_PATH)
                s.sendall(b"get")
                data = b""
                while True:
                    chunk = s.recv(65536)
                    if not chunk:
                        break
                    data += chunk
                return json.loads(data.decode())
        except Exception as e:
            print("Error fetching nethogs data:", e)
            return {}

    return await loop.run_in_executor(None, socket_query)
# ---------- Helper UI Components ----------

def create_program_row(name, sent, recv, total_bytes, index=0):
    """Creates a single row for a program in the stats table with alternating row colors."""
    bg_color = ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if index % 2 == 0 else None
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(name, expand=True),
                ft.Text(f"{sent:.2f} KB", width=80, text_align=ft.TextAlign.RIGHT),
                ft.Text(f"{recv:.2f} KB", width=80, text_align=ft.TextAlign.RIGHT),
                ft.Text(f"{total_bytes / 1024:.2f} MB", width=100, text_align=ft.TextAlign.RIGHT),
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
    gauge_value = 0.0
    max_data_usage_year = 50
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
        value=vni.get_interface(),
        options=[
            ft.dropdown.Option(i) for i in vni_interface_options
        ],
        expand=True,
        
    )
    set_year_max_button = ft.Button(
         content= "Set Max Data Usage",
         
    )

    text_input_for_max_value = ft.TextField(
        label="Enter Max Data Usage",
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
        keyboard_type=ft.KeyboardType.NUMBER, # Prompts the numeric keyboard on mobile devices
        hint_text="Only digits allowed"
    )

    value_text = ft.Text(
        "0",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE
    )

    canvas = cv.Canvas(
        width=300,
        height=160,
        shapes=[]
    )
    controls = ft.Row(
        [
            ft.Container(
                content=ft.Row(
                    [dropdown,set_year_max_button,text_input_for_max_value],
                    # horizontal_alignment="center",
                    # spacing=4,
                    
                ),
                # padding=16,
                # border_radius=12,
                # expand=True,
            ),
        ]
    )
    usage_counters = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [canvas,value_text],
                    spacing=10,
                    horizontal_alignment="center",
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
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=5,
        height=300, 
        # expand=True,
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
    def draw_gauge(value):
        nonlocal gauge_value,max_data_usage_year
        canvas.shapes.clear()

        center_x = 150
        center_y = 150
        radius = 120

        start_angle = math.pi      # 180°
        sweep_bg = math.pi         # 180°
        sweep_fg = math.pi * (value / max_data_usage_year)

        # Background arc
        canvas.shapes.append(
            cv.Arc(
                x=center_x - radius,
                y=center_y - radius,
                width=radius * 2,
                height=radius * 2,
                start_angle=start_angle,
                sweep_angle=sweep_bg,
                paint=ft.Paint(
                    color=ft.Colors.GREY_800,
                    stroke_width=18,
                    style=ft.PaintingStyle.STROKE,
                    stroke_cap=ft.StrokeCap.ROUND,
                ),
            )
        )
        # bar_color = ft.Colors.CYAN
        percent = value / max_data_usage_year
        if percent >= 0.85:
            bar_color = ft.Colors.RED
        elif percent >= 0.6:
            bar_color = ft.Colors.ORANGE
        else:
            bar_color = ft.Colors.GREEN

        # Foreground arc (filled)
        canvas.shapes.append(
            cv.Arc(
                x=center_x - radius,
                y=center_y - radius,
                width=radius * 2,
                height=radius * 2,
                start_angle=start_angle,
                sweep_angle=sweep_fg,
                paint=ft.Paint(
                    color=bar_color,
                    stroke_width=18,
                    style=ft.PaintingStyle.STROKE,
                    stroke_cap=ft.StrokeCap.ROUND,
                ),
            )
        )

        value_text.value = str(int(value))+" GB"
        page.update()

    def animate_to(target):
        nonlocal gauge_value
        current = gauge_value
        steps = 4
        step = (target - current) / steps

        for _ in range(steps):
            current += step
            gauge_value = current
            draw_gauge(current)
    def update_max_data_year():
        nonlocal max_data_usage_year
        if(text_input_for_max_value.value.isdigit()):
            max_data_usage_year = int(text_input_for_max_value.value)
        
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
        try:
            while True:
                totals = await fetch_nethogs_data()
                total_vals = []

                # Clear previous rows
                program_container.controls.clear()

                # Add rows with alternating colors
                for i, (name, data) in enumerate(totals.items()):
                    if(name == "Nethog"):
                        continue
                    program_container.controls.append(
                        create_program_row(name, data['kbps_up'], data['kbps_down'], data['kbps_total'], index=i)
                    )
                    total_vals.append(data['kbps_total'])
                    
                    print(name, data['kbps_up'], data['kbps_down'], data['kbps_total'])

                # Refresh the UI
                total_vals, sorted_controls = quick_sort_simple(total_vals, program_container.controls)
                program_container.controls.clear()
                for sc in reversed(sorted_controls):
                     program_container.controls.append(sc)
                program_container.height = (50*(0.80*len(total_vals)))
                #  = sorted_controls
                page.update()

                # Wait before the next update
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("SS")
            pass
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
            animate_to(year_up+year_down)
            # await update_nethog_ui()
            # await update_nethog_ui(page,container=program_container)
            # add_graph_point(month_timestamp,month_up, month_down)

            page.update()
            await asyncio.sleep(1)

    # ---------- Layout ----------
    dropdown.on_select=update_vni_interface
    set_year_max_button.on_click=update_max_data_year
    page.add(
        ft.Column(
            [
                controls,
                usage_counters,
                day_stats,
                month_stats,
                # chart_container,
                year_stats,
                header,
                program_container
            ],
            scroll=ft.ScrollMode.ALWAYS,
            spacing=24,
            expand=True,
        )
    )

    asyncio.create_task(update_all_stats_periodically())
    asyncio.create_task(update_nethog_ui_task())

# ---------- Run ----------
ft.run(main=main)
