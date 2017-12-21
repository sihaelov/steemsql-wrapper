from aiohttp import web
import aiohttp_jinja2
import jinja2
import aiohttp_cors

try:
    import pyodbc
except ModuleNotFoundError:
    import pypyodbc as pyodbc

import tablib

import os
import json
from datetime import datetime, date
import functools


async def index(request):
    response = aiohttp_jinja2.render_template('index.html', request, {})
    return response


async def api_run_sql(request):

    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        data = await request.post()

    sql_query = data.get('query')
    limit_rows = data.get('limit_rows')

    if limit_rows:
        limit_rows = 5000 if limit_rows > 5000 else limit_rows
        limit_rows = 0 if limit_rows < 0 else limit_rows
    else:
        limit_rows = 5000

    if not sql_query:
        return web.json_response({'headers': [], 'rows': [],
                                  'error': "Empty query"})

    db_url = 'Driver={ODBC Driver 13 for SQL Server};Server=sql.steemsql.com;Database=DBSteem;uid=steemit;pwd=steemit'
    with pyodbc.connect(db_url, timeout=60) as connection:
        cursor = connection.cursor()
        # connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        # connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        error = None
        rows = []
        try:
            rows_raw = cursor.execute(sql_query).fetchmany(limit_rows)
            headers = [header[0] for header in cursor.description]

            for row in rows_raw:
                rows.append(dict(zip(headers, row)))

        except Exception as e:
            print('Error')
            error = str(e)
            headers = []

    return web.json_response({
                              'headers': headers,
                              'rows': rows,
                              'error': error
                        }, dumps=functools.partial(json.dumps, default=str))


async def sql_export(request):
    data = await request.json()
    export_format = data.get('export_format')
    table = data.get('table')

    if not export_format:
        return web.json_response({'result': None, 'error': "Empty table"})

    tablib_dataset = tablib.Dataset()
    tablib_dataset.headers = table['headers']

    for row in table['rows']:
        row_values = list(map(row.get, table['headers']))
        tablib_dataset.append(row_values)

    # if export_format == 'markdown':
    return web.json_response({'result': str(tablib_dataset), 'error': None})


app = web.Application()

app.router.add_get('/', index)
app.router.add_post('/api', api_run_sql)
app.router.add_post('/export', sql_export)

cors = aiohttp_cors.setup(app, defaults={
        "*":  aiohttp_cors.ResourceOptions(
                expose_headers="*",
                allow_headers="*",
                allow_credentials=True
            ),
    })

for route in list(app.router.routes()):
    cors.add(route)


# ~/Projects/steemit/sql/aio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app.router.add_static('/static/', path=str(BASE_DIR + '/static'), name='static')

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
