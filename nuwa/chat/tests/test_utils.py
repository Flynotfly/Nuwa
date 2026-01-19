from unittest import TestCase

from chat.utils import update_chat_structure


class UpdateChatStructureTestCase(TestCase):
    def test_insert_new_root_message(self):
        """When current_id is None, start a new chat with new_id."""
        structure = []
        result = update_chat_structure(structure, current_id=None, new_id=1, path=[])
        self.assertEqual(result, [1])

    def test_simple(self):
        structure = [0]
        result = update_chat_structure(structure, current_id=0, new_id=1, path=[0])
        self.assertEqual(result, [0, 1])

    def test_append_to_root_level(self):
        """Append a reply to a root-level message that has no replies yet."""
        structure = [1, 2]
        result = update_chat_structure(structure, current_id=2, new_id=3, path=[1])
        self.assertEqual(result, [1, 2, 3])

    def test_append_to_existing_reply_thread(self):
        """Append to an existing reply thread at root level."""
        structure = [1, 2, 10]
        result = update_chat_structure(structure, current_id=2, new_id=11, path=[1])
        self.assertEqual(result, [1, 2, [[10], [11]]])

    def test_insert_into_nested_thread(self):
        """Insert a reply into a nested thread using a path."""
        structure = [1, 2, [[3], [4]]]
        result = update_chat_structure(structure, current_id=4, new_id=5, path=[1, 2])
        self.assertEqual(result, [1, 2, [[3], [4, 5]]])

    def test_insert_reply_to_nested_parent_creates_new_thread(self):
        """Reply to message 3 (which already has a thread), so append to its thread."""
        structure = [1, 2, [[3], [4]]]
        result = update_chat_structure(structure, current_id=3, new_id=6, path=[1, 2])
        self.assertEqual(result, [1, 2, [[3, 6], [4]]])

    def test_insert_reply_to_message_with_no_thread_creates_one(self):
        structure = [1, 2, 3, 4]
        result = update_chat_structure(structure, current_id=3, new_id=5, path=[1, 2])
        self.assertEqual(result, [1, 2, 3, [[4], [5]]])

    def test_complex(self):
        structure = [0, 1, 2, [[3, 4, 7], [5, 6, [[11, 12], [13, 14]]], [8, 9, 10]]]
        result = update_chat_structure(structure, current_id=13, new_id=15, path=[0, 1, 2, 5, 6])
        self.assertEqual(result, [0, 1, 2, [[3, 4, 7], [5, 6, [[11, 12], [13, [[14], [15]]]]], [8, 9, 10]]])

    def test_comples_2(self):
        structure = [
            0, 1, [
                [2, 4, 5, 6],
                [3, 7, 8, 9]
            ]
        ]
        result = update_chat_structure(structure, current_id=1, new_id=10, path=[0])
        self.assertEqual(result, [0, 1, [[2, 4, 5, 6], [3, 7, 8, 9], [10]]])
