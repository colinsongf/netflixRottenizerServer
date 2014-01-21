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
            obj = NetflixCacheObject(
                cache_key=cache_key,
                result=urlfetch.fetch(url).content.strip(),
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
