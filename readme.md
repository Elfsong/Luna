# Welcome to Luna 🔮

### Step 0. Prepare Environment
```shell
conda create -n luna python=3.9
conda activate luna
pip install -r requirements.txt
mkdir results
```

### Step 1. Set up Containers (Optional)
In most cases, you don't need to do this section by yourself. However, if you are curious, there is something you can check out:
* Knowledge Graph Installation (see section 'Installation' in https://shorturl.at/lyKTZ)
* LLM Inference Engine (run 'start_llm.sh')

You can also try the LLM inference engine by CURL:
```
curl 10.246.112.13:8080/generate \
    -X POST \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}' \
    -H 'Content-Type: application/json'
```

### Step 2. Run the Code
#### Graph Construction Task
To use pre-defined config in the 'data' folder, please try:
```shell
python worker.py --config_path [CONFIG_PATH] --task graph
```

If you would like to use other metadata/notes, please run:
```shell
python worker.py --task graph
```

#### Product_Name/Software_version Inference Task
If you would like to use pre-defined config in the 'data' folder, please try:
```shell
python worker.py --config_path [CONFIG_PATH] --task [product/software]
```

Otherwise, you can also try this one. The script will help you to generate the config:
```shell
python worker.py --task [product/software]
```

Please feel free to let me know if you have any concerns. Thank you!
Email: Mingzhe@nus.edu.sg

![Demo](data/demo.png)
