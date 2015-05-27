import os
from summarize import (
    ParagraphSummarizer,
    SummarizerBase,
    RandomSummarizer,
    TFSummarizer,
    TFIDFSummarizer
)
from intersection import IntersectionSummarizer
import sys

policy_dir = 'policies'
summary_dir = 'summaries'
truth_dir = 'truths'


def verify_truths(policydir, truthdir):
    summarizer = SummarizerBase()

    for f in os.listdir(policydir):
        pol_path = os.path.join(policydir, f)
        truth_path = os.path.join(truthdir, f)
        # Make sure truth file exists
        if not os.path.exists(truth_path):
            e_str = 'Truth %s not found' % f
            raise Exception(e_str)

        try:
            policy = open(pol_path, 'r').read().strip()
            truth = open(truth_path, 'r').read().strip()
        except UnicodeDecodeError as e:
            print('%s: %s' % (f, e))
            sys.exit(1)

        p_sents = summarizer.split_content_to_sentences(policy)
        t_sents = summarizer.split_content_to_sentences(truth)

        def strip_list(l):
            return [s.strip() for s in l]

        p_sents = strip_list(p_sents)
        t_sents = strip_list(t_sents)

        if len(t_sents) != 5:
            e_str = 'Truth %s has length %d' % (f, len(t_sents))
            raise Exception(e_str)

        for t_s in t_sents:
            if t_s not in p_sents:
                e_str = 'Error with truth %s. ' % f
                e_str += 'The following not found in policy sentences.\
                          \n%s' % t_s
                raise Exception(e_str)


verify_truths(policydir=policy_dir, truthdir=truth_dir)
test_classes = [
    RandomSummarizer(),
    ParagraphSummarizer(),
    IntersectionSummarizer(),
    TFSummarizer(),
    TFIDFSummarizer(corpus_dir=policy_dir)
]

for summarizer in test_classes:
    print('Testing %s' % summarizer.__class__.__name__)
    dir_files = os.listdir(policy_dir)
    n = len(dir_files)
    recall = 0
    for i, f in enumerate(dir_files):
        print('\tProgress: %d/%d' % (i, n), end='\r')
        policy_f = open(os.path.join(policy_dir, f), 'r')
        summary = summarizer.summarize(policy_f.read())
        summary_lines = summary.split('\n')
        truth = open(os.path.join(truth_dir, f), 'r').read().strip()
        truth_lines = truth.split('\n')
        num_extracted = sum(1 for tl in truth_lines if tl in summary_lines)
        recall += num_extracted
        fout = open(os.path.join(summary_dir, f), 'w')
        fout.write(summary)

    recall /= (5*n)
    print('\tRecall: %.4f' % recall)
