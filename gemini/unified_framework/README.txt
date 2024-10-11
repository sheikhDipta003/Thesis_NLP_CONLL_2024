# Experimented on Google Colab Python Environment

Step 1:
# Initialize the environment by running the commands in shell_commands 
# Copying and pasting the content of the file in a notebook will suffice

Step 2.a:
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet

Step 2.b: 
# To run the code to perform disambibuation, please use the following:
!python evaluate.py  --api_key 'yourgoogleapikey' --data_path '/content/WSD_Evaluation_Framework' --version 'semeval2015' --stop_count 1
Arguments:
api_key: Google API Key
data_path: Path to the root folder where the dataset has been exploded
version: There are six datasets: semeval2007, semeval2013, semeval2015, senseval2, senseval3, SemCor; use any name
stop_count: Limit number of tries
