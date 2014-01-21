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
import webapp2
from models import NetflixCacheObject
import logging

class NetflixHandler(webapp2.RequestHandler):
    def get(self):
        qs = self.request.query_string
        result = NetflixCacheObject.get_by_cache_key(qs).result
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(result)

class YelpHandler(webapp2.RequestHandler):
    def get(self):
        qs = self.request.query_string
        result = YelpCacheObject.get_by_cache_key(qs).result
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(result)        

app = webapp2.WSGIApplication([
    ('/netflix/?', NetflixHandler)
    ('/yelp/?', YelpHandler)
], debug=True)
