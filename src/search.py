import heapq
from typing import Dict, List, Tuple, Optional, Any
from src.models import Product

def calculate_heuristic(node_id: str, query: dict, product_map: Dict[str, Product]) -> float:
    """Estimates the relevance cost (mismatch) of a product node to a given query.
    
    Lower scores represent better matches.
    """
    if not node_id.startswith('P') or node_id not in product_map:
        # Non-product nodes (e.g. User nodes U1) have a baseline mismatch penalty
        return 20.0

    product = product_map[node_id]
    
    # 1. Category mismatch cost
    target_category = query.get("category", "").lower()
    category_cost = 0.0 if target_category in product.category.lower() else 10.0

    # 2. Rating mismatch cost: penalize products with ratings below target
    target_rating = query.get("min_rating", 0.0)
    rating_cost = max(0.0, target_rating - product.rating) * 5.0

    # 3. Price mismatch cost: penalize products with prices above target max
    max_price = query.get("max_price", 999999.0)
    price_cost = max(0.0, product.final_price_inr - max_price) / 1000.0

    return category_cost + rating_cost + price_cost


def greedy_best_first_search(
    graph: Any, 
    start_node: str, 
    query: dict, 
    product_map: Dict[str, Product]
) -> Tuple[Optional[str], int, List[str]]:
    """Performs Greedy Best-First Search prioritizing lowest heuristic cost h(n).
    
    Returns:
        Tuple of (found_product_id, num_nodes_explored, path)
    """
    pq: List[Tuple[float, int, str, List[str]]] = []
    counter = 0
    h_start = calculate_heuristic(start_node, query, product_map)
    heapq.heappush(pq, (h_start, counter, start_node, [start_node]))
    counter += 1

    visited = {start_node}
    nodes_explored = 0

    while pq:
        h_val, _, curr, path = heapq.heappop(pq)
        nodes_explored += 1

        # Goal check: product matches all query criteria (heuristic < 1.0)
        if curr.startswith('P') and h_val < 1.0:
            return curr, nodes_explored, path

        for neighbor in graph.get_neighbors(curr):
            if neighbor not in visited:
                visited.add(neighbor)
                h_neigh = calculate_heuristic(neighbor, query, product_map)
                heapq.heappush(pq, (h_neigh, counter, neighbor, path + [neighbor]))
                counter += 1

    return None, nodes_explored, []


def a_star_search(
    graph: Any, 
    start_node: str, 
    query: dict, 
    product_map: Dict[str, Product]
) -> Tuple[Optional[str], int, List[str]]:
    """Performs A* Search prioritizing f(n) = g(n) + h(n).
    
    Returns:
        Tuple of (found_product_id, num_nodes_explored, path)
    """
    pq: List[Tuple[float, float, int, str, List[str]]] = []
    counter = 0
    h_start = calculate_heuristic(start_node, query, product_map)
    heapq.heappush(pq, (h_start, 0.0, counter, start_node, [start_node]))
    counter += 1

    visited = {start_node: 0.0}  # maps node -> current g_val
    nodes_explored = 0

    while pq:
        f_val, g_val, _, curr, path = heapq.heappop(pq)
        nodes_explored += 1

        h_val = f_val - g_val
        # Goal check: product matches all query criteria
        if curr.startswith('P') and h_val < 1.0:
            return curr, nodes_explored, path

        for neighbor in graph.get_neighbors(curr):
            new_g = g_val + 1.0  # Traversal step cost = 1.0
            if neighbor not in visited or new_g < visited[neighbor]:
                visited[neighbor] = new_g
                h_neigh = calculate_heuristic(neighbor, query, product_map)
                f_neigh = new_g + h_neigh
                heapq.heappush(pq, (f_neigh, new_g, counter, neighbor, path + [neighbor]))
                counter += 1

    return None, nodes_explored, []


def bfs_search(
    graph: Any, 
    start_node: str, 
    query: dict, 
    product_map: Dict[str, Product]
) -> Tuple[Optional[str], int, List[str]]:
    """Performs uninformed Breadth-First Search to find the goal product.
    
    Returns:
        Tuple of (found_product_id, num_nodes_explored, path)
    """
    queue: List[Tuple[str, List[str]]] = [(start_node, [start_node])]
    visited = {start_node}
    nodes_explored = 0

    while queue:
        curr, path = queue.pop(0)
        nodes_explored += 1

        h_val = calculate_heuristic(curr, query, product_map)
        # Goal check: product matches all query criteria
        if curr.startswith('P') and h_val < 1.0:
            return curr, nodes_explored, path

        for neighbor in graph.get_neighbors(curr):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None, nodes_explored, []
