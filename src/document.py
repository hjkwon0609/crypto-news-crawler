from dateutil.parser import parse as datetime_parse

class Document(object):
	def __init__(self, text, keywords, created_at, url):
		self.text = text
		self.keywords = keywords
		self.created_at = created_at
		self.url = url
