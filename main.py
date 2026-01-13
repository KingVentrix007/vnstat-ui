import flet as ft
from network_gui import network_gui_main


# ---------------- GUI PAGES ---------------- #

def system_gui_main(content: ft.Column,host):
    host.controls.clear()
    host.controls.append(ft.Text("System Monitor GUI", size=30))
    content.update()


def cpu_gui_main(content: ft.Column,host):
    host.controls.clear()
    host.controls.append(ft.Text("CPU Monitor GUI", size=30))
    content.update()


def ram_gui_main(content: ft.Column,host):
    host.controls.clear()
    host.controls.append(ft.Text("RAM Monitor GUI", size=30))
    content.update()


def disk_gui_main(content: ft.Column,host):
    host.controls.clear()
    host.controls.append(ft.Text("Disk Monitor GUI", size=30))
    content.update()


def network_gui_wrapper(content: ft.Column,host):
    host.controls.clear()
    network_gui_main(content,host)
    content.update()


# ---------------- MAIN APP ---------------- #

def main(page: ft.Page):
    page.title = "System Monitor"
    page.window_width = 900
    page.window_height = 500
    page.padding = 0

    sidebar_expanded = True

    # Right-side content
    content = ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        controls=[]
    )

    # Sidebar width refs
    sidebar = ft.Container()
    sidebar.width = 200

    def load_view(cb):
        cb(page,content)

    def toggle_sidebar(e):
        nonlocal sidebar_expanded
        sidebar_expanded = not sidebar_expanded

        sidebar.width = 200 if sidebar_expanded else 60

        for btn in menu_buttons:
            btn.text = btn.data if sidebar_expanded else ""
            btn.icon = btn.icon
            btn.update()

        sidebar.update()

    # Menu buttons
    menu_buttons = [
        ft.IconButton(
            icon=ft.Icons.NETWORK_CHECK,

            data="Network",
            on_click=lambda e: load_view(network_gui_wrapper),
            style=ft.ButtonStyle(alignment=ft.alignment.Alignment.CENTER_LEFT)
        ),
        ft.IconButton(
            icon=ft.Icons.DESKTOP_WINDOWS,

            data="System",
            on_click=lambda e: load_view(system_gui_main),
            style=ft.ButtonStyle(alignment=ft.alignment.Alignment.CENTER_LEFT)
        ),
        ft.IconButton(
            icon=ft.Icons.MEMORY,
            

            on_click=lambda e: load_view(cpu_gui_main),
            style=ft.ButtonStyle(alignment=ft.alignment.Alignment.CENTER_LEFT)
        ),
        ft.IconButton(

            icon=ft.Icons.STORAGE,
            
            data="RAM",
            on_click=lambda e: load_view(ram_gui_main),
            style=ft.ButtonStyle(alignment=ft.alignment.Alignment.CENTER_LEFT)
        ),
        ft.IconButton(

            icon=ft.Icons.SAVE,
            
            data="Disk",
            on_click=lambda e: load_view(disk_gui_main),
            style=ft.ButtonStyle(alignment=ft.alignment.Alignment.CENTER_LEFT)
        ),
    ]

    sidebar.content = ft.Column(
        controls=[
            ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=toggle_sidebar
            ),
            ft.Divider(),
            *menu_buttons
        ],
        spacing=5
    )

    # Layout
    page.add(
        ft.Row(
            expand=True,
            controls=[
                sidebar,
                ft.VerticalDivider(width=1),
                ft.Container(
                    expand=True,
                    padding=20,
                    content=content
                )
            ]
        )
    )

    # Default view
    # system_gui_main(page,content)


ft.app(target=main)
