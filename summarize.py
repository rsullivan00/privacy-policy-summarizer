from collections import Counter

import nltk
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

class PrivacyPolicySummarizer:

    def summarize(self, input, numpoints=5, stopw=None):
        """
        Process a string containing the text of a privacy policy, returning
        a list of important sentences.
        """

        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(input)

        if stopw is None:
            stopw = stopwords.words('english')

        stemmer = PorterStemmer()
        tokens = Counter() 
        for w in words:
            w = w.lower()
            if w not in stopw:
                stem = stemmer.stem(w)
                tokens[stem] += 1

        print(tokens.most_common(10))

        tokenizer = PunktSentenceTokenizer()
        sentences = tokenizer.tokenize(input)

        summary = []
        for t in tokens.most_common(numpoints):
            for s in sentences:
                if t[0] in s:
                    summary.append(s)
                    sentences.remove(s)
                    break

        return '\n\n---'.join(summary)
