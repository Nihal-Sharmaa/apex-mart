import heapq
from typing import List, Any, Optional
from src.models import Order

class MinHeap:
    """A custom Min-Heap implementation from scratch using an array."""
    def __init__(self, key=lambda x: x):
        self.heap: List[Any] = []
        self.key = key

    def parent(self, i: int) -> int:
        return (i - 1) // 2

    def left_child(self, i: int) -> int:
        return 2 * i + 1

    def right_child(self, i: int) -> int:
        return 2 * i + 2

    def swap(self, i: int, j: int) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, item: Any) -> None:
        """Inserts an item into the Min-Heap."""
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def _sift_up(self, i: int) -> None:
        while i > 0 and self.key(self.heap[i]) < self.key(self.heap[self.parent(i)]):
            self.swap(i, self.parent(i))
            i = self.parent(i)

    def peek(self) -> Optional[Any]:
        """Returns the minimum element without removing it."""
        return self.heap[0] if self.heap else None

    def extract_min(self) -> Optional[Any]:
        """Removes and returns the minimum element from the heap."""
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def _sift_down(self, i: int) -> None:
        min_idx = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < len(self.heap) and self.key(self.heap[left]) < self.key(self.heap[min_idx]):
            min_idx = left

        if right < len(self.heap) and self.key(self.heap[right]) < self.key(self.heap[min_idx]):
            min_idx = right

        if i != min_idx:
            self.swap(i, min_idx)
            self._sift_down(min_idx)

    def __len__(self) -> int:
        return len(self.heap)


class MaxHeap:
    """A Max-Heap simulation using Python's heapq module (by negating values)."""
    def __init__(self):
        self._heap: List[tuple] = []
        self._index: int = 0  # tie-breaker counter

    def insert(self, product: Any) -> None:
        """Inserts a product into the Max-Heap prioritizing rating."""
        rating = getattr(product, 'rating', None)
        if rating is None:
            rating = product.get('rating', 0.0)
        
        # Negate rating to simulate max heap with heapq min heap
        heapq.heappush(self._heap, (-rating, self._index, product))
        self._index += 1

    def extract_max(self) -> Optional[Any]:
        """Removes and returns the product with the maximum rating."""
        if not self._heap:
            return None
        _, _, product = heapq.heappop(self._heap)
        return product

    def peek(self) -> Optional[Any]:
        """Returns the product with the maximum rating without removing it."""
        if not self._heap:
            return None
        return self._heap[0][2]

    def get_top_n(self, n: int) -> List[Any]:
        """Returns the n highest-rated products without mutating the heap."""
        snapshot = list(self._heap)
        items: List[Any] = []
        for _ in range(min(n, len(snapshot))):
            _, _, product = heapq.heappop(snapshot)
            items.append(product)
        return items

    def __len__(self) -> int:
        return len(self._heap)


class PriorityQueue:
    """A priority queue for order fulfillment, processing earliest delivery deadlines first."""
    def __init__(self):
        self.min_heap = MinHeap(key=lambda order: order.delivery_deadline)

    def enqueue(self, order: Order) -> None:
        """Adds an order to the priority queue."""
        self.min_heap.insert(order)

    def dequeue(self) -> Optional[Order]:
        """Removes and returns the next order to fulfill."""
        return self.min_heap.extract_min()

    def peek(self) -> Optional[Order]:
        """Returns the next order to fulfill without removing it."""
        return self.min_heap.peek()

    def __len__(self) -> int:
        return len(self.min_heap)
