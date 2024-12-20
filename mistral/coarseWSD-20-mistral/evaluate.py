import prepare_mistral_api
import json
import time
import random
import argparse
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import util
from tqdm import tqdm


sleepBetween = 1.5 # pause these many seconds between two requests

def get_word_classes(word, setname='CoarseWSD-20'):
    with open('/content/master/data/%s/%s/classes_map.txt' % (setname, word)) as classes_json_f:
        word_classes = json.load(classes_json_f)
    return word_classes


def load_instances_my(word, split, setname='CoarseWSD-20', mode='regular'):
    sense_sentencesM = {} # map containing <senseKey, sentence>
    m = sense_sentencesM
    instances = []
    word_classes = get_word_classes(word, setname)
    count = 0;
    with open('/content/master/data/%s/%s/%s.data.txt' % (setname, word, split)) as split_data_f \
      , open('/content/master/data/%s/%s/%s.gold.txt' % (setname, word, split)) as split_gold_f:
      for line1, line2 in zip(split_data_f, split_gold_f):
        word_idx, tokens = line1.split('\t')

        k = line2.strip()
        if k not in m:
          sens = []
          m[k] = sens

        m[k].append(tokens)

        count += 1
    return sense_sentencesM


def test_word(word, api_key,model=None, setname='CoarseWSD-20', split='test'):
    global _attempt, _correct
    target = word
    
    failure_file_path = f"{setname}_failure_cases.txt"
    with open(failure_file_path, 'a') as failure_file, \
         open('/content/master/data/%s/%s/%s.data.txt' % (setname, word, split)) as split_data_f, \
         open('/content/master/data/%s/%s/%s.gold.txt' % (setname, word, split)) as split_gold_f:

      total_lines = sum(1 for _ in split_data_f)
      split_data_f.seek(0)  # reset file pointer to the beginning
      for line1, line2 in tqdm(zip(split_data_f, split_gold_f), total=total_lines, desc=f"Processing the word '{word}'"):
        word_idx, tokens = line1.split('\t')
        # print("Sent:", tokens)
        sent = tokens
        sense_index = int(line2)
      
        sense_index +=1
        prompt = "Which of the following sense choices is correct for the word '" + word + "' in the following text:\n" + sent.strip() + " \n\n"
        senses_map = get_word_classes(word, setname)
        roman_dict = {}
        senseI = 1
        choice_text = ""
        for value in senses_map.values():
            roman_ltr = util.int_to_roman(senseI)
            choice_text += roman_ltr + ") " + value + "\n"
            roman_dict[roman_ltr] = len(roman_ltr)
            if senseI == sense_index:
                g = roman_ltr
            senseI +=1
           
        prompt += choice_text 
        prompt += "\nDo not provide explanations.\n"
        print("PROMPT:", prompt)
        client = model.client
        chat_response = client.chat(
             model=model.modelname, messages=[ChatMessage(role="user", content=prompt)]
        )
        
        print(chat_response.choices[0].message.content)      
        response = chat_response.choices[0].message.content

        try:
          resp = response
          resp = resp.strip().upper()
          resp_choice = util.find_roman_answer(roman_dict, resp)
          if resp_choice == -1:
            continue
          print("RESULT:", str(util.roman_to_int(resp_choice)))
            
          _attempt += 1
          
          if resp_choice == g:
            _correct+=1
            print("Matched")
          else:
            print("Not matched")
            failure_file.write(f"PROMPT: {prompt}\n")
            failure_file.write(f"RESULT: {resp_choice}\n")
            failure_file.write(f"Gold: {g}\n")
            failure_file.write("========\n\n")

          print("Gold answer:", g)
          print("Attempted:", _attempt, "Correct:", _correct, "Accuracy:", _correct/_attempt)
        except Exception as e:
          print(f"Exception occurred: {e}")
          return
        print("-------------------------------------")
        time.sleep(sleepBetween)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process data set for WSD.')
    parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
    args = parser.parse_args()

    mistral_api_key = args.api_key
    words = ['apple', 'arm', 'bank', 'bass', 'bow', 'chair', 'club', 'crane', 'deck', 'digit', 'hood', 'java', 'mole', 'pitcher', 'pound', 'seal', 'spring', 'square', 'trunk', 'yard']
    # words = ['apple']
    _attempt = 0
    _correct = 0

    model = prepare_mistral_api.prepare(mistral_api_key)
    for i in words:
      print("=======================================")
      print("Will try to run tests on: " + i )
      print("=======================================")
      # sense_sentencesM.clear()
      test_word(i, mistral_api_key, model=model)
