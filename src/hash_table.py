from typing import List, Any, Optional, Tuple, Dict
from src.models import Product

class HashNode:
    """A node in a custom hash table chain."""
    def __init__(self, key: str, value: Any) -> None:
        self.key: str = key
        self.value: Any = value
        self.next: Optional[HashNode] = None


def simple_hash(key: str, slots: int) -> int:
    """A simple ASCII sum polynomial hash function modulo slots."""
    hash_val = 0
    for char in str(key):
        hash_val = (hash_val * 31 + ord(char)) % slots
    return hash_val


class ChainingHashTable:
    """A hash table resolving collisions via chaining (linked lists)."""
    def __init__(self, slots: int = 31) -> None:
        self.slots: int = slots
        self.table: List[Optional[HashNode]] = [None] * slots
        self.num_items: int = 0

    def insert(self, key: str, value: Any) -> None:
        """Inserts a key-value pair, updating the value if the key exists."""
        idx = simple_hash(key, self.slots)
        curr = self.table[idx]
        while curr:
            if curr.key == key:
                curr.value = value
                return
            curr = curr.next

        # Insert at the head of the chain
        new_node = HashNode(key, value)
        new_node.next = self.table[idx]
        self.table[idx] = new_node
        self.num_items += 1

    def get(self, key: str) -> Optional[Any]:
        """Retrieves value by key. Returns None if not found."""
        idx = simple_hash(key, self.slots)
        curr = self.table[idx]
        while curr:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return None

    def delete(self, key: str) -> bool:
        """Removes the key-value pair. Returns True if deleted, False otherwise."""
        idx = simple_hash(key, self.slots)
        curr = self.table[idx]
        prev = None
        while curr:
            if curr.key == key:
                if prev:
                    prev.next = curr.next
                else:
                    self.table[idx] = curr.next
                self.num_items -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def contains(self, key: str) -> bool:
        """Checks if key exists in the hash table."""
        return self.get(key) is not None

    def get_stats(self) -> dict:
        """Returns statistics for collision analysis."""
        collisions = 0
        bucket_lengths = []
        for head in self.table:
            length = 0
            curr = head
            while curr:
                length += 1
                curr = curr.next
            bucket_lengths.append(length)
            if length > 1:
                collisions += (length - 1)
        
        load_factor = self.num_items / self.slots if self.slots > 0 else 0.0
        return {
            "slots": self.slots,
            "num_items": self.num_items,
            "load_factor": round(load_factor, 2),
            "collisions": collisions,
            "bucket_lengths": bucket_lengths
        }


# Sentinel to mark deleted slots in open addressing
DELETED = ("__DELETED__", None)

class OpenAddressingHashTable:
    """A hash table resolving collisions via open addressing (linear probing)."""
    def __init__(self, slots: int = 31) -> None:
        self.slots: int = slots
        self.table: List[Optional[Tuple[str, Any]]] = [None] * slots
        self.num_items: int = 0
        # Tracks cumulative insert collisions
        self.total_insert_collisions: int = 0

    def insert(self, key: str, value: Any) -> None:
        """Inserts key-value pair. Raises IndexError if table is full."""
        if self.num_items >= self.slots:
            raise IndexError("Hash Table Full")

        start_idx = simple_hash(key, self.slots)
        idx = start_idx
        first_deleted_idx = -1
        collisions = 0

        for i in range(self.slots):
            slot = self.table[idx]
            if slot is None:
                # Found empty slot
                insert_idx = first_deleted_idx if first_deleted_idx != -1 else idx
                self.table[insert_idx] = (key, value)
                self.num_items += 1
                self.total_insert_collisions += collisions
                return
            elif slot == DELETED:
                # Keep track of first deleted position to reuse
                if first_deleted_idx == -1:
                    first_deleted_idx = idx
            elif slot[0] == key:
                # Key already exists, update value
                self.table[idx] = (key, value)
                self.total_insert_collisions += collisions
                return
            else:
                # Slot is occupied by a different active key (collision!)
                collisions += 1
            
            idx = (idx + 1) % self.slots

        # If we exited loop and found a deleted slot, we can insert there
        if first_deleted_idx != -1:
            self.table[first_deleted_idx] = (key, value)
            self.num_items += 1
            self.total_insert_collisions += collisions
            return

        raise IndexError("Hash Table Full")

    def get(self, key: str) -> Optional[Any]:
        """Retrieves value by key. Returns None if not found."""
        start_idx = simple_hash(key, self.slots)
        idx = start_idx

        for _ in range(self.slots):
            slot = self.table[idx]
            if slot is None:
                return None
            if slot != DELETED and slot[0] == key:
                return slot[1]
            idx = (idx + 1) % self.slots
        return None

    def delete(self, key: str) -> bool:
        """Removes the key-value pair. Returns True if deleted, False otherwise."""
        start_idx = simple_hash(key, self.slots)
        idx = start_idx

        for i in range(self.slots):
            slot = self.table[idx]
            if slot is None:
                return False
            if slot != DELETED and slot[0] == key:
                self.table[idx] = DELETED
                self.num_items -= 1
                return True
            idx = (idx + 1) % self.slots
        return False

    def contains(self, key: str) -> bool:
        """Checks if key exists in the hash table."""
        return self.get(key) is not None

    def get_stats(self) -> dict:
        """Returns statistics for collision analysis."""
        load_factor = self.num_items / self.slots if self.slots > 0 else 0.0
        return {
            "slots": self.slots,
            "num_items": self.num_items,
            "load_factor": round(load_factor, 2),
            "collisions": self.total_insert_collisions
        }


class ProductLookupSystem:
    """A high-performance lookup system using Python's dict mapping product_id to Product."""
    def __init__(self) -> None:
        self.lookup: Dict[str, Product] = {}

    def insert(self, product: Product) -> None:
        """Adds a product to the system."""
        self.lookup[product.product_id] = product

    def search(self, product_id: str) -> Optional[Product]:
        """Retrieves product by ID in O(1) time."""
        return self.lookup.get(product_id)

    def delete(self, product_id: str) -> bool:
        """Deletes product by ID in O(1) time. Returns True if deleted."""
        if product_id in self.lookup:
            del self.lookup[product_id]
            return True
        return False

    def __len__(self) -> int:
        return len(self.lookup)


class SearchTermFrequencyCounter:
    """A search term frequency counter tracking and ranking query strings."""
    def __init__(self) -> None:
        self.frequencies: Dict[str, int] = {}

    def record_query(self, term: str) -> None:
        """Records a search query, incrementing its count."""
        cleaned_term = term.strip().lower()
        if cleaned_term:
            self.frequencies[cleaned_term] = self.frequencies.get(cleaned_term, 0) + 1

    def get_top_n(self, n: int = 5) -> List[Tuple[str, int]]:
        """Returns the top n most queried terms sorted by frequency descending."""
        sorted_terms = sorted(self.frequencies.items(), key=lambda x: (-x[1], x[0]))
        return sorted_terms[:n]
