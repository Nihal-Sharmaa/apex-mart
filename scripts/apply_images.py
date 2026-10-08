"""
Definitive image mapping — verified by viewing every image in chat.

File → Product mapping (all 48 confirmed visually):

Books (1-8):
  1 = AI Fundamentals       (navy cover, brain neural network)
  2 = Computer Networks     (black cover, world network diagram)
  3 = Data Structures       (dark blue/grey, tree diagrams)
  4 = Database Systems      (blue/teal, DB network visual)
  5 = Machine Learning      (blue/white, neural net textbook)
  6 = Python Programming    (dark, Python logo)
  7 = Statistics            (beige/navy, bell curve)
  8 = Web Development       (dark blue, JS/CSS icons)

Sports (9-16):
  9  = Badminton Racket     (Yonex Astrox 100)
  10 = Cricket Bat          (Kookaburra Kahuna Pro standing)
  11 = Football             (Adidas Al Rihla FIFA ball)
  12 = Gym Gloves           (FitnessPro leather half-finger)
  13 = Running Shoes        (Velocity blue/black pair)
  14 = Skipping Rope        (RapidJump Pro Series coiled)
  15 = Water Bottle Sports  (Hydrolyte black vacuum insulated)
  16 = Yoga Mat             (Aurora Active teal rolled)

Electronics (17-24):
  17 = Bluetooth Speaker    (Acoustic Aura with leather handle)
  18 = Laptop Stand         (aluminium silver stand)
  19 = Power Bank           (grey PD 3.0 with LED display)
  20 = Smartphone           (Samsung-style black phone)
  21 = Smartwatch           (Apple Watch style health metrics)
  22 = USB Cable            (braided Type-C coiled)
  23 = Webcam               (NexusCam Ultra HD)
  24 = Wireless Headphones  (over-ear dark grey)

Fashion (25-32):
  25 = Backpack             (grey canvas leather backpack)
  26 = Hoodie               (slate blue folded)
  27 = Jacket               (Axsl & Co navy field jacket)
  28 = Jeans                (dark denim folded)
  29 = Sneakers             (Runner white/navy)
  30 = Sunglasses           (Moderne black frame gold detail)
  31 = T-Shirt              (Aether grey folded)
  32 = Wrist Watch          (Swiss automatic blue dial brown strap)

Home & Kitchen (33-40):
  33 = Air Fryer            (Aerocook Pro with fries)
  34 = Coffee Maker         (stainless drip machine digital display)
  35 = Dinner Set           (white porcelain gold rim full set)
  36 = Electric Kettle      (Avantus stainless steel)
  37 = Mixer Grinder        (KitchenPro Elite 750W with jars)
  38 = Storage Box          (clear plastic bins set)
  39 = Table Lamp           (black stem gold base linen shade)
  40 = Water Bottle Home    (HYDRO gunmetal steel)

Beauty (41-48):
  41 = Body Lotion          (No.41 pump bottle)
  42 = Face Wash            (Daily Facial Cleanser + Gentle Face Wash duo)
  43 = Hair Serum           (amber dropper bottle)
  44 = Lip Balm             (white cylinder gold band)
  45 = Moisturizer          (frosted glass jar white lid gold ring)
  46 = Perfume              (amber crystal bottle gold cap)
  47 = Shampoo              (argan frosted bottle silver cap)
  48 = Sunscreen            (Premium Sunscreen SPF50+ duo)
"""

import shutil, os, pandas as pd

SRC      = r"c:\Users\nihsh\Downloads\AU\YEAR 2\DOE\DOE PROJECT\Apex-Mart\product_images"
ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST      = os.path.join(ROOT, "static", "images")
CSV_PATH = os.path.join(ROOT, "products.csv")

os.makedirs(DST, exist_ok=True)

# (source_filename, dest_filename, product_name, category_hint_or_None)
MAPPING = [
    # ── Books ──────────────────────────────────────────────────────────────
    ("1._Create_a_premium_e-commerce_20261001114632.jpg",  "ai_fundamentals.jpg",     "AI Fundamentals",       None),
    ("2._Create_a_premium_e-commerce_20261001114632.jpg",  "computer_networks.jpg",   "Computer Networks",     None),
    ("3._Create_a_premium_e-commerce_20261001114633.jpg",  "data_structures.jpg",     "Data Structures",       None),
    ("4._Create_a_premium_e-commerce_20261001114636.jpg",  "database_systems.jpg",    "Database Systems",      None),
    ("5._Create_a_premium_e-commerce_20261001114638.jpg",  "machine_learning.jpg",    "Machine Learning",      None),
    ("6._Create_a_premium_e-commerce_20261001114639.jpg",  "python_programming.jpg",  "Python Programming",    None),
    ("7._Create_a_premium_e-commerce_20261001114640.jpg",  "statistics.jpg",          "Statistics",            None),
    ("8._Create_a_premium_e-commerce_20261001114642.jpg",  "web_development.jpg",     "Web Development",       None),

    # ── Sports ─────────────────────────────────────────────────────────────
    ("9._Create_a_premium_e-commerce_20261001114643.jpg",  "badminton_racket.jpg",    "Badminton Racket",      None),
    ("10._Create_a_premium_e-commerce_20261001114645.jpg", "cricket_bat.jpg",         "Cricket Bat",           None),
    ("11._Create_a_premium_e-commerce_20261001114646.jpg", "football.jpg",            "Football",              None),
    ("12._Create_a_premium_e-commerce_20261001114648.jpg", "gym_gloves.jpg",          "Gym Gloves",            None),
    ("13._Create_a_premium_e-commerce_20261001114649.jpg", "running_shoes.jpg",       "Running Shoes",         None),
    ("14._Create_a_premium_e-commerce_20261001114651.jpg", "skipping_rope.jpg",       "Skipping Rope",         None),
    ("15._Create_a_premium_e-commerce_20261001114652.jpg", "water_bottle_sports.jpg", "Water Bottle",          "Sports"),
    ("16._Create_a_premium_e-commerce_20261001114654.jpg", "yoga_mat.jpg",            "Yoga Mat",              None),

    # ── Electronics ────────────────────────────────────────────────────────
    ("17._Create_a_premium_e-commerce_20261001114655.jpg", "bluetooth_speaker.jpg",   "Bluetooth Speaker",     None),
    ("18._Create_a_premium_e-commerce_20261001114656.jpg", "laptop_stand.jpg",        "Laptop Stand",          None),
    ("19._Create_a_premium_e-commerce_20261001114658.jpg", "power_bank.jpg",          "Power Bank",            None),
    ("20._Create_a_premium_e-commerce_20261001114700.jpg", "smartphone.jpg",          "Smartphone",            None),
    ("21._Create_a_premium_e-commerce_20261001114701.jpg", "smartwatch.jpg",          "Smartwatch",            None),
    ("22._Create_a_premium_e-commerce_20261001114702.jpg", "usb_cable.jpg",           "USB Cable",             None),
    ("23._Create_a_premium_e-commerce_20261001114706.jpg", "webcam.jpg",              "Webcam",                None),
    ("24._Create_a_premium_e-commerce_20261001114706.jpg", "wireless_headphones.jpg", "Wireless Headphones",   None),

    # ── Fashion ────────────────────────────────────────────────────────────
    ("25._Create_a_premium_e-commerce_20261001114706.jpg", "backpack.jpg",            "Backpack",              None),
    ("26._Create_a_premium_e-commerce_20261001114708.jpg", "hoodie.jpg",              "Hoodie",                None),
    ("27._Create_a_premium_e-commerce_20261001114709.jpg", "jacket.jpg",              "Jacket",                None),
    ("28._Create_a_premium_e-commerce_20261001114712.jpg", "jeans.jpg",               "Jeans",                 None),
    ("29._Create_a_premium_e-commerce_20261001114716.jpg", "sneakers.jpg",            "Sneakers",              None),
    ("30._Create_a_premium_e-commerce_20261001114716.jpg", "sunglasses.jpg",          "Sunglasses",            None),
    ("31._Create_a_premium_e-commerce_20261001114718.jpg", "tshirt.jpg",              "T-Shirt",               None),
    ("32._Create_a_premium_e-commerce_20261001114718.jpg", "wrist_watch.jpg",         "Wrist Watch",           None),

    # ── Home & Kitchen ─────────────────────────────────────────────────────
    ("33._Create_a_premium_e-commerce_20261001114718.jpg", "air_fryer.jpg",           "Air Fryer",             None),
    ("34._Create_a_premium_e-commerce_20261001114720.jpg", "coffee_maker.jpg",        "Coffee Maker",          None),
    ("35._Create_a_premium_e-commerce_20261001114723.jpg", "dinner_set.jpg",          "Dinner Set",            None),
    ("36._Create_a_premium_e-commerce_20261001114724.jpg", "electric_kettle.jpg",     "Electric Kettle",       None),
    ("37._Create_a_premium_e-commerce_20261001114724.jpg", "mixer_grinder.jpg",       "Mixer Grinder",         None),
    ("38._Create_a_premium_e-commerce_20261001114726.jpg", "storage_box.jpg",         "Storage Box",           None),
    ("39._Create_a_premium_e-commerce_20261001114728.jpg", "table_lamp.jpg",          "Table Lamp",            None),
    ("40._Create_a_premium_e-commerce_20261001114730.jpg", "water_bottle_home.jpg",   "Water Bottle",          "Home & Kitchen"),

    # ── Beauty ─────────────────────────────────────────────────────────────
    ("41._Create_a_premium_e-commerce_20261001114731.jpg", "body_lotion.jpg",         "Body Lotion",           None),
    ("42._Create_a_premium_e-commerce_20261001114736.jpg", "face_wash.jpg",           "Face Wash",             None),
    ("43._Create_a_premium_e-commerce_20261001114736.jpg", "hair_serum.jpg",          "Hair Serum",            None),
    ("44._Create_a_premium_e-commerce_20261001114736.jpg", "lip_balm.jpg",            "Lip Balm",              None),
    ("45._Create_a_premium_e-commerce_20261001114741.jpg", "moisturizer.jpg",         "Moisturizer",           None),
    ("46._Create_a_premium_e-commerce_20261001114738.jpg", "perfume.jpg",             "Perfume",               None),
    ("47._Create_a_premium_e-commerce_20261001114744.jpg", "shampoo.jpg",             "Shampoo",               None),
    ("48._Create_a_premium_e-commerce_20261001114742.jpg", "sunscreen.jpg",           "Sunscreen",             None),
]

# ── Step 1: Copy all files ──────────────────────────────────────────────────
print("Copying images to static/images/...")
name_cat_to_url = {}
ok = 0
missing = 0

for src_file, dst_file, product_name, cat_hint in MAPPING:
    src_path = os.path.join(SRC, src_file)
    dst_path = os.path.join(DST, dst_file)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        url = f"/images/{dst_file}"
        name_cat_to_url[(product_name, cat_hint)] = url
        name_cat_to_url[(product_name, None)]     = url
        print(f"  ✓ {product_name}{' [' + cat_hint + ']' if cat_hint else '':<20} → {dst_file}")
        ok += 1
    else:
        print(f"  ✗ MISSING: {src_file}")
        missing += 1

print(f"\nCopied: {ok}  |  Missing: {missing}")

# ── Step 2: Update products.csv ─────────────────────────────────────────────
print("\nUpdating products.csv ...")
df = pd.read_csv(CSV_PATH)

def get_url(row):
    name = row["Product_Name"]
    cat  = row["Category"]
    # Category-specific lookup first (handles Water Bottle in Sports vs Home & Kitchen)
    if (name, cat) in name_cat_to_url:
        return name_cat_to_url[(name, cat)]
    if (name, None) in name_cat_to_url:
        return name_cat_to_url[(name, None)]
    return row["Image_URL"]   # keep existing if not in mapping

df["Image_URL"] = df.apply(get_url, axis=1)
df.to_csv(CSV_PATH, index=False)

# ── Step 3: Report ───────────────────────────────────────────────────────────
local    = df["Image_URL"].str.startswith("/images/").sum()
external = df["Image_URL"].str.startswith("https://").sum()
print(f"\nResults:")
print(f"  Local  /images/ : {local} / {len(df)} rows")
print(f"  External URLs   : {external} rows")

if external > 0:
    ext_names = df[df["Image_URL"].str.startswith("https://")]["Product_Name"].unique()
    print(f"  Still using external: {sorted(ext_names)}")

print("\nPer-category breakdown:")
for cat in sorted(df["Category"].unique()):
    sub = df[df["Category"] == cat]
    loc = sub["Image_URL"].str.startswith("/images/").sum()
    print(f"  {cat:<18}: {loc}/{len(sub)} local")

print("\nSample — first unique product per category:")
for cat in sorted(df["Category"].unique()):
    row = df[df["Category"] == cat].iloc[0]
    print(f"  {cat:<18} | {row['Product_Name']:<22} → {row['Image_URL']}")
