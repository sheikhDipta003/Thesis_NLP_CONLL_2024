import prepare_gemini_api
import util
import json
import google.ai.generativelanguage
import time
import random
import argparse
from tqdm import tqdm

sleepBetween = 1.5 # pause these many seconds between two requests

def readSentences(api_key):
    model = prepare_gemini_api.prepare(api_key)
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

    with open('/content/wic/failure_cases.txt', 'w') as failure_file:
        for line in tqdm(linesdata, desc="Generating prompts"):
            spl = line.split("\t")
            print("---------------------------------------------")
            prompt = "Is the sense of '" + spl[0] + "' same in the following two sentences, say Yes or No:\n" + \
                     "sentence1: " + spl[3] + "\n" + "sentence2: " + spl[4] + "\n"
            print("PROMPT:")
            print(prompt)
            response = model.generate_content(prompt)
            feedb = response.prompt_feedback
            try:
                if (response.prompt_feedback.block_reason != google.ai.generativelanguage.GenerateContentResponse.PromptFeedback.BlockReason.BLOCK_REASON_UNSPECIFIED):
                    print("Blocked: ", response.prompt_feedback.block_reason)
                    continue
                resp = response.txt.strip().upper()
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
                    # Write failure case to file
                    failure_file.write(f"PROMPT: {prompt}\n")
                    failure_file.write(f"RESULT: {response.text}\n")
                    failure_file.write(f"Gold answer: {g}\n")
                    failure_file.write("========\n\n")
            except Exception as e:
                print(f"Exception occurred: {e}")
            print("Attempted:", attempt, "Correct:", correct, "Accuracy:", correct / attempt)
            count += 1
            time.sleep(sleepBetween)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process data set for WSD.')
    parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
    args = parser.parse_args()

    google_api_key = args.api_key
    readSentences(google_api_key)
