"""Focused regression tests for deterministic personal website listing."""

from __future__ import annotations

import importlib
import os
import unittest
from unittest.mock import patch

from config import personal_links
from core.fast_router import fast_route
from core.routers.web_router import web_route
from services import personal_link_service


PERSONAL_ENV_KEYS = (
    "PERSONAL_GITHUB_URL",
    "PERSONAL_GITHUB_PROFILE_URL",
    "PERSONAL_GITHUB_REPOSITORIES_URL",
    "PERSONAL_FACEBOOK_URL",
    "PERSONAL_FACEBOOK_PROFILE_URL",
    "PERSONAL_LINKEDIN_URL",
    "PERSONAL_LINKEDIN_PROFILE_URL",
    "PERSONAL_WEBSITE_URL",
    "PERSONAL_PORTFOLIO_URL",
    "PERSONAL_IOT_URL",
    "PERSONAL_IOT_WEBSITE_URL",
    "IOTRIX_LAB_URL",
    "JARVIS_GITHUB_URL",
    "JARVIS_REPOSITORY_URL",
    "SMART_PARKING_URL",
    "ATMERS_URL",
)


class PersonalWebsiteListTests(unittest.TestCase):
    def setUp(self):
        self._environment = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._environment)
        importlib.reload(personal_links)

    def _links_with(self, **configured):
        values = {key: "" for key in PERSONAL_ENV_KEYS}
        values.update(configured)
        with patch.dict(os.environ, values, clear=False):
            return importlib.reload(personal_links)

    def test_existing_get_and_has_link_apis_remain_compatible(self):
        links = self._links_with(
            PERSONAL_GITHUB_URL="https://example.test/github",
        )

        self.assertEqual(
            links.get_link("github"),
            "https://example.test/github",
        )
        self.assertTrue(links.has_link("github"))
        self.assertFalse(links.has_link("portfolio"))

    def test_configured_links_omit_blank_invalid_and_duplicate_entries(self):
        links = self._links_with(
            PERSONAL_GITHUB_URL="https://example.test/profile",
            PERSONAL_GITHUB_PROFILE_URL="https://example.test/profile",
            PERSONAL_PORTFOLIO_URL="https://example.test/portfolio",
            PERSONAL_FACEBOOK_URL="javascript:alert(1)",
        )

        self.assertEqual(
            links.configured_links(),
            [
                {"name": "GitHub", "url": "https://example.test/profile"},
                {"name": "Portfolio", "url": "https://example.test/portfolio"},
            ],
        )
        self.assertTrue(links.is_safe_personal_url("http://example.test"))
        self.assertFalse(links.is_safe_personal_url("file:///C:/secret"))

    def test_website_list_variants_fast_route_without_ai_or_planner(self):
        variants = (
            "open website list",
            "show website list",
            "show my websites",
            "open my websites",
            "show my links",
            "open my links",
            "personal websites",
            "personal links",
        )

        for command in variants:
            with self.subTest(command=command):
                self.assertEqual(
                    web_route(command),
                    [{"action": "show_personal_links"}],
                )
                self.assertEqual(
                    fast_route(command),
                    [{"action": "show_personal_links"}],
                )

    def test_show_action_emits_structured_links_to_hud(self):
        entries = [
            {"name": "GitHub", "url": "https://example.test/github"},
            {"name": "Portfolio", "url": "https://example.test/portfolio"},
        ]

        with patch.object(
            personal_link_service,
            "configured_links",
            return_value=entries,
        ), patch.object(
            personal_link_service.HUDIntegration,
            "personal_links",
        ) as publish:
            result = personal_link_service.show_personal_links()

        publish.assert_called_once_with(entries)
        self.assertEqual(result, "Found 2 configured personal websites.")

    def test_show_action_handles_no_configured_links(self):
        with patch.object(
            personal_link_service,
            "configured_links",
            return_value=[],
        ), patch.object(
            personal_link_service.HUDIntegration,
            "personal_links",
        ) as publish:
            result = personal_link_service.show_personal_links()

        publish.assert_called_once_with([])
        self.assertEqual(result, "No personal websites are configured.")

    def test_existing_personal_link_opening_uses_the_browser_service(self):
        with patch.object(
            personal_link_service,
            "get_link",
            return_value="https://example.test/github",
        ), patch.object(
            personal_link_service.browser,
            "open",
            return_value=True,
        ) as open_url:
            self.assertTrue(personal_link_service.open_personal_link("github"))

        open_url.assert_called_once_with("https://example.test/github")


if __name__ == "__main__":
    unittest.main()
