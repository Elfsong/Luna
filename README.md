# Welcome to Luna 🔮

### 1. Installation and Setup with testing on Sample data:

Download the repository zip from github, unzip and run the following script at bash prompt:

```
bash init_test.sh --openai_key [YOUR OPENAI KEY]
```

This script:

a) Installs the necessary Python libraries (specified in requirements.txt).

b) Trains the necessary "Call GPT or NOT binary classifier" using training data created by us (in "data").

c) Uses your provided OPENAI key to extract product_names and software_versions using the sample data from "samples".


To avoid training the model in step (b) please download the trained model from [HERE](https://drive.google.com/drive/folders/1qTd5yGKpNt8sCREOLPrHpYVDk79-ZvhQ?usp=sharing) and place it in a sub-directory called "filter_model".


### 2. Running on new data

Please edit the data files for new run in config/gpt-3.json using the entries  ```filepath_metadata/filepath_notes```

New product names/software version lists may be specified using ```tech_subtech_sw_map/tech_subtech_pnames_map```

If test_sr list has a list of valid SRs and eval is True, we also provide evaluation results at the end.


```
bash run_extractors.sh --config [CONFIG FILE PATH]
```

### 3. Train/Test "Send to GPT or not" Binary Classifier

Please check the README in ```filter_training```

Our precomputed train/test data files are listed in  ```"data/test.csv"``` and ``` "data/train.csv"```

### 4. Compiling the Product Name and Software Version lists and Creating the train/test data for the binary classifier

Please check the README in ```create_resources```

### 5. Neo4J: Visualizing your data via graphs

Please check the installation and setup details in ```neo4j_setup```
