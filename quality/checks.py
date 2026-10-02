"""Composable data quality and schema checks."""
PRIMARY_KEYS = {
    "customers": ["customer_id"],
    "inventory": ["product_id", "store_id", "inventory_date"],
    "orders": ["order_id"],
    "order_items": ["order_id", "product_id"],
    "products": ["product_id"],
    "product_prices": ["product_id", "effective_date"],
    "returns": ["return_id"],
    "shipments": ["shipment_id"],
    "stores": ["store_id"],
    "suppliers": ["supplier_id"],
}

FOREIGN_KEYS = {
    "inventory": [
        ("product_id", "products", "product_id"),
        ("store_id", "stores", "store_id"),
    ],
    "orders": [
        ("customer_id", "customers", "customer_id"),
        ("store_id", "stores", "store_id"),
    ],
    "order_items": [
        ("order_id", "orders", "order_id"),
        ("product_id", "products", "product_id"),
    ],
    "products": [
        ("supplier_id", "suppliers", "supplier_id"),
    ],
    "product_prices": [
        ("product_id", "products", "product_id"),
    ],
    "returns": [
        ("order_id", "orders", "order_id"),
        ("product_id", "products", "product_id"),
    ],
    "shipments": [
        ("supplier_id", "suppliers", "supplier_id"),
        ("store_id", "stores", "store_id"),
    ],
}

EXPECTED_SCHEMAS = {
    "customers": [
        "customer_id",
        "name",
        "email",
        "city",
        "state",
        "signup_date",
    ],
    "inventory": [
        "product_id",
        "store_id",
        "inventory_date",
        "stock_quantity",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "store_id",
        "order_date",
        "status",
    ],
    "order_items": [
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "supplier_id",
        "cost",
        "selling_price",
    ],
    "product_prices": [
        "product_id",
        "effective_date",
        "price",
    ],
    "returns": [
        "return_id",
        "order_id",
        "product_id",
        "return_date",
        "quantity",
        "reason",
    ],
    "shipments": [
        "shipment_id",
        "supplier_id",
        "store_id",
        "ship_date",
        "delivery_date",
        "status",
    ],
    "stores": [
        "store_id",
        "store_name",
        "city",
        "state",
        "region",
    ],
    "suppliers": [
        "supplier_id",
        "supplier_name",
        "state",
    ],
}


def schema_check(dataset: str, rows: list[dict]) -> bool:
    """Check that a dataset has exactly the expected columns."""
    expected = EXPECTED_SCHEMAS.get(dataset)

    if expected is None:
        return False

    if not rows:
        return True

    actual = {
        key
        for key in rows[0].keys()
        if key not in {"_ingested_at", "_source"}
    }

    return actual == set(expected)
def key_integrity_check(
    dataset: str,
    records: dict[str, list[dict]],
) -> bool:
    """Check primary-key uniqueness and foreign-key references."""

    rows = records.get(dataset, [])

    # Primary-key uniqueness
    primary_key = PRIMARY_KEYS.get(dataset, [])

    if primary_key:
        keys = [
            tuple(row.get(column) for column in primary_key)
            for row in rows
        ]

        if any(None in key or "" in key for key in keys):
            return False

        if len(keys) != len(set(keys)):
            return False

    # Foreign-key integrity
    for child_column, parent_dataset, parent_column in FOREIGN_KEYS.get(
        dataset, []
    ):
        parent_rows = records.get(parent_dataset, [])
        parent_values = {
            row.get(parent_column)
            for row in parent_rows
        }

        for row in rows:
            value = row.get(child_column)

            if value not in parent_values:
                return False

    return True

def quality_report(records: dict[str, list[dict]]) -> dict:
    """Run schema, null and duplicate checks for every dataset."""
    checks = []

    for name, rows in records.items():
        checks.append(
    {
        "dataset": name,
        "records": len(rows),
        "schema_check": schema_check(name, rows),
        "null_check": all(
            all(v not in (None, "") for v in r.values())
            for r in rows
        ),
        "duplicate_check": len(
            {tuple(sorted(r.items())) for r in rows}
        ) == len(rows),
        "key_integrity_check": key_integrity_check(name, records),
    }
)

    return {
        "datasets": checks,
        "overall": all(
            x["schema_check"]
            and x["null_check"]
            and x["duplicate_check"]
            and x["key_integrity_check"]
            for x in checks
        )
    }


def valid_references(child_rows, child_key, parent_rows, parent_key):
    """Return child rows whose key exists in the parent dataset."""
    parents = {r[parent_key] for r in parent_rows}
    return [
        r for r in child_rows
        if r.get(child_key) in parents
    ]