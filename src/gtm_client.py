import os
import json
import sys
from typing import Dict, List, Optional
from authentication import refresh_access_token

# Add path for helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'helpers')))
from http_client import HTTPClient

class GTMClient:
    """
    A basic client for Google Tag Manager API v2 using the Python standard library.
    Manages access token automatically using a refresh token.
    """
    BASE_URL = "https://tagmanager.googleapis.com/tagmanager/v2"

    def __init__(
        self,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        self.refresh_token = refresh_token or os.getenv("GTM_REFRESH_TOKEN")
        self.client_id = client_id or os.getenv("GTM_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("GTM_CLIENT_SECRET")
        self.access_token = access_token # Can be None initially
        self.headers = {
            "Content-Type": "application/json"
        }

    def _refresh_access_token(self):
        """
        Refreshes the access token using the refresh token.
        """
        self.access_token = refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token
        )

    def _get_headers(self) -> Dict:
        """
        Returns headers with the current access token.
        """
        if not self.access_token:
            self._refresh_access_token()
        
        headers = self.headers.copy()
        headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _request(self, method: str, path: str, **kwargs) -> Dict:
        """
        Centralized request handler with automatic token refresh on 401.
        """
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        
        # Try request
        response = HTTPClient.request(method, url, headers=self._get_headers(), **kwargs)
        
        if response.status_code == 401:
            # Token might be expired, refresh and retry once
            self._refresh_access_token()
            response = HTTPClient.request(method, url, headers=self._get_headers(), **kwargs)
            
        response.raise_for_status()
        
        if method == "DELETE":
            return {}
        return response.json()

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        return self._request("GET", path, params=params)

    def _post(self, path: str, data: Dict) -> Dict:
        return self._request("POST", path, json=data)

    def _put(self, path: str, data: Dict) -> Dict:
        return self._request("PUT", path, json=data)

    def _delete(self, path: str) -> None:
        self._request("DELETE", path)

    def list_accounts(self, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all GTM accounts the user has access to.
        Endpoint: GET /accounts
        """
        data = self._get("accounts", params={"pageToken": page_token})
        if "nextPageToken" in data:
            return data.get("account", []) + self.list_accounts(data["nextPageToken"])
        else:
            return data.get("account", [])

    def list_containers(self, account_path: str, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all containers in a specific account.
        account_path: e.g., 'accounts/12345'
        Endpoint: GET /{account_path}/containers
        """
        data = self._get(f"{account_path}/containers", params={"pageToken": page_token})
        containers = data.get("container", [])
        if "nextPageToken" in data:
            return containers + self.list_containers(account_path, data["nextPageToken"])
        return containers

    def list_workspaces(self, container_path: str, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all workspaces in a specific container.
        container_path: e.g., 'accounts/12345/containers/67890'
        Endpoint: GET /{container_path}/workspaces
        """
        data = self._get(f"{container_path}/workspaces", params={"pageToken": page_token})
        workspaces = data.get("workspace", [])
        if "nextPageToken" in data:
            return workspaces + self.list_workspaces(container_path, data["nextPageToken"])
        return workspaces

    def create_workspace(self, container_path: str, workspace_body: Dict) -> Dict:
        """
        Creates a new workspace in a container.
        workspace_body: e.g., {"name": "Test Workspace", "description": "..."}
        """
        return self._post(f"{container_path}/workspaces", workspace_body)

    def delete_workspace(self, workspace_path: str) -> None:
        """
        Deletes a workspace.
        """
        self._delete(workspace_path)

    def get_workspace(self, workspace_path: str) -> Dict:
        """
        Gets a specific workspace.
        workspace_path: e.g., 'accounts/12345/containers/67890/workspaces/1'
        """
        return self._get(workspace_path)

    def list_tags(self, workspace_path: str, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all tags in a workspace.
        """
        data = self._get(f"{workspace_path}/tags", params={"pageToken": page_token})
        tags = data.get("tag", [])
        if "nextPageToken" in data:
            return tags + self.list_tags(workspace_path, data["nextPageToken"])
        return tags

    def list_triggers(self, workspace_path: str, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all triggers in a workspace.
        """
        data = self._get(f"{workspace_path}/triggers", params={"pageToken": page_token})
        triggers = data.get("trigger", [])
        if "nextPageToken" in data:
            return triggers + self.list_triggers(workspace_path, data["nextPageToken"])
        return triggers

    def list_variables(self, workspace_path: str, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all variables in a workspace.
        """
        data = self._get(f"{workspace_path}/variables", params={"pageToken": page_token})
        variables = data.get("variable", [])
        if "nextPageToken" in data:
            return variables + self.list_variables(workspace_path, data["nextPageToken"])
        return variables

    # Write operations for Tags
    def create_tag(self, workspace_path: str, tag_body: Dict) -> Dict:
        """
        Creates a new tag in a workspace.
        """
        return self._post(f"{workspace_path}/tags", tag_body)

    def update_tag(self, tag_path: str, tag_body: Dict) -> Dict:
        """
        Updates an existing tag.
        tag_path: e.g., 'accounts/123/containers/456/workspaces/7/tags/8'
        """
        return self._put(tag_path, tag_body)

    def delete_tag(self, tag_path: str) -> None:
        """
        Deletes a tag.
        """
        self._delete(tag_path)

    # Write operations for Triggers
    def create_trigger(self, workspace_path: str, trigger_body: Dict) -> Dict:
        """
        Creates a new trigger in a workspace.
        """
        return self._post(f"{workspace_path}/triggers", trigger_body)

    def update_trigger(self, trigger_path: str, trigger_body: Dict) -> Dict:
        """
        Updates an existing trigger.
        """
        return self._put(trigger_path, trigger_body)

    def delete_trigger(self, trigger_path: str) -> None:
        """
        Deletes a trigger.
        """
        self._delete(trigger_path)

    # Write operations for Variables
    def create_variable(self, workspace_path: str, variable_body: Dict) -> Dict:
        """
        Creates a new variable in a workspace.
        """
        return self._post(f"{workspace_path}/variables", variable_body)

    def update_variable(self, variable_path: str, variable_body: Dict) -> Dict:
        """
        Updates an existing variable.
        """
        return self._put(variable_path, variable_body)

    def delete_variable(self, variable_path: str) -> None:
        """
        Deletes a variable.
        """
        self._delete(variable_path)

    # Built-in Variables Operations
    def list_built_in_variables(self, workspace_path: str, page_token: Optional[str] = None) -> List[Dict]:
        """
        Lists all enabled built-in variables in a workspace.
        """
        data = self._get(f"{workspace_path}/built_in_variables", params={"pageToken": page_token})
        variables = data.get("builtInVariable", [])
        if "nextPageToken" in data:
            return variables + self.list_built_in_variables(workspace_path, data["nextPageToken"])
        return variables

    def create_built_in_variables(self, workspace_path: str, variable_types: List[str]) -> List[Dict]:
        """
        Enables one or more built-in variables in a workspace.
        variable_types: List of built-in variable types (e.g., ['pageUrl', 'clickElement'])
        """
        # Create query parameters for multiple types if needed
        # The API expects type[]=pageUrl&type[]=clickElement
        params = [("type", t) for t in variable_types]
        
        # We need to use the lower level _request to handle multiple params with same key
        url = f"{self.BASE_URL}/{workspace_path.lstrip('/')}/built_in_variables"
        response = HTTPClient.request("POST", url, headers=self._get_headers(), params=params)
        
        if response.status_code == 401:
            self._refresh_access_token()
            response = HTTPClient.request("POST", url, headers=self._get_headers(), params=params)
            
        response.raise_for_status()
        data = response.json()
        return data.get("builtInVariable", [])

    def revert_built_in_variable(self, workspace_path: str, variable_type: str) -> Dict:
        """
        Disables (reverts) a built-in variable in a workspace.
        """
        path = f"{workspace_path}/built_in_variables:revert"
        # The API expects a single type parameter for revert
        params = {"type": variable_type}
        
        # We use _request but we need to pass params correctly
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        response = HTTPClient.request("POST", url, headers=self._get_headers(), params=params)
        
        if response.status_code == 401:
            self._refresh_access_token()
            response = HTTPClient.request("POST", url, headers=self._get_headers(), params=params)
            
        response.raise_for_status()
        # Revert usually returns 204 No Content or similar, but let's try to return JSON if any
        try:
            return response.json()
        except:
            return {}


if __name__ == "__main__":
    # Add helpers to path to import load_env_file
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'helpers')))
    from env_loader import load_env_file
    
    load_env_file()
    client = GTMClient()
    accounts = client.list_accounts()
    print(accounts)