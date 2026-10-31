import unittest
from rosa_core import RosaEngine

class EngineTests(unittest.TestCase):
    def setUp(self): self.engine = RosaEngine()
    def test_empty_input(self):
        self.assertTrue(self.engine.respond("").needs_clarification)
    def test_settings_requires_confirmation(self):
        reply = self.engine.respond("open settings")
        self.assertEqual(reply.action.kind, "open_settings")
        self.assertTrue(reply.action.requires_confirmation)
    def test_alarm_parsing(self):
        reply = self.engine.respond("set alarm for 7:30 pm")
        self.assertEqual(reply.action.arguments, {"hour": 19, "minute": 30})
        self.assertTrue(reply.action.requires_confirmation)
    def test_invalid_alarm_time(self):
        self.assertTrue(self.engine.respond("set alarm for 7:90").needs_clarification)
    def test_no_fake_execution_claim(self):
        self.assertIn("?", self.engine.respond("open settings").text)

if __name__ == "__main__": unittest.main()
