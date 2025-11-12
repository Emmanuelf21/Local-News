# app/utils.py
import requests
from django.conf import settings
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel
import torch

def analisar_texto_noticia(texto):
    model_name = "mrm8488/bert-tiny-finetuned-fake-news-detection"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        label = torch.argmax(probs).item()

    print("🔍 Resultado:", "Fake" if label == 0 else "Real")
    
    return label
    
    # url = "https://router.huggingface.co/hf-inference/models/portugues-bert-base-cased"
    # headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"}
    # data = {"inputs": texto}

    # try:
    #     response = requests.post(url, headers=headers, json=data, timeout=30)
    #     print("🔹 Status:", response.status_code)
    #     print("🔹 Resposta (raw):", response.text[:500])

    #     if response.status_code != 200:
    #         return "erro", 0.0

    #     result = response.json()
    #     print("🔹 Resultado completo:", result)

    #     # Processa a resposta do modelo de classificação
    #     if isinstance(result, list) and result:
    #         # Para modelos de classificação, pega a predição com maior score
    #         melhor_predicao = max(result[0], key=lambda x: x['score'])
    #         label = melhor_predicao.get('label', 'erro')
    #         score = melhor_predicao.get('score', 0.0)
    #         return label.lower(), score
        
    #     return "erro", 0.0

    # except requests.exceptions.RequestException as e:
    #     print("❌ Erro de requisição:", e)
    #     return "erro", 0.0
    # except ValueError as e:
    #     print("❌ Erro ao decodificar JSON:", e)
    #     if 'response' in locals():
    #         print("🔸 Resposta bruta:", response.text)
    #     return "erro", 0.0
    # except Exception as e:
    #     print("❌ Erro inesperado:", e)
    #     return "erro", 0.0