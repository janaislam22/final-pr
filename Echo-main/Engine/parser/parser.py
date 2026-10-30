
import sqlglot
from sqlglot import expressions as exp


def parse_sql_to_steps(sql_query: str) -> list:
    """Parse SQL into structural steps for ECHO analysis."""

    if not isinstance(sql_query, str) or not sql_query.strip():
        raise ValueError("SQL query must be a non-empty string.")

    try:
        tree = sqlglot.parse_one(sql_query)
    except Exception as exc:
        raise ValueError(f"Invalid SQL syntax: {exc}") from exc

    steps = []
    step_id = 1

    # CTE definitions
    with_clause = tree.args.get("with_")
    if with_clause:
        for cte in with_clause.expressions:
            steps.append({
                "step_id": step_id,
                "step_type": "CTE",
                "name": cte.alias,
                "sql_snippet": cte.this.sql(),
                "executable_query": cte.this.sql(),
            })
            step_id += 1

    # Base table
    from_clause = tree.args.get("from_")
    if from_clause:
        table = from_clause.this
        steps.append({
            "step_id": step_id,
            "step_type": "BASE_TABLE",
            "name": table.name if isinstance(table, exp.Table) else table.sql(),
            "sql_snippet": from_clause.sql(),
            "executable_query": None,
        })
        step_id += 1

    # JOINs
    for join in tree.args.get("joins") or []:
        target = join.this
        on_clause = join.args.get("on")

        steps.append({
            "step_id": step_id,
            "step_type": "JOIN",
            "name": target.name if isinstance(target, exp.Table) else target.sql(),
            "sql_snippet": join.sql(),
            "join_details": {
                "join_type": join.side or "INNER",
                "target_table": target.name if isinstance(target, exp.Table) else target.sql(),
                "on_condition": on_clause.sql() if on_clause else None,
            },
            "executable_query": None,
        })
        step_id += 1

    # Aggregation
    group_clause = tree.args.get("group")
    if group_clause:
        steps.append({
            "step_id": step_id,
            "step_type": "GROUP_BY",
            "name": "aggregation",
            "sql_snippet": group_clause.sql(),
            "executable_query": tree.sql(),
        })

    if not steps:
        steps.append({
            "step_id": 1,
            "step_type": "QUERY",
            "name": "main_query",
            "sql_snippet": tree.sql(),
            "executable_query": tree.sql(),
        })

    return steps
