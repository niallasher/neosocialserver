from socialserver import application
import pytest
from socialserver.util.output import console
from threading import Thread
from werkzeug.serving import make_server
from multiprocessing import Process
from os import environ


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


def run_tests():

    application_thread = TestingServer(application)
    application_thread.start()

    pytest.main(["socialserver"])

    application_thread.kill()

    console.log("Tests complete.")
    exit()
