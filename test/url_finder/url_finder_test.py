import pytest
import src.url_finder as url_finder
import time


@pytest.fixture(autouse=True)
def stub_nominatim_call(monkeypatch):
    """
    This fixture stubs the _get_location_of_coordinates function to return a fixed location.
    It prevents actual network calls during tests.
    """

    monkeypatch.setattr(
        url_finder.url_resolver,
        "_get_location_of_coordinates",
        lambda lat, lon: ("Bremgarten", "Switzerland"),
    )


def stub_duckduckgo_call(monkeypatch):
    """
    This fixture stubs the _get_url_of_coordinates_and_name function to return a fixed URL.
    It prevents actual network calls during tests.
    """

    monkeypatch.setattr(
        url_finder.url_resolver,
        "_get_url_of_coordinates_and_name",
        lambda rest_name, city, country: "https://www.restaurant-promenade.ch/",
    )


@pytest.mark.parametrize(
    "rest_name, lat, lon, expected_url",
    [("Köbis Promenade", 47.349098, 8.3464357, "https://www.restaurant-promenade.ch/")],
)
def test_does_url_get_returned(rest_name, lat, lon, expected_url):
    """
    This test, tests if the function retunrn a URL at all.
    """
    stub_duckduckgo_call(pytest.MonkeyPatch())
    url = url_finder.get_missing_url(rest_name, lat, lon)
    assert url is not None, "Expected a URL to be returned, but got None."


@pytest.mark.parametrize(
    "rest_name, lat, lon, expected_url",
    [("Köbis Promenade", 47.349098, 8.3464357, "https://www.restaurant-promenade.ch/")],
)
def test_get_missing_url(rest_name, lat, lon, expected_url):
    """
    Test the get_missing_url function with a known restaurant and its coordinates.
    It checks it 5 times and if the majority of the results match the expected URL it passes.
    Rarely the URL could be wrong due to variety of results of the DuckDuckGo search.

    """
    results = []
    print("\n")
    for i in range(5):
        url = url_finder.get_missing_url(rest_name, lat, lon)
        print(f"Attempt {i + 1}: Found URL: {url}")
        results.append(url)
        time.sleep(3)

    # Check if the expected URL is in the results at least 3 times
    assert (
        results.count(expected_url) >= 3
    ), f"Expected {expected_url} but got {results}"


if __name__ == "__main__":
    pytest.main()
