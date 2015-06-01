from collections import Counter

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from utils import ctr_len
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
        ps = content.split("\n\n")
        ps = [p for p in ps if len(p) > 0]
        return ps

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
        Uses the first sentences of paragraphs to summarize.
        Tries longer paragraphs first.
        """

        p_len = 4
        paragraphs = self.split_content_to_paragraphs(input)
        paragraphs = [self.split_content_to_sentences(p) for p in paragraphs]

        summary = []
        while len(summary) < numpoints and p_len > 0:
            ps_filtered = [p for p in paragraphs if len(p) > p_len]

            for p in ps_filtered:
                if len(summary) >= numpoints:
                    break
                # Don't add duplicates
                if p[0] not in summary:
                    summary.append(p[0])
            p_len -= 1

        return '\n\n'.join(summary)


class FirstOccurrenceSummarizer(SummarizerBase):
    def summarize(self, input, numpoints=5):
        """
        Returns n sentences as a summary, where each of the sentences is the
        first to contain one of the top n most common tokens in the text.
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
    """
    Chooses n random sentences for summary.
    """
    def summarize(self, input, numpoints=5):
        sentences = self.split_content_to_sentences(input)

        summary = []
        n = len(sentences)
        rand_ints = [random.randint(0, n-1) for i in range(numpoints)]
        for r_i in rand_ints:
            summary.append(sentences[r_i])

        return '\n\n'.join(summary)


class SigFactorSummarizer(SummarizerBase):
    """
    Ranks sentences by Luhn's significance factor.
    """
    def score(self, query_toks, doc_toks):
        if len(query_toks) == 0 or len(doc_toks) == 0:
            return 0

        result = sum([doc_toks[qt] for qt in query_toks])
        result = (result * result)/len(doc_toks)

        return result

    def summarize(self, input, numpoints=5):
        sentences = self.split_content_to_sentences(input)
        tokens = self.content_to_stemmed_tokens(input)
        sig_toks = tokens.most_common(1 + int(np.log(ctr_len(tokens))))
        sig_toks = [tup[0] for tup in sig_toks]

        scored_sentences = []
        for s in sentences:
            s_toks = self.content_to_stemmed_tokens(s)
            score = self.score(sig_toks, s_toks)
            scored_sentences.append((score, s))

        scored_sentences.sort(key=lambda tup: tup[0])
        summary = [tup[1] for tup in scored_sentences[-numpoints:]]

        return '\n\n'.join(summary)


# TODO: Add smoothing
class TFSummarizer(SummarizerBase):
    """
    Ranks sentences by term frequency.
    """
    def tf(self, term, s_toks):
        return s_toks[term]/ctr_len(s_toks)

    def score(self, query_list, doc_toks):
        if len(query_list) == 0 or len(doc_toks) == 0:
            return 0
        result = 1
        for query in query_list:
            result = result * self.tf(query, doc_toks)

        return result

    def summarize(self, input, numpoints=5):
        sentences = self.split_content_to_sentences(input)
        tokens = self.content_to_stemmed_tokens(input)

        # TODO: Which tokens do I want to query for?
        query_toks = [x[0] for x in tokens.most_common(numpoints)]
        scored_sentences = []
        for s in sentences:
            s_toks = self.content_to_stemmed_tokens(s)
            score = self.score(query_toks, s_toks)
            scored_sentences.append((score, s))

        scored_sentences.sort(key=lambda tup: tup[0])
        summary = [tup[1] for tup in scored_sentences[-numpoints:]]

        return '\n\n'.join(summary)


class TFIDFCalculator(object):
    def idf(self, tok, corpus):
        """
        log(Total # of documents/# documents with term)

        idf values are memoized for efficiency.
        """
        if not hasattr(self, 'corpus_idf'):
            self.corpus_idf = {}

        if tok not in self.corpus_idf:
            self.corpus_idf[tok] = np.log(ctr_len(corpus) /
                                          (corpus[tok]))

        return self.corpus_idf[tok]

    def tf_idf(self, term, doc, corpus):
        return self.tf(term, doc) * self.idf(term, corpus)


class TFIDFSummarizer(TFSummarizer, TFIDFCalculator):
    def score(self, query_list, doc):
        if len(query_list) == 0 or len(doc) == 0:
            return 0
        result = 0
        for query in query_list:
            result = result + self.tf_idf(query, doc, self.corpus)

        return result

    def summarize(self, input, numpoints=5):
        self.corpus = self.content_to_stemmed_tokens(input)
        return super().summarize(input, numpoints)


class TFIDFCSummarizer(TFSummarizer, TFIDFCalculator):
    def __init__(self, corpus_dir):
        super().__init__()
        self.corpus = Counter()
        for f in os.listdir(corpus_dir):
            filepath = os.path.join(corpus_dir, f)
            policy = self.read_policy(filepath)
            sentences = self.split_content_to_sentences(policy)
            sentences = [self.content_to_stemmed_tokens(s) for s in sentences]
            for s in sentences:
                self.corpus += s

    def score(self, query_list, doc):
        if len(query_list) == 0 or len(doc) == 0:
            return 0
        result = 0
        for query in query_list:
            result = result + self.tf_idf(query, doc, self.corpus)

        return result

    def summarize(self, input, numpoints=5):
        return super().summarize(input, numpoints)
