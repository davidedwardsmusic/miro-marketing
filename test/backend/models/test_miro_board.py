from unittest import TestCase

from src.backend.models.miro_board import MiroBoard


class TestMiroBoard(TestCase):
    def test_create_board(self):
        board = MiroBoard()
        self.assertIsNotNone(board)

    def test_populate_relationships(self):
        """Test that populate_relationships correctly builds parent-child relationships and identifies root items."""
        # Test data with parent-child relationships
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Main Frame'},
                'links': {'self': 'https://miro.com/item/frame1'}
            },
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Child sticky 1'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky1', 'parent': 'https://miro.com/item/frame1'}
            },
            {
                'id': 'sticky2',
                'type': 'sticky_note',
                'data': {'content': 'Child sticky 2'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky2', 'parent': 'https://miro.com/item/frame1'}
            }
        ]

        # Create board using the factory method (which calls populate_relationships)
        board = MiroBoard.create(raw_items)

        # Verify total items
        self.assertEqual(len(board.items), 3)

        # Verify root items list is populated correctly
        self.assertEqual(len(board.root_items), 1)
        root_item = board.root_items[0]
        self.assertEqual(root_item.id, 'frame1')
        self.assertEqual(root_item.type.value, 'frame')

        # Verify root item has correct children
        self.assertEqual(len(root_item.children), 2)
        self.assertIn('sticky1', root_item.children)
        self.assertIn('sticky2', root_item.children)

        # Verify children have empty children lists
        sticky1 = board.items.get('sticky1')
        sticky2 = board.items.get('sticky2')
        self.assertIsNotNone(sticky1)
        self.assertIsNotNone(sticky2)
        self.assertEqual(len(sticky1.children), 0)
        self.assertEqual(len(sticky2.children), 0)

    def test_populate_relationships_multiple_roots(self):
        """Test that populate_relationships correctly handles multiple root items."""
        # Test data with multiple root items (no parents)
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Frame 1'},
                'links': {'self': 'https://miro.com/item/frame1'}
            },
            {
                'id': 'frame2',
                'type': 'frame',
                'data': {'title': 'Frame 2'},
                'links': {'self': 'https://miro.com/item/frame2'}
            },
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Child of frame1'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky1', 'parent': 'https://miro.com/item/frame1'}
            }
        ]

        # Create board
        board = MiroBoard.create(raw_items)

        # Verify we have 2 root items
        self.assertEqual(len(board.root_items), 2)

        # Verify both frames are in root_items
        root_ids = [item.id for item in board.root_items]
        self.assertIn('frame1', root_ids)
        self.assertIn('frame2', root_ids)

        # Verify frame1 has a child, frame2 has no children
        frame1 = board.items.get('frame1')
        frame2 = board.items.get('frame2')
        self.assertEqual(len(frame1.children), 1)
        self.assertEqual(len(frame2.children), 0)

    def test_to_dict(self):
        """Test that to_dict() returns a JSON-serializable dictionary."""
        import json
        from src.backend.utils.tag_map import TagMap

        # Test data with various item types
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Test Frame'},
                'links': {'self': 'https://miro.com/item/frame1'},
                'position': {'x': 100.0, 'y': 200.0}
            },
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Test Content'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky1', 'parent': 'https://miro.com/item/frame1'},
                'position': {'x': 150.0, 'y': 250.0}
            }
        ]

        # Add some tags to test tag serialization
        tag_map = TagMap()
        tag_map.add_tags_to_item('sticky1', ['test_tag', 'important'])

        # Create board
        board = MiroBoard.create(raw_items)

        # Convert to dict
        board_dict = board.to_dict()

        # Verify it's JSON-serializable (this will raise an exception if it's not)
        json_str = json.dumps(board_dict)
        self.assertIsNotNone(json_str)

        # Verify structure - to_dict returns a dict with keys like "id_tags"
        # The dict contains only root items with their children nested
        self.assertEqual(len(board_dict), 1)  # Only 1 root item (frame1)

        # The key should be "frame1_" (id + empty tags string)
        self.assertIn('frame1_', board_dict)

        # Verify frame structure
        frame_dict = board_dict['frame1_']
        self.assertEqual(frame_dict['id'], 'frame1')
        self.assertEqual(frame_dict['type'], 'frame')  # Should be string, not enum
        self.assertIsInstance(frame_dict['tags'], str)  # tags_to_str returns a string
        self.assertEqual(frame_dict['tags'], '')  # No tags on frame

        # Verify data structure
        self.assertIn('data', frame_dict)
        self.assertEqual(frame_dict['data']['title'], 'Test Frame')
        self.assertIsNone(frame_dict['data']['content'])

        # Verify children are nested
        self.assertIn('children', frame_dict)
        self.assertEqual(len(frame_dict['children']), 1)

        # Verify sticky note (nested as child)
        sticky_dict = frame_dict['children'][0]
        self.assertEqual(sticky_dict['id'], 'sticky1')
        self.assertEqual(sticky_dict['type'], 'sticky_note')  # Should be string, not enum

        # Verify sticky data
        self.assertIn('data', sticky_dict)
        self.assertEqual(sticky_dict['data']['content'], 'Test Content')

        # Verify tags are serialized as string (tags_to_str)
        self.assertIsInstance(sticky_dict['tags'], str)
        # Tags should be sorted and comma-separated
        self.assertIn('important', sticky_dict['tags'])
        self.assertIn('test_tag', sticky_dict['tags'])

        # Verify sticky has no children
        self.assertEqual(len(sticky_dict['children']), 0)

    def test_board_equality(self):
        """Test that board equality comparison works correctly."""
        # Create two identical boards
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Test Frame'},
                'links': {'self': 'https://miro.com/item/frame1'},
                'position': {'x': 100.0, 'y': 200.0}
            },
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Test Content'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky1', 'parent': 'https://miro.com/item/frame1'},
                'position': {'x': 150.0, 'y': 250.0}
            }
        ]

        board1 = MiroBoard.create(raw_items)
        board2 = MiroBoard.create(raw_items)

        # Boards with same items should be equal
        self.assertEqual(board1, board2)

        # Create a different board
        different_raw_items = [
            {
                'id': 'frame2',
                'type': 'frame',
                'data': {'title': 'Different Frame'},
                'links': {'self': 'https://miro.com/item/frame2'},
                'position': {'x': 100.0, 'y': 200.0}
            }
        ]

        board3 = MiroBoard.create(different_raw_items)

        # Different boards should not be equal
        self.assertNotEqual(board1, board3)

        # Empty boards should be equal
        empty1 = MiroBoard()
        empty2 = MiroBoard()
        self.assertEqual(empty1, empty2)


