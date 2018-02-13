from aiohttp import web
import aiohttp_jinja2

try:
    import pyodbc
except ModuleNotFoundError:
    import pypyodbc as pyodbc

import tablib

from os import environ
import json
from datetime import datetime, date
import functools


tablib.formats.json.json = json
db_url = ('Driver={ODBC Driver 13 for SQL Server};'
          'Server=vip.steemsql.com;Database=DBSteem;'
          f'uid={environ["DB_USERNAME"]};'
          f'pwd={environ["DB_PASSWORD"]}')


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

    start_time = datetime.now()
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
    end_time = datetime.now()
    execution_time_raw = end_time - start_time
    execution_time = round(execution_time_raw.total_seconds())

    return web.json_response({
                              'headers': headers,
                              'rows': rows,
                              'error': error,
                              'execution_time': execution_time
                        }, dumps=functools.partial(json.dumps, default=str))


async def sql_export(request):
    data = await request.json()
    export_format = data.get('export_format')
    table = data.get('table')

    mime_types = {
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',

        'csv': 'text/csv',
        'json': 'application/json',
    }

    if not export_format or export_format not in ['markdown', 'xlsx', 'xls', 'csv', 'json']:
        return web.json_response({'result': None, 'error': "Empty or incorrect format"})

    tablib_dataset = tablib.Dataset()
    tablib_dataset.headers = table['headers']

    for row in table['rows']:
        row_values = list(map(row.get, table['headers']))
        tablib_dataset.append(row_values)

    if export_format == 'markdown':
        return web.json_response({'result': str(tablib_dataset), 'error': None})
    else:
        result = tablib_dataset.export(export_format)

        return web.Response(
            headers={'Content-Disposition': 'attachment; filename="data.%s' % export_format},
            content_type=mime_types[export_format],
            body=result
        )


async def get_delay(request):

    sql_query = "SELECT TOP 1 timestamp FROM Blocks ORDER BY block_num DESC"
    with pyodbc.connect(db_url, timeout=60) as connection:
        cursor = connection.cursor()
        steemsql_last_time = cursor.execute(sql_query).fetchone()[0]

    current_time = datetime.utcnow()
    delay = current_time - steemsql_last_time

    return web.json_response({'delay_seconds': round(delay.total_seconds())})
