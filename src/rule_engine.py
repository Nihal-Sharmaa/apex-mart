from typing import List, Dict, Any
from src.models import Product

class DiscountRule:
    """Base class for IF-THEN production rules."""
    def __init__(self, name: str, description: str, priority: int) -> None:
        self.name: str = name
        self.description: str = description
        self.priority: int = priority  # Lower number = higher priority

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        """Returns True if the rule conditions are met."""
        raise NotImplementedError

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        """Returns the calculated discount amount."""
        raise NotImplementedError


class SpenderDiscountRule(DiscountRule):
    """IF subtotal >= ₹5000 THEN apply 10% discount on subtotal."""
    def __init__(self) -> None:
        super().__init__("Big Spender Discount", "10% off on subtotals of ₹5000 or more", 1)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        return subtotal >= 5000.0

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        return subtotal * 0.10


class ElectronicsSpecialRule(DiscountRule):
    """IF subtotal of Electronics items >= ₹10000 THEN apply 15% discount on Electronics."""
    def __init__(self) -> None:
        super().__init__("Electronics Extravaganza", "15% off Electronics items when Electronics subtotal is ₹10000 or more", 2)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        elec_subtotal = sum(
            item["product"].final_price_inr * item["quantity"]
            for item in cart if "electronics" in item["product"].category.lower()
        )
        return elec_subtotal >= 10000.0

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        elec_subtotal = sum(
            item["product"].final_price_inr * item["quantity"]
            for item in cart if "electronics" in item["product"].category.lower()
        )
        return elec_subtotal * 0.15


class BooksMultiBuyRule(DiscountRule):
    """IF total quantity of Books items >= 3 THEN apply 12% discount on Books items."""
    def __init__(self) -> None:
        super().__init__("Bookworm Bundle", "12% off Books when buying 3 or more Books", 3)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        books_qty = sum(
            item["quantity"]
            for item in cart if "books" in item["product"].category.lower()
        )
        return books_qty >= 3

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        books_subtotal = sum(
            item["product"].final_price_inr * item["quantity"]
            for item in cart if "books" in item["product"].category.lower()
        )
        return books_subtotal * 0.12


class NewUserWelcomeRule(DiscountRule):
    """IF customer is a new user AND subtotal >= ₹2000 THEN apply ₹500 flat discount."""
    def __init__(self) -> None:
        super().__init__("New User Welcome", "Flat ₹500 discount for new users on subtotals of ₹2000 or more", 4)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        return customer_info.get("is_new_user", False) and subtotal >= 2000.0

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        return 500.0


class PremiumCategoryRule(DiscountRule):
    """IF subtotal of brand 'Nova' or 'Polar' items >= ₹15000 THEN apply ₹1000 flat discount."""
    def __init__(self) -> None:
        super().__init__("Premium Brand Reward", "Flat ₹1000 discount when buying ₹15000 or more from Nova or Polar brands", 5)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        premium_subtotal = sum(
            item["product"].final_price_inr * item["quantity"]
            for item in cart if item["product"].brand.lower() in ["nova", "polar"]
        )
        return premium_subtotal >= 15000.0

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        return 1000.0


class LowRatingClearanceRule(DiscountRule):
    """IF item has rating < 3.0 THEN apply 20% discount on those clearance items."""
    def __init__(self) -> None:
        super().__init__("Clearance Special", "20% off items rated under 3.0", 6)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        return any(item["product"].rating < 3.0 for item in cart)

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        clearance_subtotal = sum(
            item["product"].final_price_inr * item["quantity"]
            for item in cart if item["product"].rating < 3.0
        )
        return clearance_subtotal * 0.20


class BulkQuantityRule(DiscountRule):
    """IF total quantity of items in cart >= 10 THEN apply flat ₹300 discount."""
    def __init__(self) -> None:
        super().__init__("Mega Bulk Discount", "Flat ₹300 off for carts with 10 or more items", 7)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        total_items = sum(item["quantity"] for item in cart)
        return total_items >= 10

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        return 300.0


class CitySpecialRule(DiscountRule):
    """IF customer is from Bengaluru or Mumbai AND subtotal >= ₹1500 THEN apply flat ₹200 discount."""
    def __init__(self) -> None:
        super().__init__("Metro City Offer", "Flat ₹200 off for Bengaluru/Mumbai customers on subtotals of ₹1500 or more", 8)

    def evaluate_condition(self, cart: List[dict], subtotal: float, customer_info: dict) -> bool:
        city = customer_info.get("city", "").strip().lower()
        return city in ["bengaluru", "mumbai"] and subtotal >= 1500.0

    def apply_action(self, cart: List[dict], subtotal: float, customer_info: dict) -> float:
        return 200.0


class RuleEngine:
    """A production rule engine implementing prioritized forward-chaining style cart discounts."""
    def __init__(self) -> None:
        # Register and sort rules by priority
        self.rules: List[DiscountRule] = [
            SpenderDiscountRule(),
            ElectronicsSpecialRule(),
            BooksMultiBuyRule(),
            NewUserWelcomeRule(),
            PremiumCategoryRule(),
            LowRatingClearanceRule(),
            BulkQuantityRule(),
            CitySpecialRule()
        ]
        self.rules.sort(key=lambda r: r.priority)

    def evaluate_cart(self, cart: List[dict], customer_info: dict = None) -> dict:
        """Evaluates cart against prioritized production rules.
        
        Each cart item is a dict: {"product": Product, "quantity": int}
        """
        if customer_info is None:
            customer_info = {}

        # Calculate initial subtotal
        subtotal = sum(item["product"].final_price_inr * item["quantity"] for item in cart)
        
        applied_rules = []
        total_discount = 0.0
        remaining_subtotal = subtotal

        # Evaluate rules sequentially based on priority order
        for rule in self.rules:
            if rule.evaluate_condition(cart, remaining_subtotal, customer_info):
                discount = rule.apply_action(cart, remaining_subtotal, customer_info)
                # Ensure discount doesn't exceed the remaining subtotal
                if discount > remaining_subtotal:
                    discount = remaining_subtotal
                
                if discount > 0:
                    total_discount += discount
                    remaining_subtotal -= discount
                    applied_rules.append({
                        "name": rule.name,
                        "description": rule.description,
                        "discount_amount": round(discount, 2)
                    })

        tax_rate = 0.18  # 18% GST standard
        tax = remaining_subtotal * tax_rate
        final_total = remaining_subtotal + tax

        return {
            "subtotal": round(subtotal, 2),
            "total_discount": round(total_discount, 2),
            "discounted_subtotal": round(remaining_subtotal, 2),
            "applied_rules": applied_rules,
            "tax": round(tax, 2),
            "final_total": round(final_total, 2)
        }
