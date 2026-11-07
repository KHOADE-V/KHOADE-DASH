"""Verificação de sites: só biblioteca padrão (urllib), sem dependências."""

import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

USER_AGENT = "KHOADE-Dash/0.1 (+https://github.com/KHOADE-V/KHOADE-DASH)"


@dataclass
class Resultado:
    nome: str
    url: str
    ok: bool
    status_code: Optional[int]
    latencia_ms: Optional[float]
    erro: Optional[str]


def verificar_http(nome, url, timeout=5.0):
    """Faz um GET e mede o tempo de resposta. Considera 2xx/3xx como 'ok'."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            latencia = (time.perf_counter() - inicio) * 1000
            codigo = response.getcode()
            return Resultado(nome, url, codigo < 400, codigo, round(latencia, 1), None)
    except urllib.error.HTTPError as error:
        latencia = (time.perf_counter() - inicio) * 1000
        return Resultado(nome, url, False, error.code, round(latencia, 1), str(error))
    except (urllib.error.URLError, socket.timeout, OSError) as error:
        latencia = (time.perf_counter() - inicio) * 1000
        return Resultado(nome, url, False, None, round(latencia, 1), str(error.reason) if hasattr(error, "reason") else str(error))


def verificar_tcp(nome, host, porta, timeout=5.0):
    """Tenta abrir uma conexão TCP (bom para serviços sem HTTP: banco, SSH etc.)."""
    url = f"{host}:{porta}"
    inicio = time.perf_counter()
    try:
        with socket.create_connection((host, porta), timeout=timeout):
            latencia = (time.perf_counter() - inicio) * 1000
            return Resultado(nome, url, True, None, round(latencia, 1), None)
    except OSError as error:
        latencia = (time.perf_counter() - inicio) * 1000
        return Resultado(nome, url, False, None, round(latencia, 1), str(error))


def verificar_site(site, timeout=5.0):
    """Recebe um dict de configuração e despacha para o verificador certo."""
    tipo = site.get("tipo", "http")
    nome = site.get("nome", site.get("url", site.get("host", "?")))
    if tipo == "tcp":
        return verificar_tcp(nome, site["host"], int(site["porta"]), timeout)
    return verificar_http(nome, site["url"], timeout)


def verificar_todos(sites, timeout=5.0):
    return [verificar_site(site, timeout) for site in sites]
