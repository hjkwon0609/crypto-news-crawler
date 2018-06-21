from sklearn.feature_extraction.text import TfidfVectorizer


def get_keywords(corpus, num_keyword):
    # corpus: list of str(articles)
    # num_keyword: number of keywords to be extracted from each article 
    tfidf = TfidfVectorizer(ngram_range=(1,1), min_df = 0, analyzer='word', stop_words = 'english')
    tfidf_matrix = tfidf.fit_transform(corpus)
    feature_names = tfidf.get_feature_names()
    tfidf_dense = tfidf_matrix.todense()
    keywords = []
    # keywords is the output list of this module containing keywords-list of each article
    for idx in range(len(corpus)):
        article = tfidf_dense[idx].tolist()[0]
        phrase_scores = [pair for pair in zip(range(0, len(article)), article) if pair[1] > 0]
        sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
        keywords.append([feature_names[word_id] for (word_id, score) in sorted_phrase_scores[:num_keyword]])
    return keywords

if __name__ == '__main__':
	corpus = [
		'a, a, a, the, i dont know what to say',
		'do you know what i am saying huh?, a, a, the',
		'an iron fist will ruin you',
		'this is just a test you know',
		'does this work?, a, a, the, an'
	]
	print get_keywords(corpus, 2)
