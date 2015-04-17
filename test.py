import nltk, nltk.stem as st
from nltk import stem
import sys
import os
from collections import Counter
import pylab

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

def plot_word_freq_dist(tokens_tuples):
    pylab.title('Token frequency')
    pylab.xlabel("Tokens")
    pylab.ylabel("Frequency")
    keys = [x[0] for x in tokens_tuples]
    values = [x[1] for x in tokens_tuples]
    print('Keys %s' % keys)
    print('Values %s' % values)
    pylab.plot(keys, values)
    pylab.show()

plot_word_freq_dist(stemmed_toks.most_common(30))
#print('Tagging tokens %s...' % tokens[:6])
#tagged = nltk.pos_tag(tokens)
#print('Chunking tagged totkens %s...' % tagged[:6])
#entities = nltk.chunk.ne_chunk(tagged)

#entities.draw()
