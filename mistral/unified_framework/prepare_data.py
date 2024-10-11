# read the gold-keys
stopat = -1

myd = {}

def load_goldkeys(gold_key_path):
  gfile = gold_key_path
  file = open(gfile, 'r')
  lines = file.readlines()
  count = 0;
  for line in lines:
    # print(line)
    try:
      spl = line.split(" ")
      did = spl[0]
      senseid = spl[1]
      myd[did] = senseid.strip()
      count += 1
    except Exception as e:
      if count < 226037: # the last line is empty
        print(e)
      continue
    if count == stopat:
      break;
    count+=1
  return myd
# load_goldkeys("/content/WSD_Evaluation_Framework/Evaluation_Datasets/semeval2013/semeval2013.gold.key.txt")


# print(myd['d000.s008.t001'])
