import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import server


class AssistantFallbackTests(unittest.TestCase):
    def test_local_reply_for_camera_question(self):
        reply = server.get_local_assistant_reply("camera is not working")
        self.assertIn("camera", reply.lower())

    def test_local_reply_for_gesture_question(self):
        reply = server.get_local_assistant_reply("show me all gestures")
        self.assertIn("YES", reply)


if __name__ == "__main__":
    unittest.main()
