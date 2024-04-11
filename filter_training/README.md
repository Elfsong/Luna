To train and test the flan T5 model on your own data, you need first to create two directories called ```./results``` and ```./outputs``` to store the saved model and the output of the testing step. Then run the following code:

```python3 flant5-train-test.py --train_path "YOUR_TRAINING_FILE_PATH.csv" --test_path "YOUR_TESTING_FILE_PATH.csv" --batch_size "BATCH_SIZE" ```
