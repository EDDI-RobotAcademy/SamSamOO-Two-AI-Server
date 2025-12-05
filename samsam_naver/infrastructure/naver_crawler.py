import re

def extract_catalog_id(url: str):
    match = re.search(r"/catalog/(\d+)", url)
    if match:
        return match.group(1)

    match = re.search(r"/products?/(\d+)", url)
    if match:
        return match.group(1)

    return None
