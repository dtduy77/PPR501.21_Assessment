
from app.database import get_connection
from app.models import ItemResponse

def create_item(name, quantity, unit_price, total_price, vat_percent, final_price, category, upload_time, receipt_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO "Item" ("Name", "Quantity", "UnitPrice", "TotalPrice", "VatPercent", "FinalPrice", "Category", "UploadTime", "ReceiptDate")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING "Id";
    ''', (name, quantity, unit_price, total_price, vat_percent, final_price, category, upload_time, receipt_date))
    item_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return item_id

def get_items_by_date_range(start_date, end_date):
    print(f"Fetching items from {start_date} to {end_date}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Item" WHERE DATE("ReceiptDate") >= %s AND DATE("ReceiptDate") <= %s;', (start_date, end_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    items = []
    for row in rows:
        items.append(ItemResponse(
            name=row[1],
            quantity=row[2],
            unit_price=row[3],
            total_price=row[4],
            vat_percent=row[5],
            final_price=row[6],
            category=row[7],
            upload_time=row[8].strftime("%Y-%m-%d %H:%M:%S") if row[8] else None,
            receipt_date=row[9].strftime("%Y-%m-%d %H:%M:%S") if row[9] else None
        ))
    return items
