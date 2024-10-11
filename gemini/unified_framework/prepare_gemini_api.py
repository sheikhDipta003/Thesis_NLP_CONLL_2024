
# Used to securely store your API key
from google.colab import userdata
from IPython.display import display
from IPython.display import Markdown
import pathlib
import textwrap
import google.generativeai as genai


def prepare(google_api_key):
	# GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
	genai.configure(api_key=google_api_key)
	
	for m in genai.list_models():
  		if 'embedContent' in m.supported_generation_methods:
   			 print("Gemini model found: ", m.name)


	safety_settings = [
  	{
    	"category": "HARM_CATEGORY_HARASSMENT",
    	"threshold": "BLOCK_NONE"
  	},
  	{
   	 "category": "HARM_CATEGORY_HATE_SPEECH",
    	"threshold": "BLOCK_NONE"
  	},
  	{
    	"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    	"threshold": "BLOCK_NONE"
  	},
  	{
    	"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    	"threshold": "BLOCK_NONE"
  	}
	]
	
	model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
	return model

def to_markdown(text):
	text = text.replace('•', '  *')
	return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

