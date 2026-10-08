import io
import base64
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server thread safety
import matplotlib.pyplot as plt
import seaborn as sns


class EcommerceAnalytics:
    """Pandas-based Data Analysis Module for E-Commerce Product Catalog."""

    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.df: pd.DataFrame = pd.DataFrame()
        self.raw_df: pd.DataFrame = pd.DataFrame()
        self.data_status: Dict[str, Any] = {}
        self.load_and_preprocess_data()

    def load_and_preprocess_data(self) -> None:
        """Loads CSV dataset into a Pandas DataFrame and performs data cleaning and transformation."""
        # 1. Load CSV
        self.raw_df = pd.read_csv(self.csv_path)
        
        # Strip column names
        self.raw_df.columns = self.raw_df.columns.str.strip()

        df = self.raw_df.copy()

        # 2. Inspect shape & raw metadata
        raw_rows, raw_cols = df.shape
        raw_duplicates = int(df.duplicated().sum())
        raw_missing = df.isnull().sum().to_dict()

        # 3. Data Type Conversions & Cleaning
        numeric_float_cols = ['Price_INR', 'Discount_Percent', 'Final_Price_INR', 'Rating']
        numeric_int_cols = ['Reviews', 'Stock', 'Units_Sold']

        for col in numeric_float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        for col in numeric_int_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Remove duplicate records if any exist
        df = df.drop_duplicates()

        # Fill missing values for numericals with median, strings with 'Unknown'
        for col in df.columns:
            if df[col].dtype in ['float64', 'float32']:
                df[col] = df[col].fillna(df[col].median())
            elif df[col].dtype in ['int64', 'int32']:
                df[col] = df[col].fillna(0)
            elif df[col].dtype == 'object':
                df[col] = df[col].fillna('Unknown')

        # Convert / Parse Date column
        if 'Order_Date' in df.columns:
            df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
            # Extract Month in YYYY-MM format
            df['Month'] = df['Order_Date'].dt.strftime('%Y-%m')
        else:
            # Fallback if no date column
            df['Order_Date'] = pd.to_datetime('2025-01-01')
            df['Month'] = '2025-01'

        # Compute derived Revenue column
        df['Revenue'] = (df['Units_Sold'] * df['Final_Price_INR']).round(2)

        self.df = df
        clean_rows, clean_cols = self.df.shape

        self.data_status = {
            "total_records": clean_rows,
            "total_columns": clean_cols,
            "raw_records": raw_rows,
            "raw_columns": raw_cols,
            "raw_duplicates": raw_duplicates,
            "missing_values_cleaned": {k: int(v) for k, v in raw_missing.items()},
            "is_clean": True,
            "columns": list(self.df.columns),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }

    def get_dataset_overview(self) -> Dict[str, Any]:
        """Exposes shape, column names, data types, missing values, duplicates, and cleaned sample data."""
        # Convert first 10 rows for table preview
        sample_df = self.df.head(10).copy()
        if 'Order_Date' in sample_df.columns:
            sample_df['Order_Date'] = sample_df['Order_Date'].dt.strftime('%Y-%m-%d')
        
        sample_records = sample_df.to_dict(orient='records')

        return {
            "overview": self.data_status,
            "sample_records": sample_records
        }

    def filter_and_sort_products(
        self,
        min_price: float = 0.0,
        max_price: float = 1000000.0,
        category: Optional[str] = None,
        min_rating: float = 0.0,
        sort_by: str = "price",
        sort_order: str = "asc",
        search_query: str = ""
    ) -> Dict[str, Any]:
        """Filters products using Pandas boolean indexing and sorts results using sort_values."""
        df = self.df

        # Boolean Indexing Conditions
        cond = (
            (df['Final_Price_INR'] >= min_price) &
            (df['Final_Price_INR'] <= max_price) &
            (df['Rating'] >= min_rating)
        )

        if category and category.strip() and category.lower() != 'all':
            cond = cond & (df['Category'].str.lower() == category.strip().lower())

        if search_query and search_query.strip():
            q_str = search_query.strip().lower()
            search_cond = (
                df['Product_Name'].str.lower().str.contains(q_str, regex=False) |
                df['Category'].str.lower().str.contains(q_str, regex=False) |
                df['Brand'].str.lower().str.contains(q_str, regex=False) |
                df['Product_ID'].str.lower().str.contains(q_str, regex=False)
            )
            cond = cond & search_cond

        filtered_df = df[cond].copy()

        # Sorting logic via Pandas sort_values
        ascending = (sort_order.lower() == 'asc')
        if sort_by == 'price' or sort_by == 'price_asc' or sort_by == 'price_desc':
            asc = True if sort_by == 'price_asc' else (False if sort_by == 'price_desc' else ascending)
            filtered_df = filtered_df.sort_values(by='Final_Price_INR', ascending=asc)
        elif sort_by == 'rating' or sort_by == 'rating_asc' or sort_by == 'rating_desc':
            asc = False if sort_by == 'rating_desc' else (True if sort_by == 'rating_asc' else ascending)
            filtered_df = filtered_df.sort_values(by='Rating', ascending=asc)
        elif sort_by == 'orders' or sort_by == 'orders_desc':
            filtered_df = filtered_df.sort_values(by='Units_Sold', ascending=False)
        elif sort_by == 'revenue' or sort_by == 'revenue_desc':
            filtered_df = filtered_df.sort_values(by='Revenue', ascending=False)

        # Calculated Metrics
        count = len(filtered_df)
        avg_price = float(filtered_df['Final_Price_INR'].mean()) if count > 0 else 0.0
        avg_rating = float(filtered_df['Rating'].mean()) if count > 0 else 0.0
        total_revenue = float(filtered_df['Revenue'].sum()) if count > 0 else 0.0

        # Serialize records
        export_df = filtered_df.copy()
        if 'Order_Date' in export_df.columns:
            export_df['Order_Date'] = export_df['Order_Date'].dt.strftime('%Y-%m-%d')
        
        products = export_df.to_dict(orient='records')

        # Comparison Section: Top 5 by Price vs Top 5 by Rating
        price_sorted = filtered_df.sort_values(by='Final_Price_INR', ascending=False).head(5)
        rating_sorted = filtered_df.sort_values(by='Rating', ascending=False).head(5)

        for comp_df in [price_sorted, rating_sorted]:
            if 'Order_Date' in comp_df.columns:
                comp_df['Order_Date'] = comp_df['Order_Date'].dt.strftime('%Y-%m-%d')

        return {
            "total_matching": count,
            "average_price": round(avg_price, 2),
            "average_rating": round(avg_rating, 2),
            "total_revenue": round(total_revenue, 2),
            "products": products[:100],  # Return up to 100 for table display
            "comparison": {
                "top_by_price": price_sorted.to_dict(orient='records'),
                "top_by_rating": rating_sorted.to_dict(orient='records')
            }
        }

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calculates mean, median, std, min, max for Price and Rating across full dataset and by category."""
        df = self.df

        def calc_stats(series: pd.Series) -> Dict[str, float]:
            return {
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2)
            }

        overall_price = calc_stats(df['Final_Price_INR'])
        overall_rating = calc_stats(df['Rating'])

        # Groupby Category statistics
        category_stats = []
        for cat, group in df.groupby('Category'):
            p_stats = calc_stats(group['Final_Price_INR'])
            r_stats = calc_stats(group['Rating'])
            category_stats.append({
                "category": cat,
                "count": len(group),
                "price_mean": p_stats["mean"],
                "price_median": p_stats["median"],
                "price_std": p_stats["std"],
                "price_min": p_stats["min"],
                "price_max": p_stats["max"],
                "rating_mean": r_stats["mean"],
                "rating_median": r_stats["median"],
                "rating_std": r_stats["std"],
                "rating_min": r_stats["min"],
                "rating_max": r_stats["max"]
            })

        category_stats.sort(key=lambda x: x['category'])

        return {
            "overall": {
                "price": overall_price,
                "rating": overall_rating
            },
            "category_statistics": category_stats
        }

    def get_sales_analysis(self) -> Dict[str, Any]:
        """Performs GroupBy sales aggregations by Category, Month, and identifies top products."""
        df = self.df

        # 1. Revenue by Category
        cat_group = df.groupby('Category').agg(
            total_revenue=('Revenue', 'sum'),
            total_orders=('Units_Sold', 'sum'),
            avg_revenue=('Revenue', 'mean'),
            product_count=('Product_ID', 'count')
        ).reset_index()

        cat_group['total_revenue'] = cat_group['total_revenue'].round(2)
        cat_group['avg_revenue'] = cat_group['avg_revenue'].round(2)
        
        # Sort by total revenue descending
        cat_sorted = cat_group.sort_values(by='total_revenue', ascending=False)
        top_3_categories = cat_sorted.head(3).to_dict(orient='records')
        all_categories_sales = cat_sorted.to_dict(orient='records')

        # 2. Sales by Month
        monthly_group = df.groupby('Month').agg(
            total_revenue=('Revenue', 'sum'),
            total_orders=('Units_Sold', 'sum'),
            avg_order_revenue=('Revenue', 'mean')
        ).reset_index().sort_values(by='Month')

        monthly_group['total_revenue'] = monthly_group['total_revenue'].round(2)
        monthly_group['avg_order_revenue'] = monthly_group['avg_order_revenue'].round(2)
        monthly_sales = monthly_group.to_dict(orient='records')

        # 3. Top 5 Products by Number of Orders (Units_Sold)
        top_products_df = df.sort_values(by='Units_Sold', ascending=False).head(5)[
            ['Product_ID', 'Product_Name', 'Category', 'Brand', 'Units_Sold', 'Revenue', 'Rating', 'Final_Price_INR']
        ]
        top_products = top_products_df.to_dict(orient='records')

        return {
            "top_3_categories": top_3_categories,
            "category_sales": all_categories_sales,
            "monthly_sales": monthly_sales,
            "top_5_products": top_products
        }

    def generate_visualizations(self) -> Dict[str, Any]:
        """Generates 3 Matplotlib/Seaborn charts encoded as base64 PNG data URLs with dynamic business interpretations."""
        df = self.df
        charts = {}

        # Set Seaborn theme
        sns.set_theme(style="whitegrid", palette="deep")
        plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 10})

        # --- Chart 1: Bar Chart — Total Revenue by Category ---
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        cat_sales = df.groupby('Category')['Revenue'].sum().reset_index().sort_values(by='Revenue', ascending=False)
        
        bars = sns.barplot(data=cat_sales, x='Category', y='Revenue', hue='Category', legend=False, palette="viridis", ax=ax)
        ax.set_title("Total Revenue by Category (₹)", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Category", fontsize=11, fontweight='semibold')
        ax.set_ylabel("Total Revenue (INR)", fontsize=11, fontweight='semibold')
        ax.yaxis.set_major_formatter('₹{x:,.0f}')
        plt.xticks(rotation=25, ha='right')

        # Annotate bar tops
        for p in bars.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'₹{height/1e6:.1f}M', (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=9, xytext=(0, 3), textcoords='offset points')

        plt.tight_layout()
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='png', bbox_inches='tight')
        buf1.seek(0)
        chart1_b64 = base64.b64encode(buf1.getvalue()).decode('utf-8')
        plt.close(fig)

        top_cat = cat_sales.iloc[0]['Category']
        top_cat_rev = cat_sales.iloc[0]['Revenue']
        chart1_interp = f"The '{top_cat}' category generates the highest revenue at ₹{top_cat_rev:,.2f}, indicating strong consumer demand and highlighting it as a prime candidate for inventory expansion and targeted marketing."

        # --- Chart 2: Histogram — Distribution of Product Prices ---
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        sns.histplot(df['Final_Price_INR'], bins=20, kde=True, color="#4f46e5", ax=ax)
        ax.set_title("Distribution of Final Product Prices (₹)", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Final Price (INR)", fontsize=11, fontweight='semibold')
        ax.set_ylabel("Product Frequency Count", fontsize=11, fontweight='semibold')
        ax.xaxis.set_major_formatter('₹{x:,.0f}')

        median_price = df['Final_Price_INR'].median()
        mean_price = df['Final_Price_INR'].mean()
        ax.axvline(median_price, color='#d97706', linestyle='--', linewidth=2, label=f'Median: ₹{median_price:,.0f}')
        ax.axvline(mean_price, color='#059669', linestyle='-', linewidth=2, label=f'Mean: ₹{mean_price:,.0f}')
        ax.legend()

        plt.tight_layout()
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='png', bbox_inches='tight')
        buf2.seek(0)
        chart2_b64 = base64.b64encode(buf2.getvalue()).decode('utf-8')
        plt.close(fig)

        skew_desc = "right-skewed toward budget products" if mean_price > median_price else "balanced across price tiers"
        chart2_interp = f"Product prices range from ₹{df['Final_Price_INR'].min():,.2f} to ₹{df['Final_Price_INR'].max():,.2f} with a median of ₹{median_price:,.2f}. The price distribution is {skew_desc}, suggesting inventory covers both mass-market and premium segments."

        # --- Chart 3: Scatter Plot — Price vs Rating ---
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        sns.scatterplot(data=df, x='Final_Price_INR', y='Rating', hue='Category', style='Category', alpha=0.85, s=60, palette="tab10", ax=ax)
        ax.set_title("Product Price vs Customer Rating", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Final Price (INR)", fontsize=11, fontweight='semibold')
        ax.set_ylabel("Rating (out of 5.0)", fontsize=11, fontweight='semibold')
        ax.xaxis.set_major_formatter('₹{x:,.0f}')
        ax.set_ylim(0.5, 5.5)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

        plt.tight_layout()
        buf3 = io.BytesIO()
        plt.savefig(buf3, format='png', bbox_inches='tight')
        buf3.seek(0)
        chart3_b64 = base64.b64encode(buf3.getvalue()).decode('utf-8')
        corr = float(df['Final_Price_INR'].corr(df['Rating']))
        corr_desc = "weak positive" if 0 < corr <= 0.3 else ("moderate positive" if corr > 0.3 else "minimal")
        chart3_interp = f"The scatter plot reveals a {corr_desc} correlation (r = {corr:.2f}) between product price and customer rating, demonstrating that higher pricing does not strictly dictate customer satisfaction levels."

        # --- Chart 4: Line Chart — Monthly Revenue Trend ---
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        monthly_sales = df.groupby('Month')['Revenue'].sum().reset_index().sort_values(by='Month')
        sns.lineplot(data=monthly_sales, x='Month', y='Revenue', marker='o', linewidth=2.5, color='#0ea5e9', ax=ax)
        ax.set_title("Monthly Sales Revenue Trend (₹)", fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel("Month", fontsize=11, fontweight='semibold')
        ax.set_ylabel("Total Revenue (INR)", fontsize=11, fontweight='semibold')
        ax.yaxis.set_major_formatter('₹{x:,.0f}')
        plt.xticks(rotation=30, ha='right')

        plt.tight_layout()
        buf4 = io.BytesIO()
        plt.savefig(buf4, format='png', bbox_inches='tight')
        buf4.seek(0)
        chart4_b64 = base64.b64encode(buf4.getvalue()).decode('utf-8')
        plt.close(fig)

        peak_m = monthly_sales.iloc[monthly_sales['Revenue'].argmax()]['Month']
        peak_m_rev = monthly_sales['Revenue'].max()
        chart4_interp = f"Monthly sales peaked in {peak_m} reaching ₹{peak_m_rev:,.2f}, demonstrating strong seasonal momentum across category lines."

        return {
            "chart1_category_revenue": {
                "image_b64": f"data:image/png;base64,{chart1_b64}",
                "title": "Total Revenue by Category",
                "interpretation": chart1_interp
            },
            "chart2_price_distribution": {
                "image_b64": f"data:image/png;base64,{chart2_b64}",
                "title": "Distribution of Product Prices",
                "interpretation": chart2_interp
            },
            "chart3_price_vs_rating": {
                "image_b64": f"data:image/png;base64,{chart3_b64}",
                "title": "Price vs Rating Scatter Plot",
                "interpretation": chart3_interp
            },
            "chart4_monthly_sales": {
                "image_b64": f"data:image/png;base64,{chart4_b64}",
                "title": "Monthly Revenue Sales Trend",
                "interpretation": chart4_interp
            }
        }

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Calculates key landing dashboard KPIs and high-level summary cards."""
        df = self.df
        total_products = len(df)
        total_categories = int(df['Category'].nunique())
        avg_price = float(df['Final_Price_INR'].mean())
        avg_rating = float(df['Rating'].mean())
        total_orders = int(df['Units_Sold'].sum())
        total_revenue = float(df['Revenue'].sum())

        cat_rev = df.groupby('Category')['Revenue'].sum()
        top_rev_cat = str(cat_rev.idxmax())
        top_rev_val = float(cat_rev.max())

        top_prod = df.sort_values(by='Units_Sold', ascending=False).iloc[0]

        cat_rating = df.groupby('Category')['Rating'].mean()
        top_rated_cat = str(cat_rating.idxmax())
        top_rating_val = float(cat_rating.max())

        return {
            "kpis": {
                "total_products": total_products,
                "total_categories": total_categories,
                "average_price": round(avg_price, 2),
                "average_rating": round(avg_rating, 2),
                "total_orders": total_orders,
                "total_revenue": round(total_revenue, 2)
            },
            "summary_highlights": {
                "highest_revenue_category": {"category": top_rev_cat, "revenue": round(top_rev_val, 2)},
                "most_ordered_product": {
                    "product_name": str(top_prod['Product_Name']),
                    "product_id": str(top_prod['Product_ID']),
                    "orders": int(top_prod['Units_Sold']),
                    "category": str(top_prod['Category'])
                },
                "highest_rated_category": {"category": top_rated_cat, "rating": round(top_rating_val, 2)},
                "top_performing_category": {"category": top_rev_cat, "revenue": round(top_rev_val, 2)}
            }
        }

    def get_business_insights(self) -> List[Dict[str, str]]:
        """Generates automated data-driven business insights calculated directly from Pandas analytics."""
        df = self.df
        insights = []

        # 1. Top & Bottom Revenue Category
        cat_rev = df.groupby('Category')['Revenue'].sum()
        top_cat = cat_rev.idxmax()
        top_rev = cat_rev.max()
        bottom_cat = cat_rev.idxmin()
        bottom_rev = cat_rev.min()

        insights.append({
            "topic": "Revenue Leader",
            "metric": f"{top_cat} (₹{top_rev:,.2f})",
            "detail": f"The top performing category is {top_cat}, contributing ₹{top_rev:,.2f} in total sales. Focus promotional campaigns here."
        })

        insights.append({
            "topic": "Underperforming Category",
            "metric": f"{bottom_cat} (₹{bottom_rev:,.2f})",
            "detail": f"{bottom_cat} recorded the lowest total revenue at ₹{bottom_rev:,.2f}. Consider product bundling or strategic price cuts to boost volume."
        })

        # 2. Most Ordered Product
        top_prod = df.sort_values(by='Units_Sold', ascending=False).iloc[0]
        insights.append({
            "topic": "Best-Selling Product",
            "metric": f"{top_prod['Product_Name']} ({top_prod['Units_Sold']:,} orders)",
            "detail": f"Product ID {top_prod['Product_ID']} ({top_prod['Product_Name']}) in {top_prod['Category']} generated {top_prod['Units_Sold']:,} orders and ₹{top_prod['Revenue']:,.2f} revenue."
        })

        # 3. Highest Rated Category
        cat_rating = df.groupby('Category')['Rating'].mean()
        top_rated_cat = cat_rating.idxmax()
        top_cat_score = cat_rating.max()
        insights.append({
            "topic": "Highest Rated Category",
            "metric": f"{top_rated_cat} ({top_cat_score:.2f} ★)",
            "detail": f"{top_rated_cat} products achieve the highest average customer satisfaction score of {top_cat_score:.2f} out of 5.0."
        })

        # 4. Average Price & Spread
        avg_p = df['Final_Price_INR'].mean()
        med_p = df['Final_Price_INR'].median()
        insights.append({
            "topic": "Pricing Benchmark",
            "metric": f"Mean ₹{avg_p:,.2f} | Median ₹{med_p:,.2f}",
            "detail": f"Catalog average price is ₹{avg_p:,.2f} with a median of ₹{med_p:,.2f}, displaying healthy product tiering across price points."
        })

        # 5. Peak Sales Month
        if 'Month' in df.columns:
            monthly_rev = df.groupby('Month')['Revenue'].sum()
            peak_month = monthly_rev.idxmax()
            peak_val = monthly_rev.max()
            insights.append({
                "topic": "Peak Monthly Revenue",
                "metric": f"{peak_month} (₹{peak_val:,.2f})",
                "detail": f"Monthly sales peaked in {peak_month} reaching ₹{peak_val:,.2f} across all categories."
            })

        # 6. Price vs Rating Correlation
        corr = df['Final_Price_INR'].corr(df['Rating'])
        insights.append({
            "topic": "Price & Satisfaction Correlation",
            "metric": f"r = {corr:.2f}",
            "detail": f"The correlation between price and rating is {corr:.2f}, demonstrating that high ratings are earned across both budget and luxury items."
        })

        return insights
