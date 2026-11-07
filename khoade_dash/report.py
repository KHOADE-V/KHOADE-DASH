"""Gera o painel em HTML a partir dos resultados das checagens."""

from datetime import datetime, timezone
from html import escape

CSS = """
:root {
  --bg: #0b0f14; --surface: #121922; --border: #223041; --text: #e6edf3;
  --muted: #93a1b1; --ok: #3ddc97; --fail: #ef6a6a; --sans: system-ui, sans-serif;
}
@media (prefers-color-scheme: light) {
  :root { --bg: #f6f8fa; --surface: #fff; --border: #d5dde5; --text: #1f2328;
          --muted: #59636e; --ok: #0a7d50; --fail: #c22d2d; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--sans); }
main { width: min(720px, 100% - 32px); margin: 40px auto; }
h1 { font-size: 1.5rem; margin-bottom: 4px; }
.atualizado { color: var(--muted); font-size: 0.85rem; margin-bottom: 24px; }
.resumo { display: flex; gap: 12px; margin-bottom: 20px; }
.resumo div { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
              padding: 12px 16px; flex: 1; }
.resumo .valor { font-size: 1.4rem; font-weight: 700; }
ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
li { display: flex; align-items: center; gap: 12px; background: var(--surface);
     border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px; }
.bolinha { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.ok .bolinha { background: var(--ok); }
.fail .bolinha { background: var(--fail); }
.info { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.info .nome { font-weight: 600; overflow-wrap: anywhere; }
.info .detalhe { font-size: 0.8rem; color: var(--muted); overflow-wrap: anywhere; }
.latencia { font-variant-numeric: tabular-nums; color: var(--muted); font-size: 0.9rem; white-space: nowrap; }
"""


def gerar_html(resultados):
    agora = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
    total = len(resultados)
    ok = sum(1 for r in resultados if r.ok)

    itens = []
    for r in resultados:
        classe = "ok" if r.ok else "fail"
        detalhe = r.erro if r.erro else (f"HTTP {r.status_code}" if r.status_code else "conectado")
        latencia = f"{r.latencia_ms:.0f} ms" if r.latencia_ms is not None else "—"
        itens.append(
            f'<li class="{classe}"><span class="bolinha"></span>'
            f'<span class="info"><span class="nome">{escape(r.nome)}</span>'
            f'<span class="detalhe">{escape(r.url)} · {escape(detalhe)}</span></span>'
            f'<span class="latencia">{escape(latencia)}</span></li>'
        )

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KHOADE Dash</title>
<style>{CSS}</style></head>
<body><main>
<h1>KHOADE Dash</h1>
<p class="atualizado">Atualizado em {agora}</p>
<div class="resumo">
  <div><div class="valor">{ok}/{total}</div><div>no ar</div></div>
</div>
<ul>
{"".join(itens)}
</ul>
</main></body></html>
"""
