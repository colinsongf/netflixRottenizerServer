from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch
import logging

ROTTEN_TOMATOES_API_KEY = "YOUR_API_KEY_GOES_HERE"
ROTTEN_TOMATOES_API_URL = 'http://api.rottentomatoes.com/api/public/v1.0/movies.json'

class CacheObject(db.Model):
	date_created = db.DateTimeProperty(auto_now_add=True)
	date_updated = db.DateTimeProperty(auto_now=True)
	cache_key = db.StringProperty(required=True)
	result = db.TextProperty(required=True)

	@classmethod
	def get_by_cache_key(klass, cache_key):
		obj = memcache.get(cache_key)
		if not obj:
			obj = CacheObject.all().filter('cache_key =', cache_key).get()
			memcache.set(cache_key, obj)
		if not obj:
			url = '%s?apikey=%s&%s' % (ROTTEN_TOMATOES_API_URL, ROTTEN_TOMATOES_API_KEY, cache_key)
			obj = CacheObject(
				cache_key=cache_key,
				result=urlfetch.fetch(url).content.strip(),
			)
			obj.put()
			memcache.set(cache_key, obj)
		return obj