import dns.resolver
import re

def is_valid_domain(domain):
    """
    Validate the domain format using a regular expression.

    Args:
        domain (str): The domain name to validate.

    Returns:
        bool: True if the domain is valid, False otherwise.
    """
    regex = r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}$'
    return re.match(regex, domain) is not None

def fetch_dns_records(domain, record_type):
    """
    Fetch DNS records for the given domain and record type.

    Args:
        domain (str): The domain name to query.
        record_type (str): The type of DNS record to fetch (e.g., 'A', 'AAAA', 'MX', 'CNAME').

    Returns:
        list: A list of DNS records or raises an exception.
    """
    if not is_valid_domain(domain):
        raise ValueError("Invalid domain format.")

    try:
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(domain, record_type)
        return [str(record) for record in answers]

    except dns.resolver.NoAnswer:
        return f"No answer for {record_type} record of {domain}."
    except dns.resolver.NXDOMAIN:
        raise RuntimeError(f"The domain {domain} does not exist.")
    except dns.resolver.Timeout:
        raise RuntimeError("DNS query timed out.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        domain = input("Enter a domain to fetch DNS records: ")
        record_type = input("Enter the record type (A, AAAA, MX, CNAME): ").upper()
        records = fetch_dns_records(domain, record_type)
        print(f"{record_type} records for {domain}: {records}")
    except Exception as e:
        print(f"Error: {e}")
