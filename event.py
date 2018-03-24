import cherrypy
import pyrebase
import json
import user

@cherrypy.popargs('event')
class Event(object):
    def __init__(self, fb, usr):
        self.fb = fb
        self.user = usr

    @cherrypy.expose
    def add(self, name = None, event_type = None, link = None, desc = None, tags = None):
        if name is not None and event_type is not None:
            if self.user.obj is not None:

                # Handle tags
                if tags is not None:
                    tags = tags.split(',')
                else:
                    tags = []

                db = self.fb.database()
                
                data = {
                    "name": name,
                    "event_type": event_type,
                    "user": self.user.obj['localId'],
                    "link": link,
                    "tags": tags,
                    "description": desc
                }

                events = db.child("events")
                events.push(data, self.user.obj['idToken'])

                ret = '{"status": true, "message": "Event created"}'
                return json.dumps(json.loads(ret))
            else:
                ret = '{"status": false, "message":"Not logged in"}'
                return json.dumps(json.loads(ret))
        else:
            ret = '{"status": false, "message":"Missing required fields"}'
            return json.dumps(json.loads(ret))


    @cherrypy.expose
    def get(self, event_id = None, channel = None, tag = None):
        if event_id is not None:
            if self.exist(event_id):
                db = self.fb.database()

                data = db.child("events").order_by_key().equal_to(event_id).get()
                return json.dumps(data.val())
            else:
                ret = '{"status": false, "message": "Event not found"}'
                return json.dumps(json.loads(ret))
        if tag is not None:
            db = self.fb.database()

            results = {}
            
            all_events = db.child("events").get()

            for ev in all_events.each():
                try:
                    if tag in ev.val()['tags']:
                        results[ev.key()] = ev.val()
                except KeyError:
                    pass 
            try:
                return json.dumps(results)
            except IndexError:
                ret = '{"status": false, "message": "No events found"}'
                return json.dumps(json.loads(ret))
        # TODO Get events by channel
        if channel is not None:
            ret = '{"status": false, "message": "Not yet implemented"}'
            return json.dumps(json.loads(ret))
        else:
            try:
                db = self.fb.database()
                data = db.child("events").get()
                return json.dumps(data.val())
            except:
                ret = '{"status": false, "message": "Unable to fetch events"}'
                return json.dumps(json.loads(ret))


    def exist(self, event_id):
        if event_id is not None:
            db = self.fb.database()

            lookup = db.child("events").order_by_key().equal_to(event_id).get()

            try:
                lookup.val()
                return True
            except IndexError:
                return False
        else:
            return False 

