from __future__ import annotations
import os
import time
import requests

BIS_ECFR_PART_746 = "https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C/part-746"
OFAC_COUNTRY_INFO = "https://ofac.treasury.gov/sanctions-programs-and-country-information"

def download_if_needed(cache_dir: str = "data/regdocs", max_age_hours: int = 24) -> dict:
    """
    Downloads (and caches) regulatory sources so the demo works reliably.
    - Cache refreshes every max_age_hours.
    Returns dict with local file paths.
    """
    os.makedirs(cache_dir, exist_ok=True)

    targets = {
        "bis_part_746_html": (BIS_ECFR_PART_746, os.path.join(cache_dir, "bis_part_746.html")),
        "ofac_country_info_html": (OFAC_COUNTRY_INFO, os.path.join(cache_dir, "ofac_country_info.html")),
    }

    def is_stale(path: str) -> bool:
        if not os.path.exists(path):
            return True
        age_sec = time.time() - os.path.getmtime(path)
        return age_sec > (max_age_hours * 3600)

    headers = {
        "User-Agent": "RegulatedShippingAdvisorDemo/1.0 (Streamlit; +https://example.com)"
    }

    out = {}
    for key, (url, path) in targets.items():
        if is_stale(path):
            r = requests.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            with open(path, "w", encoding="utf-8") as f:
                f.write(r.text)
        out[key] = path

    return out
