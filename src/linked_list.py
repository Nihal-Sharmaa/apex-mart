from typing import Optional, Generator
from src.models import Product, ListNode

class LinkedList:
    """A custom singly linked list implementation for e-commerce catalog storage.
    
    Supports O(1) insertion at the tail and O(N) deletion/traversal.
    """
    def __init__(self) -> None:
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self._size: int = 0

    def insert(self, product: Product) -> None:
        """Inserts a product at the tail of the linked list in O(1) time."""
        new_node = ListNode(product)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def delete(self, product_id: str) -> bool:
        """Removes the product with the specified product_id from the list.
        
        Returns:
            True if the product was found and deleted, False otherwise.
        """
        curr = self.head
        prev: Optional[ListNode] = None
        
        while curr is not None:
            if curr.product.product_id == product_id:
                # Update head if it's the node to delete
                if prev is None:
                    self.head = curr.next
                    if self.head is None:
                        self.tail = None
                else:
                    prev.next = curr.next
                    # Update tail if the last node is deleted
                    if curr == self.tail:
                        self.tail = prev
                self._size -= 1
                return True
            prev = curr
            curr = curr.next
            
        return False

    def traverse(self) -> Generator[Product, None, None]:
        """Generator that yields products by traversing the list."""
        curr = self.head
        while curr is not None:
            yield curr.product
            curr = curr.next

    def __len__(self) -> int:
        """Returns the number of products currently in the list."""
        return self._size
