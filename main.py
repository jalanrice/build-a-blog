#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("404 post not found")

class Bpost(db.Model):
    title = db.StringProperty(required = True)
    bpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Index(Handler):
    def get(self):
        self.render("base.html")

class MainHandler(Handler):
    def render_blog(self, title="", bpost="", error=""):
        bposts = db.GqlQuery("SELECT * FROM Bpost ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, bpost=bpost, error=error, bposts=bposts)

    def get(self):
        self.render_blog()


class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        bpost = self.request.get("bpost")

        if title and bpost:
            a = Bpost(title = title, bpost = bpost)
            a.put()

            self.redirect('/blog/%s' % str(a.key().id()))
        else:
            error = """We need both a title and a blog post! Express yourself!
                    People care about your thoughts. They want them properly
                    prefaced, and then to read them at length."""
            self.render("newpost.html", title=title, bpost=bpost, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        id = int(id)
        bpost = Bpost.get_by_id(id, parent=None)

        if bpost:
            self.render("singlepost.html", bpost=bpost)
        # self.response.write(id)

        else:
            self.renderError(404)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', MainHandler),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
