# Copyright 2016 Google Inc.
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

import os
import webapp2
from google.appengine.ext import db
import datetime
import jinja2
import rot13

jinja_environment = jinja2.Environment(autoescape=True,
loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class Rot13Page(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        template_values = {}
        template = jinja_environment.get_template('rot13.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        text = self.request.get("text")
        rot_text = rot13.rot_13(text)
        template_values = {"text":rot_text}

        template = jinja_environment.get_template('rot13.html')
        self.response.out.write(template.render(template_values))

## Error strings for template errors
username_error = "Not a valid username, try something else"
username_blank = "Enter a username"
password_error = "Enter a valid password"
password_blank = "Enter a password"
verification_error = "Passwords entered do not match "
email_error = "Enter a valid email address"

import re
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def valid_password(password):
    return PASS_RE.match(password)

def valid_username(username):
    return USER_RE.match(username)

def valid_email(email):
    return EMAIL_RE.match(email)

class AuthenticatorPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {}

        template = jinja_environment.get_template('authenticator.html')
        self.response.out.write(template.render(template_values))
    def post(self):
        # Username validation
        template_values = {}
        try:
            username = self.request.get("username")
            if not (username and valid_username(username)):
                template_values['username_error'] = username_error
        except:
            template_values['username_error'] = username_blank

        # Password validation
        try:
            password = self.request.get("password")
            verify = self.request.get("verify")
            if not (password and valid_password(password)):
                template_values['password_error'] = password_error
            elif password != verify:
                template_values['verification_error'] = verification_error
        except:
            template_values['password_error'] = password_blank

        ## Email validation
        email = self.request.get("email")
        if email:
            if not valid_email(email):
                template_values['email_error'] = email_error

        if template_values:
            template = jinja_environment.get_template('authenticator.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/authenticator/success?name="+username)

class AuthenticationSuccessPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        name = self.request.get("name")
        template_values = {"name":name}
        template = jinja_environment.get_template('authenticationSuccess.html')
        self.response.out.write(template.render(template_values))

##Blog post database
class BlogPosts(db.Model):
    subject = db.StringProperty()
    content = db.TextProperty()
    date_created = db.DateTimeProperty(auto_now_add= True)

class BlogPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        q = BlogPosts.all()
        q.order('-date_created')
        template_values = {"data":q}
        template = jinja_environment.get_template('blog.html')
        self.response.out.write(template.render(template_values))

class PostPage(webapp2.RequestHandler):
    def get(self, id):
        self.response.headers['Content-Type'] = 'text/html'
        id = int(id)
        post = BlogPosts.get_by_id(id)
        # q.order('-date_created')
        template_values = {"data":post}
        template = jinja_environment.get_template('blogpost.html')
        self.response.out.write(template.render(template_values))


class BlogNewPostPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {}
        template = jinja_environment.get_template('newpost.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        template_values = {}
        subject = self.request.get("subject")
        content = self.request.get("content")
        # Handles errors messages
        if not subject and not content:
            template_values['error'] = "You need to enter some data for a blog post :p"
        elif not content:
            template_values['error'] = "You need to enter some content"
            template_values['subject'] = subject
        elif not subject:
            template_values['error'] = "You need to enter a subject"
            template_values["content"] = content

        if template_values:
            template = jinja_environment.get_template('newpost.html')
            self.response.out.write(template.render(template_values))
        else:
            post = BlogPosts(subject=subject, content=content)
            post_id = post.put().id()
            # print key.id()
            self.redirect('/blog/'+str(post_id))

app = webapp2.WSGIApplication([
    ('/rot13', Rot13Page), ('/authenticator', AuthenticatorPage),
    ('/authenticator/success', AuthenticationSuccessPage),
    ('/blog', BlogPage), ('/blog/newpost', BlogNewPostPage),
    (r'/blog/(\d+)', PostPage),
], debug=True)
