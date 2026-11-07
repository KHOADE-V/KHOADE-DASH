"""Carrega a lista de sites a monitorar a partir de um arquivo JSON."""

import json

EXEMPLO = [
    {"nome": "Meu site", "tipo": "http", "url": "https://exemplo.com"},
    {"nome": "Banco de dados", "tipo": "tcp", "host": "localhost", "porta": 5432},
]


def carregar(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        sites = json.load(arquivo)
    if not isinstance(sites, list):
        raise ValueError("o arquivo de configuração deve conter uma lista de sites")
    for i, site in enumerate(sites):
        if "nome" not in site:
            raise ValueError(f"site na posição {i} não tem 'nome'")
        tipo = site.get("tipo", "http")
        if tipo == "http" and "url" not in site:
            raise ValueError(f"site '{site['nome']}' é do tipo http mas não tem 'url'")
        if tipo == "tcp" and ("host" not in site or "porta" not in site):
            raise ValueError(f"site '{site['nome']}' é do tipo tcp mas falta 'host' ou 'porta'")
    return sites
