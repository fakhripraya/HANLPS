import unittest
from src.domain.entities.building.building import Building
from src.domain.entities.search import Search


class TestSearchEntity(unittest.TestCase):
    def setUp(self):
        """Set up data for testing"""
        self.building_data = {
            "building_title": "Sample Building",
            "building_address": "123 Test St",
            "building_proximity": None,
            "building_facility": "WiFi",
            "building_note": "Near public transport",
            "building_description": "A great place to live",
            "housing_price": 500,
            "owner_name": "John Doe",
            "owner_email": "johndoe@example.com",
            "owner_whatsapp": "+123456789",
            "owner_phone_number": "+987654321",
            "image_url": "http://example.com/image.jpg",
        }
        self.building_instance = Building(**self.building_data)
        self.search_data = {
            "output": "Search completed successfully",
            "output_content": [self.building_instance],
        }
        self.search_instance = Search(**self.search_data)

    def test_from_dict(self):
        """Test the from_dict method"""
        data = {
            "output": "Search completed successfully",
            "output_content": [self.building_data],  # Dict version of Building
        }
        search = Search.from_dict(data)
        self.assertEqual(search.output, "Search completed successfully")
        self.assertEqual(len(search.output_content), 1)
        self.assertEqual(search.output_content[0].building_title, "Sample Building")

    def test_to_dict(self):
        """Test the to_dict method"""
        result = self.search_instance.to_dict()
        self.assertEqual(result["output"], "Search completed successfully")
        self.assertEqual(len(result["output_content"]), 1)
        self.assertEqual(
            result["output_content"][0]["building_title"], "Sample Building"
        )

    def test_no_output_content(self):
        """Test case where output_content is None"""
        data = {
            "output": "Search completed with no results",
            "output_content": None,
        }
        search = Search.from_dict(data)
        self.assertEqual(search.output, "Search completed with no results")
        self.assertIsNone(search.output_content)

    def test_empty_output_content(self):
        """Test case where output_content is an empty list"""
        data = {
            "output": "Search completed with no results",
            "output_content": [],
        }
        search = Search.from_dict(data)
        self.assertEqual(search.output, "Search completed with no results")
        self.assertEqual(search.output_content, [])


if __name__ == "__main__":
    unittest.main()
