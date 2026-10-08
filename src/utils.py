import csv
from typing import List
from src.models import Product

def load_products_from_csv(file_path: str) -> List[Product]:
    """Loads product records from a CSV file and returns a list of Product dataclasses.
    
    Handles header mapping and type casting for the 12 fields.
    """
    products: List[Product] = []
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Strip key names in case of trailing spaces in the CSV header
            row = {k.strip(): v for k, v in row.items()}
            
            product = Product(
                product_id=row['Product_ID'],
                product_name=row['Product_Name'],
                category=row['Category'],
                brand=row['Brand'],
                price_inr=float(row['Price_INR']),
                discount_percent=float(row['Discount_Percent']),
                final_price_inr=float(row['Final_Price_INR']),
                rating=float(row['Rating']),
                reviews=int(row['Reviews']),
                stock=int(row['Stock']),
                units_sold=int(row['Units_Sold']),
                customer_city=row['Customer_City'],
                image_url=row.get('Image_URL', row.get('image_url', ''))
            )
            products.append(product)
    return products
