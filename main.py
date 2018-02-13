from aiohttp import web
import aiohttp_jinja2
import jinja2
import aiohttp_cors

import os

from views import index, api_run_sql, sql_export, get_delay


app = web.Application()

app.router.add_get('/', index)
app.router.add_post('/api', api_run_sql)
app.router.add_post('/export', sql_export)
app.router.add_get('/delay', get_delay)

cors_options = aiohttp_cors.ResourceOptions(
                expose_headers="*",
                allow_headers="*",
                allow_credentials=True
            )

cors = aiohttp_cors.setup(app, defaults={
        "https://steemrank.steemhelpers.com":  cors_options,
        "https://steemlyt.steemhelpers.com":  cors_options,
        "https://sql.steemhelpers.com":  cors_options,
        "http://127.0.0.1:8080":  cors_options,
    })

for route in list(app.router.routes()):
    cors.add(route)


# ~/Projects/steemit/sql/aio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('frontend'))
app.router.add_static('/static/', path=str(BASE_DIR + '/frontend/static'), name='static')

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8080)
