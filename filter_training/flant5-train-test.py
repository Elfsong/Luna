import os
import random
from sklearn.metrics import classification_report
#os.environ["CUDA_VISIBLE_DEVICES"] = "3"
import argparse
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import evaluate
from transformers import AutoTokenizer, DataCollatorForSeq2Seq, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer
from nltk.tokenize import sent_tokenize
from rich.console import Console

path = os.path.abspath("flant5-train-test.py")
term = path.split('/')
term="/".join(term[0:len(term)-2])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Training Flan-T5')
    parser.add_argument('--train_path', type=str,default='./data/train.csv', help='Training File Path')
    parser.add_argument('--batch_size', type=int,default=8, help='Batch size for training')
    parser.add_argument('--do_test', type=bool,default=False, help='Evaluate model on dataset')
    parser.add_argument('--test_path', type=str,default='./data/test.csv', help='Testing File Path')
    args = parser.parse_args()

    df_train = pd.read_csv(args.train_path)
    df_test = pd.read_csv(args.test_path)


def set_seed(seed):
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)


MODEL_NAME = "google/flan-t5-large"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model,label_pad_token_id=-100)
# define a rich console logger
console = Console(record=True)

class TextClassificationDataset(Dataset):
    def __init__(self, texts, plabels,labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.plabels = plabels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.inputs = []
        self.targets = []

    def __len__(self):
        return len(self.labels)
    def __getitem__(self, idx):
        
        text =  "Question: Given the list of labels, does the passage contain any of the labels? Answer True or False. Labels= " + str(self.plabels[idx]) +', passage=' + str(self.texts[idx])
        label = str(self.labels[idx])

  
        source = self.tokenizer.batch_encode_plus(
            [text],
            max_length=self.max_length,
            pad_to_max_length=True,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        target = self.tokenizer.batch_encode_plus(
            [label],
            max_length=6,
            pad_to_max_length=True,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )

        source_ids = source["input_ids"].squeeze()
        source_mask = source["attention_mask"].squeeze()
        target_ids = target["input_ids"].squeeze()
        target_mask = target["attention_mask"].squeeze()

        return {
            "input_ids": source_ids.to(dtype=torch.long),
            "attention_mask": source_mask.to(dtype=torch.long),
            "labels": target_ids.to(dtype=torch.long),
        }
    
metric = evaluate.load("f1")
def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [label.strip() for label in labels]

    # rougeLSum expects newline after each sentence
    preds = ["\n".join(sent_tokenize(pred)) for pred in preds]
    labels = ["\n".join(sent_tokenize(label)) for label in labels]

    return preds, labels

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # Some simple post-processing
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)
    pred, label = [] , []
    for j in range(len(decoded_preds)):
        if decoded_preds[j] == "True":
            pred.append(1)
        elif decoded_preds[j] == "False":
            pred.append(0)
        if decoded_labels[j] == "True":
            label.append(1)
        elif decoded_labels[j] == "False":
            label.append(0)
    result = metric.compute(predictions=pred, references=label, average='macro')
    result = {k: round(v * 100, 4) for k, v in result.items()}
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = np.mean(prediction_lens)
    return result
    
L_RATE = 5e-5
BATCH_SIZE = args.batch_size
PER_DEVICE_EVAL_BATCH = 4
WEIGHT_DECAY = 0.01
SAVE_TOTAL_LIM = 3
NUM_EPOCHS = 3

# Set up training arguments
training_args = Seq2SeqTrainingArguments(
   output_dir="./checkpoints",
   evaluation_strategy="epoch",
   learning_rate=L_RATE,
   per_device_train_batch_size=BATCH_SIZE,
   per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH,
   weight_decay=WEIGHT_DECAY,
   save_total_limit=SAVE_TOTAL_LIM,
   num_train_epochs=NUM_EPOCHS,
   predict_with_generate=True,
   push_to_hub=False
)

train2  = df_train['source'].tolist()

train_dataset = TextClassificationDataset(df_train['source'].tolist(),df_train['plabels'].tolist(), df_train['target'].tolist(), tokenizer, max_length=512)
val_dataset = TextClassificationDataset(df_test['source'].tolist(),df_test['plabels'].tolist(),  df_test['target'].tolist(), tokenizer, max_length=512)


trainer = Seq2SeqTrainer(
   model=model,
   args=training_args,
   train_dataset=train_dataset,
   eval_dataset=val_dataset,
   tokenizer=tokenizer,
   data_collator=data_collator,
   compute_metrics=None,
)

trainer.train()

trainer.save_model(term + "/filter_model/")

def validate(tokenizer, model, device, loader):

  """
  Function to evaluate model for predictions

  """
  model.eval()
  predictions = []
  actuals = []
  with torch.no_grad():
      for _, data in enumerate(loader, 0):
          y = data['labels'].to(device, dtype = torch.long)
          ids = data['input_ids'].to(device, dtype = torch.long)
          mask = data['attention_mask'].to(device, dtype = torch.long)


          generated_ids = model.generate(
              input_ids = ids
              )
          preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True) for g in generated_ids]
          target = [tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=True)for t in y]
          if _%10==0:
              console.print(f'Completed {_}')

          predictions.extend(preds)
          actuals.extend(target)
  return predictions, actuals

if args.do_test:

    output_dir="./outputs/"
    val_params = {
            "batch_size": BATCH_SIZE,
            "shuffle": False,
            "num_workers": 0,
        }
    val_loader = DataLoader(val_dataset, **val_params)
    predictions, actuals = validate(tokenizer, model, 'cuda', val_loader)
    final_df = pd.DataFrame({"Generated Text": predictions, "Actual Text": actuals})
    final_df.to_csv(os.path.join(output_dir, "predictions.csv"))
    print(classification_report(actuals, predictions))

