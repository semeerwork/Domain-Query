import whois
import dns.resolver
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

def validate_domain(domain: str) -> bool:
    """
    Validates the format of a domain name.
    """
    domain_regex = r"^(?!\-)([a-zA-Z0-9\-]{1,63}(?<!\-)\.)+[a-zA-Z]{2,}$"
    return re.match(domain_regex, domain) is not None

def format_date(date) -> Optional[str]:
    """
    Formats a date or a list of dates into a string representation.
    """
    if isinstance(date, (list, tuple)):
        return [d.strftime("%b %d, %Y") for d in date if isinstance(d, datetime)]
    if isinstance(date, datetime):
        return date.strftime("%b %d, %Y")
    return None

def clean_status(status) -> Optional[str]:
    """
    Cleans the status by extracting the first word from it.
    """
    if isinstance(status, (list, tuple)):
        return [s.split()[0] for s in status]
    if isinstance(status, str):
        return status.split()[0]
    return None

def handle_error(message: str) -> Dict[str, str]:
    """
    Returns a structured error message.
    """
    return {"error": message}

def fetch_whois(domain: str) -> Optional[Dict[str, Any]]:
    """
    Fetches WHOIS information for the given domain and formats the output.
    Returns a dictionary with relevant details.
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

def fetch_dns_record(record_type: str, domain: str) -> Optional[List[str]]:
    """
    Fetches DNS records of a specific type for the given domain.
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ['8.8.8.8', '1.1.1.1']  # Google and Cloudflare DNS servers
    try:
        answers = resolver.resolve(domain, record_type)
        return [rdata.to_text() for rdata in answers]
    except dns.resolver.NoAnswer:
        return None
    except dns.resolver.NXDOMAIN:
        return handle_error(f"Domain '{domain}' does not exist.")
    except dns.resolver.Timeout:
        return handle_error("DNS query timed out. Please check your network and try again.")
    except Exception as e:
        return handle_error(f"Error retrieving {record_type} records: {str(e)}")

def fetch_dns_records(domain: str) -> Optional[Dict[str, Any]]:
    """
    Fetches DNS records for the given domain using Google and Cloudflare DNS servers as resolvers.
    
    :param domain: The domain to query DNS records for.
    :return: Dictionary with record types as keys and lists of records as values.
             Includes user-friendly messages for missing records and errors.
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
