# app/utils.py
import requests
from django.conf import settings
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel
import torch

def analisar_texto_noticia(texto):
    model_name = "vzani/portuguese-fake-news-classifier-bertimbau-fake-br"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Tokenização
    inputs = tokenizer(
        texto,
        return_tensors="pt",
        max_length=512,
        padding='max_length',
        truncation=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        label = torch.argmax(probs).item()
        
    prob_real = probs[0][0].item()
    print(f"Prob_REAL: {prob_real}")
    if prob_real < 0.7:
        label = 1  # FAKE
    else:
        label = 0  # REAL
                
    print(f"🔍 Probabilidades: {probs.tolist()}")
    print("🔍 Resultado:", "REAL" if label == 0 else "FAKE")

    return label

    # model_name = "mrm8488/bert-tiny-finetuned-fake-news-detection"

    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    # model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # inputs = tokenizer(texto, return_tensors="pt", max_length=512,padding='max_length')

    # with torch.no_grad():
    #     outputs = model(**inputs)
    #     probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    #     label = torch.argmax(probs).item()

        
    # print("🔍 Resultado:", "Fake" if label == 0 else "Real")
    
    # return label
