#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera os artefatos da entrega do trabalho "API REST - Baozi Store":
  - diagrama_caso_de_uso.png
  - Baozi_Store_Postman_Collection.json  (importe no Postman)
  - Trabalho_Baozi_Store.pdf              (documento final para enviar)

USO:
    pip install reportlab matplotlib
    python gerar_entrega.py --nome "SeuNome" --ru 1234567 --repo "https://github.com/seuuser/baozi-store"

Depois de tirar os prints no Postman, salve-os na pasta ./prints com os nomes abaixo
e rode o script de novo: o PDF passa a incluir as imagens no lugar dos quadros vazios.
    01_post_cliente.png   02_post_produto.png   03_post_pedido.png
    04_get_clientes.png   05_get_produtos.png   06_get_pedidos.png
    07_get_cliente_id.png 08_get_produto_id.png 09_get_pedido_id.png
    10_delete_pedido.png  11_get_pedido_apos_delete.png   (aceita .png/.jpg/.jpeg)
"""
import argparse, json, os, datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle, FancyArrowPatch

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, NextPageTemplate, Table, TableStyle, Image, Preformatted,
                                KeepTogether, Flowable)

AQUI = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO (pode editar aqui ou passar por linha de comando)
# ----------------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("--nome", default="SeuNome", help="Seu primeiro nome")
ap.add_argument("--ru", default="0000000", help="Seu RU")
ap.add_argument("--nome-completo", dest="nome_completo", default=None, help="Nome completo para a capa")
ap.add_argument("--sem-capa", dest="sem_capa", action="store_true", help="Gera so o miolo (a capa vem do modelo .docx)")
ap.add_argument("--offset", type=int, default=0, help="Soma ao numero das paginas no rodape")
ap.add_argument("--produto", default="Baozi Tradicional")
ap.add_argument("--preco", default="8.50")
ap.add_argument("--quantidade", type=int, default=6)
ap.add_argument("--repo", default="https://github.com/SEU-USUARIO/baozi-store")
ap.add_argument("--data", default=datetime.date.today().isoformat(), help="Data de cadastro do cliente (AAAA-MM-DD)")
args = ap.parse_args()

NOME_RU = f"{args.nome}{args.ru}"
PRODUTO, PRECO, QTD, REPO, DATA = args.produto, args.preco, args.quantidade, args.repo, args.data
BASE_URL = "http://localhost:8080"
PASTA_PRINTS = os.path.join(AQUI, "prints")

# ----------------------------------------------------------------------------
# 1) DIAGRAMA DE CASO DE USO (UML)
# ----------------------------------------------------------------------------
def gerar_diagrama(caminho):
    fig, ax = plt.subplots(figsize=(11.5, 7.6), dpi=200)
    ax.set_xlim(-11.1, 11.1); ax.set_ylim(-3.6, 9.5); ax.axis("off")
    COR = {"Cliente": "#dbeafe", "Produto": "#dcfce7", "Pedido": "#fef3c7"}
    BORDA = {"Cliente": "#1d4ed8", "Produto": "#15803d", "Pedido": "#b45309"}
    FS = 10.5

    # fronteira do sistema
    ax.add_patch(Rectangle((-10.6, -3.4), 21.2, 12.8, fill=False, lw=2, ec="black", zorder=1))
    ax.text(0, 8.85, "Sistema: API REST – Baozi Store", ha="center", va="center",
            fontsize=14, fontweight="bold")

    # ator (boneco palito) no centro
    ax_x, ax_y = 0, 4.7
    ax.add_patch(Circle((ax_x, ax_y + 0.95), 0.28, fill=False, lw=2, zorder=5))
    ax.plot([ax_x, ax_x], [ax_y + 0.67, ax_y - 0.2], "k", lw=2, zorder=5)
    ax.plot([ax_x - 0.5, ax_x + 0.5], [ax_y + 0.4, ax_y + 0.4], "k", lw=2, zorder=5)
    ax.plot([ax_x, ax_x - 0.45], [ax_y - 0.2, ax_y - 0.85], "k", lw=2, zorder=5)
    ax.plot([ax_x, ax_x + 0.45], [ax_y - 0.2, ax_y - 0.85], "k", lw=2, zorder=5)
    ax.text(ax_x, ax_y + 1.85, "Usuário da API", ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(ax_x, ax_y + 1.5, "(Postman / cliente HTTP)", ha="center", va="center", fontsize=9, style="italic")

    ys = [7.6, 6.4, 5.2, 4.0, 2.8]
    W, H = 4.7, 1.0

    def ellipse(cx, cy, texto, ent, w=W, h=H, dashed=False):
        ax.add_patch(Ellipse((cx, cy), w, h, fc=COR[ent], ec=BORDA[ent], lw=1.8, zorder=3,
                             ls="--" if dashed else "-"))
        ax.text(cx, cy, texto, ha="center", va="center", fontsize=FS, zorder=4)

    def ligar(x0, y0, x1, y1):
        ax.plot([x0, x1], [y0, y1], color="#333", lw=1.1, zorder=2)

    # coluna esquerda: Cliente | direita: Produto
    for ent, cx, lado in (("Cliente", -7.7, -1), ("Produto", 7.7, 1)):
        art = ent.lower()
        ax.text(cx, 8.35, f"CRUD de {ent}", ha="center", fontsize=11.5, fontweight="bold", color=BORDA[ent])
        textos = [f"Cadastrar {art}\nPOST /{art}s",
                  f"Consultar {art}\nGET /{art}s/{{id}}",
                  f"Listar {art}s\nGET /{art}s",
                  f"Atualizar {art}*\nPUT /{art}s/{{id}}",
                  f"Excluir {art}\nDELETE /{art}s/{{id}}"]
        for t, y in zip(textos, ys):
            ellipse(cx, y, t, ent)
            ligar(ax_x + lado * 0.5, ax_y, cx - lado * (W / 2), y)

    # linha inferior: Pedido
    ax.text(-10.4, 1.8, "CRUD de Pedido", ha="left", fontsize=11.5, fontweight="bold", color=BORDA["Pedido"])
    xs = [-8.3, -4.15, 0, 4.15, 8.3]
    pw = 4.1
    nomes = ["Registrar pedido\nPOST /pedidos", "Consultar pedido\nGET /pedidos/{id}",
             "Listar pedidos\nGET /pedidos", "Atualizar pedido*\nPUT /pedidos/{id}",
             "Excluir pedido\nDELETE /pedidos/{id}"]
    for x, t in zip(xs, nomes):
        ellipse(x, 0.3, t, "Pedido", w=pw, h=1.05)
        ligar(ax_x, ax_y - 0.85, x, 0.3 + 0.5 if abs(x) < 0.1 else 0.3 + 0.45)
    # <<include>>: registrar pedido -> validar cliente e produto
    ellipse(-8.3, -2.3, "Validar cliente,\nproduto e estoque", "Pedido", w=pw, h=1.05, dashed=True)
    ax.add_patch(FancyArrowPatch((-8.3, -0.25), (-8.3, -1.75), arrowstyle="-|>", mutation_scale=14,
                                 lw=1.3, ls="--", color="#333", zorder=2))
    ax.text(-8.05, -1.0, "«include»", fontsize=9, style="italic", ha="left", va="center")

    # legenda
    ax.text(10.3, -3.05, "* operação opcional no enunciado (PUT)   |   Notação: UML – Casos de Uso",
            ha="right", fontsize=8.5, style="italic")
    fig.savefig(caminho, bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ----------------------------------------------------------------------------
# 2) COLEÇÃO DO POSTMAN
# ----------------------------------------------------------------------------
def req(nome, metodo, caminho, raw=None, teste=None, desc=""):
    item = {"name": nome, "request": {
        "method": metodo,
        "header": [{"key": "Content-Type", "value": "application/json"}] if raw is not None else [],
        "url": {"raw": "{{baseUrl}}" + caminho, "host": ["{{baseUrl}}"], "path": [x for x in caminho.split("/") if x]},
        "description": desc}}
    if raw is not None:
        item["request"]["body"] = {"mode": "raw", "raw": raw, "options": {"raw": {"language": "json"}}}
    if teste:
        item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": teste}}]
    return item

def gerar_postman(caminho):
    V = lambda n: 'pm.collectionVariables.get("%s")' % n
    status = lambda c, t: 'pm.test("Status %s %s", () => pm.response.to.have.status(%s));' % (c, t, c)
    rapido = 'pm.test("Tempo de resposta < 2000 ms", () => pm.expect(pm.response.responseTime).to.be.below(2000));'
    json_ct = 'pm.test("Content-Type é JSON", () => pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json"));'
    salvar = lambda var: 'pm.collectionVariables.set("%s", pm.response.json().id);' % var
    T = lambda titulo, expr: 'pm.test("%s", () => %s);' % (titulo, expr)

    # ---------- corpos ----------
    c_cliente = '{\n  "nome": "{{nomeCliente}}",\n  "clienteDesde": "{{clienteDesde}}"\n}'
    c_produto = '{\n  "nome": "{{nomeProduto}}",\n  "preco": {{precoProduto}},\n  "estoque": true\n}'
    c_pedido = '{\n  "clienteId": {{clienteId}},\n  "produtoId": {{produtoId}},\n  "quantidade": {{quantidade}}\n}'

    # ---------- testes: criar ----------
    t_post_cliente = [status(201, "Created"), rapido, json_ct, "const j = pm.response.json();",
        T("Retornou id numérico", 'pm.expect(j.id).to.be.a("number")'),
        T("Nome do cliente confere", "pm.expect(j.nome).to.eql(%s)" % V("nomeCliente")),
        T("clienteDesde confere", "pm.expect(j.clienteDesde).to.eql(%s)" % V("clienteDesde")),
        salvar("clienteId")]
    t_post_produto = [status(201, "Created"), rapido, json_ct, "const j = pm.response.json();",
        T("Retornou id numérico", 'pm.expect(j.id).to.be.a("number")'),
        T("Nome do produto confere", "pm.expect(j.nome).to.eql(%s)" % V("nomeProduto")),
        T("Preço confere", "pm.expect(Number(j.preco)).to.eql(Number(%s))" % V("precoProduto")),
        T("Produto em estoque (true)", "pm.expect(j.estoque).to.eql(true)"),
        salvar("produtoId")]
    t_post_pedido = [status(201, "Created"), rapido, json_ct, "const j = pm.response.json();",
        T("Retornou id numérico", 'pm.expect(j.id).to.be.a("number")'),
        T("clienteId confere", "pm.expect(j.clienteId).to.eql(Number(%s))" % V("clienteId")),
        T("produtoId confere", "pm.expect(j.produtoId).to.eql(Number(%s))" % V("produtoId")),
        T("Quantidade confere", "pm.expect(j.quantidade).to.eql(Number(%s))" % V("quantidade")),
        T("Cliente do pedido: nome confere", "pm.expect(j.cliente.nome).to.eql(%s)" % V("nomeCliente")),
        T("Produto do pedido: nome confere", "pm.expect(j.produto.nome).to.eql(%s)" % V("nomeProduto")),
        salvar("pedidoId")]

    # ---------- testes: listar ----------
    def t_lista(var):
        return [status(200, "OK"), rapido, json_ct, "const lista = pm.response.json();",
                T("Resposta é uma lista", 'pm.expect(lista).to.be.an("array")'),
                T("Lista não está vazia", "pm.expect(lista.length).to.be.above(0)"),
                T("Lista contém o registro criado", "pm.expect(lista.some(x => x.id === Number(%s))).to.eql(true)" % V(var))]

    # ---------- testes: por ID ----------
    t_get_cliente = [status(200, "OK"), rapido, json_ct, "const j = pm.response.json();",
        T("id confere", "pm.expect(j.id).to.eql(Number(%s))" % V("clienteId")),
        T("Nome confere", "pm.expect(j.nome).to.eql(%s)" % V("nomeCliente"))]
    t_get_produto = [status(200, "OK"), rapido, json_ct, "const j = pm.response.json();",
        T("id confere", "pm.expect(j.id).to.eql(Number(%s))" % V("produtoId")),
        T("Nome confere", "pm.expect(j.nome).to.eql(%s)" % V("nomeProduto")),
        T("Preço confere", "pm.expect(Number(j.preco)).to.eql(Number(%s))" % V("precoProduto"))]
    t_get_pedido = [status(200, "OK"), rapido, json_ct, "const j = pm.response.json();",
        T("id confere", "pm.expect(j.id).to.eql(Number(%s))" % V("pedidoId")),
        T("Quantidade confere", "pm.expect(j.quantidade).to.eql(Number(%s))" % V("quantidade")),
        T("Cliente confere", "pm.expect(j.cliente.nome).to.eql(%s)" % V("nomeCliente")),
        T("Produto confere", "pm.expect(j.produto.nome).to.eql(%s)" % V("nomeProduto"))]

    def t_erro(codigo, texto, extra=None):
        t = [status(codigo, texto), json_ct, "const j = pm.response.json();",
             T("Corpo de erro padronizado (status %s)" % codigo, "pm.expect(j.status).to.eql(%s)" % codigo),
             T("Há mensagem de erro", 'pm.expect(j.mensagem).to.be.a("string")')]
        return t + (extra or [])

    t_204 = [status(204, "No Content"), T("Corpo vazio", 'pm.expect(pm.response.text()).to.eql("")')]

    col = {
        "info": {
            "name": "Baozi Store - API REST",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "description": (
                "# Baozi Store - API REST\n\n"
                "Aluno: **%s** (RU %s)\n\n"
                "## Como usar\n"
                "1. Suba a API: `mvn spring-boot:run` (http://localhost:8080).\n"
                "2. Execute as pastas **1 a 4** na ordem (botão *Run* da coleção, ou uma a uma). "
                "Elas cobrem o que o enunciado exige: POST, GET geral, GET por ID e DELETE.\n"
                "3. As pastas **5 e 6** são extras (PUT opcional, integridade e casos de erro).\n\n"
                "## Variáveis da coleção\n"
                "Os dados da situação fictícia ficam em `nomeCliente`, `clienteDesde`, `nomeProduto`, "
                "`precoProduto` e `quantidade`. Os IDs (`clienteId`, `produtoId`, `pedidoId`) são preenchidos "
                "automaticamente pelos testes dos POST.\n\n"
                "Cada requisição tem testes automáticos (aba *Test Results*) que conferem status, JSON e valores."
            ) % ((args.nome_completo or args.nome), args.ru)},
        "variable": [
            {"key": "baseUrl", "value": BASE_URL},
            {"key": "nomeCliente", "value": NOME_RU}, {"key": "clienteDesde", "value": DATA},
            {"key": "nomeProduto", "value": PRODUTO}, {"key": "precoProduto", "value": PRECO},
            {"key": "quantidade", "value": str(QTD)},
            {"key": "clienteId", "value": ""}, {"key": "produtoId", "value": ""}, {"key": "pedidoId", "value": ""},
            {"key": "pedidoExtraId", "value": ""}, {"key": "produtoSemEstoqueId", "value": ""}],
        "item": [
            {"name": "1 - Criar (POST)", "description": "Cria cliente, produto e pedido da situação fictícia. Execute nesta ordem.", "item": [
                req("1.1 POST Cliente", "POST", "/clientes", c_cliente, t_post_cliente, "Cadastra o cliente (nome = Nome+RU)."),
                req("1.2 POST Produto", "POST", "/produtos", c_produto, t_post_produto, "Cadastra o produto vendido pela loja."),
                req("1.3 POST Pedido", "POST", "/pedidos", c_pedido, t_post_pedido,
                    "Registra o pedido ligando o cliente e o produto criados acima."),
            ]},
            {"name": "2 - Listar todos (GET)", "description": "Listagem geral das três entidades.", "item": [
                req("2.1 GET Clientes", "GET", "/clientes", None, t_lista("clienteId")),
                req("2.2 GET Produtos", "GET", "/produtos", None, t_lista("produtoId")),
                req("2.3 GET Pedidos", "GET", "/pedidos", None, t_lista("pedidoId")),
            ]},
            {"name": "3 - Consultar por ID (GET /{id})", "description": "Consulta individual usando os IDs salvos.", "item": [
                req("3.1 GET Cliente por ID", "GET", "/clientes/{{clienteId}}", None, t_get_cliente),
                req("3.2 GET Produto por ID", "GET", "/produtos/{{produtoId}}", None, t_get_produto),
                req("3.3 GET Pedido por ID", "GET", "/pedidos/{{pedidoId}}", None, t_get_pedido),
            ]},
            {"name": "4 - Apagar (DELETE /{id})", "description": "Apaga o pedido e comprova com um GET que retorna 404.", "item": [
                req("4.1 DELETE Pedido", "DELETE", "/pedidos/{{pedidoId}}", None, t_204),
                req("4.2 GET Pedido apos DELETE (404)", "GET", "/pedidos/{{pedidoId}}", None,
                    t_erro(404, "Not Found", [T("Mensagem indica pedido não encontrado", 'pm.expect(j.mensagem).to.include("Pedido não encontrado")')])),
            ]},
            {"name": "5 - Extras: PUT e integridade (opcional)",
             "description": "Atualização (PUT) e regra de integridade: não apaga cliente/produto com pedido vinculado.", "item": [
                req("5.1 PUT Cliente", "PUT", "/clientes/{{clienteId}}", c_cliente,
                    [status(200, "OK"), json_ct, "const j = pm.response.json();",
                     T("Nome mantido", "pm.expect(j.nome).to.eql(%s)" % V("nomeCliente"))]),
                req("5.2 PUT Produto", "PUT", "/produtos/{{produtoId}}", c_produto,
                    [status(200, "OK"), json_ct, "const j = pm.response.json();",
                     T("Nome mantido", "pm.expect(j.nome).to.eql(%s)" % V("nomeProduto"))]),
                req("5.3 POST Pedido extra (para os testes seguintes)", "POST", "/pedidos",
                    '{\n  "clienteId": {{clienteId}},\n  "produtoId": {{produtoId}},\n  "quantidade": 10\n}',
                    [status(201, "Created"), salvar("pedidoExtraId")]),
                req("5.4 PUT Pedido (quantidade 10 para 12)", "PUT", "/pedidos/{{pedidoExtraId}}",
                    '{\n  "clienteId": {{clienteId}},\n  "produtoId": {{produtoId}},\n  "quantidade": 12\n}',
                    [status(200, "OK"), "const j = pm.response.json();",
                     T("Quantidade atualizada para 12", "pm.expect(j.quantidade).to.eql(12)")]),
                req("5.5 DELETE Cliente com pedido (409)", "DELETE", "/clientes/{{clienteId}}", None,
                    t_erro(409, "Conflict", [T("Mensagem cita pedidos vinculados", 'pm.expect(j.mensagem).to.include("pedidos vinculados")')])),
                req("5.6 DELETE Produto com pedido (409)", "DELETE", "/produtos/{{produtoId}}", None, t_erro(409, "Conflict")),
                req("5.7 DELETE Pedido extra (limpeza)", "DELETE", "/pedidos/{{pedidoExtraId}}", None, t_204),
            ]},
            {"name": "6 - Extras: validações e erros",
             "description": "Casos negativos: dados inválidos (400), recurso inexistente (404) e produto sem estoque (422).", "item": [
                req("6.1 POST Cliente sem nome (400)", "POST", "/clientes", '{\n  "nome": "",\n  "clienteDesde": "{{clienteDesde}}"\n}',
                    t_erro(400, "Bad Request", [T("Erro aponta o campo nome", 'pm.expect(j.campos).to.have.property("nome")')])),
                req("6.2 POST Produto com preço negativo (400)", "POST", "/produtos",
                    '{\n  "nome": "Produto invalido",\n  "preco": -5,\n  "estoque": true\n}',
                    t_erro(400, "Bad Request", [T("Erro aponta o campo preco", 'pm.expect(j.campos).to.have.property("preco")')])),
                req("6.3 POST Pedido com quantidade 0 (400)", "POST", "/pedidos",
                    '{\n  "clienteId": {{clienteId}},\n  "produtoId": {{produtoId}},\n  "quantidade": 0\n}',
                    t_erro(400, "Bad Request", [T("Erro aponta o campo quantidade", 'pm.expect(j.campos).to.have.property("quantidade")')])),
                req("6.4 POST Cliente com JSON malformado (400)", "POST", "/clientes", '{ "nome": ',
                    t_erro(400, "Bad Request")),
                req("6.5 POST Pedido com cliente inexistente (404)", "POST", "/pedidos",
                    '{\n  "clienteId": 999999,\n  "produtoId": {{produtoId}},\n  "quantidade": 1\n}', t_erro(404, "Not Found")),
                req("6.6 POST Produto sem estoque (201)", "POST", "/produtos",
                    '{\n  "nome": "Baozi Esgotado",\n  "preco": 9.90,\n  "estoque": false\n}',
                    [status(201, "Created"), salvar("produtoSemEstoqueId")]),
                req("6.7 POST Pedido de produto sem estoque (422)", "POST", "/pedidos",
                    '{\n  "clienteId": {{clienteId}},\n  "produtoId": {{produtoSemEstoqueId}},\n  "quantidade": 1\n}',
                    t_erro(422, "Unprocessable Entity", [T("Mensagem cita falta de estoque", 'pm.expect(j.mensagem).to.include("sem estoque")')])),
                req("6.8 GET Cliente inexistente (404)", "GET", "/clientes/999999", None, t_erro(404, "Not Found")),
                req("6.9 GET Produto inexistente (404)", "GET", "/produtos/999999", None, t_erro(404, "Not Found")),
                req("6.10 DELETE Pedido inexistente (404)", "DELETE", "/pedidos/999999", None, t_erro(404, "Not Found")),
                req("6.11 DELETE Produto sem estoque (limpeza)", "DELETE", "/produtos/{{produtoSemEstoqueId}}", None, t_204),
            ]},
        ]}
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(col, f, indent=2, ensure_ascii=False)

    env = {"id": "baozi-store-local", "name": "Baozi Store - Local", "_postman_variable_scope": "environment",
           "values": [{"key": "baseUrl", "value": BASE_URL, "type": "default", "enabled": True}]}
    with open(os.path.join(os.path.dirname(caminho), "Baozi_Store_Local.postman_environment.json"), "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2, ensure_ascii=False)

# ----------------------------------------------------------------------------
# 3) PDF
# ----------------------------------------------------------------------------
AZUL = colors.HexColor("#0b2a5b"); DOURADO = colors.HexColor("#e0a418"); VERM = colors.HexColor("#c00000")
ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=10.5, leading=15, alignment=TA_JUSTIFY)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=9, leading=12, alignment=0)
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=16, textColor=AZUL, spaceBefore=6, spaceAfter=8, keepWithNext=1)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, textColor=AZUL, spaceBefore=10, spaceAfter=5, keepWithNext=1)
CAP = ParagraphStyle("cap", parent=BODY, fontSize=9, textColor=colors.HexColor("#444"), alignment=TA_CENTER, spaceAfter=10)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=9, leading=11.5, alignment=0)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
CODE = ParagraphStyle("code", fontName="Courier", fontSize=8.6, leading=11, backColor=colors.HexColor("#f4f4f4"),
                      borderPadding=5, leftIndent=4, spaceBefore=3, spaceAfter=8)

def tabela(dados, larguras, cab=True):
    linhas = []
    for i, l in enumerate(dados):
        linhas.append([c if isinstance(c, Flowable) else Paragraph(str(c), CELLB if (cab and i == 0) else CELL) for c in l])
    t = Table(linhas, colWidths=larguras, repeatRows=1 if cab else 0)
    est = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8b8b8")),
           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if cab:
        est += [("BACKGROUND", (0, 0), (-1, 0), AZUL)]
        est += [("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f6fc")])]
    t.setStyle(TableStyle(est))
    return t

class Moldura(Flowable):
    """Quadro tracejado para o print que ainda não foi inserido."""
    def __init__(self, largura, altura, texto):
        super().__init__(); self.w, self.h, self.texto = largura, altura, texto
    def wrap(self, aw, ah): return self.w, self.h
    def draw(self):
        c = self.canv; c.setStrokeColor(VERM); c.setDash(4, 3); c.setLineWidth(1)
        c.rect(0, 0, self.w, self.h); c.setDash()
        c.setFillColor(VERM); c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.w / 2, self.h / 2 + 6, "INSERIR PRINT DO POSTMAN AQUI")
        c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#555"))
        c.drawCentredString(self.w / 2, self.h / 2 - 8, self.texto)

def achar_print(base):
    for ext in (".png", ".jpg", ".jpeg"):
        p = os.path.join(PASTA_PRINTS, base + ext)
        if os.path.exists(p): return p
    return None

def bloco_print(titulo, arquivo, req_txt, esperado, secao=None):
    itens = ([Paragraph(secao, H1)] if secao else []) + [Paragraph(titulo, H2),
             Paragraph(f"<b>Requisição:</b> <font face='Courier'>{req_txt}</font>", SMALL),
             Paragraph(f"<b>Resultado esperado:</b> {esperado}", SMALL), Spacer(1, 4)]
    p = achar_print(arquivo)
    if p:
        from reportlab.lib.utils import ImageReader
        iw, ih = ImageReader(p).getSize()
        w = 16.6 * cm; h = w * ih / iw
        if h > 12.5 * cm: h = 12.5 * cm; w = h * iw / ih
        itens.append(Image(p, width=w, height=h))
    else:
        itens.append(Moldura(16.6 * cm, 6.2 * cm, f"arquivo sugerido: prints/{arquivo}.png"))
    itens.append(Spacer(1, 8))
    return KeepTogether(itens)

def cabecalho_rodape(canv, doc):
    canv.saveState()
    w, h = canv._pagesize
    canv.setFillColor(AZUL); canv.rect(0, h - 1.15 * cm, w, 0.55 * cm, fill=1, stroke=0)
    canv.setFillColor(DOURADO); canv.rect(0, h - 1.25 * cm, w, 0.10 * cm, fill=1, stroke=0)
    canv.setFillColor(colors.white); canv.setFont("Helvetica-Bold", 8.5)
    canv.drawString(2 * cm, h - 0.97 * cm, "UNINTER  |  Desenvolvimento Web Back-End  |  Atividade Prática")
    canv.drawRightString(w - 2 * cm, h - 0.97 * cm, "API REST – Baozi Store")
    canv.setFillColor(colors.HexColor("#555")); canv.setFont("Helvetica", 8.5)
    canv.drawString(2 * cm, 1.1 * cm, f"{NOME_RU}")
    canv.drawRightString(w - 2 * cm, 1.1 * cm, f"Página {doc.page + args.offset}")
    canv.restoreState()

def capa(canv, doc):
    canv.saveState()
    w, h = A4
    canv.setFillColor(AZUL); canv.rect(0, h - 7.2 * cm, w, 7.2 * cm, fill=1, stroke=0)
    canv.setFillColor(DOURADO); canv.rect(0, h - 7.5 * cm, w, 0.3 * cm, fill=1, stroke=0)
    canv.setFillColor(colors.white); canv.setFont("Helvetica-Bold", 30)
    canv.drawString(2.5 * cm, h - 3.6 * cm, "UNINTER")
    canv.setFont("Helvetica", 11); canv.drawString(2.5 * cm, h - 4.3 * cm, "CENTRO UNIVERSITÁRIO")
    canv.setFont("Helvetica", 10); canv.drawString(2.5 * cm, h - 5.8 * cm, "Desenvolvimento Web Back-End  |  Atividade Prática")
    canv.restoreState()

def montar_pdf(caminho, png_diagrama):
    doc = BaseDocTemplate(caminho, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                          topMargin=2.2 * cm, bottomMargin=2 * cm,
                          title="Trabalho de Desenvolvimento Web Back-End – API REST Baozi Store",
                          author=NOME_RU, subject="API REST – Baozi Store")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    frame_capa = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 6.2 * cm, id="fc")
    _capa_pt = PageTemplate(id="capa", frames=[frame_capa], onPage=capa, autoNextPageTemplate="normal")
    _normal_pt = PageTemplate(id="normal", frames=[frame], onPage=cabecalho_rodape)
    doc.addPageTemplates([_normal_pt if args.sem_capa else _capa_pt,
                          _capa_pt if args.sem_capa else _normal_pt,
                          PageTemplate(id="paisagem", pagesize=landscape(A4), onPage=cabecalho_rodape,
                                       frames=[Frame(2 * cm, 2 * cm, landscape(A4)[0] - 4 * cm,
                                                     landscape(A4)[1] - 4.3 * cm, id="fp")])])
    W = doc.width
    S = []

    # ---- CAPA ----
    S += [Spacer(1, 1.2 * cm),
          Paragraph("<font size=26 color='#c00000'>TRABALHO DE DESENVOLVIMENTO WEB BACK-END</font>",
                    ParagraphStyle("t", parent=BODY, alignment=0, leading=32)),
          Spacer(1, 10), Paragraph("<b>API REST – Baozi Store</b>", ParagraphStyle("st", parent=BODY, fontSize=17, alignment=0)),
          Spacer(1, 22),
          tabela([["Aluno(a)", (args.nome_completo or args.nome)], ["RU", args.ru], ["Disciplina", "Desenvolvimento Web Back-End"],
                  ["Professora", "Profa. Luciane Kanashiro, Me"],
                  ["Tecnologias", "Java 17, Spring Boot, Spring Data JPA, H2 / MySQL, Postman"],
                  ["Repositório", f"<font color='#0b2a5b'>{REPO}</font>"]],
                 [3.6 * cm, W - 3.6 * cm], cab=False),
          Spacer(1, 18)]
    S.append(Paragraph("<b>Sumário</b>", H2))
    for i in ["1. Descrição de uma situação fictícia", "2. Diagrama de caso de uso (UML)",
              "3. Especificação da API desenvolvida (entidades, campos e endpoints)",
              "4. Prints do Postman", "5. Link do repositório (código-fonte)"]:
        S.append(Paragraph(i, BODY))
    S.append(PageBreak())

    if args.sem_capa:
        _i = next(k for k, f in enumerate(S) if isinstance(f, PageBreak))
        S = S[_i + 1:]

    # ---- 1. SITUAÇÃO FICTÍCIA ----
    S.append(Paragraph("1. Descrição de uma situação fictícia", H1))
    S.append(Paragraph(
        f"A <b>Baozi Store</b> é uma pequena loja que vende <b>pão chinês</b>. Para melhorar a organização do negócio, "
        f"foi criado um sistema simples para controlar clientes, produtos e pedidos. Um cliente chamado "
        f"<b><u>{NOME_RU}</u></b> realizou seu cadastro no sistema. O produto vendido pela loja chama-se "
        f"<b><u>{PRODUTO}</u></b> e é vendido por unidade. Em um determinado momento, o cliente realizou um pedido de "
        f"<b><u>{QTD}</u></b> unidades do produto. O sistema registra o cliente, o produto comprado e a quantidade "
        f"solicitada, facilitando o controle da loja.", BODY))
    S.append(Spacer(1, 8))
    S.append(Paragraph(
        "Para facilitar a conferência com os prints do Postman (seção 4), os dados da situação descrita são "
        "resumidos abaixo. Esses mesmos valores são enviados nas requisições e aparecem nas respostas da API.", BODY))
    S.append(Spacer(1, 6))
    S.append(tabela([["Entidade", "Campo", "Valor na situação fictícia"],
                     ["Cliente", "nome", NOME_RU], ["Cliente", "clienteDesde", DATA],
                     ["Produto", "nome", PRODUTO], ["Produto", "preco", f"R$ {PRECO} por unidade"],
                     ["Produto", "estoque", "true (disponível)"],
                     ["Pedido", "cliente / produto", f"{NOME_RU} / {PRODUTO}"],
                     ["Pedido", "quantidade", f"{QTD} unidades"]],
                    [3 * cm, 4 * cm, W - 7 * cm]))
    S.append(Spacer(1, 6))
    S.append(Paragraph(f"Valor total do pedido (informativo): {QTD} × R$ {PRECO} = "
                       f"<b>R$ {QTD * float(PRECO):.2f}</b>.", SMALL))

    # ---- 2. CASO DE USO (página em paisagem) ----
    S.append(NextPageTemplate("paisagem"))
    S.append(PageBreak())
    S.append(Paragraph("2. Diagrama de caso de uso (UML)", H1))
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(png_diagrama).getSize()
    LW = landscape(A4)[0] - 4 * cm
    hmax = 12.6 * cm
    w = LW; h = w * ih / iw
    if h > hmax: h = hmax; w = h * iw / ih
    S.append(Image(png_diagrama, width=w, height=h))
    S.append(Paragraph("Figura 1 – Diagrama de Casos de Uso da API REST Baozi Store", CAP))
    S.append(Paragraph(
        "Notação UML padrão: o <b>ator principal</b> é o <b>Usuário da API</b> (fora da fronteira do sistema) e os "
        "<b>casos de uso</b> (elipses) ficam dentro da fronteira <i>API REST – Baozi Store</i>, cobrindo o CRUD de Cliente, "
        "Produto e Pedido. A atualização (PUT) é opcional no enunciado e foi implementada como extra. O relacionamento "
        "<i>«include»</i> indica que registrar um pedido sempre executa a validação do cliente, do produto e do estoque.", SMALL))
    S.append(NextPageTemplate("normal"))

    # ---- 3. ESPECIFICAÇÃO ----
    S.append(PageBreak())
    S.append(Paragraph("3. Especificação da API desenvolvida", H1))
    S.append(Paragraph("3.1 Tecnologias e arquitetura", H2))
    S.append(Paragraph(
        "A API foi desenvolvida em <b>Java 17</b> com <b>Spring Boot</b>, usando <b>Spring Data JPA</b> (Hibernate) para a persistência "
        "em <b>banco relacional</b> e <b>JSON</b> como formato de troca de dados, seguindo o padrão <b>MVC do Spring</b>. "
        "O projeto está organizado nos pacotes abaixo (arquitetura mínima exigida + <i>dto</i>):", BODY))
    S.append(Spacer(1, 4))
    S.append(tabela([["Pacote", "Responsabilidade"],
                     ["br.com.baozistore.model", "Entidades JPA: Cliente, Produto e Pedido"],
                     ["br.com.baozistore.repository", "Interfaces JpaRepository (acesso ao banco)"],
                     ["br.com.baozistore.controller", "Controllers REST (ClienteController, ProdutoController, PedidoController) e tratamento de erros"],
                     ["br.com.baozistore.dto", "PedidoRequest: corpo de entrada do pedido (clienteId, produtoId, quantidade)"]],
                    [5.6 * cm, W - 5.6 * cm]))
    S.append(Paragraph("3.2 Banco de dados", H2))
    S.append(Paragraph(
        "O banco padrão é o <b>H2</b> (relacional, em arquivo <font face='Courier'>./data/baozidb</font>), que dispensa instalação. "
        "Também há o perfil <b>mysql</b> (<font face='Courier'>application-mysql.properties</font>) para MySQL/MariaDB, ativado com "
        "<font face='Courier'>-Dspring-boot.run.profiles=mysql</font>. As tabelas são criadas automaticamente pelo Hibernate "
        "(<font face='Courier'>spring.jpa.hibernate.ddl-auto=update</font>). A tabela <i>pedido</i> possui duas chaves estrangeiras: "
        "<font face='Courier'>cliente_id → cliente.id</font> e <font face='Courier'>produto_id → produto.id</font> "
        "(relacionamentos N:1, conforme o DER do enunciado).", BODY))

    S.append(Paragraph("3.3 Entidades criadas e campos", H2))
    S.append(Paragraph("<b>Cliente</b> (tabela <font face='Courier'>cliente</font>)", BODY))
    S.append(tabela([["Campo", "Tipo Java", "Coluna", "Regras"],
                     ["id", "Long", "id", "Chave primária, auto incremento"],
                     ["nome", "String", "nome", "Obrigatório (@NotBlank)"],
                     ["clienteDesde", "LocalDate", "cliente_desde", "Se omitido, assume a data atual"]],
                    [3 * cm, 3 * cm, 3.4 * cm, W - 9.4 * cm]))
    S.append(Spacer(1, 6))
    S.append(Paragraph("<b>Produto</b> (tabela <font face='Courier'>produto</font>)", BODY))
    S.append(tabela([["Campo", "Tipo Java", "Coluna", "Regras"],
                     ["id", "Long", "id", "Chave primária, auto incremento"],
                     ["nome", "String", "nome", "Obrigatório (@NotBlank)"],
                     ["preco", "BigDecimal", "preco", "Obrigatório, maior que zero, DECIMAL(10,2)"],
                     ["estoque", "Boolean", "estoque", "Obrigatório; true = disponível, false = sem estoque"]],
                    [3 * cm, 3 * cm, 3.4 * cm, W - 9.4 * cm]))
    S.append(Spacer(1, 6))
    S.append(Paragraph("<b>Pedido</b> (tabela <font face='Courier'>pedido</font>)", BODY))
    S.append(tabela([["Campo", "Tipo Java", "Coluna", "Regras"],
                     ["id", "Long", "id", "Chave primária, auto incremento"],
                     ["clienteId", "Long", "cliente_id (FK)", "Obrigatório; referencia cliente (@ManyToOne)"],
                     ["produtoId", "Long", "produto_id (FK)", "Obrigatório; referencia produto (@ManyToOne)"],
                     ["quantidade", "Integer", "quantidade", "Obrigatório, mínimo 1"]],
                    [3 * cm, 3 * cm, 3.4 * cm, W - 9.4 * cm]))
    S.append(Spacer(1, 4))
    S.append(Paragraph("Na resposta JSON, o pedido traz <font face='Courier'>clienteId</font> e <font face='Courier'>produtoId</font> e também os "
                       "objetos <font face='Courier'>cliente</font> e <font face='Courier'>produto</font> completos, o que permite ver nome, "
                       "produto e quantidade no mesmo print.", SMALL))

    S.append(Paragraph("3.4 Endpoints implementados", H2))
    S.append(Paragraph("Todos os endpoints trocam dados em JSON (<font face='Courier'>Content-Type: application/json</font>). "
                       f"URL base: <font face='Courier'>{BASE_URL}</font>.", BODY))
    S.append(Spacer(1, 4))
    def eps(rec, corpo):
        return [["Método", "Endpoint", "Descrição", "Sucesso / Erros"],
                ["POST", f"/{rec}", f"Cria {rec[:-1]}. Corpo: {corpo}", "201 Created / 400"],
                ["GET", f"/{rec}/{{id}}", "Consulta por ID", "200 OK / 404"],
                ["GET", f"/{rec}", "Lista todos", "200 OK"],
                ["DELETE", f"/{rec}/{{id}}", "Apaga por ID", "204 No Content / 404" + (" / 409" if rec != "pedidos" else "")],
                ["PUT (opc.)", f"/{rec}/{{id}}", "Atualiza (opcional)", "200 OK / 400 / 404"]]
    cw = [2.2 * cm, 3.4 * cm, W - 2.2 * cm - 3.4 * cm - 4 * cm, 4 * cm]
    S.append(Paragraph("<b>Clientes</b>", BODY))
    S.append(tabela(eps("clientes", "nome, clienteDesde"), cw)); S.append(Spacer(1, 6))
    S.append(Paragraph("<b>Produtos</b>", BODY))
    S.append(tabela(eps("produtos", "nome, preco, estoque"), cw)); S.append(Spacer(1, 6))
    S.append(Paragraph("<b>Pedidos</b>", BODY))
    S.append(tabela(eps("pedidos", "clienteId, produtoId, quantidade"), cw)); S.append(Spacer(1, 8))
    S.append(Paragraph(
        "<b>Regras de negócio e erros:</b> o pedido só é criado se o cliente e o produto existirem (senão <b>404</b>) e se o produto "
        "estiver em estoque (senão <b>422</b>). Um cliente ou produto com pedidos vinculados não pode ser apagado (<b>409 Conflict</b>), "
        "preservando a integridade referencial. Dados inválidos retornam <b>400</b> com a lista de campos com erro.", BODY))

    S.append(Paragraph("3.5 Exemplos de corpo das requisições (JSON)", H2))
    mono = ParagraphStyle("mono", parent=CELL, fontName="Courier", fontSize=8.6, leading=11)
    ex = [["Requisição", "Corpo (JSON)"],
          ["POST /clientes", Paragraph(f'{{"nome": "{NOME_RU}", "clienteDesde": "{DATA}"}}', mono)],
          ["POST /produtos", Paragraph(f'{{"nome": "{PRODUTO}", "preco": {PRECO}, "estoque": true}}', mono)],
          ["POST /pedidos", Paragraph(f'{{"clienteId": 1, "produtoId": 1, "quantidade": {QTD}}}', mono)]]
    S.append(tabela(ex, [3.4 * cm, W - 3.4 * cm]))

    # ---- 4. PRINTS ----
    S.append(Paragraph("4. Prints do Postman", H1))
    S.append(Paragraph(
        f"Os testes foram executados com a API em <font face='Courier'>{BASE_URL}</font>. Em todos os prints aparecem as informações da "
        f"situação fictícia: cliente <b>{NOME_RU}</b>, produto <b>{PRODUTO}</b> e pedido de <b>{QTD}</b> unidades.", BODY))
    S.append(Spacer(1, 6))
    S.append(bloco_print("4.1.1 POST – Criar Cliente", "01_post_cliente", "POST /clientes",
                         f"status 201 Created; JSON com id e nome “{NOME_RU}”.", secao="4.1 POST de cada entidade"))
    S.append(bloco_print("4.1.2 POST – Criar Produto", "02_post_produto", "POST /produtos",
                         f"status 201 Created; JSON com id, nome “{PRODUTO}”, preço {PRECO} e estoque true."))
    S.append(bloco_print("4.1.3 POST – Criar Pedido", "03_post_pedido", "POST /pedidos",
                         f"status 201 Created; JSON com cliente “{NOME_RU}”, produto “{PRODUTO}” e quantidade {QTD}."))
    S.append(bloco_print("4.2.1 GET – Listar Clientes", "04_get_clientes", "GET /clientes", "status 200 OK; lista com o cliente cadastrado.", secao="4.2 GET geral (listagem de todas as entidades)"))
    S.append(bloco_print("4.2.2 GET – Listar Produtos", "05_get_produtos", "GET /produtos", "status 200 OK; lista com o produto cadastrado."))
    S.append(bloco_print("4.2.3 GET – Listar Pedidos", "06_get_pedidos", "GET /pedidos", "status 200 OK; lista com o pedido registrado."))
    S.append(bloco_print("4.3.1 GET – Consultar Cliente por ID", "07_get_cliente_id", "GET /clientes/1", f"status 200 OK; cliente “{NOME_RU}”.", secao="4.3 GET por ID"))
    S.append(bloco_print("4.3.2 GET – Consultar Produto por ID", "08_get_produto_id", "GET /produtos/1", f"status 200 OK; produto “{PRODUTO}”."))
    S.append(bloco_print("4.3.3 GET – Consultar Pedido por ID", "09_get_pedido_id", "GET /pedidos/1", f"status 200 OK; pedido com {QTD} unidades."))
    S.append(bloco_print("4.4.1 DELETE – Apagar Pedido", "10_delete_pedido", "DELETE /pedidos/1", "status 204 No Content (sem corpo).", secao="4.4 DELETE"))
    S.append(bloco_print("4.4.2 Confirmação – GET do pedido apagado", "11_get_pedido_apos_delete", "GET /pedidos/1",
                         "status 404 Not Found com mensagem “Pedido não encontrado: 1”, comprovando a exclusão."))

    # ---- 5. REPO ----
    S.append(PageBreak())
    S.append(Paragraph("5. Link do repositório (código-fonte)", H1))
    S.append(Paragraph(f"Repositório do projeto: <font color='#0b2a5b'><u>{REPO}</u></font>", BODY))
    S.append(Spacer(1, 8))
    S.append(Paragraph("<b>Como executar:</b>", BODY))
    S.append(Preformatted("git clone " + REPO + "\ncd baozi-store\nmvn spring-boot:run\n\n"
                          "# (opcional) usando MySQL:\nmvn spring-boot:run -Dspring-boot.run.profiles=mysql", CODE))
    S.append(Paragraph("A API sobe em http://localhost:8080. Requisitos: JDK 17+ e Maven (ou use o Maven integrado da IDE).", BODY))
    doc.build(S)

if __name__ == "__main__":
    png = os.path.join(AQUI, "diagrama_caso_de_uso.png")
    gerar_diagrama(png)
    gerar_postman(os.path.join(AQUI, "Baozi_Store_Postman_Collection.json"))
    montar_pdf(os.path.join(AQUI, "miolo.pdf" if args.sem_capa else "Trabalho_Baozi_Store.pdf"), png)
    print("OK: diagrama, coleção Postman e PDF gerados em", AQUI)
