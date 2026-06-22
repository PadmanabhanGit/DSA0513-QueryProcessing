# AI Query Optimizer

## Project Introduction
The AI Query Optimizer is a web-based system designed to help developers analyze SQL queries, estimate execution cost, and receive optimization guidance. It combines static SQL heuristics, machine learning prediction, query execution tracking, and rule-based recommendations to improve database query performance.

Key features:
- Analyze SQL query structure and extract metrics such as joins, conditions, and clauses.
- Predict query execution time using a trained Random Forest model.
- Execute queries on a MySQL database and capture actual execution metrics.
- Store query history and performance data for review.
- Provide optimization recommendations based on query characteristics.

## Methodology
The project uses a multi-step pipeline:

1. Query Input and Analysis
   - Users submit SQL queries through a Flask web UI.
   - `models/analyzer.py` inspects the query text and extracts features like query length, join count, condition count, GROUP BY count, ORDER BY count, and number of tables.

2. Machine Learning Prediction
   - `train_model.py` builds a synthetic dataset and trains a Random Forest regressor.
   - `models/predictor.py` loads the saved model (`query_model.pkl`) and predicts execution time using the extracted features.
   - If the model is unavailable, a fallback heuristic calculates a rough estimate.

3. Query Execution and Timing
   - The submitted query can be executed against the configured MySQL database.
   - The system measures actual execution time and stores query results when possible.
   - Execution metadata is persisted in the `query_history` table for later review.

4. Recommendation Generation
   - `models/recommendation.py` applies rule-based logic to identify optimization opportunities.
   - Examples include flagging `SELECT *`, missing `WHERE` clauses, excessive joins, and unnecessary sorting or grouping.

## System Architecture
The application is structured as a modular Flask project with clear separation of concerns:

- `app.py`
  - Main Flask application and route definitions.
  - Handles user requests for query analysis, dashboard metrics, history listing, CSV export, and PDF export.

- `config.py`
  - Central repository for database connection settings and application configuration.

- `models/`
  - `analyzer.py` — Query feature extraction logic.
  - `predictor.py` — ML model loading and execution time prediction.
  - `recommendation.py` — Rule-driven recommendation engine.

- `train_model.py`
  - Synthetic dataset generation and Random Forest model training.
  - Persists the trained model to `query_model.pkl`.

- `database/`
  - `schema.sql` — MySQL schema for sample data and query history.

- `templates/`
  - User interface pages for query input, results, dashboard, and history.

- `static/`
  - CSS and JavaScript assets, including dashboard visualizations and styles.

This architecture supports rapid development while keeping analysis, prediction, and presentation layers separate.

## Future Scope
Potential enhancements to evolve the project into a more robust optimizer include:

- Add SQL sanitization and safety enforcement to prevent destructive queries.
- Replace regex-based parsing with a proper SQL parser like `sqlparse` or an AST-based approach.
- Leverage `EXPLAIN` plan output for index suggestions and detection of full table scans.
- Expand ML features with real execution trace data, table statistics, and index metadata.
- Add authentication and role-based access control for secure usage.
- Containerize the application with Docker and add `docker-compose` support for reproducible deployment.
- Introduce automated tests for query analysis, prediction, and Flask routes.
- Offer advanced dashboard analytics, query performance trends, and comparison reports.

## Recommendations
For practical use and improvement, the project should prioritize:

- Enforcing only safe `SELECT` statements in production to protect the database.
- Using a read-only database user or sandboxed environment for query execution.
- Improving query analysis accuracy with formal parsing and SQL-specific feature extraction.
- Capturing and using actual query execution plans to power smarter recommendations.
- Adding a clear user history interface, pagination, and search filtering for query auditability.

These recommendations will make the system safer, more accurate, and more valuable for real-world query optimization tasks.
