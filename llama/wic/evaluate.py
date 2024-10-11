import util
import json
import time
import random
import argparse
import replicate
import os
from tqdm import tqdm

sleepBetween = 1.5  # pause these many seconds between two requests

def call_llama(prompt_my):
    full_resp = ""
    for event in replicate.stream(
        "meta/llama-2-70b-chat",
        input={
            "debug": False,
            "top_k": 50,
            "top_p": 1,
            "prompt": prompt_my,
            "temperature": 0.5,
            "system_prompt": "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible.",
            "max_new_tokens": 500,
            "min_new_tokens": -1
        },
    ):
        full_resp += str(event)
    return full_resp

def readSentences(api_key):
    os.environ["REPLICATE_API_TOKEN"] = api_key
    fdata = '/content/test/test.data.txt'
    fkey = '/content/test/test.gold.txt'

    filedata = open(fdata, 'r')
    linesdata = filedata.readlines()

    filekey = open(fkey, 'r')
    lineskey = filekey.readlines()

    if len(linesdata) != len(lineskey):
        print("Line number mismatch")
        exit()

    count = 0
    attempt = 0
    correct = 0
    exceptionflag = False
    failure_file_path = "/content/wic/wic_failure_cases.txt"
    
    with open(failure_file_path, 'w') as failure_file:
        for line in tqdm(linesdata, desc="Generating prompts"):
            spl = line.split("\t")
            print("---------------------------------------------")
            prompt = "Is the sense of '" + spl[0] + "' same in the following two sentences, say Yes or No:\n" + "sentence1: " + spl[3] + "\n" + "sentence2: " + spl[4] + "\nPlease do not provide explanations.\n"
            print("PROMPT:")
            print(prompt)
            
            response = call_llama(prompt)
        
            try:
                resp = response.strip().upper()
                print("RESULT: ", resp)
                attempt += 1

                if 'YES' in resp:
                    resp = "T"
                else:
                    resp = "F"
                g = lineskey[count].strip()
                if resp == g:
                    correct += 1
                else:
                    print("NOTMATCHED")
                    print("Gold:", lineskey[count])
                    failure_file.write(f"PROMPT: {prompt}\n")
                    failure_file.write(f"RESULT: {resp}\n")
                    failure_file.write(f"Gold answer: {g}\n")
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

    replicate_api_key = args.api_key
    readSentences(replicate_api_key)
