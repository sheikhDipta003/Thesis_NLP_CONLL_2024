import prepare_data 
import util
import collect_sense_for_a_word
import time
import argparse
import xml.etree.ElementTree as ET
import sys
from tqdm import tqdm
import os
import replicate

sleepBetween = 1.5 # pause between two requests

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

class instance:
    senses = [] # sense definitions
    correct = -1
    pt_text = "" # prompt text
    target = ""

def readTrain(api_key, topLevelDir='/content/WSD_Evaluation_Framework', version='semeval2013'):
    trainFile = ""
    senseKeyFile = ""
    if version.find("SemCor") != -1:
        trainFile = topLevelDir + "/Training_Corpora/SemCor/" + "semcor.data.xml"
        senseKeyFile = topLevelDir + "/Training_Corpora/SemCor/" + "semcor.gold.key.txt"
    else:
        trainFile = topLevelDir + "/Evaluation_Datasets/" + version + "/" + version + ".data.xml"
        senseKeyFile = topLevelDir + "/Evaluation_Datasets/" + version + "/" + version + ".gold.key.txt"
    
    si = collect_sense_for_a_word.SenseInventory()
    si.init(filePath=senseKeyFile)
    tree = ET.parse(trainFile)
    root = tree.getroot()
    lst = root.findall('text/sentence')
    print("Total number of sentences: ", len(lst))

    posmap = {
        "NOUN": "n",
        "VERB": "v",
        "ADJ": "a",
        "ADV": "r"
    }

    attempted = 0  # number of attempts to disambiguate
    correct = 0
    os.environ["REPLICATE_API_TOKEN"] = api_key
    
    failure_file_path = f"/content/unified_framework/{version}_failure_cases.txt"

    with open(failure_file_path, 'w') as failure_file:
        for i in tqdm(lst, desc="Processing sentences"):  # i contains a sentence element
            sen = ""
            instances = []
            roman_dict = {}
            for c in i:  # contains child element of a sentence
                if c.tag == "instance":
                    ins = instance()
                    senseid = c.get("id")
                    word = c.text
                    pos = posmap[c.get('pos')]
                    d = si.get_word_senses(word, pos, senseid)

                    p = ""
                    for i, sense in enumerate(d.definitions, start=1):
                        roman_ltr = util.int_to_roman(i)
                        p += roman_ltr + ") " + sense + "\n"
                        roman_dict[roman_ltr] = len(roman_ltr)

                    ins.target = word
                    ins.pt_text = p
                    ins.correct = d.correct_posn
                    instances.append(ins)

                sen += " " + c.text
            print("--------------------------------------------------------------------------------------------------------")
            for i, inst in enumerate(instances):
                nice_text = "Which of the following senses is correct for the word '" + inst.target + "'" + " in the following text: " + sen + "\n\n"
                nice_text += inst.pt_text 
                nice_text += "\nDo not provide explanations.\n"
                
                p_text1 = "Which of the following senses is correct for the word \"{}\" in the following text:\n\n{}"
                p_text2 = sen + "\n\n"
                p_text2 += inst.pt_text
                p_text2 += "\nDo not provide explanations. Just output the choice."
                
                response = call_llama(p_text1.format(inst.target, p_text2))
                print("PROMPT: ", p_text1.format(inst.target, p_text2))
                try:
                    resp = response
                    print("RESULT: ", resp)
                    resp_choice = util.find_roman_answer(roman_dict, resp)
                    
                    if resp_choice == -1:
                        continue
                    
                    print("The answer is:", resp_choice)
                    print("Gold answer is: ", inst.correct)
                    attempted += 1
                    
                    if util.roman_to_int(resp_choice) == inst.correct:
                        correct += 1
                    else:
                        failure_file.write(f"PROMPT: {p_text1.format(inst.target, p_text2)}\n")
                        failure_file.write(f"RESULT: {resp_choice}\n")
                        failure_file.write(f"Gold answer: {inst.correct}\n")
                        failure_file.write("========\n\n")
                    
                    print("Attempted:", attempted, "Correct:", correct, "Accuracy:", correct / attempted)
                    print("========\n\n")

                    time.sleep(sleepBetween)
                except Exception as e:
                    print(f"Exception occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process data set for WSD.')
    parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
    parser.add_argument('--data_path', type=str, required=True, help='Location of top-level directory for the unified framework dataset', default='/content/WSD_Evaluation_Framework')
    parser.add_argument('--version', type=str, required=True, help='Semeval2007, Semeval2013, SemCor, etc.', default='/content/WSD_Evaluation_Framework')
    args = parser.parse_args()

    replicate_api_key = args.api_key
    topLevelDir = args.data_path
    version = args.version
    readTrain(replicate_api_key, topLevelDir=topLevelDir, version=version)
