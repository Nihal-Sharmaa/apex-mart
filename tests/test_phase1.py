import unittest
import os
from src.utils import load_products_from_csv
from src.linked_list import LinkedList
from src.avl_tree import AVLTree
from src.models import Product

class TestPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Determine paths relative to this file
        cls.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products.csv"))
        cls.products = load_products_from_csv(cls.csv_path)

    def test_csv_loading(self):
        """Verify that the CSV loader successfully reads and parses the dataset."""
        self.assertEqual(len(self.products), 500, "Should load exactly 500 products from the dataset.")
        
        # Test first product attributes
        first_product = self.products[0]
        self.assertEqual(first_product.product_id, "P0001")
        self.assertEqual(first_product.product_name, "Data Structures")
        self.assertEqual(first_product.category, "Books")
        self.assertEqual(first_product.brand, "Nova")
        self.assertAlmostEqual(first_product.final_price_inr, round(first_product.price_inr * (1 - first_product.discount_percent / 100.0), 2), places=2)
        self.assertEqual(first_product.rating, 3.1)
        self.assertEqual(first_product.reviews, 12071)
        self.assertEqual(first_product.stock, 52)
        self.assertEqual(first_product.units_sold, 4467)
        self.assertEqual(first_product.customer_city, "Bengaluru")
        self.assertTrue(hasattr(first_product, 'image_url'))

    def test_linked_list_operations(self):
        """Verify LinkedList insertion, traversal, and deletion."""
        ll = LinkedList()
        
        # 1. Test insertion & length
        for p in self.products:
            ll.insert(p)
        self.assertEqual(len(ll), 500)
        
        # 2. Test traversal order
        traversed = list(ll.traverse())
        self.assertEqual(len(traversed), 500)
        self.assertEqual(traversed[0].product_id, "P0001")
        self.assertEqual(traversed[-1].product_id, "P0500")

        # 3. Test deletion from head
        deleted_head = ll.delete("P0001")
        self.assertTrue(deleted_head)
        self.assertEqual(len(ll), 499)
        self.assertNotIn("P0001", [p.product_id for p in ll.traverse()])

        # 4. Test deletion from middle
        deleted_mid = ll.delete("P0250")
        self.assertTrue(deleted_mid)
        self.assertEqual(len(ll), 498)
        self.assertNotIn("P0250", [p.product_id for p in ll.traverse()])

        # 5. Test deletion from tail
        deleted_tail = ll.delete("P0500")
        self.assertTrue(deleted_tail)
        self.assertEqual(len(ll), 497)
        self.assertNotIn("P0500", [p.product_id for p in ll.traverse()])

        # 6. Test delete non-existent ID
        deleted_fake = ll.delete("NON_EXISTENT")
        self.assertFalse(deleted_fake)
        self.assertEqual(len(ll), 497)

    def test_avl_tree_operations(self):
        """Verify AVLTree balance, sorted retrieval, and search functionality."""
        tree = AVLTree()
        
        # 1. Insert all 500 products
        for p in self.products:
            tree.insert(p)
            
        # 2. Verify height-balanced property
        self.assertTrue(tree.is_balanced(), "AVL Tree should be height-balanced after all insertions.")
        
        # 3. Verify in-order traversal returns sorted order
        sorted_products = tree.inorder_traversal()
        self.assertEqual(len(sorted_products), 500)
        
        # Verify the prices are sorted in non-decreasing order
        for i in range(len(sorted_products) - 1):
            p1 = sorted_products[i].final_price_inr
            p2 = sorted_products[i+1].final_price_inr
            self.assertTrue(p1 <= p2, f"Prices are not sorted: {p1} > {p2} at index {i}")

        # 4. Verify search operation O(log N)
        search_price = self.products[0].final_price_inr
        results = tree.search(search_price)
        self.assertTrue(len(results) >= 1)
        self.assertTrue(any(p.product_id == "P0001" for p in results))

        # Search for a price that does not exist
        fake_results = tree.search(999999.99)
        self.assertEqual(len(fake_results), 0)

if __name__ == '__main__':
    unittest.main()
