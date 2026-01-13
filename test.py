import flet as ft
import os

def main(page: ft.Page):
    page.title = "Flet Linux Notification Demo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def send_notification(e):
        title = "Flet Notification"
        message = "This is a desktop notification from your Flet app on Linux!"
        # Command to execute notify-send
        command = f'notify-send "{title}" "{message}"'
        
        # Execute the command in the shell
        os.system(command)
        
        # Optional: Provide in-app feedback
        page.add(ft.Text("Notification sent!"))

    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "Send Desktop Notification",
                    on_click=send_notification,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
