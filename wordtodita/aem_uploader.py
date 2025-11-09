import requests
from requests.auth import HTTPBasicAuth

def upload_to_aem(aem_url, username, password, dita_files):
    """Upload generated DITA files to AEM"""
    results = {}
    for filename, content in dita_files.items():
        resp = requests.put(
            f"{aem_url}/{filename}",
            data=content,
            headers={"Content-Type": "application/xml"},
            auth=HTTPBasicAuth(username, password),
        )
        results[filename] = resp.status_code
    return results
