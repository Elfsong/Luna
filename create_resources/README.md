The code provided in this directory is for creating the following two resources


1. the train and test files for training the classifier that filters cases notes to figure out (whether to make an OpenAI call or not)
2. the lists of product names and software version names that are used to build the options list for MCQ calls

The resources folder already includes these two files for the data provided as part of the WP1 (use-case#1)

After the necessary libraries installed (via init_test script)

*Alter the file paths for inputs and outputs in CRConfig (the fields to alter are marked by TO EDIT first)

To create new lists run
``python CreatePNamesSWVLists.py''


To create new train/test data run
``python CreateTrainTest_GPTClassifier.py''


To re-train the classifier, specify these new data files (in the command described in filter_training/README)








