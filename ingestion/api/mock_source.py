from fastapi import FastAPI
from scripts.generate_data import main as generate
import csv
from pathlib import Path
app = FastAPI(title="Retail Mock Source")
def rows(name):
    p = Path("data/sample") / f"{name}.csv"
    if not p.exists(): generate()
    with p.open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
@app.get("/stores")
def stores(): return rows("stores")
@app.get("/products")
def products(): return rows("products")
@app.get("/suppliers")
def suppliers(): return rows("suppliers")
@app.get("/product-prices")
def prices(): return rows("product_prices")
