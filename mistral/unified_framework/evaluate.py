import prepare_data 
import util
import collect_sense_for_a_word
import prepare_mistral_api
import time
import argparse
import xml.etree.ElementTree as ET
import sys
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from tqdm import tqdm

sleepBetween = 1.5 # pause between two requests

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

    # model = prepare_mistral_api.MistralModel(api_key)
    model = prepare_mistral_api.prepare(api_key)
    client = model.client
    
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
                nice_text = f"Which of the following senses is correct for the word '{inst.target}' in the following text: {sen}\n\n"
                nice_text += inst.pt_text 
                nice_text += "\nDo not provide explanations.\n"
                print("PROMPT: ", nice_text)
                p_text1 = f"Which of the following senses is correct for the word \"{inst.target}\" in the following text:\n\n"
                p_text2 = f"{sen}\n\n{inst.pt_text}\nDo not provide explanations."
                
                chat_response = client.chat(
                    model=model.modelname, messages=[ChatMessage(role="user", content=p_text1 + p_text2)]
                )
                
                print(chat_response.choices[0].message.content)
                response = chat_response.choices[0].message.content
                try:
                    resp = response
                    print("RESULT: ", resp)
                    resp_choice = util.find_roman_answer(roman_dict, resp)
                    if resp_choice == -1:
                        continue
                    print("The answer is:", str(util.roman_to_int(resp_choice)))
                    print("Gold answer is: ", inst.correct)
                    attempted += 1
                    if util.roman_to_int(resp_choice) == inst.correct:
                        correct += 1
                    else:
                        failure_file.write(f"PROMPT: {p_text1 + p_text2}\n")
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

    google_api_key = args.api_key
    topLevelDir = args.data_path
    version = args.version
    readTrain(google_api_key, topLevelDir=topLevelDir, version=version)
