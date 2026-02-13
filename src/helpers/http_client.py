import urllib.request
import urllib.error
import urllib.parse
import json as json_lib
from typing import Dict, Optional, Any, Union

class HTTPResponse:
    """
    Simulates a requests.Response object.
    """
    def __init__(self, status_code: int, body: bytes, headers: Any):
        self.status_code = status_code
        self.content = body
        self.headers = headers
    
    def json(self) -> Any:
        return json_lib.loads(self.content.decode("utf-8"))
    
    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise Exception(f"HTTP Error {self.status_code}: {self.text}")

class HTTPClient:
    """
    A standard library based HTTP client using urllib.
    """
    @staticmethod
    def request(
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPResponse:
        """
        Sends an HTTP request using urllib.
        """
        if params:
            # Handle both dict and sequence of tuples
            if isinstance(params, dict):
                filtered_params = {k: v for k, v in params.items() if v is not None}
            else:
                filtered_params = [(k, v) for k, v in params if v is not None]
                
            if filtered_params:
                query = urllib.parse.urlencode(filtered_params)
                url = f"{url}?{query}"
        
        request_headers = headers.copy() if headers else {}
        
        body = None
        if json is not None:
            body = json_lib.dumps(json).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        elif data is not None:
            if isinstance(data, dict):
                body = urllib.parse.urlencode(data).encode("utf-8")
                request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
            else:
                body = data
        
        req = urllib.request.Request(url, data=body, headers=request_headers, method=method)
        
        try:
            with urllib.request.urlopen(req) as resp:
                return HTTPResponse(resp.getcode(), resp.read(), resp.info())
        except urllib.error.HTTPError as e:
            return HTTPResponse(e.code, e.read(), e.info())
        except Exception as e:
            raise e

    @classmethod
    def get(cls, url: str, **kwargs) -> HTTPResponse:
        return cls.request("GET", url, **kwargs)

    @classmethod
    def post(cls, url: str, **kwargs) -> HTTPResponse:
        return cls.request("POST", url, **kwargs)

    @classmethod
    def put(cls, url: str, **kwargs) -> HTTPResponse:
        return cls.request("PUT", url, **kwargs)

    @classmethod
    def patch(cls, url: str, **kwargs) -> HTTPResponse:
        return cls.request("PATCH", url, **kwargs)

    @classmethod
    def delete(cls, url: str, **kwargs) -> HTTPResponse:
        return cls.request("DELETE", url, **kwargs)
