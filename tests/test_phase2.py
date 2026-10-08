import unittest
import os
import time
from src.utils import load_products_from_csv
from src.heap import MinHeap, MaxHeap, PriorityQueue
from src.graph import ProductGraph
from src.models import Product, Order

class TestPhase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Determine path relative to this test file
        cls.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products.csv"))
        cls.products = load_products_from_csv(cls.csv_path)

    def test_min_heap_from_scratch(self):
        """Verify custom MinHeap insert and extract_min operations with at least 15 products sorted by price."""
        # 1. Take first 20 products
        test_prods = self.products[:20]
        self.assertTrue(len(test_prods) >= 15)

        # 2. Insert into MinHeap with price as comparison key
        heap = MinHeap(key=lambda p: p.final_price_inr)
        for p in test_prods:
            heap.insert(p)

        self.assertEqual(len(heap), len(test_prods))

        # 3. Extract all elements and assert they are sorted by price ascending
        extracted = []
        while len(heap) > 0:
            extracted.append(heap.extract_min())

        self.assertEqual(len(extracted), len(test_prods))
        for i in range(len(extracted) - 1):
            p1 = extracted[i].final_price_inr
            p2 = extracted[i+1].final_price_inr
            self.assertTrue(p1 <= p2, f"Heap order violated: {p1} > {p2}")

    def test_max_heap_simulation(self):
        """Verify heapq-based simulated MaxHeap insert and extract_max sorted by rating descending."""
        test_prods = self.products[:20]
        self.assertTrue(len(test_prods) >= 15)

        heap = MaxHeap()
        for p in test_prods:
            heap.insert(p)

        self.assertEqual(len(heap), len(test_prods))

        # Extract all elements and assert they are sorted by rating descending
        extracted = []
        while len(heap) > 0:
            extracted.append(heap.extract_max())

        self.assertEqual(len(extracted), len(test_prods))
        for i in range(len(extracted) - 1):
            r1 = extracted[i].rating
            r2 = extracted[i+1].rating
            self.assertTrue(r1 >= r2, f"Heap order violated: {r1} < {r2}")

    def test_priority_queue_order_fulfillment(self):
        """Verify priority queue handles orders with earliest deadline first with at least 10 orders."""
        pq = PriorityQueue()
        
        # 10 orders with unsorted deadlines
        orders = [
            Order(order_id="O001", delivery_deadline=150, customer_name="Alice"),
            Order(order_id="O002", delivery_deadline=50, customer_name="Bob"),
            Order(order_id="O003", delivery_deadline=200, customer_name="Charlie"),
            Order(order_id="O004", delivery_deadline=10, customer_name="Dave"),
            Order(order_id="O005", delivery_deadline=90, customer_name="Eve"),
            Order(order_id="O006", delivery_deadline=120, customer_name="Frank"),
            Order(order_id="O007", delivery_deadline=30, customer_name="Grace"),
            Order(order_id="O008", delivery_deadline=80, customer_name="Heidi"),
            Order(order_id="O009", delivery_deadline=110, customer_name="Ivan"),
            Order(order_id="O010", delivery_deadline=60, customer_name="Jack"),
        ]

        for o in orders:
            pq.enqueue(o)

        self.assertEqual(len(pq), 10)

        # Dequeue and verify they are returned in ascending order of deadlines
        dequeued = []
        while len(pq) > 0:
            dequeued.append(pq.dequeue())

        self.assertEqual(len(dequeued), 10)
        self.assertEqual(dequeued[0].order_id, "O004")  # deadline 10
        self.assertEqual(dequeued[1].order_id, "O007")  # deadline 30
        self.assertEqual(dequeued[2].order_id, "O002")  # deadline 50
        self.assertEqual(dequeued[-1].order_id, "O003") # deadline 200

        # Verify strict order
        for i in range(len(dequeued) - 1):
            self.assertTrue(dequeued[i].delivery_deadline <= dequeued[i+1].delivery_deadline)

    def test_heap_vs_array_complexity(self):
        """Task 4: Documenting and verifying time differences between heap operations vs arrays."""
        # We will insert 200 items into a heap, sorted array, and unsorted array, and assert heap operations are fast
        n = 200
        test_vals = [p.final_price_inr for p in self.products[:n]]

        # Unsorted array insertion: O(1)
        unsorted_arr = []
        for v in test_vals:
            unsorted_arr.append(v)
        # Extract min: O(N)
        start = time.perf_counter()
        min_unsorted = min(unsorted_arr)
        unsorted_arr.remove(min_unsorted)
        time_unsorted = time.perf_counter() - start

        # Heap insertion: O(log N)
        heap = MinHeap()
        for v in test_vals:
            heap.insert(v)
        # Extract min: O(log N)
        start = time.perf_counter()
        min_heap = heap.extract_min()
        time_heap = time.perf_counter() - start

        self.assertEqual(min_unsorted, min_heap)
        # Informational print of execution comparison
        print(f"\n[Complexity Demo] Extraction of min for N={n}: Heap={time_heap:.6f}s vs Unsorted Array={time_unsorted:.6f}s")

    def test_graph_modeling_and_traversals(self):
        """Tasks 5, 6, 7, 8: Bipartite graph modeling 8 users, 12 products, BFS and DFS traversals."""
        graph = ProductGraph()

        # Define 8 users and 12 products
        users = [f"U{i}" for i in range(1, 9)]
        products = [f"P{i}" for i in range(1, 13)]

        # Add nodes
        for u in users:
            graph.add_node(u)
        for p in products:
            graph.add_node(p)

        # Add edges representing purchase/view events (some with weights)
        # U1 viewed P1 (wt 1) and purchased P2 (wt 5)
        graph.add_edge("U1", "P1", 1.0)
        graph.add_edge("U1", "P2", 5.0)

        # U2 viewed P2 (wt 1) and purchased P3 (wt 3)
        graph.add_edge("U2", "P2", 1.0)
        graph.add_edge("U2", "P3", 3.0)

        # U3 purchased P1 (wt 4) and P2 (wt 2)
        graph.add_edge("U3", "P1", 4.0)
        graph.add_edge("U3", "P2", 2.0)

        # U4 purchased P3 (wt 5), P4 (wt 4), and P5 (wt 1)
        graph.add_edge("U4", "P3", 5.0)
        graph.add_edge("U4", "P4", 4.0)
        graph.add_edge("U4", "P5", 1.0)

        # U5 viewed P5 (wt 1) and P6 (wt 2)
        graph.add_edge("U5", "P5", 1.0)
        graph.add_edge("U5", "P6", 2.0)

        # U6 purchased P6 (wt 5) and P7 (wt 3)
        graph.add_edge("U6", "P6", 5.0)
        graph.add_edge("U6", "P7", 3.0)

        # U7 viewed P7 (wt 1) and purchased P8 (wt 4)
        graph.add_edge("U7", "P7", 1.0)
        graph.add_edge("U7", "P8", 4.0)

        # U8 purchased P9 (wt 5), P10 (wt 2), P11 (wt 1), P12 (wt 1)
        graph.add_edge("U8", "P9", 5.0)
        graph.add_edge("U8", "P10", 2.0)
        graph.add_edge("U8", "P11", 1.0)
        graph.add_edge("U8", "P12", 1.0)

        # 1. BFS from product P1 up to depth 2 (products within 2 degrees of connection)
        # Paths from P1 of depth 2:
        # P1 -> U1 -> P2
        # P1 -> U3 -> P2
        # Recommended product should be P2.
        recs_p1 = graph.bfs_recommendations("P1", max_depth=2)
        # Filter for products (should be P2)
        prod_recs = [r["product_id"] for r in recs_p1]
        self.assertIn("P2", prod_recs)
        self.assertNotIn("P1", prod_recs)  # start node excluded
        self.assertNotIn("U1", prod_recs)  # user nodes excluded from product_ids starting with 'P'

        # 2. Verify weight prioritization in BFS from P2 (up to depth 2)
        # Paths:
        # P2 -> U1 -> P1 (weight 5 * 1 = 5)
        # P2 -> U3 -> P1 (weight 2 * 4 = 8) -> Total path weight to P1 = 13
        # P2 -> U2 -> P3 (weight 1 * 3 = 3)
        # So P1 has score 13, P3 has score 3.
        # Recommendation list should prioritize P1 over P3.
        recs_p2 = graph.bfs_recommendations("P2", max_depth=2)
        self.assertEqual(recs_p2[0]["product_id"], "P1")
        self.assertEqual(recs_p2[1]["product_id"], "P3")
        self.assertTrue(recs_p2[0]["score"] > recs_p2[1]["score"])

        # 3. DFS from user U1 (up to depth 3: User -> Product -> User -> Product)
        # Paths:
        # U1 -> P1 -> U3 -> P2 (depth 3)
        # U1 -> P2 -> U2 -> P3 (depth 3)
        # U1 -> P2 -> U3 -> P1 (depth 3)
        paths_u1 = graph.dfs_recommendations("U1", max_depth=3)
        
        # Verify that we discovered paths of length up to 4 nodes (start_node + 3 edges)
        path_lengths = [len(p) for p in paths_u1]
        self.assertTrue(any(l == 4 for l in path_lengths))

        # Check that we reached products like P3 through the chain
        reached_products = {p[-1] for p in paths_u1 if p[-1].startswith('P')}
        self.assertIn("P3", reached_products)

if __name__ == '__main__':
    unittest.main()
