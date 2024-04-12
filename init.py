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

# Function to check if two xlsx files exist in a directory
def check_xlsx_files(directory):
    files = os.listdir(directory)
    list_of_files = [file for file in files if file.endswith('.csv') or file.endswith('.xlsx')]
    if 'tech_subtech_pnames.csv' in list_of_files and 'tech_subtech_swv_norm2.csv' in list_of_files:
        print("resources exist")
    else:
        print("Creating ressources")

# Function to check if a callable pretrained flant5 model exists in a certain directory
def check_pretrained_model(directory):
    if os.path.exists(directory):
        if os.path.isfile(os.path.join(directory, 'model.safetensors')):
            print("Pretrained Flant5 model exists")
        else:
            print("Pretrained Flant5 model does not exist")
            print("training the model from scratch...")
            subprocess.check_call(["python",'./filter_training/flant5-train-test.py'])
    else:
        print("Directory does not exist")
        print("creating ./model directory")
        os.makedirs(directory)
        os.makedirs('./checkpoints')
        os.makedirs('./outputs')
        print("training the model from scratch...")
        subprocess.check_call(["python",'flant5-train-test.py', '--train_path',"./data/train.csv" ,'--test_path', "./data/test.csv"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initializing the environment')
    parser.add_argument('--resources_path', type=str,default='./resources', help='Resources Files path')
    parser.add_argument('--filter_path', type=str,default="./filter_model", help='Filter model path')
    args = parser.parse_args()
    # Install libraries from requirements.txt
    install_libraries()
    # Check if two xlsx files exist in a directory
    check_xlsx_files(args.resources_path)
    # Check if a callable pretrained flant5 model exists in a certain directory
    check_pretrained_model(args.filter_path)
