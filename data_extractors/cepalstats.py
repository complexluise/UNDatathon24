import requests
from typing import Optional, Dict, Union, List
from dataclasses import dataclass
from enum import Enum


class Language(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"


class Format(str, Enum):
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    EXCEL = "excel"


@dataclass
class CepalstatConfig:
    base_url: str = "https://api-cepalstat.cepal.org"
    language: Language = Language.ENGLISH
    format: Format = Format.JSON


class CepalstatAPI:
    """
    Python SDK for interacting with the CEPALSTAT API.
    """

    def __init__(self, config: Optional[CepalstatConfig] = None):
        """
        Initialize the CEPALSTAT API client.

        Args:
            config: Optional configuration object. If not provided, defaults will be used.
        """
        self.config = config or CepalstatConfig()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the CEPALSTAT API.

        Args:
            endpoint: API endpoint to call
            params: Optional query parameters

        Returns:
            API response as dictionary
        """
        url = f"{self.config.base_url}{endpoint}"
        default_params = {
            "lang": self.config.language.value,
            "format": self.config.format.value
        }
        if params:
            default_params.update(params)

        response = requests.get(url, params=default_params)
        response.raise_for_status()
        return response.json()

    def get_thematic_tree(self) -> Dict:
        """
        Get the thematic tree of areas and indicators.

        Returns:
            Dictionary containing the thematic tree structure
        """
        return self._make_request("/cepalstat/api/v1/thematic-tree")

    def get_indicator_publications(self, indicator_id: int) -> Dict:
        """
        Get publications related to a specific indicator.

        Args:
            indicator_id: ID of the indicator

        Returns:
            Dictionary containing related publications
        """
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/publications")

    def get_indicator_dimensions(
            self,
            indicator_id: int,
            include_all: bool = False,
            include_path: bool = False
    ) -> Dict:
        """
        Get dimensions for a specific indicator.

        Args:
            indicator_id: ID of the indicator
            include_all: If True, includes all dimension disaggregations. If False, only present ones
            include_path: If True, includes dimensional member path

        Returns:
            Dictionary containing indicator dimensions
        """
        params = {
            "in": 1 if not include_all else 0,
            "path": 1 if include_path else 0
        }
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/dimensions", params)

    def get_indicator_footnotes(self, indicator_id: int) -> Dict:
        """
        Get footnotes for a specific indicator.

        Args:
            indicator_id: ID of the indicator

        Returns:
            Dictionary containing indicator footnotes
        """
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/footnotes")

    def get_indicator_metadata(self, indicator_id: int) -> Dict:
        """
        Get metadata for a specific indicator.

        Args:
            indicator_id: ID of the indicator

        Returns:
            Dictionary containing indicator metadata
        """
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/metadata")

    def get_indicator_sources(self, indicator_id: int) -> Dict:
        """
        Get sources for a specific indicator.

        Args:
            indicator_id: ID of the indicator

        Returns:
            Dictionary containing indicator sources
        """
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/sources")

    def get_indicator_records(
            self,
            indicator_id: int,
            members: Optional[List[Union[int, str]]] = None
    ) -> Dict:
        """
        Get data records for a specific indicator.

        Args:
            indicator_id: ID of the indicator
            members: Optional list of dimension members to filter by

        Returns:
            Dictionary containing indicator records
        """
        params = {}
        if members:
            params["members"] = ",".join(str(m) for m in members)
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/records", params)

    def get_indicator_areas(self, indicator_id: int) -> Dict:
        """
        Get areas for a specific indicator.

        Args:
            indicator_id: ID of the indicator

        Returns:
            Dictionary containing indicator areas
        """
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/areas")

    def get_indicator_data(
            self,
            indicator_id: int,
            members: Optional[List[Union[int, str]]] = None,
            include_all: bool = False,
            include_path: bool = False
    ) -> Dict:
        """
        Get complete data for a specific indicator including metadata, dimensions, sources, and notes.

        Args:
            indicator_id: ID of the indicator
            members: Optional list of dimension members to filter by
            include_all: If True, includes all dimension disaggregations. If False, only present ones
            include_path: If True, includes dimensional member path

        Returns:
            Dictionary containing complete indicator information
        """
        params = {
            "in": 1 if not include_all else 0,
            "path": 1 if include_path else 0
        }
        if members:
            params["members"] = ",".join(str(m) for m in members)
        return self._make_request(f"/cepalstat/api/v1/indicator/{indicator_id}/data", params)


if __name__ == "__main__":
    cepalstat_api = CepalstatAPI()
    #thematic_tree = cepalstat_api.get_thematic_tree()

    print(cepalstat_api.get_indicator_metadata(4263))

