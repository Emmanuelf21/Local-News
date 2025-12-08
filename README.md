# Local News

## Instalando Dependências

Este guia explica como instalar as ferramentas necessárias para o seu projeto Django. Vamos instalar o Django, Django REST Framework, Django Taggit, Django Summernote, Pillow, Folium, Geopy e timezonefinderL. Siga as etapas abaixo para configurar seu ambiente de desenvolvimento.

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
pip install -r requirements.txt
```

Isso irá instalar as seguintes ferramentas:

* Django: Framework web para criar aplicações web.

* Django REST Framework (DRF): Ferramenta poderosa para criar APIs RESTful com Django.

* Django Taggit: Biblioteca para adicionar tags aos seus modelos.

* Django Summernote: Editor WYSIWYG (What You See Is What You Get) para campos de texto em Django.

* Pillow: Biblioteca para manipulação de imagens.

* Folium: Biblioteca para criar mapas interativos com Leaflet.js.

* Geopy: Biblioteca para geocodificação e localização geográfica.

* timezonefinderL: Alterar os horários de publicações e comentários de acordo com a localização do usuário. 

3. Fazer as Configurações e migrações

Foi utilizado o PostgreSQL como Banco de Dados e é necessário configurar o usuário, a senha e o nome do banco no arquivo [settings](https://github.com/Emmanuelf21/Local-News/blob/main/portal/settings.py)
Têm duas configurações, uma para o banco local que está comentada e outra para o banco hospedado.
Após a instalação e a configuração do banco, execute o seguinte comando para garantir que o Django está funcionando corretamente:
```
python manage.py makemigrations
python manage.py migrate
```

Inserir os dados nas tabelas

```
INSERT INTO public.noticias_perfil (perfil) VALUES ('usuário'), ('editor'),('admin');

INSERT INTO public.taggit_tag (name, slug) VALUES
('Economia', 'economia'),
('Saúde', 'saúde'),
('Tecnologia', 'tecnologia'),
('Entretenimento', 'entretenimento'),
('Esportes', 'esportes'),
('Política', 'política'),
('Outros', 'outros');

INSERT INTO public.noticias_bairro (bairro, latitude, longitude) VALUES
('Calafate', -9.977137, -67.8766039),
('Nova Esperança', -9.977375, -67.8414052),
('Jardim América', -9.9521151, -67.8259596),
('Baixa da Colina', -9.9597888, -67.8011337),
('Centro', -9.9696487, -67.8248029),
('Quinze', -9.9861707, -67.8111672);


INSERT INTO public.noticias_categoria (categoria) VALUES 
('Real'), 
('Fake');
```


4. Após as configurações

Rodar o projeto
```
python manage.py runserver
```

Abra o navegador e acesse http://127.0.0.1:8000/. Você deverá ver a página inicial do projeto.
Após criar a primeira conta, é necessário alterar diretamente no banco de dados para o 'perfil' de 'admin' colocando o id como 3
```
UPDATE public.noticias_usuario
SET perfil_id = 3
WHERE id = <id do usuário>;
```

5. Documentação

[notion](https://mesquite-tumble-17b.notion.site/Local-News-27d42cb686c18046b8b1ec21c634e686?pvs=73)
