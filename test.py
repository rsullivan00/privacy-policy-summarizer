import os
from summarize import PrivacyPolicySummarizer
from intersection import IntersectionSummarizer

policy_dir = 'policies'
summary_dir = 'summaries'

pps = PrivacyPolicySummarizer()
pps = IntersectionSummarizer()
for f in os.listdir(policy_dir):
    infile = open(os.path.join(policy_dir, f), 'r')
    print('Processing %s' % os.path.basename(f))
    summary = pps.summarize(infile.read())
    fout = open(os.path.join(summary_dir, f), 'w')
    fout.write(summary)
