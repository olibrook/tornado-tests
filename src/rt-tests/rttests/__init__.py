"""Runs a Tornado web application which can handle websockets.

The Tornado event-loop is single-threaded. To read or write to the database
without blocking the main thread we can use concurrent.futures in Python3
to do this work in the background. Because of the GIL this mostly makes
sense for IO-bound tasks.

"""
import concurrent.futures as futures
import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rttests.web.settings")
from django.core.wsgi import get_wsgi_application
from tornado.options import options, define, parse_command_line
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.websocket

import rttests.web.common.models as models

_logger = logging.getLogger(__name__)

# Uses queue.Queue behind the scenes - can keep submitting work from the main
# thread.
_executor = futures.ThreadPoolExecutor(max_workers=10)

# Connected WebSocketChatHandler clients
_clients = []

# Count of previous connections (since these can come and go)
_connection_count = 0


def run_background(fn, callback, *args, **kwargs):
    """Run `fn` in the background"""
    def _callback(future):
        tornado.ioloop.IOLoop.instance().add_callback(
            lambda: callback(future.result())
        )
    future = _executor.submit(fn, *args, **kwargs)
    future.add_done_callback(_callback)


def save_message(client_id, message):
    """Save a new Message instance."""
    message = models.Message(
        content=message
    )
    message.save()  # Blocks!
    return client_id, message


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        global _connection_count
        global _clients
        _clients.append(self)
        self.id = _connection_count = _connection_count + 1
        _logger.info("WebSocket opened")

    def on_message(self, message):
        run_background(save_message, self.on_message_accepted, self.id, message)

    def on_message_accepted(self, result):
        client_id, message_instance = result
        for client in _clients:
            client.write_message("Client {} says: {}".format(str(client_id), message_instance.content))

    def on_close(self):
        _logger.info("WebSocket closed")
        _clients.remove(self)


def main():
    tornado_app = tornado.web.Application([
        ('/websocket', WebSocketHandler),
        ('.*', tornado.web.FallbackHandler,
            dict(
                fallback=tornado.wsgi.WSGIContainer(get_wsgi_application())
            )
        ),
    ], debug=True)
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
