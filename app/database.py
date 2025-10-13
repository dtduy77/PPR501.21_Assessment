import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('PGHOST'),
    'dbname': os.getenv('PGDATABASE'),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'sslmode': os.getenv('PGSSLMODE'),
    'channel_binding': os.getenv('PGCHANNELBINDING')
}

def get_connection():
    """Create and return a new PostgreSQL connection using the config above."""
    return psycopg2.connect(**DB_CONFIG)


# Tạo bảng Item duy nhất để lưu kết quả ExtractionResult
def create_table_item():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS "Item" (
            "Id" serial4 PRIMARY KEY,
            "Name" text NOT NULL,
            "Quantity" numeric(12, 2) NULL,
            "UnitPrice" numeric(12, 2) NULL,
            "TotalPrice" numeric(12, 2) NULL,
            "VatPercent" numeric(5, 2) NULL,
            "FinalPrice" numeric(12, 2) NULL,
            "Category" text NULL,
            "UploadTime" timestamp NULL,
            "ReceiptDate" timestamp NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()


def mock_insert_items():
    """Insert mock data for Item table."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Kiểm tra xem đã có data chưa để tránh insert trùng
    cur.execute('SELECT COUNT(*) FROM "Item"')
    existing_count = cur.fetchone()[0]
    
    if existing_count > 0:
        print(f"Database đã có {existing_count} items. Bỏ qua việc insert mock data.")
        cur.close()
        conn.close()
        return
    
    # Sample mock data for items (2025 - current year)
    mock_items_2025 = [
        # Food items
        ("Bánh mì thịt", 2.0, 15000.0, 30000.0, 8.0, 32400.0, "food", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
        ("Phở bò", 1.0, 45000.0, 45000.0, 8.0, 48600.0, "food", datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=2)),
        ("Cơm gà", 1.0, 35000.0, 35000.0, 8.0, 37800.0, "food", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
        ("Pizza margherita", 1.0, 120000.0, 120000.0, 10.0, 132000.0, "food", datetime.now(), datetime.now()),
        ("Bánh cuốn", 1.0, 25000.0, 25000.0, 8.0, 27000.0, "food", datetime.now() - timedelta(hours=5), datetime.now() - timedelta(hours=5)),
        
        # Coffee items
        ("Cà phê đen", 1.0, 20000.0, 20000.0, 8.0, 21600.0, "coffee", datetime.now() - timedelta(hours=3), datetime.now() - timedelta(hours=3)),
        ("Cà phê sữa", 2.0, 25000.0, 50000.0, 8.0, 54000.0, "coffee", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
        ("Cappuccino", 1.0, 45000.0, 45000.0, 10.0, 49500.0, "coffee", datetime.now() - timedelta(hours=2), datetime.now() - timedelta(hours=2)),
        ("Trà sữa trân châu", 1.0, 35000.0, 35000.0, 8.0, 37800.0, "coffee", datetime.now(), datetime.now()),
        
        # Transport items
        ("Xe bus", 1.0, 7000.0, 7000.0, None, 7000.0, "transport", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
        ("Grab bike", 1.0, 15000.0, 15000.0, None, 15000.0, "transport", datetime.now() - timedelta(hours=4), datetime.now() - timedelta(hours=4)),
        ("Taxi", 1.0, 85000.0, 85000.0, None, 85000.0, "transport", datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=2)),
        ("Xe ôm", 1.0, 25000.0, 25000.0, None, 25000.0, "transport", datetime.now() - timedelta(hours=6), datetime.now() - timedelta(hours=6)),
        
        # Shopping items
        ("Áo thun", 1.0, 150000.0, 150000.0, 10.0, 165000.0, "shopping", datetime.now() - timedelta(days=3), datetime.now() - timedelta(days=3)),
        ("Giày sneaker", 1.0, 800000.0, 800000.0, 10.0, 880000.0, "shopping", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
        ("Sách lập trình", 2.0, 120000.0, 240000.0, 5.0, 252000.0, "shopping", datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=2)),
        ("Tai nghe", 1.0, 250000.0, 250000.0, 10.0, 275000.0, "shopping", datetime.now() - timedelta(hours=8), datetime.now() - timedelta(hours=8)),
        
        # Other items
        ("Cắt tóc", 1.0, 50000.0, 50000.0, None, 50000.0, "other", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
        ("Rửa xe", 1.0, 30000.0, 30000.0, None, 30000.0, "other", datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=2)),
        ("Vé xem phim", 2.0, 75000.0, 150000.0, 8.0, 162000.0, "other", datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1)),
    ]
    
    # Mock data for 2024 (last year) - different months
    mock_items_2024 = [
        # January 2024
        ("Bánh mì pate", 1.0, 12000.0, 12000.0, 8.0, 12960.0, "food", datetime(2024, 1, 15), datetime(2024, 1, 15)),
        ("Cà phê đen", 1.0, 15000.0, 15000.0, 8.0, 16200.0, "coffee", datetime(2024, 1, 20), datetime(2024, 1, 20)),
        ("Xe bus", 1.0, 6000.0, 6000.0, None, 6000.0, "transport", datetime(2024, 1, 25), datetime(2024, 1, 25)),
        
        # March 2024
        ("Phở gà", 1.0, 40000.0, 40000.0, 8.0, 43200.0, "food", datetime(2024, 3, 10), datetime(2024, 3, 10)),
        ("Trà sữa", 1.0, 30000.0, 30000.0, 8.0, 32400.0, "coffee", datetime(2024, 3, 15), datetime(2024, 3, 15)),
        ("Grab bike", 1.0, 12000.0, 12000.0, None, 12000.0, "transport", datetime(2024, 3, 20), datetime(2024, 3, 20)),
        ("Áo khoác", 1.0, 200000.0, 200000.0, 10.0, 220000.0, "shopping", datetime(2024, 3, 25), datetime(2024, 3, 25)),
        
        # June 2024
        ("Cơm tấm", 1.0, 30000.0, 30000.0, 8.0, 32400.0, "food", datetime(2024, 6, 5), datetime(2024, 6, 5)),
        ("Sinh tố bơ", 1.0, 25000.0, 25000.0, 8.0, 27000.0, "coffee", datetime(2024, 6, 12), datetime(2024, 6, 12)),
        ("Taxi", 1.0, 75000.0, 75000.0, None, 75000.0, "transport", datetime(2024, 6, 18), datetime(2024, 6, 18)),
        ("Quần jeans", 1.0, 350000.0, 350000.0, 10.0, 385000.0, "shopping", datetime(2024, 6, 22), datetime(2024, 6, 22)),
        ("Karaoke", 2.0, 100000.0, 200000.0, 8.0, 216000.0, "other", datetime(2024, 6, 28), datetime(2024, 6, 28)),
        
        # September 2024
        ("Bánh xèo", 1.0, 35000.0, 35000.0, 8.0, 37800.0, "food", datetime(2024, 9, 8), datetime(2024, 9, 8)),
        ("Cà phê sữa đá", 1.0, 18000.0, 18000.0, 8.0, 19440.0, "coffee", datetime(2024, 9, 14), datetime(2024, 9, 14)),
        ("Xe ôm", 1.0, 20000.0, 20000.0, None, 20000.0, "transport", datetime(2024, 9, 19), datetime(2024, 9, 19)),
        ("Giày thể thao", 1.0, 500000.0, 500000.0, 10.0, 550000.0, "shopping", datetime(2024, 9, 24), datetime(2024, 9, 24)),
        
        # December 2024
        ("Lẩu Thái", 2.0, 150000.0, 300000.0, 8.0, 324000.0, "food", datetime(2024, 12, 5), datetime(2024, 12, 5)),
        ("Trà đá", 1.0, 8000.0, 8000.0, None, 8000.0, "coffee", datetime(2024, 12, 12), datetime(2024, 12, 12)),
        ("Grab car", 1.0, 95000.0, 95000.0, None, 95000.0, "transport", datetime(2024, 12, 15), datetime(2024, 12, 15)),
        ("Áo len", 1.0, 300000.0, 300000.0, 10.0, 330000.0, "shopping", datetime(2024, 12, 20), datetime(2024, 12, 20)),
        ("Massage", 1.0, 80000.0, 80000.0, None, 80000.0, "other", datetime(2024, 12, 25), datetime(2024, 12, 25)),
    ]
    
    # Mock data for different months in 2025
    mock_items_2025_other_months = [
        # February 2025
        ("Bún bò Huế", 1.0, 50000.0, 50000.0, 8.0, 54000.0, "food", datetime(2025, 2, 10), datetime(2025, 2, 10)),
        ("Matcha latte", 1.0, 55000.0, 55000.0, 10.0, 60500.0, "coffee", datetime(2025, 2, 14), datetime(2025, 2, 14)),
        ("Be", 1.0, 18000.0, 18000.0, None, 18000.0, "transport", datetime(2025, 2, 20), datetime(2025, 2, 20)),
        
        # May 2025
        ("Gỏi cuốn", 3.0, 15000.0, 45000.0, 8.0, 48600.0, "food", datetime(2025, 5, 8), datetime(2025, 5, 8)),
        ("Nước ép cam", 1.0, 35000.0, 35000.0, 8.0, 37800.0, "coffee", datetime(2025, 5, 15), datetime(2025, 5, 15)),
        ("Xích lô", 1.0, 50000.0, 50000.0, None, 50000.0, "transport", datetime(2025, 5, 22), datetime(2025, 5, 22)),
        ("Túi xách", 1.0, 450000.0, 450000.0, 10.0, 495000.0, "shopping", datetime(2025, 5, 28), datetime(2025, 5, 28)),
        
        # July 2025
        ("Chè bưởi", 1.0, 20000.0, 20000.0, 8.0, 21600.0, "food", datetime(2025, 7, 5), datetime(2025, 7, 5)),
        ("Kem tràng tiền", 1.0, 25000.0, 25000.0, 8.0, 27000.0, "coffee", datetime(2025, 7, 12), datetime(2025, 7, 12)),
        ("Tàu điện", 1.0, 8000.0, 8000.0, None, 8000.0, "transport", datetime(2025, 7, 18), datetime(2025, 7, 18)),
        
        # August 2025
        ("Bánh tráng nướng", 2.0, 12000.0, 24000.0, 8.0, 25920.0, "food", datetime(2025, 8, 3), datetime(2025, 8, 3)),
        ("Cà phê cốt dừa", 1.0, 40000.0, 40000.0, 8.0, 43200.0, "coffee", datetime(2025, 8, 10), datetime(2025, 8, 10)),
        ("Thẻ xe bus tháng", 1.0, 200000.0, 200000.0, None, 200000.0, "transport", datetime(2025, 8, 15), datetime(2025, 8, 15)),
        ("Kính mát", 1.0, 300000.0, 300000.0, 10.0, 330000.0, "shopping", datetime(2025, 8, 20), datetime(2025, 8, 20)),
        ("Spa", 1.0, 150000.0, 150000.0, 8.0, 162000.0, "other", datetime(2025, 8, 25), datetime(2025, 8, 25)),
    ]
    
    # Combine all mock data
    all_mock_items = mock_items_2025 + mock_items_2024 + mock_items_2025_other_months
    
    try:
        # Insert mock data
        insert_query = '''
            INSERT INTO "Item" ("Name", "Quantity", "UnitPrice", "TotalPrice", "VatPercent", "FinalPrice", "Category", "UploadTime", "ReceiptDate")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        cur.executemany(insert_query, all_mock_items)
        conn.commit()
        print(f"✅ Đã insert thành công {len(all_mock_items)} mock items vào database!")
        print(f"   - Items năm 2025 (tháng hiện tại): {len(mock_items_2025)}")
        print(f"   - Items năm 2024 (các tháng khác): {len(mock_items_2024)}")
        print(f"   - Items năm 2025 (các tháng khác): {len(mock_items_2025_other_months)}")
        
    except Exception as e:
        print(f"Lỗi khi insert mock data: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def init_database():
    """Initialize database - create tables and insert mock data if needed."""
    try:
        print("Khởi tạo database...")
        create_table_item()
        mock_insert_items()
        print("Database đã sẵn sàng!")
    except Exception as e:
        print(f"Lỗi khởi tạo database: {e}")


if __name__ == "__main__":
    # Test database connection
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT version();')
        print("Database connection:", cur.fetchone()[0])
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connection database failed: {e}")
        exit(1)
    
    # Initialize database
    init_database()
