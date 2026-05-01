from unittest.mock import MagicMock, patch

from sirocco.api import fetch_pollen


def test_fetch_pollen_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "hourly": {
            "time": ["2026-05-01T00:00", "2026-05-01T01:00"],
            "grass_pollen": [10.0, 15.0],
            "alder_pollen": [0.0, 0.0],
            "birch_pollen": [5.0, 8.0],
            "mugwort_pollen": [None, None],
            "ragweed_pollen": [0.0, 0.0],
        }
    }
    mock_resp.raise_for_status = MagicMock()
    with patch("sirocco.api.httpx.get", return_value=mock_resp):
        result = fetch_pollen(51.0, -0.1, "Europe/London")
    assert "time" in result
    assert "grass_pollen" in result
    assert result["grass_pollen"] == [10.0, 15.0]


def test_fetch_pollen_error_returns_empty():
    with patch("sirocco.api.httpx.get", side_effect=Exception("timeout")):
        result = fetch_pollen(51.0, -0.1, "Europe/London")
    assert result == {}


def test_fetch_pollen_http_error_returns_empty():
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("404")
    with patch("sirocco.api.httpx.get", return_value=mock_resp):
        result = fetch_pollen(51.0, -0.1, "Europe/London")
    assert result == {}
