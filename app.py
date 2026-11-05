# Importa os recursos do Flask
from flask import Flask, render_template, request
# Biblioteca utilizada para acessar páginas da Web
import requests
# Biblioteca utilizada para interpretar o HTML
from bs4 import BeautifulSoup
# Cria a aplicação Flask
app = Flask(__name__)

# Endereço base das páginas de produto do Scraping Sandbox.
# Exemplo: https://scrapingsandbox.com/product/1
URL_BASE = "https://scrapingsandbox.com/product/"

# Quantidade de produtos (páginas) que serão coletados
TOTAL_PRODUTOS = 200

# Tempo máximo (em segundos) de espera pela resposta do site
TEMPO_LIMITE = 10

# Guarda os produtos já coletados. Assim o Web Scraping é feito
# apenas na primeira pesquisa e as próximas ficam instantâneas.
produtos_coletados = []


# ==========================================================
# COLETA DE UM PRODUTO
# ==========================================================
def coletar_produto(sessao, id_produto):
    # Monta o endereço da página do produto.
    #
    # Exemplo:
    # https://scrapingsandbox.com/product/100
    url = f"{URL_BASE}{id_produto}"

    # Realiza a requisição para o site.
    # Se houver erro de conexão ou demora, ignora este produto
    # em vez de interromper a aplicação.
    try:
        resposta = sessao.get(url, timeout=TEMPO_LIMITE)
    except requests.RequestException:
        print(f"Erro ao acessar {url}")
        return None

    # Se não conseguimos acessar a página, ignora este produto
    if resposta.status_code != 200:
        return None

    # Interpreta o HTML recebido
    soup = BeautifulSoup(resposta.text, "html.parser")

    # Localiza o nome do produto: <h1>
    titulo = soup.find("h1")
    # Localiza a categoria: primeiro <span class="inline-flex">
    tag_categoria = soup.select_one("span.inline-flex")
    # Localiza o preço: <span class="text-3xl">
    tag_preco = soup.select_one("span.text-3xl")

    # Se algum dado essencial não existir, ignora este produto
    if titulo is None or tag_categoria is None or tag_preco is None:
        return None

    # Converte o preço de texto ("$51.11") para número (51.11).
    # Se o texto vier em um formato inesperado, ignora este produto
    try:
        preco = float(tag_preco.get_text(strip=True).replace("$", "").replace(",", ""))
    except ValueError:
        return None

    # Localiza a avaliação. Pode não existir em alguns produtos
    tag_avaliacao = soup.select_one("span.text-sm.font-mono.font-semibold")
    avaliacao = None
    if tag_avaliacao:
        try:
            avaliacao = float(tag_avaliacao.get_text(strip=True))
        except ValueError:
            avaliacao = None

    # Cada produto é representado por um dicionário
    return {
        "nome": titulo.get_text(strip=True),
        "preco": preco,
        "categoria": tag_categoria.get_text(strip=True),
        "avaliacao": avaliacao,
        "link": url
    }


# ==========================================================
# COLETA DE VÁRIOS PRODUTOS (PAGINAÇÃO)
# ==========================================================
# Na listagem do Scraping Sandbox, os botões de página (1, 2, 3...)
# funcionam com JavaScript: o endereço "/?page=2" devolve os mesmos
# produtos da primeira página. Por isso a paginação é feita pelas
# páginas de cada produto, que seguem uma sequência numérica:
#   /product/1, /product/2, /product/3, ...
# Cada número é uma página diferente do site.
def coletar_produtos(total=TOTAL_PRODUTOS):
    # Lista que armazenará os produtos coletados
    produtos = []

    # A sessão reaproveita a conexão com o site (coleta mais rápida)
    sessao = requests.Session()

    # Percorre as páginas de produto: 1, 2, 3, ... até o total
    for id_produto in range(1, total + 1):
        print(f"Acessando produto {id_produto}...")

        produto = coletar_produto(sessao, id_produto)

        # Se o produto foi coletado, adiciona na lista
        if produto:
            produtos.append(produto)

    return produtos


# ==========================================================
# PÁGINA INICIAL
# ==========================================================
@app.route("/")
def inicio():
    # Mostra a página que contém o formulário
    return render_template("index.html")


# ==========================================================
# ROTA RESPONSÁVEL PELA PESQUISA
# ==========================================================
@app.route("/pesquisar", methods=["POST"])
def pesquisar():
    # Recebe a categoria escolhida no formulário
    categoria = request.form.get("categoria")

    # Realiza o Web Scraping somente se os produtos ainda não foram coletados.
    # "global" permite alterar a variável criada fora da função
    global produtos_coletados
    if not produtos_coletados:
        produtos_coletados = coletar_produtos()
    produtos = produtos_coletados

    # Lista que armazenará somente os produtos da categoria escolhida
    produtos_filtrados = []

    # Filtra os produtos pela categoria
    for produto in produtos:
        if produto["categoria"] == categoria:
            produtos_filtrados.append(produto)

    # Valores da análise (começam vazios)
    quantidade = len(produtos_filtrados)
    menor = None
    maior = None
    media = None
    melhor = None

    # Só calcula se existir pelo menos um produto na categoria
    if quantidade > 0:
        # Produtos de menor e maior preço (key indica o campo comparado)
        menor = min(produtos_filtrados, key=lambda p: p["preco"])
        maior = max(produtos_filtrados, key=lambda p: p["preco"])

        # Preço médio: soma dos preços dividida pela quantidade
        precos = []
        for produto in produtos_filtrados:
            precos.append(produto["preco"])
        media = sum(precos) / len(precos)

        # Melhor avaliação: considera somente produtos que têm nota
        com_avaliacao = []
        for produto in produtos_filtrados:
            if produto["avaliacao"] is not None:
                com_avaliacao.append(produto)
        if com_avaliacao:
            melhor = max(com_avaliacao, key=lambda p: p["avaliacao"])

    # Envia os resultados para o HTML
    return render_template(
        "resultado.html",
        categoria=categoria,
        quantidade=quantidade,
        menor=menor,
        maior=maior,
        media=media,
        melhor=melhor,
        produtos=produtos_filtrados
    )


# ==========================================================
# EXECUÇÃO
# ==========================================================
if __name__ == "__main__":
    app.run(debug=True)