import pandas as pd
import warnings
import os
import sys
import io

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

warnings.filterwarnings("ignore")

print("=" * 90)
print("AIRPURE PROJECT - QUICK EDA (Inspection Only - No Visualization)")
print("=" * 90)

files = {
    "AQI Data": "AQI_data.csv",
    "Health Data": "health_data.csv",
    "Vehicle Data": "vehicle_data.csv",
    "Population Data": "population_data.xlsx"
}

datasets = {}

for dataset_name, file_path in files.items():
    print(f"\n{'=' * 90}")
    print(f"📊 {dataset_name.upper()}")
    print(f"{'=' * 90}")
    
    try:
        # Load file based on extension
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            # Load CSV file with robust encoding handling
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='latin-1')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, encoding='cp1252')
        datasets[dataset_name] = df
        
        # ────────────────────────────────────────────────────────────────────────
        # 1. SHAPE
        # ────────────────────────────────────────────────────────────────────────
        print(f"\n✅ File loaded successfully!")
        print(f"\n📈 SHAPE:")
        print(f"   Rows    : {df.shape[0]:,}")
        print(f"   Columns : {df.shape[1]}")
        
        # ────────────────────────────────────────────────────────────────────────
        # 2. COLUMN NAMES & DATA TYPES
        # ────────────────────────────────────────────────────────────────────────
        print(f"\n📋 COLUMN NAMES & DATA TYPES:")
        for i, col in enumerate(df.columns, 1):
            dtype = str(df[col].dtype)
            print(f"   {i:2}. {col:40} → {dtype}")
        
        # ────────────────────────────────────────────────────────────────────────
        # 3. FIRST 5 ROWS (Sample Data)
        # ────────────────────────────────────────────────────────────────────────
        print(f"\n👀 FIRST 5 ROWS (Sample Data):")
        print(df.head().to_string())
        
        # ────────────────────────────────────────────────────────────────────────
        # 4. MISSING VALUES
        # ────────────────────────────────────────────────────────────────────────
        print(f"\n❓ MISSING VALUES:")
        missing_total = df.isnull().sum().sum()
        print(f"   Total missing cells: {missing_total}")
        
        missing_by_col = df.isnull().sum()
        if missing_by_col.sum() > 0:
            print(f"\n   Missing by column:")
            for col in missing_by_col[missing_by_col > 0].index:
                count = missing_by_col[col]
                pct = (count / len(df)) * 100
                print(f"   • {col:40} → {count:6,} ({pct:5.1f}%)")
        else:
            print(f"   ✓ No missing values detected!")
        
        # ────────────────────────────────────────────────────────────────────────
        # 5. DUPLICATE ROWS
        # ────────────────────────────────────────────────────────────────────────
        print(f"\n🔄 DUPLICATE ROWS:")
        dup_count = df.duplicated().sum()
        print(f"   Total duplicates: {dup_count}")
        if dup_count > 0:
            print(f"   ⚠️  Action needed in Power BI: Remove duplicates")
        else:
            print(f"   ✓ No duplicates found!")
        
        # ────────────────────────────────────────────────────────────────────────
        # 6. UNIQUE VALUES IN KEY COLUMNS
        # ────────────────────────────────────────────────────────────────────────
        print(f"\n🔑 UNIQUE VALUES (Key Columns):")
        for col in df.columns:
            unique_count = df[col].nunique()
            print(f"   • {col:40} → {unique_count:5} unique values")
            
            # Show sample values if reasonable number
            if unique_count <= 15:
                unique_vals = df[col].dropna().unique()[:10]
                print(f"     Sample: {unique_vals}")
        
        # ────────────────────────────────────────────────────────────────────────
        # 7. BASIC STATISTICS (Numeric Columns Only)
        # ────────────────────────────────────────────────────────────────────────
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(f"\n📊 BASIC STATISTICS (Numeric Columns):")
            for col in numeric_cols:
                print(f"\n   {col}:")
                print(f"      Min      : {df[col].min()}")
                print(f"      Max      : {df[col].max()}")
                print(f"      Mean     : {df[col].mean():.2f}")
                print(f"      Median   : {df[col].median():.2f}")
                print(f"      Std Dev  : {df[col].std():.2f}")
        
        # ────────────────────────────────────────────────────────────────────────
        # 8. DATE COLUMNS (if any)
        # ────────────────────────────────────────────────────────────────────────
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            print(f"\n📅 DATE COLUMNS:")
            for col in date_cols:
                print(f"   {col}:")
                print(f"      Min date : {df[col].min()}")
                print(f"      Max date : {df[col].max()}")
                print(f"      Range    : {(df[col].max() - df[col].min()).days} days")
        
        # Try to find date columns that are stored as object/string
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Try to convert to datetime
                    test_dates = pd.to_datetime(df[col], errors='coerce')
                    if test_dates.notna().sum() > len(df) * 0.8:  # If 80%+ can be dates
                        print(f"\n   ⚠️  Column '{col}' appears to be date but stored as text")
                        print(f"      Min date : {test_dates.min()}")
                        print(f"      Max date : {test_dates.max()}")
                        print(f"      Action: Convert to datetime in Power BI")
                except:
                    pass
        
        print(f"\n✅ {dataset_name} inspection complete!")
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: File not found!")
        print(f"   Expected: {file_path}")
        print(f"   Make sure this file is in the SAME FOLDER as this script!")
        print(f"   Current working directory: {os.getcwd()}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

# ════════════════════════════════════════════════════════════════════════════════
# SUMMARY & NEXT STEPS
# ════════════════════════════════════════════════════════════════════════════════

print(f"\n\n{'=' * 90}")
print("📋 SUMMARY & NEXT STEPS")
print(f"{'=' * 90}")

if len(datasets) == 4:
    print(f"\n✅ All 4 datasets loaded successfully!")
    print(f"\n📊 Dataset Summary:")
    for name, df in datasets.items():
        print(f"   • {name:20} → {df.shape[0]:,} rows × {df.shape[1]} columns")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. Review the inspection output above")
    print(f"   2. Note any issues:")
    print(f"      • Missing values? (will clean in Power BI)")
    print(f"      • Date columns as text? (will convert in Power BI)")
    print(f"      • Duplicates? (will remove in Power BI)")
    print(f"      • Data types incorrect? (will fix in Power BI)")
    print(f"\n   3. Open Power BI")
    print(f"   4. Import these 4 CSV/Excel files")
    print(f"   5. Use Power Query to clean & transform")
    print(f"   6. Create your data visualizations")
    
else:
    print(f"\n⚠️  Only {len(datasets)} out of 4 files loaded")
    print(f"   Please check file paths and try again")

print(f"\n{'=' * 90}")
print("✅ EDA COMPLETE - Ready for Power BI!")
print(f"{'=' * 90}\n")

print(f"💡 Tip: If files not found, check your working directory:")
print(f"   Current folder: {os.getcwd()}")
print(f"   Files in this folder: {os.listdir('.')}")