import os
import unittest
from src.analytics import EcommerceAnalytics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "products.csv")


class TestEcommerceAnalytics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.analytics = EcommerceAnalytics(CSV_PATH)

    def test_01_dataset_loading_and_preprocessing(self):
        status = self.analytics.data_status
        self.assertEqual(status["total_records"], 500)
        self.assertGreaterEqual(status["total_columns"], 13)
        self.assertTrue(status["is_clean"])
        self.assertIn("Revenue", status["columns"])
        self.assertIn("Month", status["columns"])

    def test_02_dataset_overview_api(self):
        overview = self.analytics.get_dataset_overview()
        self.assertIn("overview", overview)
        self.assertIn("sample_records", overview)
        self.assertEqual(len(overview["sample_records"]), 10)

    def test_03_boolean_filtering_and_sorting(self):
        result = self.analytics.filter_and_sort_products(
            min_price=1000.0,
            max_price=10000.0,
            category="Books",
            min_rating=3.0,
            sort_by="price",
            sort_order="asc"
        )
        self.assertIn("total_matching", result)
        self.assertIn("products", result)
        self.assertIn("comparison", result)

        for prod in result["products"]:
            self.assertGreaterEqual(prod["Final_Price_INR"], 1000.0)
            self.assertLessEqual(prod["Final_Price_INR"], 10000.0)
            self.assertEqual(prod["Category"].lower(), "books")
            self.assertGreaterEqual(prod["Rating"], 3.0)

        # Check sorting low to high
        if len(result["products"]) > 1:
            prices = [p["Final_Price_INR"] for p in result["products"]]
            self.assertEqual(prices, sorted(prices))

    def test_04_summary_statistics(self):
        stats = self.analytics.get_summary_statistics()
        self.assertIn("overall", stats)
        self.assertIn("category_statistics", stats)

        overall_p = stats["overall"]["price"]
        self.assertGreater(overall_p["mean"], 0)
        self.assertGreater(overall_p["max"], overall_p["min"])

        cat_stats = stats["category_statistics"]
        self.assertGreater(len(cat_stats), 0)
        for cat in cat_stats:
            self.assertIn("price_mean", cat)
            self.assertIn("rating_mean", cat)

    def test_05_sales_analysis_groupby(self):
        sales = self.analytics.get_sales_analysis()
        self.assertIn("top_3_categories", sales)
        self.assertEqual(len(sales["top_3_categories"]), 3)
        self.assertIn("monthly_sales", sales)
        self.assertGreater(len(sales["monthly_sales"]), 0)
        self.assertIn("top_5_products", sales)
        self.assertEqual(len(sales["top_5_products"]), 5)

        # Verify top 5 products sorted by Units_Sold descending
        units = [p["Units_Sold"] for p in sales["top_5_products"]]
        self.assertEqual(units, sorted(units, reverse=True))

    def test_06_visualizations_generation(self):
        viz = self.analytics.generate_visualizations()
        self.assertIn("chart1_category_revenue", viz)
        self.assertIn("chart2_price_distribution", viz)
        self.assertIn("chart3_price_vs_rating", viz)

        for key, chart in viz.items():
            self.assertTrue(chart["image_b64"].startswith("data:image/png;base64,"))
            self.assertGreater(len(chart["interpretation"]), 10)

    def test_07_business_insights(self):
        insights = self.analytics.get_business_insights()
        self.assertGreaterEqual(len(insights), 5)
        for item in insights:
            self.assertIn("topic", item)
            self.assertIn("metric", item)
            self.assertIn("detail", item)

    def test_08_dashboard_summary(self):
        db_summary = self.analytics.get_dashboard_summary()
        self.assertIn("kpis", db_summary)
        self.assertIn("summary_highlights", db_summary)
        kpis = db_summary["kpis"]
        self.assertEqual(kpis["total_products"], 500)
        self.assertGreater(kpis["total_revenue"], 0)


if __name__ == "__main__":
    unittest.main()

