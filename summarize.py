from collections import Counter

from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


class SummarizerBase:

    def __init__(self, stopws=None):
        self.stemmer = PorterStemmer()
        self.stopwords = stopwords.words('english')
        if stopws is not None:
            self.stopwords.extend(stopws)

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


class ParagraphSummarizer(SummarizerBase):
    def summarize(self, input, numpoints=5):
        """
        Process a string containing the text of a privacy policy, returning
        a list of important sentences.
        """

        words = self.split_content_to_tokens(input)
        words = self.filter_stopwords(words)

        tokens = Counter()
        for w in words:
            stem = self.stem(w)
            tokens[stem] += 1

        sentences = self.split_content_to_sentences(input)

        summary = []
        for t in tokens.most_common(numpoints):
            for s in sentences:
                if t[0] in s:
                    summary.append(s)
                    sentences.remove(s)
                    break

        return '\n\n'.join(summary)
