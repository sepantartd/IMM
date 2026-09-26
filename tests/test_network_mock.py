"""
Network Mock Test Suite for IMM.
Simulates Instagram API HTTP responses using unittest.mock to test error handling and edge cases.
"""

import unittest
from unittest.mock import patch, MagicMock
import httpx
from app.instagram.client import InstagramClient
from app.utils.exceptions import InstagramAPIError


class TestNetworkMock(unittest.TestCase):
    """Mock tests for network requests, rate limits, and API error status codes."""

    def setUp(self):
        self.client = InstagramClient()

    def tearDown(self):
        self.client.close()

    @patch.object(httpx.Client, "get")
    def test_fetch_user_reels_success_mock(self, mock_get):
        """Tests successful retrieval of user reels with mocked HTTP response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "edge_owner_to_timeline_media": {
                        "edges": [
                            {
                                "node": {
                                    "id": "mock_reel_123",
                                    "shortcode": "sc_123",
                                    "is_video": True,
                                    "edge_media_to_caption": {
                                        "edges": [{"node": {"text": "Python automation #code"}}]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_get.return_value = mock_response

        reels = self.client.get_user_reels("test_user", limit=1)
        self.assertEqual(len(reels), 1)
        self.assertEqual(reels[0].reel_id, "mock_reel_123")
        self.assertIn("Python automation", reels[0].caption)

    @patch.object(httpx.Client, "post")
    def test_post_comment_rate_limited_429_mock(self, mock_post):
        """Tests 429 Too Many Requests error handling during comment submission."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_post.return_value = mock_response

        with self.assertRaises(InstagramAPIError) as ctx:
            self.client.post_comment(reel_id="mock_123", comment_text="Great post!")

        self.assertEqual(ctx.exception.status_code, 429)

    @patch.object(httpx.Client, "get")
    def test_auth_error_401_mock(self, mock_get):
        """Tests 401 Unauthorized handling during API requests."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        with self.assertRaises(InstagramAPIError) as ctx:
            self.client.get_user_reels("private_user")

        self.assertEqual(ctx.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
