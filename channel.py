import pyrebase

class Channel(object):

    def add(self, fb_obj, user, name):
        db = fb_obj.database()

        data = {
            "name": name
        }

        channels = db.child("channels")
        channels.push(data, user['idToken']) 

    def get(self, fb_obj, name = None):
        db = fb_obj.database()

        if name is None:
            return db.child("channels").get()
        else:
            return db.child("channels").order_by_child("name").equal_to(name).get()


    def exists(self, fb_obj, name):
        db = fb_obj.database()

        lookup = db.child("channels").order_by_child("name").equal_to(name).get()

        try:
            lookup.val()
            return True
        except IndexError:
            return False

        
