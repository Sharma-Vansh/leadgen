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
    "agnipathvayu.cdac.in",
    "mod.gov.in",
    "assamrifles.gov.in",
    "ncs.gov.in",
    "pesb.gov.in",
    "employmentnews.gov.in",
    "hssc.gov.in",
    "upsssc.gov.in",
    "niti.gov.in",
    "meity.gov.in",
    "nic.in",
    "cdac.in",
    "bel-india.in",
    "careers.bhel.in",
    "bhel.in",
    "hal-india.co.in",
    "ongcindia.com",
    "iocl.com",
    "careers.ntpc.co.in",
    "ntpc.co.in",
    "powergrid.in",
    "gailonline.com",
    "coalindia.in",
    "rites.com",
    "rvnl.org",
    "dfccil.com",
    "fssai.gov.in",
    "epfindia.gov.in",
    "esic.gov.in",
    "irctc.com",
    "mprojgar.gov.in",
    "sarkariresult.com",
    "freejobalert.com",
    "sarkariexam.com",
    "govtjobsalert.in",
    "indgovtjobs.in",
    "rojgarresult.com",
    "sarkarijobfind.com"
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
