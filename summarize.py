from collections import Counter

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import random
import numpy as np
import os


class SummarizerBase(object):
    def __init__(self, stopws=None):
        self.stemmer = PorterStemmer()
        self.stopwords = stopwords.words('english')
        if stopws is not None:
            self.stopwords.extend(stopws)

    def read_policy(self, filepath):
        return open(filepath).read().strip()

    def stem(self, content):
        if isinstance(content, str):
            return self.stemmer.stem(content)
        elif isinstance(content, list):
            return [self.stem(x) for x in content]

        raise ValueError('Stemming failed with %s' % content)

    def split_content_to_sentences(self, content):
        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set([
            'dr', 'vs', 'mr', 'mrs', 'prof', 'inc', 'e.g', 'i.e'])

        # Use built in sentence splitter.
        tokenizer = PunktSentenceTokenizer(punkt_param)
        tokens = tokenizer.tokenize(content)
        sentences = []
        # Make sure sentences don't include multiple lines.
        for t in tokens:
            t_split = t.split('\n')
            for t_s in t_split:
                sentences.append(t_s)
        return sentences

    # Naively split paragraphs.
    def split_content_to_paragraphs(self, content):
        return content.split("\n\n")

    def split_content_to_tokens(self, content):
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(content)
        return tokens

    def filter_stopwords(self, wordlist):
        return list(filter(
            lambda x: x.lower() not in self.stopwords, wordlist))

    def content_to_stemmed_tokens(self, content):
        words = self.split_content_to_tokens(content)
        words = self.filter_stopwords(words)

        tokens = Counter()
        for w in words:
            stem = self.stem(w)
            tokens[stem] += 1

        return tokens


class ParagraphSummarizer(SummarizerBase):
    def summarize(self, input, numpoints=5):
        """
        Process a string containing the text of a privacy policy, returning
        a list of important sentences.
        """

        tokens = self.content_to_stemmed_tokens(input)
        sentences = self.split_content_to_sentences(input)

        summary = []
        for t in tokens.most_common(numpoints):
            for s in sentences:
                if t[0] in s:
                    summary.append(s)
                    sentences.remove(s)
                    break

        return '\n\n'.join(summary)


class RandomSummarizer(SummarizerBase):
    def summarize(self, input, numpoints=5):
        """
        Process a string containing the text of a privacy policy, returning
        a list of important sentences.
        """

        sentences = self.split_content_to_sentences(input)

        summary = []
        n = len(sentences)
        rand_ints = [random.randint(0, n-1) for i in range(numpoints)]
        for r_i in rand_ints:
            summary.append(sentences[r_i])

        return '\n\n'.join(summary)


class TFSummarizer(SummarizerBase):
    def tf(self, term, s):
        return s.count(term)/len(s)

    def score(self, query_list, doc):
        if len(query_list) == 0 or len(doc) == 0:
            return 0
        result = 1
        for query in query_list:
            result = result * self.tf(query, doc)

        return result

    def summarize(self, input, numpoints=5):
        """
        Process a string containing the text of a privacy policy, returning
        a list of important sentences.
        """

        sentences = self.split_content_to_sentences(input)
        tokens = self.content_to_stemmed_tokens(input)

        # TODO: Which tokens do I want to query for?
        query_toks = [x[0] for x in tokens.most_common(numpoints)]
        scored_sentences = []
        for s in sentences:
            score = self.score(query_toks, s)
            scored_sentences.append((score, s))

        scored_sentences.sort(key=lambda tup: tup[0])
        summary = [tup[1] for tup in scored_sentences[-numpoints:]]

        return '\n\n'.join(summary)


class TFIDFSummarizer(TFSummarizer):
    def __init__(self, corpus_dir):
        super().__init__()
        self.corpus = []
        for f in os.listdir(corpus_dir):
            filepath = os.path.join(corpus_dir, f)
            policy = self.read_policy(filepath)
            sentences = self.split_content_to_sentences(policy)
            sentences = [self.content_to_stemmed_tokens(s) for s in sentences]
            self.corpus.extend(sentences)

    def idf(self, term, corpus):
        """
        log(Total # of documents/# documents with term)
        """
        # TODO: Need to memoize this information
        return np.log(len(corpus)/(1 + len(
            [1 for doc in corpus if term in doc])))

    def tf_idf(self, term, doc, corpus):
        # print(self.tf(term, doc), self.idf(term, corpus))
        return self.tf(term, doc) * self.idf(term, corpus)

    def score(self, query_list, doc):
        if len(query_list) == 0 or len(doc) == 0:
            return 0
        result = 0
        for query in query_list:
            result = result + self.tf_idf(query, doc, self.corpus)

        return result

    def summarize(self, input, numpoints=5):
        # self.corpus = self.content_to_stemmed_tokens(input)
        return super().summarize(input, numpoints)
