import base64
import hashlib
import hmac
import string
import random
import requests
import time
from urllib import urlencode, quote


class TwitterApi(object):
	def __init__(self):
		self.host = 'https://api.twitter.com/1.1'
		self.consumer_key = 'KxuWAmRiIAvJq1zU0PxlxQRs3'
		self.consumer_secret = 'L29O19yNXNAFoP2A20drMzWUjlNgXAFTOeuFNknuEsFYewnUmL'
		self.token = '157319880-RziVIx4UUui1YNn1jxEGpQeM533Fm3hDsC0gD329'
		self.token_secret = 'G8iIfp7cIRcI2zLobzzTJ2pJ2BfzgeYSzEwshnnY9CWWK'

	def invoke_api(self, method, endpoint, body=None, params=None):
		if not body:
			body = {}
		if not params:
			params = {}

		method_str = method.func_name.upper()
		authorization_params = {
			'oauth_consumer_key': self.consumer_key,
		    'oauth_nonce': self._generate_nonce(),
		    'oauth_signature_method': 'HMAC-SHA1',
		    'oauth_timestamp': str(int(time.time())),
		    'oauth_token': self.token,
		    'oauth_version': '1.0'
		}

		sign_params = sorted(authorization_params.items() + params.items() + body.items())
		encoded_params = self._percent_encode_params(sign_params)
		base_url = self.host + endpoint

		signature_base_string = '&'.join([method_str, self._percent_encode(base_url), self._percent_encode(encoded_params)])

		signing_key = '{}&{}'.format(quote(self.consumer_secret), quote(self.token_secret))
		signature = quote(base64.b64encode(
			hmac.new(
				signing_key.encode('utf8'),
				signature_base_string.encode('utf8'),
				hashlib.sha1
			).digest()
		))

		authorization_params['oauth_signature'] = signature
		header = {
			'Authorization': 'OAuth {}'.format(', '.join(
				'{}="{}"'.format(k, v) for k, v in sorted(authorization_params.items())
			)),
			'User-Agent': 'OAuth gem v0.4.4',
			'Content-Type': 'application/x-www-form-urlencoded',
		}
		return method(base_url, data=body, params=params, headers=header)


	def get_keyword_tweets(self, keywords, max_id=None):
		method = 'GET'
		endpoint = '/search/tweets.json'
		params = {
			'q': ' OR '.join(keywords),
			'result_type': 'recent',
			'count': '100'
		}
                print 'q: {}'.format(keywords)
		if max_id:
			params.update({'max_id': max_id})

		return self.invoke_api(requests.get, endpoint, None, params).json()

	def _generate_nonce(self):
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))

	def _percent_encode_params(self, params):
		params.sort()
		return '&'.join('{}={}'.format(self._percent_encode(k), self._percent_encode(v)) for k, v in params)

	def _percent_encode(self, s):
		return quote(str(s), safe='')

if __name__ == '__main__':
	api = TwitterApi()
	resp = api.get_keyword_tweets(['bitcoin', '2014'])
	result = resp
	print result
