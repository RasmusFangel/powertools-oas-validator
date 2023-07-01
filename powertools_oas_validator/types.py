from dataclasses import dataclass
from typing import Any, Dict, Hashable, Mapping


@dataclass
class LoadedSpec:
    spec_dict: Mapping[Hashable, Any]
    spec_url: str


class ValidationConfig:
    config: Dict[str, bool]

    def __init__(
        self,
        validate_body: bool = True,
        validate_headers: bool = True,
        validate_query: bool = True,
        validate_path: bool = True,
        validate_cookies: bool = True,
    ) -> None:
        self.config = {
            "body": validate_body,
            "headers": validate_headers,
            "query": validate_query,
            "path": validate_path,
            "cookies": validate_cookies,
        }
