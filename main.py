from aiohttp import web
import aiohttp_jinja2
import jinja2

try:
    import pyodbc
except ModuleNotFoundError:
    import pypyodbc as pyodbc

import os
import json
from datetime import datetime, date


async def index(request):
    response = aiohttp_jinja2.render_template('index.html', request, {})
    return response


async def run_sql(request):

    data = await request.post()
    sql_query = data.get('sql')

    db_url = 'Driver={ODBC Driver 13 for SQL Server};Server=sql.steemsql.com;Database=DBSteem;uid=steemit;pwd=steemit'
    with pyodbc.connect(db_url, timeout=60) as connection:
        cursor = connection.cursor()
        # connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        # connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        error = None
        try:
            rows_raw = cursor.execute(sql_query).fetchmany(5000)
            rows = [list(row_raw) for row_raw in rows_raw]
            headers = [header[0] for header in cursor.description]
        except Exception as e:
            print('Error')
            error = str(e)
            rows = []
            headers = []

    rows_json = json.dumps(rows, default=str)
    return web.json_response({'headers': headers, 'rows': rows_json,
                              'error': error})


app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/query/', run_sql)

# ~/Projects/steemit/sql/aio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app.router.add_static('/static/', path=str(BASE_DIR + '/static'), name='static')

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
