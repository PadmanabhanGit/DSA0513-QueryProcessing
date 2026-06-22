import re
from typing import Dict


class QueryAnalyzer:
    """Extract simple statistics from an SQL query string."""

    JOIN_PAT = re.compile(r"\bJOIN\b", re.IGNORECASE)
    WHERE_PAT = re.compile(r"\bWHERE\b", re.IGNORECASE)
    GROUP_BY_PAT = re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE)
    ORDER_BY_PAT = re.compile(r"\bORDER\s+BY\b", re.IGNORECASE)
    TABLE_PAT = re.compile(r"\bFROM\s+([\w`\.]+)", re.IGNORECASE)

    @staticmethod
    def analyze(query: str) -> Dict[str, int]:
        q = query or ""
        length = len(q)
        joins = len(QueryAnalyzer.JOIN_PAT.findall(q))
        where = len(QueryAnalyzer.WHERE_PAT.findall(q))
        group_by = len(QueryAnalyzer.GROUP_BY_PAT.findall(q))
        order_by = len(QueryAnalyzer.ORDER_BY_PAT.findall(q))
        tables = len(QueryAnalyzer.TABLE_PAT.findall(q))

        return {
            "query_length": length,
            "joins": joins,
            "conditions": where,
            "group_by_count": group_by,
            "order_by_count": order_by,
            "tables_used": tables,
        }


if __name__ == "__main__":
    sample = "SELECT * FROM employees e JOIN departments d ON e.department=d.name WHERE salary>70000 GROUP BY department ORDER BY salary"
    print(QueryAnalyzer.analyze(sample))
