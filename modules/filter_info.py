import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = AutoModelForSequenceClassification.from_pretrained("hamzzi/xlm-roberta-filter-news", num_labels=2)

model.to(device)
tokenizer = AutoTokenizer.from_pretrained("hamzzi/xlm-roberta-filter-news")

with open('/Users/taewonyun/Documents/GitHub/Prototype/data_collection/kotra_commodity_info_0207.json','r', encoding='utf-8') as f:
    kotra_commodity_info = json.load(f)

for item in kotra_commodity_info[:5]:
    item['hscode'] = '9018'
    
    # hscode 앞 4글자와 상품명 영어를 합쳐서 string으로 만들기
    hscode = 'hscode:9018\nMedical, surgical, dental or veterinary instruments'

    content = item['content']

    inputs = tokenizer(
        hscode,
        content,
        truncation=True,
        return_token_type_ids=False,
        pad_to_max_length=True,
        add_special_tokens=True,
        max_length=512,
        return_tensors="pt" 
    )

    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    # 모델에 입력 데이터 전달하여 결과 얻기
    with torch.no_grad():
        output = model(input_ids, attention_mask=attention_mask)

    # 예측 결과 가져오기
    logits = output.logits

    probabilities = torch.nn.functional.softmax(logits, dim=1)

    predictions = torch.argmax(probabilities, dim=1).cpu().numpy()

    item['related_info'] = predictions[0]

with open('kotra_commodity_info_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(kotra_commodity_info, f, ensure_ascii=False, indent=2)

    