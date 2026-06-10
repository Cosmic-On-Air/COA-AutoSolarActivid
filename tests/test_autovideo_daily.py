import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

import requests

from scripts import autovideo_daily


class FakeResponse:
    def __init__(self, status_code=200, text="", content=b"image"):
        self.status_code = status_code
        self.text = text
        self.content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class DummyExecutor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def map(self, func, items):
        return [func(item) for item in items]


class DownloadSohoImagesTests(unittest.TestCase):
    def test_falls_back_to_previous_archive_day(self):
        target_day = datetime(2026, 6, 10)

        def fake_http_get(url, **kwargs):
            if "20260610" in url:
                return FakeResponse(status_code=404)
            if url.endswith("/20260609/full_512.lst"):
                return FakeResponse(text="20260609_0000_c2_512.jpg\n20260609_0015_c2_512.jpg\n")
            if "20260609/" in url and url.endswith(".jpg"):
                return FakeResponse()
            return FakeResponse(status_code=404)

        with tempfile.TemporaryDirectory() as tmpdir, \
             patch.object(autovideo_daily, "BASE_DIR", tmpdir), \
             patch.object(autovideo_daily, "ThreadPoolExecutor", DummyExecutor), \
             patch.object(autovideo_daily, "http_get", side_effect=fake_http_get):
            paths = autovideo_daily.download_soho_images(target_day)

        self.assertEqual(len(paths), 2)
        self.assertTrue(all("soho_09062026_images" in path for path in paths))

    def test_uses_esa_mirror_when_primary_host_has_no_archive(self):
        target_day = datetime(2026, 6, 10)
        requested_urls = []

        def fake_http_get(url, **kwargs):
            requested_urls.append(url)
            if "soho.nascom.nasa.gov" in url:
                return FakeResponse(status_code=404)
            if url.endswith("/20260610/full_512.lst"):
                return FakeResponse(text="20260610_0000_c2_512.jpg\n")
            if "soho.esac.esa.int" in url and url.endswith(".jpg"):
                return FakeResponse()
            return FakeResponse(status_code=404)

        with tempfile.TemporaryDirectory() as tmpdir, \
             patch.object(autovideo_daily, "BASE_DIR", tmpdir), \
             patch.object(autovideo_daily, "ThreadPoolExecutor", DummyExecutor), \
             patch.object(autovideo_daily, "http_get", side_effect=fake_http_get):
            paths = autovideo_daily.download_soho_images(target_day)

        self.assertEqual(len(paths), 1)
        self.assertTrue(any("soho.esac.esa.int" in url for url in requested_urls))


if __name__ == "__main__":
    unittest.main()
