from quality.checks import quality_report, valid_references
from spark.transformations.local import build_gold
def test_quality_detects_duplicate():
    assert quality_report({"x": [{"id": "1"}, {"id": "1"}]})["overall"] is False
def test_reference_filter():
    assert valid_references([{"product_id": "1"}, {"product_id": "9"}], "product_id", [{"product_id": "1"}], "product_id") == [{"product_id": "1"}]
def test_local_gold(tmp_path):
    rows = {"orders": [{"order_id":"1", "customer_id":"2", "store_id":"3", "order_date":"2026-01-01"}], "products":[{"product_id":"4", "category":"Grocery", "cost":"5"}], "order_items":[{"order_id":"1","product_id":"4","quantity":"2","unit_price":"8","discount":"1"}]}
    assert build_gold(rows, tmp_path)[0]["revenue"] == 15.0
