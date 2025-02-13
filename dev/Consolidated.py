# file: ui.py                               
import flet as ft
from utils import fetch_whois_info,fetch_dns_records

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


#file: utils.py

import whois
import dns.resolver
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

def validate_domain(domain: str) -> bool:
    """
    Validates the format of a domain name.
    """
    domain_regex = r"^(?!\-)([a-zA-Z0-9\-]{1,63}(?<!\-)\.)+[a-zA-Z]{2,}$"
    return bool(re.match(domain_regex, domain))

def format_date(date: Union[datetime, List[datetime]]) -> Union[Optional[str], List[str]]:
    """
    Formats a date or a list of dates into a string representation.
    """
    if isinstance(date, (list, tuple)):
        return [d.strftime("%b %d, %Y") for d in date if isinstance(d, datetime)]
    if isinstance(date, datetime):
        return date.strftime("%b %d, %Y")
    return None

def clean_status(status: Union[str, List[str]]) -> Union[Optional[str], List[str]]:
    """
    Cleans the status by extracting the first word from it.
    """
    if isinstance(status, (list, tuple)):
        return [s.split()[0] for s in status if isinstance(s, str)]
    if isinstance(status, str):
        return status.split()[0]
    return None

def handle_error(message: str) -> Dict[str, str]:
    """
    Returns a structured error message.
    """
    return {"error": message}

def fetch_whois(domain: str) -> Union[Dict[str, Any], Dict[str, str]]:
    """
    Fetches WHOIS information for the given domain and formats the output.
    """
    try:
        w = whois.whois(domain)
        return {
            "Registrar": w.registrar,
            "Created Date": format_date(w.creation_date),
            "Expiry Date": format_date(w.expiration_date),
            "Status": clean_status(w.status),
            "Nameservers": list(w.name_servers) if w.name_servers else None,
        }
    except whois.WhoisException as e:
        return handle_error(f"WHOIS lookup failed: {str(e)}")
    except Exception as e:
        return handle_error(f"An unexpected error occurred while fetching WHOIS information: {str(e)}")

def fetch_dns_record(record_type: str, domain: str) -> Union[List[str], Dict[str, str]]:
    """
    Fetches DNS records of a specific type for the given domain.
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ['8.8.8.8', '1.1.1.1']
    try:
        answers = resolver.resolve(domain, record_type)
        return [rdata.to_text() for rdata in answers]
    except dns.resolver.NoAnswer:
        return handle_error(f"No {record_type} records found.")
    except dns.resolver.NXDOMAIN:
        return handle_error(f"Domain '{domain}' does not exist.")
    except dns.resolver.Timeout:
        return handle_error("DNS query timed out. Please check your network.")
    except Exception as e:
        return handle_error(f"Error retrieving {record_type} records: {str(e)}")

def fetch_dns_records(domain: str) -> Dict[str, Union[List[str], str]]:
    """
    Fetches DNS records for the given domain using Google and Cloudflare DNS servers.
    """
    record_types = ['A', 'NS', 'CNAME', 'MX', 'TXT']
    records = {}

    for record_type in record_types:
        result = fetch_dns_record(record_type, domain)
        if isinstance(result, dict) and 'error' in result:
            records[record_type] = result['error']
        elif result is None:
            records[record_type] = f"No records found for {record_type}."
        else:
            records[record_type] = result

    return records
