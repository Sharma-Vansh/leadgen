"""
Tier 2 Verifier: Official Domain Whitelist
Verifies if an extracted destination URL belongs to a legitimate Indian Govt, PSU, or Academic portal.
"""
from urllib.parse import urlparse
from typing import Set

ALLOWED_TLDS: Set[str] = {
    ".gov.in",
    ".nic.in",
    ".ac.in",
    ".edu.in",
    ".res.in",
    ".org.in"
}

ALLOWED_EXPLICIT_DOMAINS: Set[str] = {
    "ssc.gov.in",
    "upsc.gov.in",
    "ibps.in",
    "indianrailways.gov.in",
    "drdo.gov.in",
    "isro.gov.in",
    "barc.gov.in",
    "joinindianarmy.nic.in",
    "joinindiannavy.gov.in",
    "careerindianairforce.cdac.in",
    "sarkariresult.com",
    "freejobalert.com"
}


class DomainWhitelistVerifier:
    @classmethod
    def is_official_govt_domain(cls, url: str) -> bool:
        if not url:
            return False
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]

            # Check explicit domains
            if netloc in ALLOWED_EXPLICIT_DOMAINS:
                return True

            # Check official government suffixes
            for suffix in ALLOWED_TLDS:
                if netloc.endswith(suffix):
                    return True

            return False
        except Exception:
            return False
