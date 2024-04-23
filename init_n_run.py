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
def check_pretrained_model(directory, type):
    if os.path.exists(directory):
        if os.path.isfile(os.path.join(directory, 'model.safetensors')) or os.path.isfile(os.path.join(directory, 'pytorch_model.bin')):
            print("Pretrained Flant5 model exists")
        else:
            print("Pretrained Flant5 model does not exist")
            print("training the model from scratch...")
            if type == "swv":
                subprocess.check_call(["python",'./filter_training/flant5-train-test.py', "--train_path", "./filter_training/data/train.csv",'--swv_or_pname',"swv", "--test_path", "./filter_training/data/test.csv", "--save_path", "./filter_model"])
            elif type == "pname":
                subprocess.check_call(["python",'./filter_training/flant5-train-test.py', "--train_path", "./filter_training/data/train.csv",'--swv_or_pname',"pname", "--test_path", "./filter_training/data/test.csv", "--save_path", "./filter_model_p"])
    else:
        print("Directory does not exist")
        print(f"creating {directory} directory")
        os.makedirs(directory)
        if not os.path.exists('./filter_training/outputs'):
            os.makedirs('./filter_training/outputs')
        print("training the model from scratch...")
        if type == "swv":
            subprocess.check_call(["python",'./filter_training/flant5-train-test.py', "--train_path", "./filter_training/data/train.csv",'--swv_or_pname',"swv", "--test_path", "./filter_training/data/test.csv", "--save_path", "./filter_model"])
        elif type == "pname":
            subprocess.check_call(["python",'./filter_training/flant5-train-test.py', "--train_path", "./filter_training/data/train.csv",'--swv_or_pname',"pname", "--test_path", "./filter_training/data/test.csv", "--save_path", "./filter_model_p"])

def run_cli(key,eval_flag,config_flag):
    if os.path.exists('cli_worker_general.py'):
        cmd = ["python", "cli_worker_general.py"]
        if key:
            cmd = cmd + ['--openai_key', key]
        if eval_flag:
            cmd = cmd + ["--eval", eval_flag]
        if config_flag:
            cmd = cmd + ["--config_path", config_flag]
        subprocess.check_call(cmd)
    else:
        print("cli_worker_general.py not found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initializing the environment')
    parser.add_argument('--resources_path', type=str,default='./resources', help='Resources Files path')
    parser.add_argument('--filter_path_swv', type=str,default="./filter_model", help='Filter model path for swv prediction')
    parser.add_argument('--filter_path_p', type=str,default="./filter_model_p", help='Filter model path for pname prediction')
    parser.add_argument('--openai_key', type=str,default=None, help='your openai key')
    parser.add_argument('--eval', type=bool,default=False,help="evaluate on glod SRs")
    parser.add_argument('--config', type=str,default=None,help="config path")
    args = parser.parse_args()
    # Install libraries from requirements.txt
    install_libraries()
    # Check if a callable pretrained flant5 model exists in a certain directory
    check_pretrained_model(args.filter_path_swv, "swv")
    check_pretrained_model(args.filter_path_p, "pname")
    # Run the CLI
    run_cli(args.openai_key,args.eval, args.config)
