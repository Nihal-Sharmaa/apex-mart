from typing import List, Optional
from src.models import Product, AVLNode

class AVLTree:
    """An auto-balancing Binary Search Tree (AVL Tree) indexing products by Final_Price_INR.
    
    Supports duplicate keys by storing lists of products within each AVLNode.
    """
    def __init__(self) -> None:
        self.root: Optional[AVLNode] = None

    def insert(self, product: Product) -> None:
        """Inserts a product into the AVL Tree in O(log N) average/worst-case time."""
        self.root = self._insert(self.root, product)

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _right_rotate(self, y: AVLNode) -> AVLNode:
        """Performs a right rotation around node y.
        
             y                x
            / \              / \
           x   T3   -->     T1  y
          / \                  / \
         T1  T2               T2  T3
        """
        x = y.left
        assert x is not None
        T2 = x.right

        # Perform rotation
        x.right = y
        y.left = T2

        # Update heights
        y.height = max(self._get_height(y.left), self._get_height(y.right)) + 1
        x.height = max(self._get_height(x.left), self._get_height(x.right)) + 1

        return x

    def _left_rotate(self, x: AVLNode) -> AVLNode:
        """Performs a left rotation around node x.
        
             x                y
            / \              / \
           T1  y    -->     x   T3
              / \          / \
             T2  T3       T1  T2
        """
        y = x.right
        assert y is not None
        T2 = y.left

        # Perform rotation
        y.left = x
        x.right = T2

        # Update heights
        x.height = max(self._get_height(x.left), self._get_height(x.right)) + 1
        y.height = max(self._get_height(y.left), self._get_height(y.right)) + 1

        return y

    def _insert(self, node: Optional[AVLNode], product: Product) -> AVLNode:
        price = product.final_price_inr
        
        # 1. Standard BST Insertion
        if not node:
            return AVLNode(price, product)
        
        # Handling floats: check equality using a small delta
        if abs(node.price - price) < 1e-9:
            node.products.append(product)
            return node
        elif price < node.price:
            node.left = self._insert(node.left, product)
        else:
            node.right = self._insert(node.right, product)

        # 2. Update Height of Ancestor Node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

        # 3. Get the Balance Factor
        balance = self._get_balance(node)

        # 4. Handle 4 Unbalance Cases
        # Left-Left Case
        if balance > 1 and node.left and price < node.left.price:
            return self._right_rotate(node)

        # Right-Right Case
        if balance < -1 and node.right and price > node.right.price:
            return self._left_rotate(node)

        # Left-Right Case
        if balance > 1 and node.left and price > node.left.price:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right-Left Case
        if balance < -1 and node.right and price < node.right.price:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def search(self, price: float) -> List[Product]:
        """Searches for products with a specific final price in O(log N) time."""
        node = self._search(self.root, price)
        return node.products if node else []

    def _search(self, node: Optional[AVLNode], price: float) -> Optional[AVLNode]:
        if not node or abs(node.price - price) < 1e-9:
            return node
        if price < node.price:
            return self._search(node.left, price)
        return self._search(node.right, price)

    def range_query(self, min_price: float, max_price: float) -> List[Product]:
        """Returns products whose final price falls in [min_price, max_price] in O(k + log N)."""
        results: List[Product] = []
        self._range_query(self.root, min_price, max_price, results)
        return results

    def _range_query(self, node: Optional[AVLNode], min_price: float, max_price: float, results: List[Product]) -> None:
        if not node:
            return
        if node.price > min_price:
            self._range_query(node.left, min_price, max_price, results)
        if min_price <= node.price <= max_price:
            results.extend(node.products)
        if node.price < max_price:
            self._range_query(node.right, min_price, max_price, results)

    def inorder_traversal(self) -> List[Product]:
        """Traverses the AVL tree in-order to retrieve products in sorted order by price.
        
        Note: Retrieving all N elements in-order is O(N) time.
        """
        products_sorted: List[Product] = []
        self._inorder(self.root, products_sorted)
        return products_sorted

    def _inorder(self, node: Optional[AVLNode], lst: List[Product]) -> None:
        if node:
            self._inorder(node.left, lst)
            lst.extend(node.products)
            self._inorder(node.right, lst)

    def is_balanced(self) -> bool:
        """Verifies that the AVL tree satisfies the height-balance property."""
        return self._is_balanced_recursive(self.root)

    def _is_balanced_recursive(self, node: Optional[AVLNode]) -> bool:
        if not node:
            return True
        lh = self._get_height(node.left)
        rh = self._get_height(node.right)
        if abs(lh - rh) > 1:
            return False
        # Verify cached node height is correct
        if node.height != max(lh, rh) + 1:
            return False
        return self._is_balanced_recursive(node.left) and self._is_balanced_recursive(node.right)
