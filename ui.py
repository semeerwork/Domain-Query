import flet as ft
from whois import fetch_whois_info
from dns import fetch_dns_records

def build_ui(page: ft.Page):
    # Status bar
    status_bar = ft.Text("Ready", size=12, color=ft.colors.GRAY)

    # Domain input and buttons
    domain_input = ft.TextField(label="Enter Domain", width=300)
    fetch_button = ft.IconButton(icon=ft.icons.SEARCH, tooltip="Fetch Data")
    refresh_button = ft.IconButton(icon=ft.icons.REFRESH, tooltip="Refresh Data")
    theme_toggle = ft.IconButton(icon=ft.icons.BRIGHTNESS_6, tooltip="Toggle Dark/Light Mode")

    # Tab content
    whois_content = ft.Column()
    dns_content = ft.Column()

    loading_indicator = ft.ProgressRing(visible=False)

    def update_status(message):
        status_bar.value = message
        page.update()

    async def fetch_data(e):
        domain = domain_input.value.strip()
        if not domain:
            update_status("Error: Invalid Domain")
            return

        loading_indicator.visible = True
        update_status("Fetching Data...")
        page.update()

        try:
            whois_info = await fetch_whois_info(domain)
            dns_info = await fetch_dns_records(domain)

            # Clear previous content
            whois_content.controls.clear()
            dns_content.controls.clear()

            # Populate WHOIS data
            if whois_info:
                for key, value in whois_info.items():
                    whois_content.controls.append(
                        ft.Card(
                            content=ft.Row([ft.Text(key), ft.Text(value)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            elevation=2,
                        )
                    )

            # Populate DNS data
            for record_type, records in dns_info.items():
                dns_content.controls.append(
                    ft.Collapsible(
                        label=record_type,
                        content=ft.Column([ft.Text(record) for record in records]),
                    )
                )

            update_status("Ready")
        except Exception as e:
            update_status(f"Error: {str(e)}")

        loading_indicator.visible = False
        page.update()

    fetch_button.on_click = fetch_data
    refresh_button.on_click = fetch_data

    # Dark/Light mode toggle
    def toggle_theme(e):
        if page.theme == ft.ThemeMode.LIGHT:
            page.theme = ft.ThemeMode.DARK
            theme_toggle.icon = ft.icons.BRIGHTNESS_7
        else:
            page.theme = ft.ThemeMode.LIGHT
            theme_toggle.icon = ft.icons.BRIGHTNESS_6
        page.update()

    theme_toggle.on_click = toggle_theme

    # Tabs
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="WHOIS", content=whois_content),
            ft.Tab(text="DNS", content=dns_content),
        ],
    )

    # Layout
    page.add(
        ft.Row([domain_input, fetch_button, refresh_button, theme_toggle]),
        loading_indicator,
        tabs,
        status_bar,
    )

    # Keyboard Navigation
    page.on_key_down = lambda e: (
        tabs.selected_index = (tabs.selected_index + 1) % len(tabs.tabs) if e.key == ft.KeyCode.TAB else None
    )
