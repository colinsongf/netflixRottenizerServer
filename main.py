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
from models import *
import logging

class NetflixHandler(webapp2.RequestHandler):
    def get(self):
        qs = self.request.query_string
        movie = NetflixCacheObject.get_by_cache_key(qs)
        if movie:
            result = movie.result
        else:
            result = {"error": "Probably hit the rate limit, poll again"}
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

class FoursquareSearchHandler(webapp2.RequestHandler):
    def get(self):
        qs = self.request.query_string
        result = FoursquareSearchCacheObject.get_by_cache_key(qs).venue_id
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(result)

class FoursquareVenueHandler(webapp2.RequestHandler):
    def get(self):
        qs = self.request.query_string
        venue = FoursquareVenueCacheObject.get_by_cache_key(qs)
        if venue:
            result = venue.result
        else:
            result = {'error': 'something went wrong :('}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(result)    

app = webapp2.WSGIApplication([
    ('/', NetflixHandler),
    ('/netflix/?', NetflixHandler),
    ('/yelp/?', YelpHandler),
    ('/foursquare/search/?', FoursquareSearchHandler),
    ('/foursquare/venue/?', FoursquareVenueHandler),
], debug=True)
