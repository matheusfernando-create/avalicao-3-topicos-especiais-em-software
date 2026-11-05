# Catálogo de Produtos com Web Scraping

Aplicação Web em Flask que coleta produtos do site [Scraping Sandbox](https://scrapingsandbox.com/) por meio de Web Scraping, filtra pela categoria escolhida pelo usuário e apresenta uma análise dos produtos encontrados.

## Tecnologias

- Python
- Flask
- requests
- BeautifulSoup
- HTML / Jinja

## Como executar

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Inicie a aplicação:

   ```bash
   python app.py
   ```

3. Acesse no navegador: http://127.0.0.1:5000

## Funcionamento

1. Na página inicial, o usuário escolhe uma categoria e clica em **Pesquisar**.
2. O Flask recebe a categoria pela rota `/pesquisar`.
3. O programa acessa as páginas de produto do Scraping Sandbox (`/product/1` até `/product/200`) com `requests` e interpreta o HTML com `BeautifulSoup`.
4. De cada produto são obtidos: nome, preço, categoria, avaliação e link.
5. O Python filtra os produtos da categoria escolhida e calcula:
   - quantidade de produtos encontrados;
   - produto de menor preço;
   - produto de maior preço;
   - preço médio;
   - produto com melhor avaliação.
6. Os resultados são enviados para o template `resultado.html` e exibidos no navegador.

## Paginação

Na listagem do Scraping Sandbox, a troca de página é feita por JavaScript (o endereço `/?page=2` devolve os mesmos produtos da primeira página). Por isso a paginação é feita pelas páginas individuais dos produtos, que seguem uma sequência numérica: `/product/1`, `/product/2`, `/product/3`...

A primeira pesquisa realiza a coleta (cerca de 10 segundos). Os produtos ficam guardados na memória, então as pesquisas seguintes são instantâneas.

## Estrutura

```
app.py                 # Aplicação Flask, Web Scraping e análises
templates/index.html   # Página inicial com o formulário
templates/resultado.html  # Página de resultados
requirements.txt       # Dependências do projeto
```
