# Welcome to Luna 🔮

### Step 0. Prepare Environment
```shell
conda create -n luna python=3.9
conda activate luna
python init.py 
python init_n_run.py --openai_key "YOUR_KEY"
```

### Quick run
First start by downloading the filter model and store it in a directory under the name ``` "filter" ```, make sure this directory is in the same level as ```init_run.sh``` file. Otherwise the code will train a model from scratch with the default data, this may take time and depend on the computational capabilities of your machine. we highly suggest that you download the filter model from the following link: "the_link" .

Afterward run the following command and make sure you replace the field in capital letters with your own openai key.
```
bash int_run.sh --openai_key "YOUR_OPENAI_KEY"
```

### Train your own model

If you want to retrain the filter with your own data run the following command
```
flant5-train-test.py --train_path "TRAINING FILE PATH" --test_path "TESTING FILE PATH" --batch_size "BATCH_SIZE" --do_test "TRUE/FALSE"
```

Make sure you specify a train/test file path and that the files are in the correct format.

the batch size will depend on the size of your GPU default is 8

the do_test flag will evaluate the model on the test_set

The config file can be found in the config directory, changing this file is crucial to run the inference model.

#### Adding the OpenAi Key and choosing the inference model 

First you have to replace the open_ai_key field in the config file by your own openai key, see more details at the [openai website](https://platform.openai.com/api-keys)
Second, you have to replace the model_name field in the config file with a valid openai model name. It is highly advised to use ```gpt-4-0125-preview``` or ```gpt-3.5-turbo-0125``` models.

![change](data/openai.png)

#### Changing the metadata files and the case notes files

You have to change the ```graph_metadata``` and the ```graph_notes``` fields in the config file with the paths to you json file containing the metadata and the case notes data respectively.

![change](data/change_files.png)

#### Further config changes

You can change the ```test_sr``` field in the config file, by specifying the SRs for which you want to test, if you keep this field as an empty list [], the cli will test for all the SRs present in the metadata files that have case notes in the casenote file

The ```eval``` flag in the config file should be set to true if the user want to evaluate the performance of the model. for the inference case, set this flag to false.

![change](data/testing_srs.png)

### Step 3. Run the Code
#### Graph Construction Task
To use pre-defined config in the 'data' folder, please try:
```shell
python cli_worker.py --config_path [CONFIG_PATH] --task graph
```

If you would like to use other metadata/notes, please run:
```shell
python cli_worker.py --task graph
```

#### Product_Name/Software_version Inference Task
If you would like to use pre-defined config in the 'data' folder, please try:
```shell
python cli_worker.py --config_path [CONFIG_PATH] --task [product/software]
```

Otherwise, you can also try this one. The script will help you to generate the config:
```shell
python cli_worker.py --task [product/software]
```

Please feel free to let me know if you have any concerns. Thank you!
Email: mingzhe@nus.edu.sg

---

Watch the demo video ⬇️

[![Demo](data/demo.png)](https://www.youtube.com/watch?v=ZA4cExEgurE)
