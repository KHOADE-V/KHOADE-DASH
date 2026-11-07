# KHOADE Dash

Painel de status (uptime e latência) para seus sites e serviços, rodando localmente. Só biblioteca padrão do Python, sem dependências.

## Como usar

1. Copie o arquivo de exemplo e edite com os seus sites:

   ```bash
   cp sites.exemplo.json sites.json
   ```

   ```json
   [
     { "nome": "Meu site", "tipo": "http", "url": "https://exemplo.com" },
     { "nome": "Banco de dados", "tipo": "tcp", "host": "localhost", "porta": 5432 }
   ]
   ```

   `tipo` pode ser `http` (faz um GET e considera 2xx/3xx como no ar) ou `tcp` (só testa se a porta abre — bom para bancos de dados, SSH etc.).

2. Rode uma checagem:

   ```bash
   python -m khoade_dash
   ```

   Isso gera `painel.html` — abra no navegador para ver o status.

3. Para checar continuamente:

   ```bash
   python -m khoade_dash --intervalo 60
   ```

## Opções

```
-c, --config     arquivo JSON com os sites (padrão: sites.json)
-o, --saida      arquivo HTML de saída (padrão: painel.html)
-t, --timeout    timeout por site, em segundos (padrão: 5)
-i, --intervalo  repete a cada N segundos (padrão: 0, roda uma vez só)
```

O comando também termina com código de saída diferente de zero se algum site estiver fora do ar — útil para rodar num cron e ser avisado.

## Testes

```bash
python -m unittest discover -s tests -v
```

## Licença

MIT.
