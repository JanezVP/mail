from google.appengine.ext import ndb


class Sporocilo(ndb.Model):
    besedilo_sporocila = ndb.StringProperty()
    avtor = ndb.StringProperty()
    prejemnik = ndb.StringProperty()
    posiljatelj = ndb.StringProperty()
    poslano = ndb.DateTimeProperty(auto_now_add=True)
    je_izbrisano = ndb.BooleanProperty(default=False)