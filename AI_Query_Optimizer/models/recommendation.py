from typing import Dict, List


def generate_recommendations(query: str, stats: dict) -> List[Dict[str, str]]:
    recs = []
    q = (query or "").upper()

    def add(issue: str, fix: str, example: str = ""):
        recs.append({
            "issue": issue,
            "fix": fix,
            "example": example,
        })

    if "SELECT *" in q:
        add(
            "Avoid SELECT *.",
            "Specify only the columns you need so the database can reduce I/O and scanning overhead.",
            "SELECT id, first_name, last_name FROM employees WHERE department_id = 5"
        )

    if stats.get("conditions", 0) == 0:
        add(
            "No WHERE clause detected.",
            "Add filtering conditions to narrow the result set and avoid full table scans. If you only need a sample, use LIMIT.",
            "SELECT col1, col2 FROM sales WHERE sale_date >= '2025-01-01' LIMIT 100"
        )

    if stats.get("joins", 0) > 2:
        add(
            "Excessive joins detected.",
            "Try rewriting the query using fewer joins, derived tables, or correlated subqueries to simplify execution.",
            "SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.order_date > '2025-01-01'"
        )

    if stats.get("order_by_count", 0) > 0:
        add(
            "ORDER BY clause present.",
            "Ensure ORDER BY columns are indexed or limit the output to reduce sorting overhead.",
            "SELECT id, total FROM invoices WHERE created_at >= '2025-01-01' ORDER BY created_at DESC LIMIT 50"
        )

    if stats.get("group_by_count", 0) > 0:
        add(
            "GROUP BY clause present.",
            "Index grouped columns and aggregate only the fields you need to improve grouping performance.",
            "SELECT department_id, COUNT(*) FROM employees GROUP BY department_id"
        )

    if stats.get("query_length", 0) > 300:
        add(
            "Query is very long.",
            "Break large queries into smaller pieces using CTEs or temporary tables so each step stays easier to optimize and maintain.",
            "WITH filtered AS (SELECT id, amount FROM sales WHERE region = 'west') SELECT region, SUM(amount) FROM filtered GROUP BY region"
        )

    if "LIMIT" not in q and "SELECT" in q and "WHERE" not in q and stats.get("query_length", 0) > 120:
        add(
            "Potential unbounded result set.",
            "Add a LIMIT clause or filter criteria when querying large tables to prevent expensive full scans.",
            "SELECT id, name FROM products WHERE category = 'hardware' LIMIT 100"
        )

    if not recs:
        add(
            "Query appears optimized.",
            "The query has no obvious rule-based issues. Continue validating performance with actual execution plans and indexes.",
            ""
        )

    return recs


if __name__ == "__main__":
    print(generate_recommendations("SELECT * FROM employees", {"conditions":0, "joins":3, "order_by_count":1, "group_by_count":0, "query_length":400}))
