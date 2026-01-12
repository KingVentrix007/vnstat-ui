import flet as ft
import math
import time
import flet.canvas as cv
MAX_VALUE = 100


def main(page: ft.Page):
    page.bgcolor = ft.Colors.BLACK
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    gauge_value = 0.0
    # gauge_value.current = 0.0

    canvas = cv.Canvas(
        width=300,
        height=160,
        shapes=[]
    )

    value_text = ft.Text(
        "0",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE
    )

    def draw_gauge(value):
        nonlocal gauge_value
        canvas.shapes.clear()

        center_x = 150
        center_y = 150
        radius = 120

        start_angle = math.pi      # 180°
        sweep_bg = math.pi         # 180°
        sweep_fg = math.pi * (value / MAX_VALUE)

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
                    color=ft.Colors.CYAN,
                    stroke_width=18,
                    style=ft.PaintingStyle.STROKE,
                    stroke_cap=ft.StrokeCap.ROUND,
                ),
            )
        )

        value_text.value = str(int(value))
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
            # time.sleep(0.015)

    # Initial draw
    draw_gauge(0)

    page.add(
        ft.Column(
            spacing=10,
            horizontal_alignment="center",
            controls=[
                canvas,
                value_text,
                ft.Slider(
                    min=0,
                    max=MAX_VALUE,
                    value=0,
                    on_change=lambda e: animate_to(e.control.value),
                ),
            ],
        )
    )


ft.app(target=main)
