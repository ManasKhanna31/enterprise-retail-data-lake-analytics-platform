"""Composable quality checks."""
def quality_report(records: dict[str, list[dict]]) -> dict:
    checks = []
    for name, rows in records.items():
        checks.append({"dataset": name, "records": len(rows), "null_check": all(all(v not in (None, "") for v in r.values()) for r in rows), "duplicate_check": len({tuple(sorted(r.items())) for r in rows}) == len(rows)})
    return {"datasets": checks, "overall": all(x["null_check"] and x["duplicate_check"] for x in checks)}
def valid_references(child_rows, child_key, parent_rows, parent_key):
    parents = {r[parent_key] for r in parent_rows}
    return [r for r in child_rows if r.get(child_key) in parents]
