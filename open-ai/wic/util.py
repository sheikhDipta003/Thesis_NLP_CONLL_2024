import random

def prepareRandom(end_range, sample_size=40):
    # end_range: the number of lines in the training set
    # how many samples will be fetched
    start_range = 0
    rand_lines = {}
    kount = sample_size
    i=0
    while True:
      random_number = random.randint(start_range, end_range)
      if random_number in rand_lines:
        continue
      rand_lines[random_number] = random_number
      i = i+1
      # print(random_number);
      if (i==kount):
        break;

    return rand_lines;
