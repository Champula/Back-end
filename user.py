import pyrebase
import cherrypy
import json

@cherrypy.popargs('user')
class User(object):

    def __init__(self, fb):
        self.obj = None;
        self.fb = fb

    # Login: Authenticates a registered user
    # params: username, password
    @cherrypy.expose
    def login(self, username = None, password = None):
        if username is not None and password is not None:
            try:
                auth = self.fb.auth()
                self.obj = auth.sign_in_with_email_and_password(username, password)    
                ret = '{"status": true, "message": "Success"}'
                return json.dumps(json.loads(ret))
            except:
                ret = '{"status": false, "message": "Something bad happened"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message": "Missing username or password"}'
            return json.dumps(json.loads(ret))

    # User Info: Returns data associated with the authenticated user
    @cherrypy.expose
    def info(self):
        try:
            return json.dumps(self.user)
        except:
            ret = '{"status": false, "message":"Not logged in"}'
            return json.dumps(json.loads(ret))


