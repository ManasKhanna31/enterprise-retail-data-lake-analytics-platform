"""Local reference implementation for the Spark transformation contract."""
from pathlib import Path
import json
def build_gold(records, output_dir):
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    orders = {r["order_id"]: r for r in records.get("orders", [])}; products = {r["product_id"]: r for r in records.get("products", [])}
    sales = []
    for item in records.get("order_items", []):
        order, product = orders.get(item.get("order_id")), products.get(item.get("product_id"))
        if not order or not product: continue
        quantity = int(item["quantity"]); revenue = quantity * float(item["unit_price"]) - float(item.get("discount") or 0)
        sales.append({"order_id": order["order_id"], "order_date": order["order_date"], "customer_id": order["customer_id"], "store_id": order["store_id"], "product_id": item["product_id"], "category": product["category"], "quantity": quantity, "revenue": round(revenue, 2), "profit": round(revenue - quantity * float(product["cost"]), 2)})
    (out / "fact_sales.json").write_text(json.dumps(sales, indent=2), encoding="utf-8"); return sales
