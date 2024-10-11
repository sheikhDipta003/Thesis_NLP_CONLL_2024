import nltk
from nltk.corpus import wordnet
import prepare_data

class word_senses_defn:
  senses = []
  correct_posn = -1
  definitions = []

class SenseInventory:
    def init(self, filePath='/content/WSD_Evaluation_Framework'):
        self.myd = prepare_data.load_goldkeys(filePath)
        # print(len(self.myd))

    def get_word_senses(self, word, pos, senseId):
        lex_definition = self.myd[senseId]
        # print("get_word_senses: ", word, pos, lex_definition)
        target_sense = wordnet.synset_from_sense_key(lex_definition)
        # print("target_sense:", target_sense)
        synsets = wordnet.synsets(word, pos=pos)

        d = word_senses_defn()
        d.senses = []
        d.correct_posn = -1
        d.definitions = []

        # Iterate over synsets and extract definitions
        posn = 0
        for synset in synsets:
            posn+=1
            d.senses.append(synset)
            if target_sense == synset: # match
                d.correct_posn = posn

            definition = synset.definition()
            # Append the definition to the list of word senses
            d.definitions.append(definition)

        return d


# word = 'treat'
# pos = 'v'  # 'n' for noun, 'v' for verb, 'a' for adjective, 'r' for adverb
# lex_definition = 'treat%2:29:00::'
# d = get_word_senses(word, pos, lex_definition)

# print(f"Word senses for '{word}' (POS: {pos}):")
# for i, sense in enumerate(d.senses, start=1):
    # print(f"Sense {i}: {sense}")
# print("Correct:", d.correct_posn)
# for i, sense in enumerate(d.definitions, start=1):
    # print(f"Sense {i}: {sense}")
