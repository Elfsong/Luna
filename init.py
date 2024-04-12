import os
import subprocess
import argparse
# Function to install libraries from requirements.txt
def install_libraries():
    if os.path.exists('./config/requirements.txt'):
        try:
            subprocess.check_call(['pip', 'install', '-r', './config/requirements.txt' ,'--upgrade-strategy' ,'only-if-needed'])
        except:
            subprocess.check_call(["python", "-m", 'pip', 'install', '-r', './config/requirements.txt' ,'--upgrade-strategy' ,'only-if-needed'])
    else:
        print("requirements.txt not found")

    if os.path.exists('./results'):
        pass
    else:
        os.makedirs('./results')

# Function to check if a callable pretrained flant5 model exists in a certain directory
def check_pretrained_model(directory):
    if os.path.exists(directory):
        if os.path.isfile(os.path.join(directory, 'model.safetensors')):
            print("Pretrained Flant5 model exists")
        else:
            print("Pretrained Flant5 model does not exist")
            print("training the model from scratch...")
            subprocess.check_call(["python",'./filter_training/flant5-train-test.py', "--train_path", "./filter_training/data/train.csv", "--test_path", "./filter_training/data/test.csv", "--save_path", "./filter_model"])
    else:
        print("Directory does not exist")
        print("creating ./filter_model directory")
        os.makedirs(directory)
        os.makedirs('./filter_training/checkpoints')
        os.makedirs('./filter_training/outputs')
        print("training the model from scratch...")
        subprocess.check_call(["python",'./filter_training/flant5-train-test.py', "--train_path", "./filter_training/data/train.csv", "--test_path", "./filter_training/data/test.csv", "--save_path", "./filter_model"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initializing the environment')
    parser.add_argument('--resources_path', type=str,default='./resources', help='Resources Files path')
    parser.add_argument('--filter_path', type=str,default="./filter_model", help='Filter model path')
    args = parser.parse_args()
    # Install libraries from requirements.txt
    install_libraries()
    # Check if a callable pretrained flant5 model exists in a certain directory
    check_pretrained_model(args.filter_path)
