import json
import socket
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from khoade_dash.checker import verificar_http, verificar_tcp, verificar_todos
from khoade_dash.config import carregar
from khoade_dash.report import gerar_html


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/ok":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(500)
            self.end_headers()

    def log_message(self, *args):
        pass


class ServidorDeTeste:
    def __enter__(self):
        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def porta_livre():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class CheckerTests(unittest.TestCase):
    def test_http_sucesso(self):
        with ServidorDeTeste() as servidor:
            resultado = verificar_http("teste", f"http://127.0.0.1:{servidor.port}/ok")
            self.assertTrue(resultado.ok)
            self.assertEqual(resultado.status_code, 200)

    def test_http_falha_5xx(self):
        with ServidorDeTeste() as servidor:
            resultado = verificar_http("teste", f"http://127.0.0.1:{servidor.port}/erro")
            self.assertFalse(resultado.ok)
            self.assertEqual(resultado.status_code, 500)

    def test_http_conexao_recusada(self):
        porta = porta_livre()
        resultado = verificar_http("teste", f"http://127.0.0.1:{porta}/", timeout=1)
        self.assertFalse(resultado.ok)
        self.assertIsNotNone(resultado.erro)

    def test_tcp_sucesso(self):
        with ServidorDeTeste() as servidor:
            resultado = verificar_tcp("teste", "127.0.0.1", servidor.port)
            self.assertTrue(resultado.ok)

    def test_tcp_falha(self):
        resultado = verificar_tcp("teste", "127.0.0.1", porta_livre(), timeout=1)
        self.assertFalse(resultado.ok)

    def test_verificar_todos_mistura_tipos(self):
        with ServidorDeTeste() as servidor:
            sites = [
                {"nome": "web", "tipo": "http", "url": f"http://127.0.0.1:{servidor.port}/ok"},
                {"nome": "tcp", "tipo": "tcp", "host": "127.0.0.1", "porta": servidor.port},
            ]
            resultados = verificar_todos(sites)
            self.assertTrue(all(r.ok for r in resultados))


class ConfigTests(unittest.TestCase):
    def test_carrega_lista_valida(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "sites.json"
            caminho.write_text(json.dumps([{"nome": "x", "url": "http://x"}]), encoding="utf-8")
            sites = carregar(caminho)
            self.assertEqual(len(sites), 1)

    def test_rejeita_site_sem_nome(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "sites.json"
            caminho.write_text(json.dumps([{"url": "http://x"}]), encoding="utf-8")
            with self.assertRaises(ValueError):
                carregar(caminho)

    def test_rejeita_http_sem_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "sites.json"
            caminho.write_text(json.dumps([{"nome": "x"}]), encoding="utf-8")
            with self.assertRaises(ValueError):
                carregar(caminho)


class ReportTests(unittest.TestCase):
    def test_html_contem_nomes_e_resumo(self):
        from khoade_dash.checker import Resultado

        resultados = [
            Resultado("site a", "http://a", True, 200, 10.0, None),
            Resultado("site b", "http://b", False, None, 5.0, "timeout"),
        ]
        html = gerar_html(resultados)
        self.assertIn("site a", html)
        self.assertIn("site b", html)
        self.assertIn("1/2", html)


if __name__ == "__main__":
    unittest.main()
