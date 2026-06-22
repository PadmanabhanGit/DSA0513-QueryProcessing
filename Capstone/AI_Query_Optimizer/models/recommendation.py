from typing import List


def generate_recommendations(query: str, stats: dict) -> List[str]:
    recs = []
    q = (query or "").upper()

    if "SELECT *" in q:
        recs.append("Avoid SELECT * and retrieve only required columns.")

    if stats.get("conditions", 0) == 0:
        recs.append("Add WHERE clause to reduce table scans.")

    if stats.get("joins", 0) > 2:
        recs.append("Reduce excessive joins.")

    if stats.get("order_by_count", 0) > 0:
        recs.append("Consider indexing ORDER BY columns.")

    if stats.get("group_by_count", 0) > 0:
        recs.append("Ensure grouped columns are indexed.")

    if stats.get("query_length", 0) > 300:
        recs.append("Break large queries into smaller optimized queries.")

    if not recs:
        recs.append("Query appears optimized.")

    return recs


if __name__ == "__main__":
    print(generate_recommendations("SELECT * FROM employees", {"conditions":0, "joins":3, "order_by_count":1, "group_by_count":0, "query_length":400}))
