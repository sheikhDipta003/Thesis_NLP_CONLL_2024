import prepare_data 
import util
import collect_sense_for_a_word
import prepare_gemini_api
import time
import google.ai.generativelanguage
import argparse
from tqdm import tqdm

sleepBetween = 1.5 # pause between two requests

def readTrain(api_key, filePath):
    model = prepare_gemini_api.prepare(api_key)
    train_file = filePath + "/test/test.zero-shot.txt"
    si = collect_sense_for_a_word.SenseInventory()
    si.init(filePath=filePath + '/senses.txt')
  
    file = open(train_file, 'r')
    lines = file.readlines()

    attempted = 0  # number of attempts to disambiguate
    correct = 0

    with open('zero_shot_incorrect_attempt.txt', 'w') as file_incorrect, open('zero_shot_correct_attempt.txt', 'w') as file_correct:
        for line in tqdm(lines, desc="Generating prompts"):
            prompt1 = "Which of the following senses is correct for the word \"{}\" in the following text:\n\n{}"
            line = line.strip()
            prompt2 = " in the following text:\n"

            p1 = line.find("<WSD>")
            if p1 >= 0:
                p2 = line.find("</WSD>")
                word = line[p1 + 5:p2]

                # if more than 1 target word, skip
                subs = line[p2 + 6:len(line)]
                if subs.find("</WSD>") != -1:
                    continue

                # find the sense
                p3 = line.find("\t")
                sense = line[p3:len(line)].strip()
                senses = si.collectWords(sense)
                prompt3 = senses.promptText

                prompt2 = line[0:p3].replace("<WSD>", "").replace("</WSD>", "")
                prompt2 += prompt3
                
                print("-------------------------------------")
                print("Target word: ", word)
                print("PROMPT: ")
                print("Which of the following senses is correct for the word '" + word + "' " + "in the following text:\n")
                print(prompt2)
                
                response = model.generate_content(prompt1.format(word, prompt2))
                feedb = response.prompt_feedback
                
                try:
                    if (response.prompt_feedback.block_reason != google.ai.generativelanguage.GenerateContentResponse.PromptFeedback.BlockReason.BLOCK_REASON_UNSPECIFIED):
                        print("Blocked: ", response.prompt_feedback.block_reason)
                        continue
                    resp = response.text
                    print("RESULT: ", resp)

                    # find the ordinal position of the answer
                    fnd = resp.find(")")
                    if fnd != -1:
                        roman = resp[0:fnd]
                        model_response = str(util.roman_to_int(roman))
                        print("The answer is:", model_response)
                    attempted += 1
                    
                    if model_response == str(senses.correctPosn):
                        correct += 1
                        file_correct.write(line + "\n")
                    else:
                        print("Gold answer:", senses.correctPosn)
                        file_incorrect.write(f"PROMPT: {prompt1.format(word, prompt2)}\n")
                        file_incorrect.write(f"RESULT: {model_response}\n")
                        file_incorrect.write(f"Gold answer: {senses.correctPosn}\n")
                        file_incorrect.write("========\n\n")
                    print("Attempted:", attempted, "Correct:", correct, "Accuracy:", correct / attempted)
                except Exception as e:
                    print(f"Exception occurred: {e}")
                time.sleep(sleepBetween)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process data set for WSD.')
    parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
    parser.add_argument('--data_path', type=str, required=True, help='Location of top-level directory for FEWS dataset', default='/content/fews')
    args = parser.parse_args()

    google_api_key = args.api_key
    filePath = args.data_path
    readTrain(google_api_key, filePath=filePath)
