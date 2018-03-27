import pyrebase
import cherrypy
import json

@cherrypy.popargs('user')
class User(object):

    def __init__(self, fb):
        self.obj = None;
        self.fb = fb

    # Login: Authenticates a registered user
    # params: email, password
    @cherrypy.expose
    def login(self, email = None, password = None):
        if email is not None and password is not None:
            try:
                auth = self.fb.auth()
                self.obj = auth.sign_in_with_email_and_password(email, password)    
                ret = '{"status": true, "message": "Success"}'
                return json.dumps(json.loads(ret))
            except:
                ret = '{"status": false, "message": "Something bad happened"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message": "Missing email or password"}'
            return json.dumps(json.loads(ret))

    # Create: Creates a user
    @cherrypy.expose
    def create(self, email = None, password = None):
        if email is not None and password is not None:
            try:
                auth = self.fb.auth()
                auth.create_user_with_email_and_password(email, password)
                auth.sign_in_with_email_and_password(email, password)
                ret = '{"status": true, "message": "Success"}'
                return json.dumps(json.loads(ret))
            except:
                ret = '{"status": false, "message": "Something bad happened"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message": "Missing email or password"}'
            return json.dumps(json.loads(ret))

    # User Info: Returns data associated with the authenticated user
    @cherrypy.expose
    def info(self):
        try:
            return json.dumps(self.user)
        except:
            ret = '{"status": false, "message":"Not logged in"}'
            return json.dumps(json.loads(ret))


