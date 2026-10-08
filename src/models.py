from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Product:
    """Represents an e-commerce product matching the dataset schema."""
    product_id: str
    product_name: str
    category: str
    brand: str
    price_inr: float
    discount_percent: float
    final_price_inr: float
    rating: float
    reviews: int
    stock: int
    units_sold: int
    customer_city: str
    image_url: str = ""


class ListNode:
    """A node in a custom singly linked list."""
    def __init__(self, product: Product) -> None:
        self.product: Product = product
        self.next: Optional[ListNode] = None


class AVLNode:
    """A node in an auto-balancing AVL Tree.
    
    To handle duplicate keys (multiple products with the exact same Final_Price_INR),
    each node stores a list of Product objects that share the same price.
    """
    def __init__(self, price: float, product: Product) -> None:
        self.price: float = price
        self.products: List[Product] = [product]
        self.left: Optional[AVLNode] = None
        self.right: Optional[AVLNode] = None
        self.height: int = 1


@dataclass
class Order:
    """Represents a customer order with a delivery deadline."""
    order_id: str
    delivery_deadline: int
    customer_name: str

