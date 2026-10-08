import unittest
import os
from src.utils import load_products_from_csv
from src.graph import ProductGraph
from src.search import (
    calculate_heuristic,
    greedy_best_first_search,
    a_star_search,
    bfs_search,
)


class TestPhase4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products.csv"))
        products = load_products_from_csv(cls.csv_path)
        cls.product_map = {p.product_id: p for p in products}

        # Bipartite user–product graph used as the search space
        cls.graph = ProductGraph()
        users = [f"U{i}" for i in range(1, 6)]
        for u in users:
            cls.graph.add_node(u)

        # Connect users to a mix of matching and non-matching products
        cls.graph.add_edge("U1", "P0016", 1.0)  # Electronics, cheap, high rating
        cls.graph.add_edge("U1", "P0001", 1.0)  # Books, expensive, rating 3.1
        cls.graph.add_edge("U2", "P0016", 1.0)
        cls.graph.add_edge("U2", "P0028", 1.0)  # Books, 1827.5, rating 3.8  (goal)
        cls.graph.add_edge("U3", "P0003", 1.0)  # Books, expensive, rating 4.5
        cls.graph.add_edge("U3", "P0028", 1.0)
        cls.graph.add_edge("U4", "P0013", 1.0)  # Electronics
        cls.graph.add_edge("U5", "P0004", 1.0)  # Fashion

        cls.query = {
            "category": "Books",
            "min_rating": 3.5,
            "max_price": 5000.0,
        }

    def test_heuristic_costs(self):
        """Heuristic h(n) is 0 for a perfect match and penalizes mismatches."""
        h_goal = calculate_heuristic("P0028", self.query, self.product_map)
        self.assertEqual(h_goal, 0.0)

        h_user = calculate_heuristic("U1", self.query, self.product_map)
        self.assertEqual(h_user, 20.0)

        h_electronics = calculate_heuristic("P0016", self.query, self.product_map)
        self.assertGreaterEqual(h_electronics, 10.0)

        h_expensive_book = calculate_heuristic("P0001", self.query, self.product_map)
        self.assertGreater(h_expensive_book, 1.0)

    def test_greedy_best_first_search(self):
        """Greedy Best-First Search finds a product matching the query."""
        found, explored, path = greedy_best_first_search(
            self.graph, "U1", self.query, self.product_map
        )
        self.assertEqual(found, "P0028")
        self.assertGreaterEqual(explored, 1)
        self.assertEqual(path[0], "U1")
        self.assertEqual(path[-1], "P0028")
        self.assertLess(
            calculate_heuristic(found, self.query, self.product_map), 1.0
        )
        print(f"\n[GBFS] found={found}, nodes_explored={explored}, path={path}")

    def test_a_star_search(self):
        """A* finds the same goal using f(n) = g(n) + h(n)."""
        found, explored, path = a_star_search(
            self.graph, "U1", self.query, self.product_map
        )
        self.assertEqual(found, "P0028")
        self.assertGreaterEqual(explored, 1)
        self.assertEqual(path[0], "U1")
        self.assertEqual(path[-1], "P0028")
        print(f"\n[A*] found={found}, nodes_explored={explored}, path={path}")

    def test_uninformed_bfs_search(self):
        """Uninformed BFS also reaches a valid goal product."""
        found, explored, path = bfs_search(
            self.graph, "U1", self.query, self.product_map
        )
        self.assertEqual(found, "P0028")
        self.assertGreaterEqual(explored, 1)
        self.assertEqual(path[0], "U1")
        self.assertEqual(path[-1], "P0028")
        print(f"\n[BFS] found={found}, nodes_explored={explored}, path={path}")

    def test_informed_vs_uninformed_comparison(self):
        """Compare nodes expanded by GBFS, A*, and BFS from the same start."""
        gbfs = greedy_best_first_search(self.graph, "U1", self.query, self.product_map)
        astar = a_star_search(self.graph, "U1", self.query, self.product_map)
        bfs = bfs_search(self.graph, "U1", self.query, self.product_map)

        self.assertEqual(gbfs[0], "P0028")
        self.assertEqual(astar[0], "P0028")
        self.assertEqual(bfs[0], "P0028")

        print("\n[Search Comparison] start=U1, goal=Books rating>=3.5 price<=5000")
        print(f"  Greedy Best-First: explored={gbfs[1]}, path_len={len(gbfs[2])}")
        print(f"  A*:                explored={astar[1]}, path_len={len(astar[2])}")
        print(f"  Uninformed BFS:    explored={bfs[1]}, path_len={len(bfs[2])}")


if __name__ == "__main__":
    unittest.main()
