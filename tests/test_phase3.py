import unittest
import os
from src.utils import load_products_from_csv
from src.hash_table import (
    simple_hash,
    ChainingHashTable,
    OpenAddressingHashTable,
    ProductLookupSystem,
    SearchTermFrequencyCounter
)

class TestPhase3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Determine path relative to this test file
        cls.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products.csv"))
        cls.products = load_products_from_csv(cls.csv_path)

    def test_simple_hash_and_collisions(self):
        """Verify custom simple_hash distribution on 20 products."""
        # 1. Take 20 products
        test_prods = self.products[:20]
        self.assertEqual(len(test_prods), 20)

        # 2. Map names to hashes
        slots = 15
        hashes = [simple_hash(p.product_name, slots) for p in test_prods]
        
        # Calculate collisions
        unique_hashes = set(hashes)
        collisions = len(hashes) - len(unique_hashes)
        
        print(f"\n[Simple Hash Analysis] 20 products in {slots} slots: {collisions} collisions, {len(unique_hashes)} unique slots filled.")
        # Ensure our hash functions operates within modulo bounds
        for h in hashes:
            self.assertTrue(0 <= h < slots)

    def test_chaining_vs_open_addressing(self):
        """Insert identical datasets into chaining and open addressing tables and compare."""
        # Take 20 products
        test_prods = self.products[:20]
        slots = 25  # Load factor = 20 / 25 = 0.80

        chain_table = ChainingHashTable(slots=slots)
        open_table = OpenAddressingHashTable(slots=slots)

        for p in test_prods:
            chain_table.insert(p.product_id, p)
            open_table.insert(p.product_id, p)

        # Assert all elements can be retrieved in both tables
        for p in test_prods:
            self.assertEqual(chain_table.get(p.product_id).product_id, p.product_id)
            self.assertEqual(open_table.get(p.product_id).product_id, p.product_id)

        # Compare stats
        chain_stats = chain_table.get_stats()
        open_stats = open_table.get_stats()

        self.assertEqual(chain_stats["load_factor"], 0.80)
        self.assertEqual(open_stats["load_factor"], 0.80)

        print(f"\n[Collision Rate Comparison] Load Factor = 0.80")
        print(f"Chaining Hash Table: {chain_stats['collisions']} collisions")
        print(f"Open Addressing (Linear Probing): {open_stats['collisions']} collisions")

        # Test deletion in both tables
        target_id = test_prods[5].product_id
        self.assertTrue(chain_table.delete(target_id))
        self.assertTrue(open_table.delete(target_id))

        self.assertFalse(chain_table.contains(target_id))
        self.assertFalse(open_table.contains(target_id))

        # Check retrieval of other keys in open addressing to verify linear probe chain is NOT broken
        next_id = test_prods[6].product_id
        self.assertEqual(open_table.get(next_id).product_id, test_prods[6].product_id)

    def test_product_lookup_system(self):
        """Verify dict-based ProductLookupSystem supports O(1) insert, search, and delete."""
        lookup_sys = ProductLookupSystem()
        
        # Insert 15 products
        test_prods = self.products[:15]
        for p in test_prods:
            lookup_sys.insert(p)

        self.assertEqual(len(lookup_sys), 15)

        # Search existing product
        target = test_prods[10]
        found = lookup_sys.search(target.product_id)
        self.assertIsNotNone(found)
        self.assertEqual(found.product_name, target.product_name)

        # Search non-existing product
        self.assertIsNone(lookup_sys.search("NON_EXISTENT_ID"))

        # Delete product
        self.assertTrue(lookup_sys.delete(target.product_id))
        self.assertEqual(len(lookup_sys), 14)
        self.assertIsNone(lookup_sys.search(target.product_id))
        self.assertFalse(lookup_sys.delete(target.product_id))

    def test_search_term_frequency_counter(self):
        """Verify SearchTermFrequencyCounter correctly tracks query counts and returns top 5."""
        counter = SearchTermFrequencyCounter()

        # Seed queries
        queries = [
            ("laptop", 8),
            ("running shoes", 5),
            ("t-shirt", 6),
            ("smartphone", 10),
            ("coffee mug", 3),
            ("backpack", 1),
            ("charger", 2),
        ]

        for query, count in queries:
            for _ in range(count):
                counter.record_query(query)

        # Retrieve top 5
        top_5 = counter.get_top_n(5)
        self.assertEqual(len(top_5), 5)

        # Expected order based on count: smartphone (10), laptop (8), t-shirt (6), running shoes (5), coffee mug (3)
        self.assertEqual(top_5[0][0], "smartphone")
        self.assertEqual(top_5[0][1], 10)
        self.assertEqual(top_5[1][0], "laptop")
        self.assertEqual(top_5[2][0], "t-shirt")
        self.assertEqual(top_5[3][0], "running shoes")
        self.assertEqual(top_5[4][0], "coffee mug")

if __name__ == '__main__':
    unittest.main()
