import time
import csv
import io
import traceback
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask import Blueprint
import mysql.connector
from config import DB_CONFIG, MODEL_PATH
from models.analyzer import QueryAnalyzer
from models.predictor import Predictor
from models.recommendation import generate_recommendations
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
main = Blueprint('main', __name__)
logging.basicConfig(level=logging.INFO)


HISTORY_PAGE_SIZE = 10

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        logging.error('MySQL connection failed: %s', e)
        raise


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def is_safe_select(query: str) -> bool:
    """Allow only simple SELECT queries and reject destructive or non-SELECT statements."""
    if not query:
        return False

    normalized = query.strip().lower()
    if not normalized.startswith('select'):
        return False

    # disallow multiple statements and dangerous keywords
    if ';' in normalized.strip().rstrip(';'):
        return False

    forbidden = [
        'insert ', 'update ', 'delete ', 'drop ', 'truncate ', 'alter ',
        'create ', 'replace ', 'grant ', 'revoke ', 'exec ', 'execute ',
        'call ', 'merge ', 'set ', 'use ', 'describe ', 'alter ', 'shutdown '
    ]
    if any(token in normalized for token in forbidden):
        return False

    return True


@main.route('/analyze', methods=['POST'])
def analyze():
    query = request.form.get('query', '').strip()
    if not query:
        return redirect(url_for('main.index'))

    stats = QueryAnalyzer.analyze(query)
    predictor = Predictor()
    predicted = predictor.predict(stats)

    if not is_safe_select(query):
        error_message = 'Only SELECT queries are allowed. Please avoid INSERT, UPDATE, DELETE, DROP, and other non-SELECT statements.'
        return render_template('result.html', query_text=query, stats=stats, predicted_time=predicted,
                               execution_time=None, recs=[], rows=[], cols=[], error_message=error_message)

    # Execute query and measure
    execution_time = None
    status = 'failed'
    rows = []
    cols = []
    rows_returned = 0
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        start = time.time()
        cur.execute(query)
        if cur.with_rows:
            rows = cur.fetchmany(200)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows_returned = len(rows)
        else:
            conn.commit()
        end = time.time()
        execution_time = (end - start) * 1000.0
        status = 'success'
    except Exception as e:
        logging.error('Query execution failed: %s', e)
        execution_time = None
        status = f'error: {str(e)[:200]}'
        rows = []
        cols = []
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass

    # Save history
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO query_history (query_text, execution_time, predicted_time, status, rows_returned) VALUES (%s,%s,%s,%s,%s)",
                    (query, execution_time or 0.0, predicted, status, rows_returned))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logging.error('Failed to save history: %s', e)

    recs = generate_recommendations(query, stats)

    return render_template('result.html', query_text=query, stats=stats, predicted_time=predicted,
                           execution_time=execution_time, recs=recs, rows=rows, cols=cols)


@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main.route('/history')
def history():
    q = request.args.get('q', '')
    page = max(int(request.args.get('page', 1)), 1)
    offset = (page - 1) * HISTORY_PAGE_SIZE

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        if q:
            count_query = "SELECT COUNT(*) as total FROM query_history WHERE query_text LIKE %s"
            cur.execute(count_query, ('%' + q + '%',))
        else:
            count_query = "SELECT COUNT(*) as total FROM query_history"
            cur.execute(count_query)
        total_rows = cur.fetchone()['total']
        total_pages = max((total_rows + HISTORY_PAGE_SIZE - 1) // HISTORY_PAGE_SIZE, 1)

        if q:
            cur.execute(
                "SELECT * FROM query_history WHERE query_text LIKE %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
                ('%' + q + '%', HISTORY_PAGE_SIZE, offset)
            )
        else:
            cur.execute(
                "SELECT * FROM query_history ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (HISTORY_PAGE_SIZE, offset)
            )

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('history.html', rows=rows, page=page, total_pages=total_pages, query_term=q)
    except mysql.connector.Error as e:
        logging.error('Database auth/connect failure in history: %s', e)
        return render_template('error.html',
                               error_title='Database Connection Failed',
                               error_message='Unable to access query history because MySQL authentication failed.',
                               details=str(e))
    except Exception as e:
        logging.error('Unexpected history error: %s', e)
        return render_template('error.html',
                               error_title='Unexpected Error',
                               error_message='An unexpected error occurred while loading history.',
                               details=str(e))


@main.route('/api/stats')
def api_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) as total FROM query_history")
        total = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as slow FROM query_history WHERE execution_time>1000")
        slow = cur.fetchone()['slow']
        cur.execute("SELECT AVG(execution_time) as avg_time FROM query_history")
        avg_time = cur.fetchone()['avg_time'] or 0.0
        cur.execute("SELECT status, COUNT(*) as cnt FROM query_history GROUP BY status")
        status_rows = cur.fetchall()
        status = {r['status']: r['cnt'] for r in status_rows}

        # trend: last 10 entries
        cur.execute("SELECT DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') as dt, execution_time FROM query_history ORDER BY created_at DESC LIMIT 20")
        trend_rows = cur.fetchall()
        trend_rows = list(reversed(trend_rows))
        labels = [r['dt'] for r in trend_rows]
        data = [r['execution_time'] or 0 for r in trend_rows]

        cur.close()
        conn.close()

        return jsonify({
            'total_queries': total,
            'slow_queries': slow,
            'avg_time': avg_time,
            'status': status,
            'trend': {'labels': labels, 'data': data},
            'optimizations': 0
        })
    except Exception as e:
        logging.error('Failed to compute stats: %s', e)
        return jsonify({})


@main.route('/download_history')
def download_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT query_text, execution_time, predicted_time, status, created_at FROM query_history ORDER BY created_at DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['query_text','execution_time','predicted_time','status','created_at'])
        cw.writerows(rows)
        mem = io.BytesIO()
        mem.write(si.getvalue().encode('utf-8'))
        mem.seek(0)
        return send_file(mem, mimetype='text/csv', download_name='query_history.csv', as_attachment=True)
    except Exception as e:
        logging.error('Failed to download history: %s', e)
        return (str(e), 500)


@main.route('/export_pdf')
def export_pdf():
    qid = request.args.get('id')
    if not qid:
        return ("Missing id", 400)
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM query_history WHERE id=%s", (qid,))
        rec = cur.fetchone()
        cur.close()
        conn.close()
        if not rec:
            return ("Not found", 404)

        mem = io.BytesIO()
        p = canvas.Canvas(mem, pagesize=letter)
        p.setFont('Helvetica', 12)
        p.drawString(30, 750, 'Query Analysis Report')
        y = 720
        for k in ['id','query_text','execution_time','predicted_time','status','created_at']:
            p.drawString(30, y, f"{k}: {rec.get(k)}")
            y -= 20
        p.showPage()
        p.save()
        mem.seek(0)
        return send_file(mem, mimetype='application/pdf', download_name='report.pdf', as_attachment=True)
    except Exception as e:
        logging.error('Failed to export PDF: %s', e)
        return (str(e), 500)


app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
