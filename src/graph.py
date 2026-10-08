from typing import Dict, List, Set, Tuple, Any

class ProductGraph:
    """An adjacency-list graph representing user-product interactions (purchases/views)."""
    def __init__(self) -> None:
        # Maps node_id -> {neighbor_id: weight}
        self.adj: Dict[str, Dict[str, float]] = {}

    def add_node(self, node_id: str) -> None:
        """Adds a node to the graph if it doesn't already exist."""
        if node_id not in self.adj:
            self.adj[node_id] = {}

    def add_edge(self, node_a: str, node_b: str, weight: float = 1.0) -> None:
        """Adds an undirected edge between node_a and node_b with a given weight."""
        self.add_node(node_a)
        self.add_node(node_b)
        self.adj[node_a][node_b] = self.adj[node_a].get(node_b, 0.0) + weight
        self.adj[node_b][node_a] = self.adj[node_b].get(node_a, 0.0) + weight

    def get_neighbors(self, node_id: str) -> Dict[str, float]:
        """Returns the neighbors of a node and their edge weights."""
        return self.adj.get(node_id, {})

    def bfs_recommendations(self, start_node: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Performs BFS up to max_depth to find recommended products.
        
        Returns:
            List of dicts containing 'product_id', 'depth', and 'score' (path strength).
        """
        if start_node not in self.adj:
            return []

        visited = {start_node}
        # queue elements: (current_node, current_depth, path_weight_product)
        queue = [(start_node, 0, 1.0)]
        recommendations = {}

        # BFS Queue traversal
        head = 0
        while head < len(queue):
            curr, depth, path_weight = queue[head]
            head += 1

            if depth > 0:
                # If it's a product node (starts with 'P') and not the starting node
                if curr.startswith('P') and curr != start_node:
                    # Recommendation score is the maximum or sum of path weights.
                    # We will sum path weights for multiple discovery paths.
                    recommendations[curr] = recommendations.get(curr, 0.0) + path_weight

            if depth < max_depth:
                # Sort neighbors by weight descending to process stronger connections first
                neighbors = sorted(self.adj[curr].items(), key=lambda x: x[1], reverse=True)
                for neighbor, weight in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        # Accumulate path weight (e.g., sum of edge weights or product of weights)
                        queue.append((neighbor, depth + 1, path_weight * weight))

        # Format and sort recommendations by score descending, then depth ascending
        result = []
        for prod_id, score in recommendations.items():
            # Find the depth at which it was first visited
            # Let's search queue for the node
            dep = next(q[1] for q in queue if q[0] == prod_id)
            result.append({
                "product_id": prod_id,
                "depth": dep,
                "score": score
            })

        result.sort(key=lambda x: (-x["score"], x["depth"]))
        return result

    def dfs_recommendations(self, start_node: str, max_depth: int = 3) -> List[List[str]]:
        """Performs DFS to find all paths of user-product-user chains up to max_depth.
        
        Returns:
            List of exploration paths (lists of node IDs).
        """
        if start_node not in self.adj:
            return []

        paths: List[List[str]] = []
        self._dfs(start_node, max_depth, [start_node], {start_node}, paths)
        return paths

    def _dfs(self, node: str, max_depth: int, current_path: List[str], visited: Set[str], paths: List[List[str]]) -> None:
        if len(current_path) - 1 >= 1:
            paths.append(list(current_path))

        if len(current_path) - 1 >= max_depth:
            return

        for neighbor in self.adj.get(node, {}):
            if neighbor not in visited:
                visited.add(neighbor)
                self._dfs(neighbor, max_depth, current_path + [neighbor], visited, paths)
                visited.remove(neighbor)  # Backtrack
