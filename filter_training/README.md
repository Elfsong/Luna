To train and test the flan T5 model on your own data, you need first to create a directory ```./outputs``` to store the output of the testing step. Then run the following code:

```python3 flant5-train-test.py --train_path "YOUR_TRAINING_FILE_PATH.csv" --test_path "YOUR_TESTING_FILE_PATH.csv" --batch_size "BATCH_SIZE" --swv_or_pname "CHOOSE_EITHER_swv_OR_pname" --do_test "TRUE/FALSE" --save_path "PATH_WHERE_TO_STORE_THE_MODEL" ```
