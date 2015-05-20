"""
Provides a summary of multi-paragraph text
using an algorithm described at
http://thetokenizer.com/2013/04/28/build-your-own-summary-tool/

Adapted from Shlomi Babluki's code here:
https://gist.github.com/shlomibabluki/5473521
"""
from summarize import SummarizerBase
import re


class IntersectionSummarizer(SummarizerBase):
    def sentence_to_set(self, sent):
        sent = self.split_content_to_tokens(sent)
        sent = self.filter_stopwords(sent)
        sent = self.stem(sent)
        return set(sent)

    def sentences_intersection(self, s1, s2):
        # If there is not intersection, just return 0
        if (len(s1) + len(s2)) == 0:
            return 0

        # We normalize the result by the average number of words
        return len(s1.intersection(s2)) / ((len(s1) + len(s2)) / 2)

    # Format a sentence - remove all non-alphanumeric chars from the sentence
    # We'll use the formatted sentence as a key in our sentences dictionary
    def format_sentence(self, sentence):
        sentence = re.sub(r'\W+', '', sentence)
        return sentence

    # Convert the content into a dictionary <K, V>
    # k = The formatted sentence
    # V = The rank of the sentence
    def get_sentences_ranks(self, content):

        # Split the content into sentences
        sentences = self.split_content_to_sentences(content)

        # Calculate the intersection of every two sentences
        n = len(sentences)
        values = [[0 for x in range(n)] for x in range(n)]

        # Create sentence sets before intersections for speed.
        sentence_sets = [self.sentence_to_set(x) for x in sentences]
        for i in range(0, n):
            for j in range(0, n):
                values[i][j] = self.sentences_intersection(
                    sentence_sets[i],
                    sentence_sets[j]
                )

        # Build the sentences dictionary
        # The score of a sentences is the sum of all its intersection
        sentences_dic = {}
        for i in range(0, n):
            score = 0
            for j in range(0, n):
                if i == j:
                    continue
                score += values[i][j]
            sentences_dic[self.format_sentence(sentences[i])] = score
        return sentences_dic

    # Return the best sentence in a paragraph
    def get_best_sentence(self, paragraph, sentences_dic):

        # Split the paragraph into sentences
        sentences = self.split_content_to_sentences(paragraph)

        # Ignore short paragraphs
        if len(sentences) < 2:
            return ""

        # Get the best sentence according to the sentences dictionary
        best_sentence = ""
        max_value = 0
        for s in sentences:
            strip_s = self.format_sentence(s)
            if strip_s:
                if sentences_dic[strip_s] > max_value:
                    max_value = sentences_dic[strip_s]
                    best_sentence = s

        return best_sentence

    def summarize(self, input, max_length=10):

        sentences_dic = self.get_sentences_ranks(input)

        # Split the content into paragraphs.
        paragraphs = self.split_content_to_paragraphs(input)

        summary = []

        # Add the best sentence from each paragraph.
        for p in paragraphs:
            sentence = self.get_best_sentence(p, sentences_dic).strip()
            if sentence:
                summary.append(sentence)

        # If the summary is still too long, summarize the summary.
        if len(summary) > max_length:
            new_content = ''
            for i in range(max_length):
                n = int(len(summary)/max_length)
                new_content += ' '.join(summary[i*n:(i+1)*n])
                new_content += '\n\n'

            return self.summarize(new_content)

        return ("\n").join(summary)
