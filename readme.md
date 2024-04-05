# Welcome to Luna 🔮

### 1. Installation and Setup with testing on Sample data:

Download the repository zip from github, unzip and run the following script at bash prompt
```
bash init_run.sh --openai_key [YOUR OPENAI KEY]
```

This script 
* a. Installs the necessary Python libraries (specified in requirements.txt).
* b. Trains the necessary "Call GPT or NOT binary classifier" using training data created by us (in "data")
* c. Uses your provided OPENAI key to extract product_names and software_versions using the sample data from "samples"

To avoid training the model in step (b) please download the trained model from [MOUAD LINK] and place it in "filter_model"

### 2. Running on new data

Please edit the data files for new run in config/gpt-3.json using the entries  graph_metadata/graph_notes

If test_sr list has a list of valid SRs and eval is True, we also provide evaluation results at the end.

```
bash init_run.sh --openai_key [YOUR OPENAI KEY]  (If nothing else has changed, this script will simply run on the new data files specified as above)
```

### 3. Train/Test "Send to GPT or not" Binary Classifier related code can be found under src/filter_training

```
python flant5-train-test.py --train_path "TRAINING FILE PATH" --test_path "TESTING FILE PATH" --batch_size "BATCH_SIZE" --do_test "TRUE/FALSE"
```

Our precomputed train/test data files are listed in  ```"data/test_gold_data.csv"``` and ``` "data/train2_data.csv"```

The relevant scripts to generate new training data are also listed in this directory. Further documentation on how to do this for new data is TBD (and will be ready next week)

Creating Product Name and Software Version lists for use in predictions

The relevant scripts to compile software name and product name lists are provided in src/create_lists. 
We also include version extraction scripts to normalize all software mentions. 
Further documentation on how to do this for new data is TBD (and will be ready next week)
