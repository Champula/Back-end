import cherrypy
import user
import pyrebase
import json

@cherrypy.popargs('channel')
class Channel(object):
    def __init__(self, fb, usr):
        self.fb = fb
        self.user = usr

    # Channel: handle channels
    # func: add, get, exist
    # params: Additional params
    @cherrypy.expose
    def add(self, name = None):
        if name is not None:
            if self.user.obj is not None:
                if self.exist(name):
                    ret = '{"status": false, "message":"Channel already exists"}'
                    return json.dumps(json.loads(ret))
                else:
                    db = self.fb.database()

                    data = {
                        "name": name
                    }

                    channels = db.child("channels")
                    channels.push(data, self.user.obj['idToken'])

                    ret = '{"status": true, "message": "Channel created"}'
                    return json.dumps(json.loads(ret))
            else:
                ret = '{"status": false, "message":"Not logged in"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message":"Wrong number of parameters"}'
            return json.dumps(json.loads(ret))


    @cherrypy.expose
    def get(self, name = None):
        if name is not None:
            if self.exist(name):
                db = self.fb.database()
                data = db.child("channels").order_by_child("name").equal_to(name).get()
                return json.dumps(data.val())
            else:
                ret = '{"status": false, "message": "Channel not found"}'
                return json.dumps(json.loads(ret))
        else:
            try:
                db = self.fb.database()
                data = db.child("channels").get()
                return json.dumps(data.val())
            except:
                ret = '{"status": false, "message": "Unable to fetch channels"}'
                return json.dumps(json.loads(ret))

    def exist(self, name = None):
        if name is not None:
            db = self.fb.database()

            lookup = db.child("channels").order_by_child("name").equal_to(name).get()

            try:
                lookup.val()
                return True
            except IndexError:
                return False
        else:
            return False

       
