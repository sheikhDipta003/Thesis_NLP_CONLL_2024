import util
import json
import time
import random
import argparse
from openai import OpenAI
import os
from tqdm import tqdm

sleepBetween = 1.5  # pause these many seconds between two requests

def call_openai(prompt_my, client_openai):
    completion = client_openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are an expert assistant"},
            {"role": "user", "content": prompt_my}
        ]
    )
    resp = completion.choices[0].message.content
    return resp

def readSentences(api_key):
    os.environ["OPENAI_API_KEY"] = api_key
    client_openai = OpenAI()
    fdata = '/content/test/test.data.txt'
    fkey = '/content/test/test.gold.txt'

    filedata = open(fdata, 'r')
    linesdata = filedata.readlines()

    filekey = open(fkey, 'r')
    lineskey = filekey.readlines()

    if len(linesdata) != len(lineskey):
        print("Line number mismatch")
        exit()

    attempt = 0
    correct = 0
    count = 0
    exceptionflag = False
    failure_cases_file = "/content/wic/failure_cases.txt"
    
    with open(failure_cases_file, 'w') as failure_file:
        for line in tqdm(linesdata, desc="Generating prompts"):
            spl = line.split("\t")
            prompt = "Is the sense of '" + spl[0] + "' same in the following two sentences, say Yes or No:\n" + \
                     "sentence1: " + spl[3] + "\n" + "sentence2: " + spl[4] + "\nPlease do not provide explanations.\n"
            print("PROMPT:")
            print(prompt)

            response = call_openai(prompt, client_openai)

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
                    failure_file.write(f"PROMPT: {prompt}\n")
                    failure_file.write(f"RESULT: {resp}\n")
                    failure_file.write(f"Gold answer: {g}\n")
                    failure_file.write("========\n\n")
                    print("NOTMATCHED")
                    print("Gold:", g)
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

    openai_api_key = args.api_key
    readSentences(openai_api_key)
