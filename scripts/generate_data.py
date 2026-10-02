"""Generate deterministic retail fixtures, including intentional bad records."""
from pathlib import Path
import csv
from datetime import date, timedelta
from openpyxl import Workbook

ROOT = Path("data/sample")

def write_csv(name, rows):
    path = ROOT / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    suppliers = [{"supplier_id": i, "supplier_name": f"Supplier {i}", "state": "KA" if i % 2 else "MH"} for i in range(1, 4)]
    stores = [{"store_id": i, "store_name": f"Store {i}", "city": "Bengaluru" if i % 2 else "Mumbai", "state": "KA" if i % 2 else "MH", "region": "South" if i % 2 else "West"} for i in range(1, 4)]
    products = [{"product_id": i, "product_name": f"Product {i}", "category": "Grocery" if i % 2 else "Home", "subcategory": "Daily" if i % 2 else "Utility", "supplier_id": (i % 3) + 1, "cost": 10.0 + i, "selling_price": 18.0 + i} for i in range(1, 6)]
    customers = [{"customer_id": i, "name": f"Customer {i}", "email": f"customer{i}@example.com", "city": "Bengaluru", "state": "KA", "signup_date": "2026-01-01"} for i in range(1, 6)]
    orders = [{"order_id": i, "customer_id": (i % 5) + 1, "store_id": (i % 3) + 1, "order_date": str(date(2026, 1, 1) + timedelta(days=i)), "status": "completed"} for i in range(1, 11)]
    items = [{"order_id": i, "product_id": (i % 5) + 1, "quantity": (i % 3) + 1, "unit_price": 18.0 + ((i % 5) + 1), "discount": 1.0 if i % 4 == 0 else 0.0} for i in range(1, 11)]
    inventory = [{"product_id": p, "store_id": s, "inventory_date": "2026-01-31", "stock_quantity": 5 + p + s} for p in range(1, 6) for s in range(1, 4)]
    shipments = [{"shipment_id": i, "supplier_id": (i % 3) + 1, "store_id": (i % 3) + 1, "ship_date": "2026-01-10", "delivery_date": "2026-01-13", "status": "delivered"} for i in range(1, 4)]
    returns = [{"return_id": 1, "order_id": 2, "product_id": 3, "return_date": "2026-01-20", "quantity": 1, "reason": "damaged"}]
    prices = [{"product_id": i, "effective_date": "2026-01-01", "price": 18.0 + i} for i in range(1, 6)]
    for name, rows in [("suppliers", suppliers), ("stores", stores), ("products", products), ("customers", customers), ("orders", orders), ("order_items", items), ("shipments", shipments), ("returns", returns), ("product_prices", prices)]: write_csv(name, rows)
    inventory[0]["stock_quantity"] = "bad-number"; inventory.append(inventory[0].copy())
    write_csv("inventory", inventory)
    wb = Workbook(); ws = wb.active; ws.append(list(inventory[0]))
    for row in inventory[:5]: ws.append(list(row.values()))
    wb.save(ROOT / "inventory.xlsx")
    print(f"Generated {len(list(ROOT.glob('*.csv')))} CSV fixtures and inventory.xlsx in {ROOT}")

if __name__ == "__main__": main()
