import cherrypy
import pyrebase
import channel
import event
import json
import user

config_path = ""

@cherrypy.popargs('dis')
class DisApi(object):
    def __init__(self):
        config = {
            "apiKey": "",
            "authDomain": "dis-test-146a0.firebaseapp.com",
            "databaseURL": "https://dis-test-146a0.firebaseio.com",
            "projectId": "dis-test-146a0",
            "storageBucket": "dis-test-146a0.appspot.com",
            "messagingSenderId": "502618154240"
        }

        self.firebase = pyrebase.initialize_app(config)
        self.user = user.User(self.firebase)
        self.event = event.Event(self.firebase, self.user)
        self.channel = channel.Channel(self.firebase, self.user)

        



cherrypy.config.update({
    #'environment': 'production',
    'log.screen': True,
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 26714,
})
cherrypy.quickstart(DisApi(), '/', config_path)
