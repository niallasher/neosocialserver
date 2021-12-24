from os import rmdir, remove, path
from socialserver.util.output import console
from socialserver import application
from werkzeug.serving import make_server
from threading import Thread


class TestingServer(Thread):

    def __init__(self, application_object):
        Thread.__init__(self)
        self.server = make_server("127.0.0.1",
                                  9801,
                                  application_object)
        self.ctx = application_object.app_context()
        self.ctx.push()

    def run(self):
        console.log("Starting test server.")
        self.server.serve_forever()

    def kill(self):
        console.log("Killing test server.")
        self.server.shutdown()


def pytest_sessionstart():
    # start a copy of the flask server in a background
    # thread, so we can test against it.
    application_thread.start()
    pass


def pytest_sessionfinish():
    application_thread.kill()
    remove('/tmp/test.db')
    if path.exists('/tmp/socialserver_testing'):
        remove('/tmp/socialserver_testing/config.toml')
        # we should probably use this for testing in the future,
        # but right now it relies on SOCIALSERVER_ROOT being set before
        # execution.
        remove('/tmp/socialserver_testing/socialserver.db')
        rmdir('/tmp/socialserver_testing')


application_thread = TestingServer(application)
