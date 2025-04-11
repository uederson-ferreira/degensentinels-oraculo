# listar_apolices.py

import os
import json
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table

APOLICE_DIR = "oracle-backend/apolices"
console = Console()

def listar_apolices():
    if not os.path.exists(APOLICE_DIR):
        console.print("[red]❌ Pasta de apólices não encontrada.[/red]")
        return

    arquivos = [f for f in os.listdir(APOLICE_DIR) if f.startswith("apolice_") and f.endswith(".json")]

    if not arquivos:
        console.print("[yellow]⚠️ Nenhuma apólice registrada.[/yellow]")
        return

    table = Table(title="📑 Apólices Registradas", show_lines=True)
    table.add_column("ID", style="bold cyan", justify="center")
    table.add_column("Local", style="green", justify="center")
    table.add_column("Duração (dias)", justify="center")
    table.add_column("Limite de Chuva (mm)", justify="center")
    table.add_column("Indenização (wei)", justify="center")
    table.add_column("Expiração (timestamp)", justify="center")
    table.add_column("Contratante", style="magenta", overflow="fold", justify="left")

    for arquivo in sorted(arquivos):
        caminho = os.path.join(APOLICE_DIR, arquivo)
        with open(caminho, "r") as f:
            dados = json.load(f)

        table.add_row(
            str(dados["policy_id"]),
            dados["local"],
            str(dados["duracao_dias"]),
            str(dados["limite_chuva"]),
            str(dados["valor_indemnizacao"]),
            str(dados["expiration"]),
            dados["contratante"]
        )

    console.print(table)

if __name__ == "__main__":
    listar_apolices()