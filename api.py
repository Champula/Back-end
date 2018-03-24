import cherrypy
import pyrebase
import channel
import json

config_path = ""

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
        self.user = None

        
    # Login: Authenticates a registered user
    # params: email, password
    @cherrypy.expose
    def login(self, email = None, password = None):
        if email is not None and password is not None:
            try:
                auth = self.firebase.auth()
                self.user = auth.sign_in_with_email_and_password(email, password)    
            except:
                ret = '{"status": false, "message": "Something bad happened"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message": "Missing username or password"}'
            return json.dumps(json.loads(ret))

    # User Info: Returns data associated with the authenticated user
    @cherrypy.expose
    def user_info(self):
        try:
            return json.dumps(self.user)
        except:
            ret = '{"status": false, "message":"Not logged in"}'
            return json.dumps(json.loads(ret))



    # Channel: handle channels
    # func: add, get, exist
    # params: Additional params
    @cherrypy.expose
    def channel(self, func = None, *params):
        ch = channel.Channel()

        if func == "add":
            if len(params) == 1:
                if self.user is not None:
                    if ch.exists(self.firebase, params[0]):
                        ret = '{"status": false, "message":"Channel already exists"}'
                        return json.dumps(json.loads(ret))
                    else:
                        ch.add(self.firebase, self.user, params[0])
                        ch.get(self.firebase, params[0])
                        ret = '{"status": true, "message": "Channel created"}'
                        return json.dumps(json.loads(ret))
                else:
                    ret = '{"status": false, "message":"Not logged in"}'
                    return json.dumps(json.loads(ret))
            else:
                ret = '{"status": false, "message":"Wrong number of parameters"}'
                return json.dumps(json.loads(ret))
        elif func == "get":
            if len(params) > 0:
                if ch.exists(self.firebase, params[0]):
                    data = ch.get(self.firebase, params[0]).val()
                    return json.dumps(data)
                else:
                    ret = '{"status": false, "message": "Channel not found"}'
                    return json.dumps(json.loads(ret))
            else:
                try:
                    data = ch.get(self.firebase).val()
                    return json.dumps(data)
                except:
                    ret = '{"status": false, "message": "Unable to fetch channels"}'
                    return json.dumps(json.loads(ret))
        elif func == "exist":
            if len(params) == 1:
                exist = ch.exists(self.firebase, params[0])
                ret = '{"status": '
                if exist:
                    ret += 'true'
                else:
                    ret += 'false'
                ret += '}' 
                return json.dumps(json.loads(ret))
            else:
                ret = '{"status": false, "message":"Wrong number of parameters"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message": "No such function for channel"}'
            return json.dumps(json.loads(ret))
    
cherrypy.config.update({
    #'environment': 'production',
    'log.screen': True,
    'server.socket_host': '127.0.0.1',
    'server.socket_port': 26714,
})
cherrypy.quickstart(DisApi(), '/', config_path)
