# app/utils.py
import requests
from django.conf import settings
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel
import torch
import folium
from .models import Noticia

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
    if prob_real > 0.40:
        label = 1  # FAKE
    else:
        label = 0  # REAL
                
    print(f"🔍 Probabilidades: {probs.tolist()}")
    print("🔍 Resultado:", "REAL" if label == 0 else "FAKE")

    return label


def mapa_noticias():
    noticias = Noticia.objects.select_related('bairro', 'usuario', 'tema')

    # 🌎 Mapa centralizado em Rio Branco - AC, com mobile funcionando
    mapa = folium.Map(
        location=[-9.97499, -67.8243],  # Rio Branco - AC
        zoom_start=12,
        zoom_control=True,        # habilita controle de zoom para mobile
        scrollWheelZoom=True,     # permite zoom por gesto
        dragging=True,            # permite arrastar em mobile
        touchZoom=True,           # zoom por pinça no celular
    )

    # 🟦 Adiciona marcadores das notícias
    for noticia in noticias:
        bairro = noticia.bairro
        if bairro.latitude and bairro.longitude:

            popup_text = f"""
                    <div style="
                            width: 230px;
                            font-family: Arial, sans-serif;
                            border-radius: 10px;
                            overflow: hidden;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                            background: #ffffff;
                        ">
                            <img src='{noticia.image.url if noticia.image else ""}'
                                style="width: 100%; height: 120px; object-fit: cover; display: block;" />

                            <div style="padding: 10px;">
                                <h4 style="margin: 0 0 5px 0; font-size: 15px; font-weight: bold; color: #333;">
                                    {noticia.titulo}
                                </h4>

                                <p style="margin: 0; font-size: 13px; color: #666;">
                                    <i>{bairro.bairro}</i>
                                </p>

                                <p style="margin: 4px 0 10px 0; font-size: 12px; color: #999;">
                                    {noticia.tema}
                                </p>

                                <a href='/noticia/{noticia.id}/'
                                target='_blank'
                                style="
                                        display: inline-block;
                                        background: #2563eb;
                                        color: white;
                                        padding: 6px 10px;
                                        border-radius: 6px;
                                        text-decoration: none;
                                        font-size: 12px;
                                        font-weight: bold;
                                ">
                                    Ver notícia →
                                </a>
                            </div>
                        </div>

            """

            folium.Marker(
                location=[bairro.latitude, bairro.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=noticia.titulo,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)

    # 🔒 Define limites aproximados de Rio Branco (opcional)
    mapa.options['maxBounds'] = [
        [-10.20, -68.00],  # sudoeste
        [-9.90, -67.60]    # nordeste
    ]

    mapa_html = mapa._repr_html_()
    return mapa_html
