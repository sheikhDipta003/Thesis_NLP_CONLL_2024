# Experimented on Google Colab Python Environment

Step 1:
# Initialize the environment by running the commands in shell_commands 
# Copying and pasting the content of the file in a notebook will suffice

Step 2: 
# To run the code to perform disambibuation, please use the following:
!python evaluate.py  --api_key 'yourapikey' --data_path '/content/fews/' --stop_count 1
Arguments:
api_key: OpenAI API Key
data_path: Path to the root folder where fews dataset has been exploded
stop_count: Limit number of tries
