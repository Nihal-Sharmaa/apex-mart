"""
Regenerate products.csv with:
  - Realistic INR retail prices per product type
  - Recalculated Final_Price_INR
  - Curated Unsplash image URLs per product name
"""
import pandas as pd
import random
import os

random.seed(42)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "products.csv")

df = pd.read_csv(CSV_PATH)

# ── Realistic INR retail price ranges (min, max) per product name ──────────
PRICE_RANGES = {
    # Beauty
    "Lip Balm":            (149,   349),
    "Face Wash":           (149,   499),
    "Body Lotion":         (199,   699),
    "Shampoo":             (199,   599),
    "Moisturizer":         (299,   999),
    "Sunscreen":           (299,   799),
    "Hair Serum":          (299,   899),
    "Perfume":             (799,  2499),
    # Books (education/tech)
    "Data Structures":     (349,   699),
    "Statistics":          (299,   649),
    "Computer Networks":   (349,   749),
    "Database Systems":    (349,   699),
    "Python Programming":  (399,   799),
    "Web Development":     (349,   749),
    "AI Fundamentals":     (449,   899),
    "Machine Learning":    (499,   999),
    # Electronics
    "USB Cable":           (199,   499),
    "Laptop Stand":        (699,  1999),
    "Power Bank":          (999,  2999),
    "Bluetooth Speaker":   (999,  4999),
    "Webcam":              (1499, 4999),
    "Wireless Headphones": (1499, 7999),
    "Smartwatch":          (2499, 7999),
    "Smartphone":          (8999, 24999),
    # Fashion
    "T-Shirt":             (299,   999),
    "Jeans":               (799,  2499),
    "Hoodie":              (799,  2499),
    "Sunglasses":          (499,  1999),
    "Backpack":            (799,  2999),
    "Sneakers":            (1299, 4999),
    "Jacket":              (1499, 4999),
    "Wrist Watch":         (1499, 5999),
    # Home & Kitchen
    "Water Bottle":        (299,   799),
    "Storage Box":         (349,   899),
    "Table Lamp":          (499,  1499),
    "Electric Kettle":     (699,  1999),
    "Dinner Set":          (999,  2999),
    "Mixer Grinder":       (1999, 4999),
    "Coffee Maker":        (1999, 5999),
    "Air Fryer":           (2999, 7999),
    # Sports
    "Skipping Rope":       (199,   499),
    "Gym Gloves":          (299,   699),
    "Football":            (499,  1499),
    "Yoga Mat":            (499,  1499),
    "Badminton Racket":    (799,  2499),
    "Cricket Bat":         (999,  3499),
    "Running Shoes":       (1499, 5999),
}

# ── High-quality Unsplash image URLs per product name ─────────────────────
IMAGES = {
    "Lip Balm":            "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?auto=format&fit=crop&w=600&q=80",
    "Face Wash":           "https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?auto=format&fit=crop&w=600&q=80",
    "Body Lotion":         "https://images.unsplash.com/photo-1526758097130-bab247274f58?auto=format&fit=crop&w=600&q=80",
    "Shampoo":             "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?auto=format&fit=crop&w=600&q=80",
    "Moisturizer":         "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80",
    "Sunscreen":           "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=600&q=80",
    "Hair Serum":          "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=600&q=80",
    "Perfume":             "https://images.unsplash.com/photo-1541643600914-78b084683702?auto=format&fit=crop&w=600&q=80",
    "Data Structures":     "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
    "Statistics":          "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80",
    "Computer Networks":   "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=600&q=80",
    "Database Systems":    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=600&q=80",
    "Python Programming":  "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=600&q=80",
    "Web Development":     "https://images.unsplash.com/photo-1547658719-da2b51169166?auto=format&fit=crop&w=600&q=80",
    "AI Fundamentals":     "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?auto=format&fit=crop&w=600&q=80",
    "Machine Learning":    "https://images.unsplash.com/photo-1555949963-aa79dcee981c?auto=format&fit=crop&w=600&q=80",
    "USB Cable":           "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=600&q=80",
    "Laptop Stand":        "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?auto=format&fit=crop&w=600&q=80",
    "Power Bank":          "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=600&q=80",
    "Bluetooth Speaker":   "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=600&q=80",
    "Webcam":              "https://images.unsplash.com/photo-1587202372583-49330a15584d?auto=format&fit=crop&w=600&q=80",
    "Wireless Headphones": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80",
    "Smartwatch":          "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80",
    "Smartphone":          "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
    "T-Shirt":             "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=600&q=80",
    "Jeans":               "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=600&q=80",
    "Hoodie":              "https://images.unsplash.com/photo-1556821840-3a63f15732ce?auto=format&fit=crop&w=600&q=80",
    "Sunglasses":          "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=600&q=80",
    "Backpack":            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80",
    "Sneakers":            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
    "Jacket":              "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80",
    "Wrist Watch":         "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80",
    "Water Bottle":        "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=600&q=80",
    "Storage Box":         "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=600&q=80",
    "Table Lamp":          "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80",
    "Electric Kettle":     "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=600&q=80",
    "Dinner Set":          "https://images.unsplash.com/photo-1599565117931-7b801663dfe0?auto=format&fit=crop&w=600&q=80",
    "Mixer Grinder":       "https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=600&q=80",
    "Coffee Maker":        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=600&q=80",
    "Air Fryer":           "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?auto=format&fit=crop&w=600&q=80",
    "Skipping Rope":       "https://images.unsplash.com/photo-1599058945522-28d584b6f0ff?auto=format&fit=crop&w=600&q=80",
    "Gym Gloves":          "https://images.unsplash.com/photo-1534258936925-c58bed479fcb?auto=format&fit=crop&w=600&q=80",
    "Football":            "https://images.unsplash.com/photo-1575361204480-aadea25e6e68?auto=format&fit=crop&w=600&q=80",
    "Yoga Mat":            "https://images.unsplash.com/photo-1599447292180-45fd84092ef4?auto=format&fit=crop&w=600&q=80",
    "Badminton Racket":    "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=600&q=80",
    "Cricket Bat":         "https://images.unsplash.com/photo-1531415074968-036ba1b575da?auto=format&fit=crop&w=600&q=80",
    "Running Shoes":       "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
}


def realistic_price(name, current_price):
    """Return a realistic retail INR price for the given product name."""
    lo, hi = PRICE_RANGES.get(name, (current_price * 0.8, current_price * 1.2))
    raw = random.uniform(lo, hi)
    # 60% X99-ending pricing, 40% round-to-50
    if random.random() < 0.6:
        base = int(raw / 100) * 100
        price = base + 99
        if price > hi:
            price = base - 1
        price = max(lo, price)
    else:
        price = round(raw / 50) * 50
        price = max(lo, min(hi, price))
    return round(float(price), 2)


# Apply new prices
new_prices = []
for _, row in df.iterrows():
    new_prices.append(realistic_price(row['Product_Name'], row['Price_INR']))

df['Price_INR'] = new_prices
df['Final_Price_INR'] = (df['Price_INR'] * (1 - df['Discount_Percent'] / 100)).round(2)

# Apply curated image URLs (overwrite all; fallback keeps existing if name not in dict)
df['Image_URL'] = df['Product_Name'].map(IMAGES).combine_first(df['Image_URL'])

# Save back
df.to_csv(CSV_PATH, index=False)
print("Done! products.csv updated.")
print(f"Rows: {len(df)}, Columns: {list(df.columns)}")
print()
print("Price distribution by category:")
for cat in sorted(df['Category'].unique()):
    sub = df[df['Category'] == cat]
    print(f"  {cat}: min={sub['Price_INR'].min():.0f}  max={sub['Price_INR'].max():.0f}  avg={sub['Price_INR'].mean():.0f}")
print()
print("Sample rows (first 6):")
print(df[['Product_ID', 'Product_Name', 'Category', 'Price_INR', 'Discount_Percent', 'Final_Price_INR', 'Image_URL']].head(6).to_string(index=False))
print()
print("Image_URL nulls:", df['Image_URL'].isna().sum())
