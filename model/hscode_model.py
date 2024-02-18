import pandas as pd
import numpy as np
import random
import os
from torch.utils.data import DataLoader
from dataset import TRAINDataset
from train import training
from transformers import AutoModelForSequenceClassification
import torch
from sklearn.model_selection import train_test_split
import json
from tqdm import tqdm
from torch.nn import functional as F
from transformers import get_linear_schedule_with_warmup
from adamp import AdamP
from torch.utils.data import Dataset
from transformers import AutoTokenizer
from sklearn.metrics import f1_score, accuracy_score

with open('/backup/taewon/Robust_sum/data/data_practice.json') as json_file:
    data = []
    for line in json_file:
        data.append(json.loads(line))

data_list = []

for item in data:
    try:
        relevant_data = json.loads(item['response'].split('```json')[-1].strip().rstrip('`'))[0]['relevant']
        for item2 in relevant_data:
            item2['content'] = item['content']
            item2['label'] = 1
            data_list.append(item2)

            item2['content'] = item['SMMAR_CN']
            item2['label'] = 1
            data_list.append(item2)
    except:
        pass

    try:
        irrelevant_data = json.loads(item['response'].split('```json')[-1].strip().rstrip('`'))[0]['irrelevant']
        for item2 in irrelevant_data:
            item2['content'] = item['content']
            item2['label'] = 0
            data_list.append(item2)

            item2['content'] = item['SMMAR_CN']
            item2['label'] = 0
            data_list.append(item2)
    except:
        pass

df = pd.DataFrame(data_list)

df = df[(df['hscode'] != 'None') & (df['content'] != 'None')]

df = df[df['hscode'].str.len() == 4]

df = df[~df['name'].str.contains('규칙')]

df['hscode_content'] = 'hscode:' + df['hscode'] +'\n' + df['name']

df = df[['hscode_content','content','label']]

train, test_label = train_test_split(df, test_size=0.2, random_state=42)

test = test_label[['hscode_content','content']]

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def calc_accuracy(X, Y):
    max_vals, max_indices = torch.max(X, 1)
    train_acc = (max_indices == Y).sum().item() / max_indices.size()[0]
    return train_acc

class TRAINDataset(Dataset):
    def __init__(self, data):
        self.dataset = data
        self.tokenizer = AutoTokenizer.from_pretrained("FacebookAI/xlm-roberta-base")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        row = self.dataset.iloc[idx, 0:3].values
        sentence1 = row[0]
        sentence2 = row[1]
        y = row[2]
        inputs = self.tokenizer(
            sentence1,
            sentence2,
            truncation=True,
            return_token_type_ids=False,
            pad_to_max_length=True,
            add_special_tokens=True,
            max_length=512
        )

        input_ids = torch.tensor(inputs['input_ids'])
        attention_mask = torch.tensor(inputs['attention_mask'])

        return input_ids, attention_mask, y

def training(train_loader, valid_loader, model, epochs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    optimizer = AdamP(model.parameters(), lr=1e-5, betas=(0.9, 0.999), weight_decay=1e-2)
    total_steps = len(train_loader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, 
                                                num_warmup_steps=0,
                                                num_training_steps=total_steps)
    
    for e in range(epochs):
        model.train()
        train_true = []
        train_preds = []
        
        for batch_id, (token_ids, attention_masks, label) in tqdm(enumerate(train_loader), total=len(train_loader)):
            optimizer.zero_grad()
            token_ids, attention_masks, label = token_ids.to(device), attention_masks.to(device), label.to(device)
            outputs = model(token_ids, attention_mask=attention_masks).logits
            loss = F.cross_entropy(outputs, label)
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            _, predicted = torch.max(outputs, 1)
            train_preds.extend(predicted.cpu().numpy())
            train_true.extend(label.cpu().numpy())

        train_f1 = f1_score(train_true, train_preds, average='macro')
        train_acc = accuracy_score(train_true, train_preds)
        print(f"Epoch {e + 1} Train Acc: {train_acc}, Train F1: {train_f1}")

        model.eval()
        valid_true = []
        valid_preds = []
        with torch.no_grad():
            for batch_id, (token_ids, attention_masks, label) in tqdm(enumerate(valid_loader), total=len(valid_loader)):
                token_ids, attention_masks, label = token_ids.to(device), attention_masks.to(device), label.to(device)
                outputs = model(token_ids, attention_mask=attention_masks).logits
                
                _, predicted = torch.max(outputs, 1)
                valid_preds.extend(predicted.cpu().numpy())
                valid_true.extend(label.cpu().numpy())

        valid_f1 = f1_score(valid_true, valid_preds, average='macro')
        valid_acc = accuracy_score(valid_true, valid_preds)
        print(f"Epoch {e + 1} Valid Acc: {valid_acc}, Valid F1: {valid_f1}")

# Cross-validation
def main():
    # Split the train dataset into train and validation to monitor the training process
    train_data, valid_data = train_test_split(train, test_size=0.2, random_state=42)

    print('Starting training...')
    train_dataset = TRAINDataset(train_data)
    valid_dataset = TRAINDataset(valid_data)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=16, shuffle=False)
    model = AutoModelForSequenceClassification.from_pretrained("FacebookAI/xlm-roberta-base", num_labels=2)
    training(train_loader, valid_loader, model, epochs=10)
    torch.save(model, '/backup/taewon/Robust_sum/model2/model.pt')

if __name__ == "__main__":
    set_seed(2024)
    main()  # Start training
