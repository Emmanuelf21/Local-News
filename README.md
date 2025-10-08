# Local News

## Instalando Dependências

Este guia explica como instalar as ferramentas necessárias para o seu projeto Django. Vamos instalar o Django, Django REST Framework, Django Taggit, Django Summernote, Pillow, Folium e Geopy. Siga as etapas abaixo para configurar seu ambiente de desenvolvimento.

Pré-requisitos

Certifique-se de que você tem o Python e o pip (gerenciador de pacotes do Python) instalados na sua máquina.

Para verificar se o Python e o pip estão instalados corretamente, execute os seguintes comandos no terminal:
```
python --version
pip --version
```

Se algum desses comandos não retornar uma versão válida, você precisará instalar o Python e o pip. Você pode seguir a documentação oficial do Python
 para isso. [instalar Python](https://www.python.org/).

1. Criar e Ativar um Ambiente Virtual

É altamente recomendável usar um ambiente virtual para gerenciar dependências do projeto.

Criar o Ambiente Virtual:
```
python -m venv venv
```

Ativar o Ambiente Virtual:

No Windows:
```
.\venv\Scripts\activate
```

No macOS ou Linux:
```
source venv/bin/activate
```

2. Instalar as Dependências

Agora, com o ambiente virtual ativado, instale as dependências necessárias executando o seguinte comando:
```
pip install django djangorestframework django-taggit django-summernote pillow folium geopy psycopg2
```

Isso irá instalar as seguintes ferramentas:

* Django: Framework web para criar aplicações web.

* Django REST Framework (DRF): Ferramenta poderosa para criar APIs RESTful com Django.

* Django Taggit: Biblioteca para adicionar tags aos seus modelos.

* Django Summernote: Editor WYSIWYG (What You See Is What You Get) para campos de texto em Django.

* Pillow: Biblioteca para manipulação de imagens.

* Folium: Biblioteca para criar mapas interativos com Leaflet.js.

* Geopy: Biblioteca para geocodificação e localização geográfica.

3. Verificar a Instalação

Após a instalação, execute o seguinte comando para garantir que o Django está funcionando corretamente:
```
python manage.py runserver
```

Abra o navegador e acesse http://127.0.0.1:8000/. Você deverá ver a página padrão do Django indicando que o servidor está funcionando.
