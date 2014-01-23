from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch

import json
import oauth2 as oauth
import optparse
import urllib
import urllib2
import logging

ROTTEN_TOMATOES_API_KEY = "uhzgyvqdx58cytaqsjdzgpq2"
ROTTEN_TOMATOES_API_URL = 'http://api.rottentomatoes.com/api/public/v1.0/movies.json'

YELP_CONSUMER_KEY = "xBWEtNhGsOkpL7MoiyUOkQ"
YELP_CONSUMER_SECRET = "uzGP6Nb_1Gj1fDu8IkdRtXpohMc"
YELP_TOKEN = "hlhGRCZ-iZ7JdnKOQy77SlWi6rvlrcWr"
YELP_TOKEN_SECRET = "gUMxvGAfbVgyF2rq1pEkXSGsGHg"
YELP_API_URL = "http://api.yelp.com/v2/search/"

FOURSQUARE_CLIENT_ID = "5WOKV1QPMOQFBQFX0EUCYWNRSHMXTB2ZOF3HML4TZHJHTORE"
FOURSQUARE_CLIENT_SECRET = "KO0SGYHUTB3SANZUK0F1WUZTLYT01414MK4LGHHFTGXTBHJP"
FOURSQUARE_SEARCH_API_URL = "https://api.foursquare.com/v2/venues/search"
FOURSQUARE_VENUE_API_URL = "https://api.foursquare.com/v2/venues/"

class NetflixCacheObject(db.Model):
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_updated = db.DateTimeProperty(auto_now=True)
    cache_key = db.StringProperty(required=True)
    result = db.TextProperty(required=True)

    @classmethod
    def get_by_cache_key(klass, cache_key):
        obj = memcache.get(cache_key)
        
        # not in memcache, so check database
        if not obj:
            obj = NetflixCacheObject.all().filter('cache_key =', cache_key).get()
            memcache.set(cache_key, obj)
        
        # not in db, so hit rotten tomatoes api
        if not obj:
            url = '%s?apikey=%s&%s' % (ROTTEN_TOMATOES_API_URL, ROTTEN_TOMATOES_API_KEY, cache_key)
            
            result = urlfetch.fetch(url).content.strip()
            json_result = json.loads(result)

            if not 'error' in json_result:
                obj = NetflixCacheObject(
                    cache_key=cache_key,
                    result=result,
                )
                obj.put()
                memcache.set(cache_key, obj)
        return obj

class YelpCacheObject(db.Model):
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_updated = db.DateTimeProperty(auto_now=True)
    cache_key = db.StringProperty(required=True)
    result = db.TextProperty(required=True)

    @classmethod
    def get_by_cache_key(klass, search_term):
        obj = memcache.get(search_term)
        
        # not in memcache, so check database and set memcache
        if not obj:
            obj = YelpCacheObject.all().filter('cache_key =', search_term).get()
            memcache.set(search_term, obj)
        
        # not in db, so hit yelp's api and put in db and memcache
        if not obj:
            url = '%s?%s' % (YELP_API_URL, search_term)

            # Sign the URL
            consumer = oauth.Consumer(YELP_CONSUMER_KEY, YELP_CONSUMER_SECRET)
            oauth_request = oauth.Request('GET', url, {})
            oauth_request.update({
                'oauth_nonce': oauth.generate_nonce(),
                'oauth_timestamp': oauth.generate_timestamp(),
                'oauth_token': YELP_TOKEN,
                'oauth_consumer_key': YELP_CONSUMER_KEY
            })

            token = oauth.Token(YELP_TOKEN, YELP_TOKEN_SECRET)
            oauth_request.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
            signed_url = oauth_request.to_url()
            
            obj = YelpCacheObject(
                cache_key=search_term,
                result=urlfetch.fetch(signed_url).content.strip(),
            )
            obj.put()
            memcache.set(search_term, obj)
        return obj

class FoursquareSearchCacheObject(db.Model):
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_updated = db.DateTimeProperty(auto_now=True)
    cache_key = db.StringProperty(required=True)
    venue_id = db.TextProperty(required=True)

    @classmethod
    def get_by_cache_key(klass, search_term):
        obj = memcache.get(search_term)
        
        # not in memcache, so check database and set memcache
        if not obj:
            obj = FoursquareSearchCacheObject.all().filter('cache_key =', search_term).get()
            memcache.set(search_term, obj)
        
        # not in db, so hit yelp's api and put in db and memcache
        if not obj:
            url = '%s?client_id=%s&client_secret=%s&%s' % (FOURSQUARE_SEARCH_API_URL, FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET, search_term)
            response = urlfetch.fetch(url).content.strip()
            json_response = json.loads(response)

            # get venue id
            venue_id = json.dumps(json_response['response']['groups'][0]['items'][0]['id'])
            # venue_id = str(venue_id.replace('"', ''))

            obj = FoursquareSearchCacheObject(
                cache_key=search_term,
                venue_id=venue_id
            )
            obj.put()
            memcache.set(search_term, obj)
        return obj

class FoursquareVenueCacheObject(db.Model):
    date_created = db.DateTimeProperty(auto_now_add=True)
    date_updated = db.DateTimeProperty(auto_now=True)
    cache_key = db.StringProperty(required=True)
    result = db.TextProperty(required=True)

    @classmethod
    def get_by_cache_key(klass, search_term):
        obj = memcache.get(search_term)
        
        # not in memcache, so check database and set memcache
        if not obj:
            obj = FoursquareVenueCacheObject.all().filter('cache_key =', search_term).get()
            memcache.set(search_term, obj)
        
        # not in db, so hit yelp's api and put in db and memcache
        if not obj:
            url = '%s%s?client_id=%s&client_secret=%s' % (FOURSQUARE_VENUE_API_URL, search_term, FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET )
            response = urlfetch.fetch(url).content.strip()
            response = json.loads(response)
            response = json.dumps(response)

            obj = FoursquareVenueCacheObject(
                cache_key=search_term,
                result=response
            )
            obj.put()
            memcache.set(search_term, obj)
        return obj













