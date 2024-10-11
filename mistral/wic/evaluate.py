import prepare_mistral_api
import util
import json
import time
import random
import argparse
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from tqdm import tqdm

sleepBetween = 1.5  # pause these many seconds between two requests

def readSentences(api_key):
    model = prepare_mistral_api.prepare(api_key)
    fdata = '/content/test/test.data.txt'
    fkey = '/content/test/test.gold.txt'

    filedata = open(fdata, 'r')
    linesdata = filedata.readlines()

    filekey = open(fkey, 'r')
    lineskey = filekey.readlines()

    if len(linesdata) != len(lineskey):
        print("Line number mismatch")
        exit

    attempt = 0
    correct = 0
    count = 0
    exceptionflag = False
    
    failure_file_path = "/content/wic/failure_cases.txt"
    
    with open(failure_file_path, 'w') as failure_file:
        for line in tqdm(linesdata, desc="Generating prompts"):
            spl = line.split("\t")
            print("---------------------------------------------")
            prompt = "Is the sense of '" + spl[0] + "' same in the following two sentences, say Yes or No:\n" + "sentence1: " + spl[3] + "\n" + "sentence2: " + spl[4] + "\nPlease do not provide explanations.\n"
            print("PROMPT:")
            print(prompt)

            client = model.client
            chat_response = client.chat(
                model=model.modelname, messages=[ChatMessage(role="user", content=prompt)]
            )
            
            print(chat_response.choices[0].message.content)      
            response = chat_response.choices[0].message.content

            try:
                resp = response.strip().upper()
                attempt += 1
                print("RESULT: ", resp)
                
                if 'YES' in resp:
                    resp = "T"
                else:
                    resp = "F"
                g = lineskey[count].strip()
                if resp == g:
                    correct += 1
                else:
                    print("NOTMATCHED")
                    print("Gold:", g)
                    failure_file.write(f"PROMPT: {prompt}\n")
                    failure_file.write(f"RESULT: {resp}\n")
                    failure_file.write(f"Gold: {g}\n")
                    failure_file.write("========\n\n")
            except Exception as e:
                print(f"Exception occurred: {e}")
                exceptionflag = True
            
            print("Attempted:", attempt, "Correct:", correct, "Accuracy:", correct / attempt)
            if exceptionflag:
                break
            time.sleep(sleepBetween)
            count += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process data set for WSD.')
    parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
    args = parser.parse_args()

    mistral_api_key = args.api_key
    readSentences(mistral_api_key)
