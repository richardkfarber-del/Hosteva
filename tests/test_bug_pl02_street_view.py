"""BUG-PL-02: Street View / Places image — geocode retry before stock; placeholder labeled."""
import os
from unittest.mock import MagicMock, patch

import pytest

from app.routers.properties import (
    FALLBACK_PROPERTY_IMAGE_URL,
    fetch_real_property_image,
    is_fallback_property_image,
)


STABLE_RUN = "15758 Stable Run Drive, Spring Hill, FL 34610"
FORMATTED = "15758 Stable Run Dr, Spring Hill, FL 34610, USA"
LATLNG = "28.4741,-82.5301"


def _mock_resp(status_code=200, json_data=None, content=b"", text=""):
    r = MagicMock()
    r.status_code = status_code
    r.json.return_value = json_data or {}
    r.content = content
    r.text = text or str(json_data or "")
    return r


def test_is_fallback_helpers():
    assert is_fallback_property_image(None) is True
    assert is_fallback_property_image("") is True
    assert is_fallback_property_image(FALLBACK_PROPERTY_IMAGE_URL) is True
    assert is_fallback_property_image("/static/property_images/abc.jpg") is False


@patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False)
@patch("app.routers.properties.requests.get")
def test_raw_street_view_ok_no_geocode_needed(mock_get):
    """Happy path: metadata OK on raw address → property_images, no geocode."""
    meta = _mock_resp(200, {"status": "OK"}, text='{"status":"OK"}')
    img = _mock_resp(200, content=b"fake-jpeg-bytes")
    mock_get.side_effect = [meta, img]

    with patch("app.routers.properties.geocode_address") as mock_geo:
        url = fetch_real_property_image(STABLE_RUN)
        mock_geo.assert_not_called()

    assert url.startswith("/static/property_images/")
    assert url.endswith(".jpg")
    assert not is_fallback_property_image(url)
    # cleanup saved file
    disk = "app" + url  # /static/... -> app/static/...
    if os.path.exists(disk):
        os.remove(disk)


@patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False)
@patch("app.routers.properties.geocode_address")
@patch("app.routers.properties.requests.get")
def test_metadata_miss_retries_geocode_latlng_before_fallback(mock_get, mock_geo):
    """Hypothesis: metadata miss on raw address must retry geocode-normalized location."""
    mock_geo.return_value = {
        "city": "Spring Hill",
        "county": "Pasco County",
        "state": "FL",
        "address_components": [],
        "formatted_address": FORMATTED,
        "lat": 28.4741,
        "lng": -82.5301,
    }

    zero = _mock_resp(200, {"status": "ZERO_RESULTS"}, text='{"status":"ZERO_RESULTS"}')
    places_empty = _mock_resp(200, {"candidates": []}, text='{"candidates":[]}')
    # formatted address SV miss
    zero2 = _mock_resp(200, {"status": "ZERO_RESULTS"}, text='{"status":"ZERO_RESULTS"}')
    # latlng SV hit
    ok = _mock_resp(200, {"status": "OK"}, text='{"status":"OK"}')
    img = _mock_resp(200, content=b"latlng-jpeg")

    mock_get.side_effect = [zero, places_empty, zero2, ok, img]

    url = fetch_real_property_image(STABLE_RUN)
    assert url.startswith("/static/property_images/")
    assert not is_fallback_property_image(url)
    mock_geo.assert_called_once_with(STABLE_RUN)

    # Confirm a Street View metadata call used lat,lng
    locations = []
    for call in mock_get.call_args_list:
        args, kwargs = call
        url_arg = args[0] if args else ""
        params = kwargs.get("params") or {}
        if "streetview/metadata" in str(url_arg):
            locations.append(params.get("location"))
    assert LATLNG in locations

    disk = "app" + url
    if os.path.exists(disk):
        os.remove(disk)


@patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False)
@patch("app.routers.properties.requests.get")
def test_uses_passed_geocoded_without_second_geocode(mock_get):
    zero = _mock_resp(200, {"status": "ZERO_RESULTS"})
    places_empty = _mock_resp(200, {"candidates": []})
    ok = _mock_resp(200, {"status": "OK"})
    img = _mock_resp(200, content=b"fmt-jpeg")
    mock_get.side_effect = [zero, places_empty, ok, img]

    geo = {
        "formatted_address": FORMATTED,
        "lat": 28.4741,
        "lng": -82.5301,
        "city": "Spring Hill",
        "county": "Pasco",
        "state": "FL",
        "address_components": [],
    }
    with patch("app.routers.properties.geocode_address") as mock_geo:
        url = fetch_real_property_image(STABLE_RUN, geocoded=geo)
        mock_geo.assert_not_called()

    assert url.startswith("/static/property_images/")
    disk = "app" + url
    if os.path.exists(disk):
        os.remove(disk)


@patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}, clear=False)
@patch("app.routers.properties.geocode_address")
@patch("app.routers.properties.requests.get")
def test_all_misses_returns_fallback(mock_get, mock_geo):
    mock_geo.return_value = {
        "formatted_address": FORMATTED,
        "lat": 28.4741,
        "lng": -82.5301,
        "city": "Spring Hill",
        "county": "Pasco",
        "state": "FL",
        "address_components": [],
    }
    zero = _mock_resp(200, {"status": "ZERO_RESULTS"})
    places_empty = _mock_resp(200, {"candidates": []})
    # raw SV, raw Places, formatted SV, latlng SV, formatted Places
    mock_get.side_effect = [zero, places_empty, zero, zero, places_empty]

    url = fetch_real_property_image(STABLE_RUN)
    assert url == FALLBACK_PROPERTY_IMAGE_URL
    assert is_fallback_property_image(url) is True


@patch.dict(os.environ, {}, clear=True)
def test_no_api_key_returns_fallback():
    # Ensure neither alias is set
    os.environ.pop("GOOGLE_MAPS_API_KEY", None)
    os.environ.pop("Maps_API_KEY", None)
    url = fetch_real_property_image(STABLE_RUN)
    assert url == FALLBACK_PROPERTY_IMAGE_URL


def test_dashboard_labels_street_view_unavailable():
    """UI must label stock placeholder — not look like unlabeled real facade."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    # dashboard may redirect unauth — still serve template content via route or file
    resp = client.get("/dashboard")
    # Accept 200 or redirect; read template from disk if needed
    html = resp.text if resp.status_code == 200 else open("app/templates/dashboard.html").read()
    if "Street View unavailable" not in html:
        html = open("app/templates/dashboard.html").read()
    assert "Street View unavailable" in html
    assert "single-prop-image-placeholder-label" in html
    assert "property-card-image-placeholder-label" in html
    assert "image_is_placeholder" in html
