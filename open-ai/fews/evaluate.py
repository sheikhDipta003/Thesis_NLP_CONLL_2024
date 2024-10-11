import prepare_data 
import util
import collect_sense_for_a_word
import time
import argparse
from openai import OpenAI
import os
from tqdm import tqdm

sleepBetween = 1.5 # pause these many seconds between two requests

def call_openai(prompt_my, client_openai):
    resp = ""
    completion = client_openai.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=[
       {"role": "system", "content": "You are an expert assistant"},
       {"role": "user", "content": prompt_my}
     ]
    )
    
    resp = completion.choices[0].message.content
    return resp;

def readTrain(api_key, filePath):
  os.environ["OPENAI_API_KEY"] = api_key
  client_openai = OpenAI()
  train_file = filePath + "/test/test.few-shot.txt"
  si = collect_sense_for_a_word.SenseInventory()
  si.init(filePath= filePath + '/senses.txt')
  
  file = open(train_file, 'r')
  lines = file.readlines()

  attempted = 0 # number of attempts to disambiguate
  correct = 0

  # print("rand_lines: ", rand_lines)
  with open('/content/Fews/incorrect_attempt.txt', 'w') as file_incorrect, open('/content/Fews/correct_attempt.txt', 'w') as file_correct:
    exceptionflag = False
    for line in tqdm(lines, desc="Generating prompts"):
      prompt1 = "Which of the following senses is correct for the word \"{}\" in the following text:\n\n{}"
      line = line.strip()
      prompt2 = " in the following text:\n"
      #print("Train line: ", line)
      p1 = line.find("<WSD>")
      if p1>=0:
        p2 = line.find("</WSD>")
        word = line[p1+5:p2]

        # if more than 1 target work skip
        subs = line[p2+6:len(line)]
        if subs.find("</WSD>") !=-1:
          continue

        # find the sense
        p3 = line.find("\t")
        sense = line[p3:len(line)].strip()
        # print("sense: ", sense)
        senses = si.collectWords(sense)
        prompt3 = senses.promptText

        # print(prompt)
        # print("prompt word: ", word)

        prompt2 = line[0:p3].replace("<WSD>", "").replace("</WSD>", "")
        prompt2 += prompt3
        prompt2 += "\nPrint a choice. Do not provide explanations. Just output the choice.\n"
        # print("prompt text: ", prompt2)
        print("-------------------------------------")
        print("Target word: ", word)
        print("PROMPT: ")
        print("Which of the following senses is correct for the word '" \
          + word + "' " + "in the following text:\n")
        print(prompt2)
        
        response = call_openai(prompt1.format(word, prompt2), client_openai)

        try:
          resp = response
          print("RESULT: ", resp)

          # find the ordinal position of the answer
          resp_choice = util.find_roman_answer(senses.roman_dict, resp)
          if resp_choice == -1:
            continue
          attempted += 1
          if util.roman_to_int(resp_choice) == senses.correctPosn:
            correct += 1
            file_correct.write(line + "\n")
          else:
            print("Gold answer:", senses.correctPosn)
            file_incorrect.write(f"PROMPT: {prompt1.format(word, prompt2)}\n")
            file_incorrect.write(f"RESULT: {resp_choice}\n")
            file_incorrect.write(f"Gold answer: {senses.correctPosn}\n")
            file_incorrect.write("========\n\n")
          print("Attempted:", attempted, "Correct:", correct, "Accuracy:", correct/attempted)
        except Exception as e:
          print(f"Exception occurred: {e}")
          exceptionflag = True
        time.sleep(sleepBetween)
      if exceptionflag:
        break

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Process data set for WSD.')
  parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
  parser.add_argument('--data_path', type=str, required=True,
	  help='Location of top-level directory for FEWS dataset', default='/content/fews')
  args = parser.parse_args()

  openai_api_key = args.api_key
  filePath = args.data_path
  readTrain(openai_api_key, filePath=filePath)



