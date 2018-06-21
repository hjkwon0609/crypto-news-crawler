from dateutil.parser import parse as datetime_parse
import re
import time

from twitter_api import TwitterApi
from document import Document

class Scorer(object):
	def __init__(self):
		self.api = TwitterApi()

	def score_document(self, doc):
		"""
		doc:
			created_at
			url
			title
			keywords
		"""
		max_id = None
		last_created_date = doc.created_at
		score = 0

		while last_created_date >= doc.created_at:
			results = self.api.get_keyword_tweets(doc.keywords, max_id)['statuses']
			print 'got {} tweets'.format(len(results))
			print 'last date', last_created_date
			
			for tweet in results:
				score += self.compute_score(doc, tweet)
				max_id = int(tweet['id'])
				last_created_date = datetime_parse(tweet['created_at'])
				if last_created_date < doc.created_at:
					return score

			if len(results) == 0:
				return score

			max_id -= 1
			time.sleep(4)  # rate limit 450 per 30 minutes 

		return score

	def compute_score(self, doc, tweet):
		"""
		score = (num keywords in text) * 
			(1 + handle_followers / 100000) * 
			(1 + favorites / 1000) * 
			(1 + retweets / 100000) * 
			(1 + 0.2 * (doc_url in tweet_urls)) *
			(1 + 0.5 * (title in tweet_text))
		"""
		tweet_text = tweet['text']
		tweet_urls = set(url['expanded_url'] for url in tweet['entities']['urls'])
		favorites = int(tweet['favorite_count'])
		retweets = int(tweet['retweet_count'])
		handle_followers = int(tweet['user']['followers_count'])

		keyword_occurrences = 0
		for word in doc.keywords:
			keyword_occurrences += len([o for o in re.finditer(word, tweet_text)])

		score = \
			(keyword_occurrences) * \
			(1 + handle_followers / 100000) * \
			(1 + favorites / 1000) * \
			(1 + retweets / 100000) * \
			(1 + 0.2 * (doc.url in tweet_urls)) * \
			(1 + 0.5 * (1 if re.finditer(doc.title, tweet['text']) else 0))

		return score

if __name__ == '__main__':
	scorer = Scorer()
	print scorer.score_document(Document(
		'test title',
		'do you know what i am saying huh?, a, a, the',
		['saying', 'know'],
		datetime_parse('Thu Jun 21 12:30:03 +0000 2018'),
		'https://www.google.com'
	))
