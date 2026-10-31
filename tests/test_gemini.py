import json
import unittest
from unittest.mock import patch
from rosa_core.gemini import GeminiClient, GeminiError

class FakeResponse:
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self):
        return json.dumps({"candidates":[{"content":{"parts":[{"text":"Namaste!"}]}}]}).encode()

class GeminiTests(unittest.TestCase):
    def test_missing_key_fails_safely(self):
        with self.assertRaises(GeminiError):
            GeminiClient(api_key="").generate("hello")
    @patch("urllib.request.urlopen", return_value=FakeResponse())
    def test_parses_response_and_sends_key_header(self, mocked):
        result = GeminiClient(api_key="test-secret").generate("hello", "en")
        self.assertEqual(result, "Namaste!")
        request = mocked.call_args.args[0]
        self.assertEqual(request.get_header("X-goog-api-key"), "test-secret")
    def test_empty_message_rejected(self):
        with self.assertRaises(GeminiError):
            GeminiClient(api_key="x").generate(" ")

if __name__ == "__main__": unittest.main()
