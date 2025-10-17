"""URL validation and security utilities."""
import requests
from urllib.parse import urlparse

def is_url_reachable(url, timeout=5):
    """Check if URL is reachable with HEAD request.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Boolean indicating if URL is reachable
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except requests.RequestException:
        return False

def is_malicious_url(url):
    """Basic malicious URL detection.
    
    Args:
        url: URL to check
        
    Returns:
        Boolean indicating if URL appears malicious
    """
    parsed = urlparse(url)
    
    # Basic blacklist check
    suspicious_domains = [
        'bit.ly', 'tinyurl.com', 'short.link',  # Avoid nested shorteners
        'malware.com', 'phishing.com'  # Example blacklist
    ]
    
    suspicious_keywords = [
        'phishing', 'malware', 'virus', 'hack', 'scam'
    ]
    
    domain = parsed.netloc.lower()
    full_url = url.lower()
    
    # Check domain blacklist
    if any(suspicious in domain for suspicious in suspicious_domains):
        return True
        
    # Check for suspicious keywords
    if any(keyword in full_url for keyword in suspicious_keywords):
        return True
        
    return False