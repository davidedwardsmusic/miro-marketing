from unittest import TestCase

from src.backend.models.miro_board import MiroBoard
from src.backend.models.miro_item import MiroItem


class TestMiroItem(TestCase):
    def test_item_equality(self):
        """Test that MiroItem equality comparison works correctly."""
        # Create a board with two identical items
        raw_items = [
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Test Content'},
                'links': {'self': 'https://miro.com/item/sticky1'},
                'position': {'x': 100.0, 'y': 200.0}
            }
        ]
        
        board1 = MiroBoard.create(raw_items)
        board2 = MiroBoard.create(raw_items)
        
        item1 = board1.get('sticky1')
        item2 = board2.get('sticky1')
        
        # Items with same properties should be equal (even if from different boards)
        self.assertEqual(item1, item2)
        
    def test_item_inequality_different_content(self):
        """Test that items with different content are not equal."""
        raw_items1 = [
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Content A'},
                'links': {'self': 'https://miro.com/item/sticky1'},
            }
        ]
        
        raw_items2 = [
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Content B'},
                'links': {'self': 'https://miro.com/item/sticky1'},
            }
        ]
        
        board1 = MiroBoard.create(raw_items1)
        board2 = MiroBoard.create(raw_items2)
        
        item1 = board1.get('sticky1')
        item2 = board2.get('sticky1')
        
        # Items with different content should not be equal
        self.assertNotEqual(item1, item2)
        
    def test_item_inequality_different_tags(self):
        """Test that items with different tags are not equal."""
        from src.backend.utils.tag_map import TagMap
        
        raw_items = [
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Test Content'},
                'links': {'self': 'https://miro.com/item/sticky1'},
            }
        ]
        
        # Create two boards with same items
        board1 = MiroBoard.create(raw_items)
        board2 = MiroBoard.create(raw_items)
        
        # Add different tags to the items
        item1 = board1.get('sticky1')
        item2 = board2.get('sticky1')
        
        item1.tags.add('tag_a')
        item2.tags.add('tag_b')
        
        # Items with different tags should not be equal
        self.assertNotEqual(item1, item2)
        
    def test_item_inequality_different_children(self):
        """Test that items with different children are not equal."""
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Test Frame'},
                'links': {'self': 'https://miro.com/item/frame1'},
            }
        ]
        
        board1 = MiroBoard.create(raw_items)
        board2 = MiroBoard.create(raw_items)
        
        item1 = board1.get('frame1')
        item2 = board2.get('frame1')
        
        # Manually add different children
        item1.children = ['child1']
        item2.children = ['child2']
        
        # Items with different children should not be equal
        self.assertNotEqual(item1, item2)

    def test_get_descendants(self):
        """Test that get_descendants returns all descendant item IDs recursively."""
        # Create a nested hierarchy: frame1 -> sticky1 -> sticky2 -> sticky3
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Root Frame'},
                'links': {'self': 'https://miro.com/item/frame1'},
            },
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Child 1'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky1', 'parent': 'https://miro.com/item/frame1'},
            },
            {
                'id': 'sticky2',
                'type': 'sticky_note',
                'data': {'content': 'Child 2'},
                'parent': {'id': 'sticky1'},
                'links': {'self': 'https://miro.com/item/sticky2', 'parent': 'https://miro.com/item/sticky1'},
            },
            {
                'id': 'sticky3',
                'type': 'sticky_note',
                'data': {'content': 'Child 3'},
                'parent': {'id': 'sticky2'},
                'links': {'self': 'https://miro.com/item/sticky3', 'parent': 'https://miro.com/item/sticky2'},
            }
        ]

        board = MiroBoard.create(raw_items)

        # Test frame1 descendants (should include all children recursively)
        frame1 = board.get('frame1')
        descendants = frame1.get_descendant_ids()
        self.assertEqual(descendants, {'sticky1', 'sticky2', 'sticky3'})

        # Test sticky1 descendants (should include sticky2 and sticky3)
        sticky1 = board.get('sticky1')
        descendants = sticky1.get_descendant_ids()
        self.assertEqual(descendants, {'sticky2', 'sticky3'})

        # Test sticky2 descendants (should include only sticky3)
        sticky2 = board.get('sticky2')
        descendants = sticky2.get_descendant_ids()
        self.assertEqual(descendants, {'sticky3'})

        # Test sticky3 descendants (should be empty - no children)
        sticky3 = board.get('sticky3')
        descendants = sticky3.get_descendant_ids()
        self.assertEqual(descendants, set())

    def test_get_descendants_multiple_branches(self):
        """Test get_descendants with multiple branches in the hierarchy."""
        # Create a tree structure:
        #       frame1
        #      /      \
        #  sticky1   sticky2
        #     |
        #  sticky3
        raw_items = [
            {
                'id': 'frame1',
                'type': 'frame',
                'data': {'title': 'Root Frame'},
                'links': {'self': 'https://miro.com/item/frame1'},
            },
            {
                'id': 'sticky1',
                'type': 'sticky_note',
                'data': {'content': 'Branch 1'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky1', 'parent': 'https://miro.com/item/frame1'},
            },
            {
                'id': 'sticky2',
                'type': 'sticky_note',
                'data': {'content': 'Branch 2'},
                'parent': {'id': 'frame1'},
                'links': {'self': 'https://miro.com/item/sticky2', 'parent': 'https://miro.com/item/frame1'},
            },
            {
                'id': 'sticky3',
                'type': 'sticky_note',
                'data': {'content': 'Child of Branch 1'},
                'parent': {'id': 'sticky1'},
                'links': {'self': 'https://miro.com/item/sticky3', 'parent': 'https://miro.com/item/sticky1'},
            }
        ]

        board = MiroBoard.create(raw_items)

        # Test frame1 descendants (should include all items in both branches)
        frame1 = board.get('frame1')
        descendants = frame1.get_descendant_ids()
        self.assertEqual(descendants, {'sticky1', 'sticky2', 'sticky3'})

        # Test sticky1 descendants (should include only sticky3)
        sticky1 = board.get('sticky1')
        descendants = sticky1.get_descendant_ids()
        self.assertEqual(descendants, {'sticky3'})

        # Test sticky2 descendants (should be empty - no children)
        sticky2 = board.get('sticky2')
        descendants = sticky2.get_descendant_ids()
        self.assertEqual(descendants, set())

