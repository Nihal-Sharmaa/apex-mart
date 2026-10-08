import unittest
import os
from src.utils import load_products_from_csv
from src.rule_engine import (
    RuleEngine,
    SpenderDiscountRule,
    ElectronicsSpecialRule,
    BooksMultiBuyRule,
    NewUserWelcomeRule,
    PremiumCategoryRule,
    LowRatingClearanceRule,
    BulkQuantityRule,
    CitySpecialRule,
)


class TestPhase5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "products.csv"))
        products = load_products_from_csv(csv_path)
        cls.by_id = {p.product_id: p for p in products}
        cls.engine = RuleEngine()

    def _item(self, product_id, quantity):
        return {"product": self.by_id[product_id], "quantity": quantity}

    def test_rule_priority_order(self):
        """Eight production rules are registered and sorted by priority."""
        self.assertEqual(len(self.engine.rules), 8)
        priorities = [r.priority for r in self.engine.rules]
        self.assertEqual(priorities, sorted(priorities))
        self.assertIsInstance(self.engine.rules[0], SpenderDiscountRule)
        self.assertIsInstance(self.engine.rules[-1], CitySpecialRule)

    def test_big_spender_discount(self):
        """IF subtotal >= 5000 THEN 10% off."""
        cart = [self._item("P0004", 5)]  # Backpack
        subtotal = self.by_id["P0004"].final_price_inr * 5
        rule = SpenderDiscountRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {}))
        self.assertAlmostEqual(rule.apply_action(cart, subtotal, {}), subtotal * 0.10, places=2)

        small = [self._item("P0016", 1)]  # USB Cable
        self.assertFalse(rule.evaluate_condition(small, self.by_id["P0016"].final_price_inr, {}))

    def test_electronics_extravaganza(self):
        """IF Electronics subtotal >= 10000 THEN 15% off Electronics."""
        cart = [self._item("P0013", 20)]  # Laptop Stand x 20
        subtotal = self.by_id["P0013"].final_price_inr * 20
        rule = ElectronicsSpecialRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {}))
        self.assertAlmostEqual(rule.apply_action(cart, subtotal, {}), subtotal * 0.15, places=2)

        cheap_elec = [self._item("P0016", 1)]
        self.assertFalse(rule.evaluate_condition(cheap_elec, self.by_id["P0016"].final_price_inr, {}))

    def test_bookworm_bundle(self):
        """IF 3 or more Books THEN 12% off Books."""
        cart = [self._item("P0028", 3)]
        rule = BooksMultiBuyRule()
        books_subtotal = self.by_id["P0028"].final_price_inr * 3
        self.assertTrue(rule.evaluate_condition(cart, books_subtotal, {}))
        self.assertAlmostEqual(rule.apply_action(cart, books_subtotal, {}), books_subtotal * 0.12, places=2)

        two_books = [self._item("P0028", 2)]
        self.assertFalse(rule.evaluate_condition(two_books, self.by_id["P0028"].final_price_inr * 2, {}))

    def test_new_user_welcome(self):
        """IF new user AND subtotal >= 2000 THEN flat 500."""
        cart = [self._item("P0004", 2)]
        subtotal = self.by_id["P0004"].final_price_inr * 2
        rule = NewUserWelcomeRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {"is_new_user": True}))
        self.assertEqual(rule.apply_action(cart, subtotal, {"is_new_user": True}), 500.0)
        self.assertFalse(rule.evaluate_condition(cart, subtotal, {"is_new_user": False}))

    def test_premium_brand_reward(self):
        """IF Nova/Polar subtotal >= 15000 THEN flat 1000."""
        cart = [self._item("P0001", 30)]  # Nova Books x 30
        subtotal = self.by_id["P0001"].final_price_inr * 30
        rule = PremiumCategoryRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {}))
        self.assertEqual(rule.apply_action(cart, subtotal, {}), 1000.0)

        non_premium = [self._item("P0003", 1)]  # Prime brand
        self.assertFalse(rule.evaluate_condition(non_premium, self.by_id["P0003"].final_price_inr, {}))

    def test_clearance_special(self):
        """IF rating < 3.0 THEN 20% off those items."""
        cart = [self._item("P0004", 1)]  # rating 2.8
        subtotal = self.by_id["P0004"].final_price_inr
        rule = LowRatingClearanceRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {}))
        self.assertAlmostEqual(rule.apply_action(cart, subtotal, {}), subtotal * 0.20, places=2)

        high_rated = [self._item("P0016", 1)]  # rating 4.7
        self.assertFalse(rule.evaluate_condition(high_rated, self.by_id["P0016"].final_price_inr, {}))

    def test_mega_bulk_discount(self):
        """IF total quantity >= 10 THEN flat 300."""
        cart = [self._item("P0016", 10)]
        subtotal = self.by_id["P0016"].final_price_inr * 10
        rule = BulkQuantityRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {}))
        self.assertEqual(rule.apply_action(cart, subtotal, {}), 300.0)

        small_cart = [self._item("P0016", 9)]
        self.assertFalse(rule.evaluate_condition(small_cart, self.by_id["P0016"].final_price_inr * 9, {}))

    def test_metro_city_offer(self):
        """IF Bengaluru/Mumbai AND subtotal >= 1500 THEN flat 200."""
        cart = [self._item("P0004", 2)]
        subtotal = self.by_id["P0004"].final_price_inr * 2
        rule = CitySpecialRule()
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {"city": "Bengaluru"}))
        self.assertTrue(rule.evaluate_condition(cart, subtotal, {"city": "Mumbai"}))
        self.assertEqual(rule.apply_action(cart, subtotal, {"city": "Mumbai"}), 200.0)
        self.assertFalse(rule.evaluate_condition(cart, subtotal, {"city": "Chennai"}))

    def test_forward_chaining_cart_evaluation(self):
        """Engine applies matching rules in priority order and adds 18% GST."""
        # New Bengaluru user buying a low-rated backpack (triggers several rules)
        cart = [self._item("P0004", 4)]
        subtotal = self.by_id["P0004"].final_price_inr * 4
        result = self.engine.evaluate_cart(
            cart, {"is_new_user": True, "city": "Bengaluru"}
        )

        self.assertAlmostEqual(result["subtotal"], subtotal, places=2)
        self.assertGreater(result["total_discount"], 0)
        self.assertLess(result["discounted_subtotal"], result["subtotal"])
        self.assertAlmostEqual(
            result["tax"], result["discounted_subtotal"] * 0.18, delta=0.02
        )
        self.assertAlmostEqual(
            result["final_total"],
            result["discounted_subtotal"] + result["tax"],
            delta=0.02,
        )

        applied_names = [r["name"] for r in result["applied_rules"]]
        self.assertIn("Big Spender Discount", applied_names)
        self.assertIn("New User Welcome", applied_names)
        self.assertIn("Clearance Special", applied_names)
        self.assertIn("Metro City Offer", applied_names)

        print("\n[Rule Engine] cart=P0004 x1, new user in Bengaluru")
        print(f"  subtotal={result['subtotal']}")
        print(f"  rules={[r['name'] for r in result['applied_rules']]}")
        print(f"  total_discount={result['total_discount']}")
        print(f"  tax={result['tax']} final_total={result['final_total']}")

    def test_empty_cart(self):
        result = self.engine.evaluate_cart([])
        self.assertEqual(result["subtotal"], 0.0)
        self.assertEqual(result["total_discount"], 0.0)
        self.assertEqual(result["applied_rules"], [])
        self.assertEqual(result["final_total"], 0.0)


if __name__ == "__main__":
    unittest.main()
