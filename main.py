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
        self.response.write("Oops! Something went wrong.")

class Bpost(db.Model):
    title = db.StringProperty(required = True)
    bpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Index(Handler):
    def get(self):
        self.render("base.html")

class MainHandler(Handler):
    def render_blog(self, title="", bpost="", error=""):
        bposts = db.GqlQuery("SELECT * FROM Bpost ORDER BY created DESC")

        self.render("blog.html", title=title, bpost=bpost, error=error, bposts=bposts)

    def get(self):
        self.render_blog()

    def post(self):
        title = self.request.get("title")
        bpost = self.request.get("bpost")

        if title and bpost:
            a = Bpost(title = title, bpost = bpost)
            a.put()

            self.redirect("/blog")
        else:
            error = "We need both a title and a blog post! Express yourself! People care about what you think and want to read about it at length."
            self.render_blog(title, bpost, error)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', MainHandler)
], debug=True)
