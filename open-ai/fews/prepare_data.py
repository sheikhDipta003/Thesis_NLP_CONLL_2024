# !wget https://nlp.cs.washington.edu/fews/fews.zip
# !unzip fews.zip

# load senses from senses.txt
def load_senses(filepath):
    senses = {}
    with open(filepath, 'r') as f:
        s = {}
        for line in f:
            line = line.strip()
            if len(line) == 0:
                senses[s['sense_id']] = s
                s = {}
            else:
                line = line.strip().split(':\t')
                key = line[0]
                if len(line) > 1:
                    value = line[1]
                else:
                    key = key[:-1]
                    value = ''
                s[key] = value
    return senses


# prepare sense dictionary
# myd = load_senses('fews/senses.txt')
