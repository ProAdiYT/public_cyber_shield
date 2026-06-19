import math
import re
from urllib.parse import urlparse
import requests
from collections import Counter

class URLExtractor:
    def __init__(self):
        # Common high-risk TLDs
        self.high_risk_tlds = {
            'xyz', 'top', 'click', 'club', 'info', 'live', 'cc', 'su', 'ru', 'online', 'vip', 'work', 'gq', 'cf', 'tk', 'ml'
        }
        # Phishing/scam indicator keywords
        self.suspicious_keywords = [
            'login', 'verify', 'bank', 'upi', 'pay', 'kyc', 'secure', 'update', 'account', 'signin', 
            'wallet', 'bonus', 'gift', 'free', 'reward', 'claims', 'support', 'helpdesk', 'office'
        ]

    def get_entropy(self, text):
        """Calculates Shannon Entropy of a string."""
        if not text:
            return 0
        counts = Counter(text)
        length = len(text)
        entropy = 0.0
        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    def extract_features(self, url, skip_lookup=False):
        """Extracts text-based and network-based features from a URL."""
        # Ensure url starts with a scheme for proper parsing
        if not re.match(r'^https?://', url, re.IGNORECASE):
            # Default to http for parsing if no scheme given
            parsed_url = urlparse('http://' + url)
        else:
            parsed_url = urlparse(url)

        hostname = parsed_url.hostname or ''
        path = parsed_url.path or ''
        query = parsed_url.query or ''
        
        url_len = len(url)
        is_https = 1 if url.lower().startswith('https://') else 0
        
        # Subdomains check
        domain_parts = hostname.split('.')
        # E.g. www.google.com has parts ['www', 'google', 'com'] -> subdomain count is 1 (www)
        # If it's just google.com, parts is ['google', 'com'] -> subdomain count is 0
        if len(domain_parts) > 2:
            subdomains = len(domain_parts) - 2
        else:
            subdomains = 0
            
        hostname_len = len(hostname)
        
        # Count digits
        digit_count = sum(c.isdigit() for c in url)
        digit_ratio = digit_count / url_len if url_len > 0 else 0
        
        # Count special characters
        special_chars = re.sub(r'[a-zA-Z0-9]', '', url)
        special_ratio = len(special_chars) / url_len if url_len > 0 else 0
        
        # Entropy
        entropy = self.get_entropy(url)
        
        # Suspicious keywords
        keyword_count = sum(1 for kw in self.suspicious_keywords if kw in url.lower())
        
        # TLD Risk
        tld = domain_parts[-1].lower() if domain_parts else ''
        tld_risk = 1 if tld in self.high_risk_tlds else 0
        
        # Redirect count via HTTP request check (non-blocking lookup with low timeout)
        redirect_count = 0
        if not skip_lookup:
            try:
                # Add scheme if missing
                req_url = url if re.match(r'^https?://', url, re.IGNORECASE) else 'http://' + url
                response = requests.head(req_url, allow_redirects=True, timeout=1.5)
                redirect_count = len(response.history)
            except Exception:
                # Fallback to 0 if server offline or DNS lookup fails
                redirect_count = 0
            
        return {
            'URLLength': url_len,
            'IsHTTPS': is_https,
            'NoOfSubDomain': subdomains,
            'DomainLength': hostname_len,
            'DegitRatioInURL': digit_ratio,
            'SpacialCharRatioInURL': special_ratio,
            'Entropy': entropy,
            'SuspiciousKeywordsCount': keyword_count,
            'TLDRisk': tld_risk,
            'NoOfURLRedirect': redirect_count
        }
