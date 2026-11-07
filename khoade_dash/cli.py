"""Interface de linha de comando do KHOADE Dash."""

import argparse
import sys
import time

from . import __version__
from .checker import verificar_todos
from .config import carregar
from .report import gerar_html


def executar_uma_vez(args):
    sites = carregar(args.config)
    resultados = verificar_todos(sites, timeout=args.timeout)
    html = gerar_html(resultados)
    with open(args.saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)
    for r in resultados:
        marca = "OK " if r.ok else "FALHA"
        print(f"[{marca}] {r.nome} ({r.url}) — {r.latencia_ms} ms")
    falhas = sum(1 for r in resultados if not r.ok)
    print(f"\n{len(resultados) - falhas}/{len(resultados)} no ar. Painel salvo em {args.saida}")
    return 1 if falhas else 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="khoade-dash", description="Painel de status de sites.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-c", "--config", default="sites.json", help="arquivo JSON com os sites")
    parser.add_argument("-o", "--saida", default="painel.html", help="arquivo HTML de saída")
    parser.add_argument("-t", "--timeout", type=float, default=5.0, help="timeout por site, em segundos")
    parser.add_argument(
        "-i", "--intervalo", type=float, default=0,
        help="repete a checagem a cada N segundos (0 = roda uma vez só)",
    )
    args = parser.parse_args(argv)

    try:
        if args.intervalo <= 0:
            return executar_uma_vez(args)
        print(f"Checando a cada {args.intervalo}s. Ctrl+C para parar.")
        while True:
            executar_uma_vez(args)
            time.sleep(args.intervalo)
    except FileNotFoundError:
        print(f"erro: arquivo de configuração não encontrado: {args.config}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nencerrado.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
