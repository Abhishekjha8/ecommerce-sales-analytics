"""
================================================================
  E-Commerce Sales Analytics
  Script 1: Data Cleaning & Exploratory Data Analysis
  Author : Abhishek Jha
  Tools  : Python, pandas, numpy
================================================================
"""

import pandas as pd
import numpy as np
import os

print("=" * 60)
print("  E-Commerce Sales Analytics — Data Cleaning & EDA")
print("=" * 60)

# ─────────────────────────────────────────────
# STEP 1: LOAD DATA
# ─────────────────────────────────────────────
print("\n[STEP 1] Loading dataset...")

# Try both possible filenames
possible_files = [
    "data/Sample - Superstore.csv",
    "data/superstore_raw.csv",
    "data/Sample-Superstore.csv"
]

df = None
for f in possible_files:
    if os.path.exists(f):
        df = pd.read_csv(f, encoding='latin-1')
        print(f"  Loaded: {f}")
        break

if df is None:
    print("  ERROR: Could not find dataset file in data/ folder!")
    exit()

print(f"  Rows: {len(df):,}  |  Columns: {len(df.columns)}")
print(f"  Columns: {list(df.columns)}")

# ─────────────────────────────────────────────
# STEP 2: DATA CLEANING
# ─────────────────────────────────────────────
print("\n[STEP 2] Cleaning data...")

# 2a. Check nulls
null_counts = df.isnull().sum()
print(f"\n  Null values:")
if null_counts.sum() == 0:
    print("    No nulls found — clean dataset!")
else:
    print(null_counts[null_counts > 0])

# 2b. Check duplicates
dupes = df.duplicated().sum()
print(f"\n  Duplicate rows: {dupes}")
if dupes > 0:
    df = df.drop_duplicates()
    print(f"  Removed {dupes} duplicates")

# 2c. Rename columns — remove spaces for MySQL compatibility
df.columns = [c.strip().replace(" ", "_").replace("-", "_").replace("/", "_") for c in df.columns]
print(f"\n  Cleaned column names: {list(df.columns)}")

# 2d. Convert date columns
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Ship_Date']  = pd.to_datetime(df['Ship_Date'])

# 2e. Engineer new columns
df['Order_Year']      = df['Order_Date'].dt.year
df['Order_Month']     = df['Order_Date'].dt.month
df['Order_Month_Name']= df['Order_Date'].dt.strftime('%b')
df['Order_Quarter']   = df['Order_Date'].dt.quarter.map({1:'Q1',2:'Q2',3:'Q3',4:'Q4'})
df['Order_Day']       = df['Order_Date'].dt.day_name()
df['Shipping_Days']   = (df['Ship_Date'] - df['Order_Date']).dt.days
df['Profit_Margin']   = (df['Profit'] / df['Sales'] * 100).round(2)
df['Is_Loss']         = df['Profit'] < 0
df['Discount_Band']   = pd.cut(
    df['Discount'],
    bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
    labels=['No Discount','1-10%','11-20%','21-30%','31-50%','51%+']
)

print("\n  Engineered columns added:")
print("    Order_Year, Order_Month, Order_Month_Name, Order_Quarter")
print("    Order_Day, Shipping_Days, Profit_Margin, Is_Loss, Discount_Band")

# ─────────────────────────────────────────────
# STEP 3: KEY METRICS
# ─────────────────────────────────────────────
print("\n[STEP 3] Key Business Metrics")
print(f"  Total Orders          : {len(df):,}")
print(f"  Total Revenue         : ${df['Sales'].sum():,.2f}")
print(f"  Total Profit          : ${df['Profit'].sum():,.2f}")
print(f"  Overall Profit Margin : {(df['Profit'].sum()/df['Sales'].sum()*100):.1f}%")
print(f"  Loss-making Orders    : {df['Is_Loss'].sum():,} ({df['Is_Loss'].mean()*100:.1f}%)")
print(f"  Avg Shipping Days     : {df['Shipping_Days'].mean():.1f} days")
print(f"  Unique Customers      : {df['Customer_ID'].nunique():,}")
print(f"  Unique Products       : {df['Product_ID'].nunique():,}")

# ─────────────────────────────────────────────
# STEP 4: CATEGORY ANALYSIS
# ─────────────────────────────────────────────
print("\n[STEP 4] Category Performance")
cat = df.groupby('Category').agg(
    Orders        = ('Order_ID','count'),
    Revenue       = ('Sales','sum'),
    Profit        = ('Profit','sum'),
    Profit_Margin = ('Profit_Margin','mean')
).round(2).sort_values('Revenue', ascending=False)
print(cat.to_string())

# ─────────────────────────────────────────────
# STEP 5: REGIONAL ANALYSIS
# ─────────────────────────────────────────────
print("\n[STEP 5] Regional Performance")
reg = df.groupby('Region').agg(
    Revenue       = ('Sales','sum'),
    Profit        = ('Profit','sum'),
    Orders        = ('Order_ID','count'),
    Profit_Margin = ('Profit_Margin','mean')
).round(2).sort_values('Profit', ascending=False)
print(reg.to_string())

# ─────────────────────────────────────────────
# STEP 6: DISCOUNT IMPACT
# ─────────────────────────────────────────────
print("\n[STEP 6] Discount Impact on Profit")
disc = df.groupby('Discount_Band').agg(
    Orders        = ('Order_ID','count'),
    Avg_Profit    = ('Profit','mean'),
    Loss_Orders   = ('Is_Loss','sum')
).round(2)
print(disc.to_string())

# ─────────────────────────────────────────────
# STEP 7: SEGMENT ANALYSIS
# ─────────────────────────────────────────────
print("\n[STEP 7] Customer Segment Performance")
seg = df.groupby('Segment').agg(
    Revenue       = ('Sales','sum'),
    Profit        = ('Profit','sum'),
    Orders        = ('Order_ID','count'),
    Avg_Order_Val = ('Sales','mean')
).round(2).sort_values('Revenue', ascending=False)
print(seg.to_string())

# ─────────────────────────────────────────────
# STEP 8: SAVE CLEAN DATA
# ─────────────────────────────────────────────
print("\n[STEP 8] Saving clean dataset...")

# Convert date columns to string for CSV
df_save = df.copy()
df_save['Order_Date'] = df_save['Order_Date'].dt.strftime('%Y-%m-%d')
df_save['Ship_Date']  = df_save['Ship_Date'].dt.strftime('%Y-%m-%d')
df_save['Is_Loss']    = df_save['Is_Loss'].astype(int)
df_save['Discount_Band'] = df_save['Discount_Band'].astype(str)

df_save.to_csv('data/superstore_clean.csv', index=False)
print("  Saved: data/superstore_clean.csv")

print("\n" + "=" * 60)
print("  CLEANING COMPLETE")
print(f"  Clean rows  : {len(df):,}")
print(f"  Total Revenue: ${df['Sales'].sum():,.0f}")
print(f"  Total Profit : ${df['Profit'].sum():,.0f}")
print(f"  Profit Margin: {(df['Profit'].sum()/df['Sales'].sum()*100):.1f}%")
print("=" * 60)
