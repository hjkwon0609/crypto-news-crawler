#!/usr/bin/env python2
import json
import dateutil.parser
from pprint import pprint

import tf_idf
from document import Document
from scorer import Scorer

if __name__ == '__main__':
    documents = []
    corpus = []

    with open('crawler/output/2018-06-21_18:36:39.jsonl', 'r') as f:
        for line in f.readlines():
            try:
                doc = json.loads(line)
                documents.append(doc)
                corpus.append(doc['content'])
            except:
                pass

    keywords = tf_idf.get_keywords(corpus, 3)
    for i in xrange(len(documents)):
        documents[i]['keywords'] = keywords[i]

    documents = filter(lambda d: 'title' in d, documents)

    documents = [Document(doc['title'],
                          doc['content'],
                          doc['keywords'],
                          dateutil.parser.parse(doc['date']),
                          '') for doc in documents]

    documents = sorted(documents, key=lambda d: d.created_at, reverse=True)

    scorer = Scorer()    
    for doc in documents[10:20]:
        score = scorer.score_document(doc)
        print u"""
        Title: {}
        Keywords: {}
        Score: {}
        """.format(doc.title, doc.keywords, score)
