import re
from typing import Dict, Optional

def parse_gtm_workspace_url(url: str) -> Optional[Dict[str, str]]:
    """
    Parses a GTM workspace URL and returns a dictionary with account_id, container_id, and workspace_id.
    
    URL format: https://tagmanager.google.com/#/container/accounts/[ACCOUNT_ID]/containers/[CONTAINER_ID]/workspaces/[WORKSPACE_ID]
    """
    # Pattern to match the IDs in the URL
    pattern = r"accounts/(\d+)/containers/(\d+)/workspaces/(\d+)"
    match = re.search(pattern, url)
    
    if match:
        return {
            "account_id": match.group(1),
            "container_id": match.group(2),
            "workspace_id": match.group(3)
        }
    return None
