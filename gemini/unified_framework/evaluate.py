import prepare_data 
import util
import collect_sense_for_a_word
import prepare_gemini_api
import time
import google.ai.generativelanguage
import argparse
import xml.etree.ElementTree as ET
import google.ai.generativelanguage
import sys
from tqdm import tqdm

sleepBetween = 1.5  # pause between two requests

class instance:
    senses = []  # sense definitions
    correct = -1
    pt_text = ""  # prompt text
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
    failureFileName = "/content/unified_framework/" + version + "_failure_cases.txt"
    
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
    model = prepare_gemini_api.prepare(api_key)
    with open(failureFileName, 'w') as failure_file:
        for i in tqdm(lst, desc="Processing sentences"): # i contains a sentence element
            sen = ""
            instances = []
            for c in i: # contains child element of a sentence
                if c.tag == "instance":
                    ins = instance()
                    senseid = c.get("id")
                    word = c.text
                    pos = posmap[c.get('pos')]
                    d = si.get_word_senses(word, pos, senseid)

                    p = ""
                    for i, sense in enumerate(d.definitions, start=1):
                        p += util.int_to_roman(i) + ") " + sense + "\n"

                    ins.target = word
                    ins.pt_text = p
                    ins.correct = d.correct_posn
                    instances.append(ins)

                sen += " " + c.text
            print("--------------------------------------------------------------------------------------------------------")
            for i, inst in enumerate(instances):
                nice_text = "Which of the following senses is correct for the word '" + inst.target + "'" + " in the following text: " + sen + "\n\n"
                nice_text += inst.pt_text 
                print("PROMPT: ", nice_text)
                p_text1 = "Which of the following senses is correct for the word \"{}\" in the following text:\n\n{}"
                p_text2 = sen + "\n\n"
                p_text2 += inst.pt_text
                response = model.generate_content(p_text1.format(inst.target, p_text2))
                feedb = response.prompt_feedback
                try:
                    if (response.prompt_feedback.block_reason != google.ai.generativelanguage.GenerateContentResponse.PromptFeedback.BlockReason.BLOCK_REASON_UNSPECIFIED):
                        print("Blocked: ", response.prompt_feedback.block_reason)
                        continue
                    resp = response.text
                    print("RESULT: ", resp)
                    # find the ordinal position of the answer
                    fnd = resp.find(")")
                    if fnd != -1 and inst.correct != -1:
                        roman = resp[0:fnd]
                        print("The answer is:", str(util.roman_to_int(roman)))
                        print("Gold answer is: ", inst.correct)
                        attempted += 1
                        if util.roman_to_int(roman) == inst.correct:
                            correct += 1
                        else:
                            failure_file.write(f"PROMPT: {nice_text}\n")
                            failure_file.write(f"RESULT: {resp}\n")
                            failure_file.write(f"Gold answer is: {inst.correct}\n")
                            failure_file.write("========\n\n")
                        print(f"Attempted: {attempted}, Correct: {correct}, Accuracy: {correct/attempted}")
                        print("========\n\n")
                    time.sleep(sleepBetween)
                except Exception as e:
                    print(f"Exception occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process data set for WSD.')
    parser.add_argument('--api_key', type=str, default='giveyourapi', required=True)
    parser.add_argument('--data_path', type=str, required=True,
                        help='Location of top-level directory for the unified framework dataset', default='/content/WSD_Evaluation_Framework')
    parser.add_argument('--version', type=str, required=True,
                        help='Semeval2007, Semeval2013, SemCor, etc.',
                        default='/content/WSD_Evaluation_Framework')
    args = parser.parse_args()

    google_api_key = args.api_key
    topLevelDir = args.data_path
    version = args.version
    readTrain(google_api_key, topLevelDir=topLevelDir, version=version)
