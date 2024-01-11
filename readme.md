# Welcome to Luna 🔮

### Step 0. Prepare Environment
'''
conda create -n luna python=3.9
conda activate luna
pip install -r requirements.txt
'''

### Step 1. Set up Containers (Optional)
1) Knowledge Graph
see https://shorturl.at/lyKTZ
2) LLM Inference Engine
run 'start_llm.sh'

### Step 2. Run the Code
If you would like to use predefined config in the 'data' folder, please try:
'''
python worker.py --config_path [CONFIG_PATH]
'''
Otherwise, you can also try this one. The script will help you to generate the config:
'''
python worker.py
'''

Please feel free to drop me a message, if you have any conern. Thank you!
Email: Mingzhe@nus.edu.sg