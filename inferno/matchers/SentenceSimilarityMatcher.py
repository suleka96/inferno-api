import nltk
from py_stringmatching import MongeElkan
from pywsd.lesk import simple_lesk
import numpy as np

from inferno.preprocessors.SpacyNluAnnotator import SpacyNluAnnotator


class SentenceSimilarityMatcher:

    def __init__(self):
        print("Initializing INFERNO Knowledge-based Sentence Similarity Matcher...")
        self.me = MongeElkan()

    def compute_string_based_similarity(self, sentence1, sentence2):
        sent1_tokens = SpacyNluAnnotator(sentence1).extract_tokens()
        sent2_tokens = SpacyNluAnnotator(sentence2).extract_tokens()
        return self.me.get_raw_score(sent1_tokens, sent2_tokens)

    def extract_nouns_and_verbs(self, sentence):
        """
            Extracting nouns and verbs for word-based comparison
        """
        # Tokenize sentence
        tokens = nltk.word_tokenize(sentence)
        # Extract POS tags from tokens
        pos_tags = nltk.pos_tag(tokens)
        # Filter tags that are nouns and verbs
        pos_tags = [tag for tag in pos_tags if tag[1].startswith('N') or tag[1].startswith('V')]
        return pos_tags

    def disambiguate_word_senses(self, sentence):
        """
            Disambiguating word senses for nouns and verbs using the LESK algorithm
        """
        # Extract nouns and verbs
        pos_tags = self.extract_nouns_and_verbs(sentence)
        sense = []
        for tag in pos_tags:
            # Fetch correct synset for each tag based on surrounding context
            disambiguated_term = simple_lesk(sentence, tag[0], pos=tag[1][0].lower())
            if disambiguated_term is not None:
                sense.append(disambiguated_term)
        return set(sense)

    def calculate_similarity(self, sense_array_1, sense_array_2):
        """
            Generate similarity indexes and vectors
        """
        # List of highest synset similarities for 2 sentences
        similarity_vector = []
        for i, synset_1 in enumerate(sense_array_1):
            similarity_indexes = []
            for synset_2 in sense_array_2:
                # Wu-Palmer similarity is used to calculate the similarity between synsets from each sentence
                # This method is based on the depth of the synsets in the WordNet taxonomy and their common ancestor
                similarity = wn.wup_similarity(synset_1, synset_2)
                if similarity is not None:
                    similarity_indexes.append(similarity)
                else:
                    similarity_indexes.append(0.0)
            # Sort similarity indexes in descending order
            similarity_indexes = sorted(similarity_indexes, reverse=True)
            # Get index with highest similarity
            similarity_vector.append(similarity_indexes[0])

        average_similarity = sum(similarity_vector)/len(similarity_vector)
        return average_similarity

    def match_and_fetch_score(self, input_sentences, generated_sentences):
        """
            Execute sentence similarity matcher
        """
        similarity_scores = []
        input_sentence_senses = []
        generated_sentence_senses = []
        for input_sentence in input_sentences:
            input_sentence_sense = self.disambiguate_word_senses(input_sentence)
            input_sentence_senses.append({
                'sentence': input_sentence,
                'sense': input_sentence_sense
            })
        for generated_sentence in generated_sentences:
            generated_sentence_sense = self.disambiguate_word_senses(generated_sentence)
            generated_sentence_senses.append({
                'sentence': generated_sentence,
                'sense': generated_sentence_sense
            })

        # Calculate similarity
        for generated_sense in generated_sentence_senses:
            for input_sense in input_sentence_senses:
                # Compute string-based similarity
                string_similarity_score = self.compute_string_based_similarity(input_sense['sentence'],
                                                                               generated_sense['sentence'])
                print("*" * 80)
                print("Monge-Elkan Score for \"" + input_sense['sentence'] + "\" & \"" +
                      generated_sense['sentence'] + "\": " + str(string_similarity_score))

                # Compute knowledge-based similarity
                knowledge_based_similarity_score = self.calculate_similarity(input_sense['sense'], generated_sense['sense'])
                print("Wu-Palmer Score for \"" + input_sense['sentence'] + "\" & \"" +
                      generated_sense['sentence'] + "\": " + str(knowledge_based_similarity_score))
                print("*" * 80)

                similarity_scores.append({
                    "generated": generated_sense['sentence'],
                    "kb_score": knowledge_based_similarity_score,
                    "me_score": string_similarity_score
                })

        return similarity_scores
