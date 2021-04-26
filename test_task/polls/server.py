from aiohttp import web
from routes import setup_routes
from settings import config
from db import init_pg,close_pg

app = web.Application()
setup_routes(app)
app['config'] = config
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
web.run_app(app)
