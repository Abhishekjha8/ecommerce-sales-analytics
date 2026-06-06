"""
================================================================
  E-Commerce Sales Analytics
  Script 2: Load Clean Data into MySQL (Star Schema)
  Author : Abhishek Jha
  Tools  : Python, mysql-connector-python, pandas
================================================================
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error

print("=" * 60)
print("  E-Commerce Sales Analytics — MySQL Loader")
print("=" * 60)

# ─────────────────────────────────────────────
# CONFIG — update password if different
# ─────────────────────────────────────────────
DB_CONFIG = {
    'host'    : 'localhost',
    'user'    : 'root',
    'password': 'root@7488',
    'database': 'ecommerce_db'
}

# ─────────────────────────────────────────────
# STEP 1: LOAD CLEAN DATA
# ─────────────────────────────────────────────
print("\n[STEP 1] Loading clean dataset...")
df = pd.read_csv('data/superstore_clean.csv', encoding='latin-1')
print(f"  Rows loaded: {len(df):,}")

# ─────────────────────────────────────────────
# STEP 2: CONNECT TO MYSQL
# ─────────────────────────────────────────────
print("\n[STEP 2] Connecting to MySQL...")
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("  Connected successfully!")
except Error as e:
    print(f"  ERROR: {e}")
    exit()

# ─────────────────────────────────────────────
# STEP 3: CREATE TABLES
# ─────────────────────────────────────────────
print("\n[STEP 3] Creating tables...")

# Drop existing tables in correct order
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
for t in ['fact_orders','dim_customer','dim_product','dim_region','dim_segment','dim_ship_mode']:
    cursor.execute(f"DROP TABLE IF EXISTS {t}")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# dim_region
cursor.execute("""
CREATE TABLE dim_region (
    region_id   INT AUTO_INCREMENT PRIMARY KEY,
    region      VARCHAR(50) NOT NULL,
    country     VARCHAR(50) DEFAULT 'United States'
)
""")

# dim_segment
cursor.execute("""
CREATE TABLE dim_segment (
    segment_id  INT AUTO_INCREMENT PRIMARY KEY,
    segment     VARCHAR(50) NOT NULL
)
""")

# dim_ship_mode
cursor.execute("""
CREATE TABLE dim_ship_mode (
    ship_mode_id INT AUTO_INCREMENT PRIMARY KEY,
    ship_mode    VARCHAR(50) NOT NULL
)
""")

# dim_customer
cursor.execute("""
CREATE TABLE dim_customer (
    customer_id     VARCHAR(20) PRIMARY KEY,
    customer_name   VARCHAR(100),
    segment_id      INT,
    city            VARCHAR(100),
    state           VARCHAR(100),
    postal_code     VARCHAR(20),
    region_id       INT,
    FOREIGN KEY (segment_id) REFERENCES dim_segment(segment_id),
    FOREIGN KEY (region_id)  REFERENCES dim_region(region_id)
)
""")

# dim_product
cursor.execute("""
CREATE TABLE dim_product (
    product_id      VARCHAR(20) PRIMARY KEY,
    product_name    VARCHAR(255),
    category        VARCHAR(50),
    sub_category    VARCHAR(50)
)
""")

# fact_orders
cursor.execute("""
CREATE TABLE fact_orders (
    row_id          INT PRIMARY KEY,
    order_id        VARCHAR(20),
    order_date      DATE,
    ship_date       DATE,
    ship_mode_id    INT,
    customer_id     VARCHAR(20),
    product_id      VARCHAR(20),
    sales           DECIMAL(10,2),
    quantity        INT,
    discount        DECIMAL(5,2),
    profit          DECIMAL(10,2),
    profit_margin   DECIMAL(10,2),
    shipping_days   INT,
    order_year      INT,
    order_month     INT,
    order_month_name VARCHAR(10),
    order_quarter   VARCHAR(5),
    order_day       VARCHAR(15),
    discount_band   VARCHAR(20),
    is_loss         TINYINT(1),
    FOREIGN KEY (ship_mode_id)  REFERENCES dim_ship_mode(ship_mode_id),
    FOREIGN KEY (customer_id)   REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id)    REFERENCES dim_product(product_id)
)
""")

conn.commit()
print("  All tables created successfully!")

# ─────────────────────────────────────────────
# STEP 4: LOAD DIMENSION TABLES
# ─────────────────────────────────────────────
print("\n[STEP 4] Loading dimension tables...")

# dim_region
regions = df['Region'].unique()
region_map = {}
for r in regions:
    cursor.execute("INSERT INTO dim_region (region) VALUES (%s)", (r,))
    region_map[r] = cursor.lastrowid
conn.commit()
print(f"  dim_region: {len(regions)} rows")

# dim_segment
segments = df['Segment'].unique()
segment_map = {}
for s in segments:
    cursor.execute("INSERT INTO dim_segment (segment) VALUES (%s)", (s,))
    segment_map[s] = cursor.lastrowid
conn.commit()
print(f"  dim_segment: {len(segments)} rows")

# dim_ship_mode
ship_modes = df['Ship_Mode'].unique()
ship_map = {}
for s in ship_modes:
    cursor.execute("INSERT INTO dim_ship_mode (ship_mode) VALUES (%s)", (s,))
    ship_map[s] = cursor.lastrowid
conn.commit()
print(f"  dim_ship_mode: {len(ship_modes)} rows")

# dim_customer
customers = df[['Customer_ID','Customer_Name','Segment','City','State','Postal_Code','Region']].drop_duplicates('Customer_ID')
for _, row in customers.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO dim_customer
        (customer_id, customer_name, segment_id, city, state, postal_code, region_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        row['Customer_ID'], row['Customer_Name'],
        segment_map[row['Segment']],
        row['City'], row['State'], str(row['Postal_Code']),
        region_map[row['Region']]
    ))
conn.commit()
print(f"  dim_customer: {len(customers)} rows")

# dim_product
products = df[['Product_ID','Product_Name','Category','Sub_Category']].drop_duplicates('Product_ID')
for _, row in products.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO dim_product
        (product_id, product_name, category, sub_category)
        VALUES (%s,%s,%s,%s)
    """, (row['Product_ID'], row['Product_Name'], row['Category'], row['Sub_Category']))
conn.commit()
print(f"  dim_product: {len(products)} rows")

# ─────────────────────────────────────────────
# STEP 5: LOAD FACT TABLE
# ─────────────────────────────────────────────
print("\n[STEP 5] Loading fact_orders...")
loaded = 0
errors = 0

for _, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT IGNORE INTO fact_orders (
                row_id, order_id, order_date, ship_date,
                ship_mode_id, customer_id, product_id,
                sales, quantity, discount, profit,
                profit_margin, shipping_days,
                order_year, order_month, order_month_name,
                order_quarter, order_day, discount_band, is_loss
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            int(row['Row_ID']), row['Order_ID'],
            row['Order_Date'], row['Ship_Date'],
            ship_map[row['Ship_Mode']],
            row['Customer_ID'], row['Product_ID'],
            float(row['Sales']), int(row['Quantity']),
            float(row['Discount']), float(row['Profit']),
            float(row['Profit_Margin']), int(row['Shipping_Days']),
            int(row['Order_Year']), int(row['Order_Month']),
            row['Order_Month_Name'], row['Order_Quarter'],
            row['Order_Day'], str(row['Discount_Band']),
            int(row['Is_Loss'])
        ))
        loaded += 1
    except Error as e:
        errors += 1

conn.commit()
print(f"  fact_orders: {loaded:,} rows loaded, {errors} errors")

# ─────────────────────────────────────────────
# STEP 6: VERIFY
# ─────────────────────────────────────────────
print("\n[STEP 6] Verifying data...")
tables = ['dim_region','dim_segment','dim_ship_mode','dim_customer','dim_product','fact_orders']
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"  {t}: {count:,} rows")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("  MYSQL LOAD COMPLETE")
print("  Database: ecommerce_db")
print("  Tables  : 6 (1 fact + 5 dimensions)")
print(f"  Total rows in fact_orders: {loaded:,}")
print("=" * 60)
