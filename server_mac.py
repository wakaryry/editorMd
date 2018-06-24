from tornado.options import options, define, parse_command_line
from multiprocessing import Pool
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from django.core.wsgi import get_wsgi_application
import sys
import os
# This will raise a `no module named project_name` error
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_name.settings")


SITE_ROOT = os.path.dirname(os.getcwd())
PROJECT_NAME = os.path.basename(os.getcwd())

sys.path.append(SITE_ROOT)
settings_path = PROJECT_NAME + '.settings'
# need append root into path and write settings path in the way.
# otherwise it will raise no module named XXX when you run via cmd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_path)

define('port', type=int, default=8000)


class HelloHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("Welcome Home {}".format(os.getpid()))


def run(port=8000):
    # need move the config ahead.
    # It will raise DJANGO_SETTING_MODULE error via cmd run
    # Here we reset the setting
    os.environ['DJANGO_SETTING_MODULE'] = settings_path
    parse_command_line()
    wsgi_app = get_wsgi_application()
    container = tornado.wsgi.WSGIContainer(wsgi_app)
    handlers = [('/', HelloHandler), ('.*', tornado.web.FallbackHandler, dict(fallback=container))]
    # we now got a static file not found error
    # but it's right when just in Django sys.
    # from django.conf import settings
    # static_dirs = settings.STATICFILES_DIRS
    # but it expected str, bytes or os.PathLike object, not tuple
    # setting = dict(
    # static_path=static_dirs[0]
    # )
    # we need to config static for tornado, or not found statics
    # tornado_app = tornado.web.Application(handlers, **setting)
    tornado_app = tornado.web.Application(handlers)
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    # why with Pool it reports mistakes: Bad file descriptor
    # pool = Pool(4)
    # pool.map(run, [8000, 8001, 8002, 8003])
    # we could use cmd: python server_mac.py --port=8002 style to have more port
    run()
