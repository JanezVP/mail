#!/usr/bin/env python
import os
import jinja2
import webapp2
import json
import random

from models import Sporocilo

from google.appengine.api import users

from google.appengine.api import urlfetch

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            logout_url = users.create_logout_url("/")
            params = {"user": user, "logout_url": logout_url}
            return self.render_template("hello.html", params=params)
        else:
            return self.redirect_to("login")

class OsnovnaStran(BaseHandler):
    def get(self):
        return self.render_template("base.html")


class RezultatHandler(BaseHandler):
    def post(self):

        user = users.get_current_user()

        if user:

            besedilo = self.request.get("sporocilo")

            ime = user.nickname()

            prejemnik = self.request.get("email")

            posiljatelj = self.request.get("email")

            sporocilo = Sporocilo(besedilo_sporocila=besedilo,
                              avtor=ime, prejemnik=prejemnik, posiljatelj=posiljatelj)

            sporocilo.put()

            return self.render_template("rezultat.html")

        else:
            return self.redirect_to("login")


class PrejetoHandler(BaseHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            sporocila = Sporocilo.query(Sporocilo.prejemnik == user.email()).fetch()

            params = {"sporocila": sporocila}

            return self.render_template("prejeto.html", params=params)
        else:
            return self.rediret_to("login")

class PoslanoHandler(BaseHandler):
    def get(self):

        user = users.get_current_user()

        if user:

            sporocila = Sporocilo.query(Sporocilo.posiljatelj == user.email()).fetch()

            params = {"sporocila": sporocila}

            return self.render_template("poslano.html", params=params)
        else:
            return self.rediret_to("login")



class SporocilaHandler(BaseHandler):
    def get(self):

        sporocila = Sporocilo.query(Sporocilo.je_izbrisano == False).fetch()

        params = {"sporocila": sporocila}

        return self.render_template("vsa_sporocila.html",
                             params=params)

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):

        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}

        return self.render_template("posamezno_sporocilo.html",
                                    params=params)



class EditHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("uredi_sporocilo.html",
                                    params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        sporocilo.besedilo_sporocila = self.request.get("text-sporocila")
        sporocilo.avtor = self.request.get("ime")

        sporocilo.put()

        return self.redirect_to("seznam-sporocil")

class DeleteHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))
        params = {"sporocilo": sporocilo}
        return self.render_template("izbrisi.html",
                                    params=params)

    def post(self, sporocilo_id):
        sporocilo = Sporocilo.get_by_id(int(sporocilo_id))

        sporocilo.je_izbrisano = True

        sporocilo.put()

        return self.redirect_to("seznam-sporocil")

class LoginHandler(BaseHandler):
    def get(self):
        login_url = users.create_login_url("/")

        params = {"login_url": login_url}
        return self.render_template("login.html", params=params)


class VremeHandler(BaseHandler):
    def get(self):

        mesto = "Medvode"

        url = "http://api.openweathermap.org/data/2.5/weather?q={ime_mesta}&units=metric&appid=9dd7b0a4edb5382122b6d3db4413c133".format(ime_mesta=mesto)
        result = urlfetch.fetch(url)

        json_data = json.loads(result.content)

        params = {"vreme": json_data}

        return self.render_template("vreme.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route("/login", LoginHandler, name="login"),
    webapp2.Route('/rezultat', RezultatHandler),
    webapp2.Route('/mywebsite.html', OsnovnaStran),
    webapp2.Route('/prejeto', PrejetoHandler),
    webapp2.Route('/poslano', PoslanoHandler),
    webapp2.Route('/vsa_sporocila', SporocilaHandler, name="seznam-sporocil"),
    webapp2.Route('/sporocila/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocila/<sporocilo_id:\d+>/edit', EditHandler),
    webapp2.Route('/vreme', VremeHandler),
    webapp2.Route('/sporocila/<sporocilo_id:\d+>/delete', DeleteHandler)
], debug=True)
