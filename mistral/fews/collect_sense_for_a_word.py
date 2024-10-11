import prepare_data
import util

# prepare sense dictionary
# myd = prepare_data.load_senses('fews/senses.txt')

class Senses:
  correctPosn = -1 # holds the ordinal position of the correct sense
  correctSenseId = ""
  promptText = ""
  error = False
  roman_dict = {} #contains roman letters choices sorted by length
  
class SenseInventory:
  def init(self, filePath='fews/senses.txt'):
    self.myd = prepare_data.load_senses(filePath)

    # iterates over myd dictionary to find all senses for a word
    # can expand to include all pos
  def collectWords(self, senseid):
    # some keys might not be present
    if senseid not in self.myd:
      senses = Senses()
      senses.error = False
      return senses

    spl = senseid.split(".")
    word = spl[0]
    pos = spl[1]
    sno = spl[2]
    if len(spl) != 3: # trop..adjective.0
      word = spl[0] + "."
      pos = spl[2]
      sno = spl[3]

    # print(word)
    # print(pos)
    # print(sno)

    senses = Senses()
    senses.correctSenseId = senseid

    glss = []
    # iterate by incrementing 1; bail (except?) when no more senses found in the dictionary
    i=0
    while True:
      try:
        senseNew = word + '.' + pos + '.' + str(i)
        sentry = self.myd[senseNew]
        glss.append(sentry['gloss'])
        if (senseNew == senseid):
          senses.correctPosn = i+1
      except KeyError as ke:
        # print(ke)
        break
      i+=1

    prompt = "\n"
    count = 1;
    for i in glss:
      # print(i)
      prompt += util.int_to_roman(count) + ") " + i + "\n"
      roman_ltr = util.int_to_roman(count)
      senses.roman_dict[roman_ltr] = len(roman_ltr)
      count+=1

    if len(glss) == 0:
      return None
    senses.promptText = prompt
    return senses

# si = SenseInventory
# senses = si.collectWords('dictionary.noun.2')

#senses = collectWords('trop..adjective.0')
#senses = collectWords('dictionary.noun.2')
# print(senses.promptText)
# print(senses.correctPosn)
# print(senses.correctSenseId)
# print(senses.error)


