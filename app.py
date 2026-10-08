"""Web API wrapping the custom data-structure catalog."""
import os
import time
from dataclasses import asdict
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.avl_tree import AVLTree
from src.graph import ProductGraph
from src.hash_table import ProductLookupSystem, SearchTermFrequencyCounter, ChainingHashTable
from src.heap import MaxHeap, PriorityQueue
from src.linked_list import LinkedList
from src.models import Order, Product
from src.rule_engine import RuleEngine
from src.search import a_star_search, bfs_search, greedy_best_first_search
from src.utils import load_products_from_csv
from src.analytics import EcommerceAnalytics

from contextlib import asynccontextmanager

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(ROOT, "products.csv")
STATIC_DIR = os.path.join(ROOT, "static")

catalog = LinkedList()
price_tree = AVLTree()
lookup = ProductLookupSystem()
top_rated = MaxHeap()
orders = PriorityQueue()
graph = ProductGraph()
rules = RuleEngine()
trending = SearchTermFrequencyCounter()
chaining_demo = ChainingHashTable(slots=31)
product_map = {}
products: List[Product] = []
analytics: Optional[EcommerceAnalytics] = None


def to_dict(product: Product) -> dict:
    return asdict(product)


def seed_structures() -> None:
    global products, analytics
    products = load_products_from_csv(CSV_PATH)
    analytics = EcommerceAnalytics(CSV_PATH)

    for product in products:
        catalog.insert(product)
        price_tree.insert(product)
        lookup.insert(product)
        top_rated.insert(product)
        chaining_demo.insert(product.product_id, product)
        product_map[product.product_id] = product

    # Bipartite user–product graph: 12 users, edges by round-robin category groups
    user_count = 12
    for i in range(1, user_count + 1):
        graph.add_node(f"U{i}")

    for idx, product in enumerate(products):
        user_a = f"U{(idx % user_count) + 1}"
        user_b = f"U{((idx * 3) % user_count) + 1}"
        weight = 1.0 + (product.rating / 5.0)
        graph.add_edge(user_a, product.product_id, weight)
        if user_a != user_b:
            graph.add_edge(user_b, product.product_id, max(1.0, product.units_sold / 5000.0))


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_structures()
    yield



app = FastAPI(title="Apex Mart E-Commerce Catalog", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CartItemIn(BaseModel):
    product_id: str
    quantity: int = 1


class CartIn(BaseModel):
    items: List[CartItemIn]
    is_new_user: bool = False
    city: str = ""


class OrderIn(BaseModel):
    customer_name: str
    delivery_deadline: int
    product_ids: List[str] = []


class ProductImageUpdate(BaseModel):
    image_url: str


class SearchQuery(BaseModel):
    category: str = "Books"
    min_rating: float = 3.5
    max_price: float = 5000.0
    start_node: str = "U1"


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "products": len(products)}


@app.get("/api/products")
def list_products(
    category: Optional[str] = None,
    min_rating: float = 0.0,
    limit: int = Query(60, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    items = []
    for product in catalog.traverse():
        if category and product.category.lower() != category.lower():
            continue
        if product.rating < min_rating:
            continue
        items.append(to_dict(product))
    return {
        "total": len(items),
        "products": items[offset:offset + limit],
        "categories": sorted({p.category for p in products}),
    }


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    start = time.perf_counter_ns()
    product = lookup.search(product_id)
    elapsed = (time.perf_counter_ns() - start) / 1000.0
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": to_dict(product), "lookup_us": round(elapsed, 3), "structure": "hash table"}


@app.post("/api/products/{product_id}/image")
def update_product_image(product_id: str, body: ProductImageUpdate) -> dict:
    product = lookup.search(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.image_url = body.image_url.strip()
    if analytics is not None and hasattr(analytics, 'df') and not analytics.df.empty:
        analytics.df.loc[analytics.df['Product_ID'] == product_id, 'Image_URL'] = body.image_url.strip()
    return {"status": "success", "product": to_dict(product)}


@app.get("/api/price-range")
def price_range(min_price: float = 0.0, max_price: float = 100000.0) -> dict:
    start = time.perf_counter_ns()
    matches = price_tree.range_query(min_price, max_price)
    avl_us = (time.perf_counter_ns() - start) / 1000.0

    start = time.perf_counter_ns()
    linear = [p for p in products if min_price <= p.final_price_inr <= max_price]
    linear_us = (time.perf_counter_ns() - start) / 1000.0

    return {
        "count": len(matches),
        "products": [to_dict(p) for p in matches[:80]],
        "avl_us": round(avl_us, 3),
        "linear_scan_us": round(linear_us, 3),
        "balanced": price_tree.is_balanced(),
    }


@app.get("/api/top-rated")
def get_top_rated(n: int = Query(10, ge=1, le=50)) -> dict:
    return {"products": [to_dict(p) for p in top_rated.get_top_n(n)]}


@app.get("/api/recommendations/{product_id}")
def recommendations(product_id: str) -> dict:
    if lookup.search(product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    recs = graph.bfs_recommendations(product_id, max_depth=2)
    hydrated = []
    for rec in recs[:8]:
        product = lookup.search(rec["product_id"])
        if product:
            row = to_dict(product)
            row["score"] = rec["score"]
            row["depth"] = rec["depth"]
            hydrated.append(row)
    return {"product_id": product_id, "recommendations": hydrated}


@app.get("/api/search")
def search_products(q: str = "") -> dict:
    term = q.strip()
    if term:
        trending.record_query(term)
    needle = term.lower()
    matches = []
    for product in products:
        blob = f"{product.product_name} {product.category} {product.brand} {product.product_id}".lower()
        if not needle or needle in blob:
            matches.append(to_dict(product))
        if len(matches) >= 40:
            break
    return {"query": term, "products": matches, "trending": trending.get_top_n(5)}


@app.post("/api/search/heuristic")
def heuristic_search(body: SearchQuery) -> dict:
    query = {
        "category": body.category,
        "min_rating": body.min_rating,
        "max_price": body.max_price,
    }
    start = body.start_node if body.start_node in graph.adj else "U1"
    gbfs = greedy_best_first_search(graph, start, query, product_map)
    astar = a_star_search(graph, start, query, product_map)
    bfs = bfs_search(graph, start, query, product_map)

    def pack(result):
        found, explored, path = result
        product = to_dict(product_map[found]) if found and found in product_map else None
        return {"found": found, "nodes_explored": explored, "path": path, "product": product}

    return {"query": query, "start": start, "gbfs": pack(gbfs), "astar": pack(astar), "bfs": pack(bfs)}


@app.post("/api/cart/evaluate")
def evaluate_cart(body: CartIn) -> dict:
    cart = []
    for item in body.items:
        product = lookup.search(item.product_id)
        if product is None:
            raise HTTPException(status_code=404, detail=f"Unknown product {item.product_id}")
        cart.append({"product": product, "quantity": max(1, item.quantity)})
    result = rules.evaluate_cart(cart, {"is_new_user": body.is_new_user, "city": body.city})
    result["items"] = [
        {
            "product_id": item["product"].product_id,
            "product_name": item["product"].product_name,
            "quantity": item["quantity"],
            "unit_price": item["product"].final_price_inr,
        }
        for item in cart
    ]
    return result


demo_orders: List[dict] = []


class CheckoutOrderIn(BaseModel):
    order_id: str
    customer_name: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    pin: str
    payment_method: str
    items: List[dict]
    subtotal: float
    shipping: float
    tax: float
    total: float
    order_date: str
    status: str = "Order Placed"


@app.post("/api/orders/checkout")
def record_checkout_order(body: CheckoutOrderIn) -> dict:
    order_data = body.model_dump() if hasattr(body, 'model_dump') else body.dict()
    demo_orders.insert(0, order_data)
    return {"status": "success", "order": order_data}


@app.get("/api/orders/history")
def get_checkout_orders() -> dict:
    return {"orders": demo_orders}


@app.post("/api/orders")
def place_order(body: OrderIn) -> dict:
    order_id = f"O{len(orders) + 1:04d}"
    orders.enqueue(Order(order_id=order_id, delivery_deadline=body.delivery_deadline, customer_name=body.customer_name))
    return {"order_id": order_id, "queue_size": len(orders)}


@app.get("/api/orders/next")
def peek_next_order() -> dict:
    nxt = orders.peek()
    if nxt is None:
        return {"order": None}
    return {"order": asdict(nxt), "queue_size": len(orders)}


@app.post("/api/orders/process")
def process_next_order() -> dict:
    nxt = orders.dequeue()
    if nxt is None:
        return {"message": "No pending orders", "order": None}
    return {"message": "Processing earliest deadline", "order": asdict(nxt), "queue_size": len(orders)}


@app.get("/api/lab/stats")
def lab_stats() -> dict:
    return {
        "catalog_size": len(catalog),
        "avl_balanced": price_tree.is_balanced(),
        "hash_table": chaining_demo.get_stats(),
        "trending_searches": trending.get_top_n(5),
        "top_rated": [to_dict(p) for p in top_rated.get_top_n(5)],
        "order_queue_size": len(orders),
        "graph_nodes": len(graph.adj),
        "rules": [{"name": r.name, "priority": r.priority, "description": r.description} for r in rules.rules],
    }


class AnalyticsFilterIn(BaseModel):
    min_price: float = 0.0
    max_price: float = 1000000.0
    category: Optional[str] = "all"
    min_rating: float = 0.0
    sort_by: str = "price"
    sort_order: str = "asc"
    search_query: str = ""


@app.get("/api/analytics/kpis")
def get_analytics_kpis() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return analytics.get_dashboard_summary()


@app.get("/api/analytics/dataset-overview")
def get_dataset_overview() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return analytics.get_dataset_overview()


@app.post("/api/analytics/filter")
def filter_analytics_products(body: AnalyticsFilterIn) -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return analytics.filter_and_sort_products(
        min_price=body.min_price,
        max_price=body.max_price,
        category=body.category,
        min_rating=body.min_rating,
        sort_by=body.sort_by,
        sort_order=body.sort_order,
        search_query=body.search_query
    )


@app.get("/api/analytics/statistics")
def get_summary_statistics() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return analytics.get_summary_statistics()


@app.get("/api/analytics/sales-summary")
def get_sales_summary() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return analytics.get_sales_analysis()


@app.get("/api/analytics/visualizations")
def get_visualizations() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return analytics.generate_visualizations()


@app.get("/api/analytics/business-insights")
def get_business_insights() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return {"insights": analytics.get_business_insights()}


@app.get("/api/analytics/full-dashboard")
def get_full_dashboard() -> dict:
    if analytics is None:
        raise HTTPException(status_code=500, detail="Analytics module not initialized")
    return {
        "dashboard_summary": analytics.get_dashboard_summary(),
        "overview": analytics.get_dataset_overview(),
        "statistics": analytics.get_summary_statistics(),
        "sales": analytics.get_sales_analysis(),
        "visualizations": analytics.generate_visualizations(),
        "insights": analytics.get_business_insights(),
        "default_filter": analytics.filter_and_sort_products()
    }



app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

