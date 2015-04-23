import nltk, nltk.stem as st
import sys
import os
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

dirname = 'policies'
#stemmer = nltk.stem.WordNetLemmatizer()
stemmer = st.PorterStemmer()
stemmed_toks = Counter()

for f in os.listdir(dirname):
    infile = open(os.path.join(dirname, f), 'r')
    print('Processing %s' % os.path.basename(f))
    tokens = nltk.tokenize.word_tokenize(infile.read())
    for t in tokens:
        #stem = stemmer.lemmatize(t.lower())
        stem = stemmer.stem(t.lower())
        stemmed_toks[stem] += 1

blacklist = [',', '.', 'to', 'and', 'the', '(', ')', ':']
for w in blacklist:
    if stemmed_toks[w]:
        del stemmed_toks[w]

print(stemmed_toks.most_common(30))

def plot_word_freq_dist(tokens_tuples, log=False):
    plt.title('Tokens vs. frequency')
    plt.xlabel("Tokens")
    plt.ylabel("Frequency")
    keys = [x[0] for x in tokens_tuples]
    values = [x[1] for x in tokens_tuples]
    ind = np.arange(len(keys))
    plt.xticks(ind, keys, rotation='vertical')
    print('Keys %s' % keys)
    print('Values %s' % values)
    plt.bar(ind, values, log=log)
    plt.show()

plot_word_freq_dist(stemmed_toks.most_common(30))
plot_word_freq_dist(stemmed_toks.most_common(30), True)
#print('Tagging tokens %s...' % tokens[:6])
#tagged = nltk.pos_tag(tokens)
#print('Chunking tagged totkens %s...' % tagged[:6])
#entities = nltk.chunk.ne_chunk(tagged)

#entities.draw()
