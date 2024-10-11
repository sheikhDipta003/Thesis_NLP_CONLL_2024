# Used to securely store your API key
from google.colab import userdata
from IPython.display import display
from IPython.display import Markdown
import pathlib
import textwrap
from mistralai.client import MistralClient

class MistralModel:
	def __init__(self, api_key):
		self.modelname = "open-mistral-7b"
		self.client = MistralClient(api_key=api_key)
		

def prepare(api_key):
	mistralmodel = MistralModel(api_key)
	return mistralmodel



