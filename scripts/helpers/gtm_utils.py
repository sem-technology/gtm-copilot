import re
import os
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

def resolve_gtm_path(provided_path: Optional[str], gtm_public_id: str) -> str:
    """
    Resolves the export/import path based on the provided path, environment variable, and GTM ID.
    
    Priority:
    1. provided_path (if not None)
    2. GTM_EXPORT_ROOT_PATH environment variable
    3. Default path: tmp/[[GTM_ID]]
    
    Replaces [[GTM_ID]] with the actual gtm_public_id.
    """
    path = provided_path
    if not path:
        path = os.getenv("GTM_EXPORT_ROOT_PATH")
    
    if not path:
        path = os.path.join("tmp", "[[GTM_ID]]")
        
    return path.replace("[[GTM_ID]]", gtm_public_id)
