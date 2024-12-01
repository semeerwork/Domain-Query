import whois
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

def fetch_whois_info(domain):
    """
    Fetch WHOIS information for the given domain.

    Args:
        domain (str): The domain name to query.

    Returns:
        dict: A dictionary containing WHOIS information or raises an exception.
    """
    if not is_valid_domain(domain):
        raise ValueError("Invalid domain format.")

    try:
        w = whois.whois(domain)

        # Prepare the WHOIS information
        whois_info = {
            'Registrar': w.registrar,
            'Created Date': w.creation_date,
            'Expiry Date': w.expiration_date,
            'Status': w.status,
            'Nameservers': w.nameservers
        }

        # Filter out None values
        return {key: value for key, value in whois_info.items() if value is not None}

    except whois.WhoisException as e:
        raise RuntimeError(f"WHOIS query failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        domain = input("Enter a domain to fetch WHOIS info: ")
        result = fetch_whois_info(domain)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
