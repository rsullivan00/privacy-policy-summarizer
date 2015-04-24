import os
from summarize import PrivacyPolicySummarizer

dirname = 'policies'
pps = PrivacyPolicySummarizer()
for f in os.listdir(dirname):
    infile = open(os.path.join(dirname, f), 'r')
    print('Processing %s' % os.path.basename(f))
    ret = pps.summarize(infile.read())
    print(ret)
