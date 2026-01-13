import flet as ft
from network_gui import network_gui_main
# Example callback functions
# def network_gui_main(page: ft.Page):
#     page.controls.clear()
#     page.add(ft.Text("Network Monitor GUI", size=30))
#     page.update()

def system_gui_main(page: ft.Page):
    page.controls.clear()
    page.add(ft.Text("System Monitor GUI", size=30))
    page.update()

def cpu_gui_main(page: ft.Page):
    page.controls.clear()
    page.add(ft.Text("CPU Monitor GUI", size=30))
    page.update()

def ram_gui_main(page: ft.Page):
    page.controls.clear()
    page.add(ft.Text("RAM Monitor GUI", size=30))
    page.update()

def disk_gui_main(page: ft.Page):
    page.controls.clear()
    page.add(ft.Text("Disk Monitor GUI", size=30))
    page.update()

# Main Flet app
def main(page: ft.Page):
    page.title = "System Monitor"
    page.window_width = 800
    page.window_height = 500

    # Sidebar menu buttons
    menu_buttons = [
        ("Network", network_gui_main),
        ("System", system_gui_main),
        ("CPU", cpu_gui_main),
        ("RAM", ram_gui_main),
        ("Disk", disk_gui_main),
    ]

    # Container for main content
    content_container = ft.Column()

    # Function to handle sidebar button clicks
    def on_menu_click(callback):
        def wrapper(e):
            callback(page)
        return wrapper

    # Create sidebar
    sidebar = ft.Column(
        controls=[
            ft.ElevatedButton(
                name,
                on_click=on_menu_click(cb),
                width=150
            )
            for name, cb in menu_buttons
        ],
        spacing=10
    )

    # Layout: sidebar on left, content on right
    page.add(
        ft.Row(
            controls=[
                sidebar,
                ft.Container(width=20),  # small spacer
                content_container,
            ],
        )
    )

    # Initially show system GUI
    # system_gui_main(page)

ft.app(target=main)
