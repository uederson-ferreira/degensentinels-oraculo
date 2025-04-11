# listar_apolices.py

import os
import json
from rich import print
from rich.console import Console
from rich.table import Table
from pathlib import Path

# Define o diretório de apólices relativo à pasta deste script
APOLICE_DIR = os.path.join(Path(__file__).parent, "apolices")
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
    table.add_column("Dias de Chuva", justify="center")
    table.add_column("Limite de Chuva (mm)", justify="center")
    table.add_column("Indenização (wei)", justify="center")
    table.add_column("Expiração (timestamp)", justify="center")
    table.add_column("Tx Hash", overflow="fold", justify="center")

    for arquivo in sorted(arquivos):
        caminho = os.path.join(APOLICE_DIR, arquivo)
        with open(caminho, "r") as f:
            dados = json.load(f)

        table.add_row(
            str(dados.get("policy_id", "")),
            dados.get("local", ""),
            str(dados.get("dias_chuva", "")),
            str(dados.get("limite_chuva", "")),
            str(dados.get("valor_indemnizacao", "")),
            str(dados.get("expiration", "")),
            dados.get("tx_hash", "")
        )

    console.print(table)

if __name__ == "__main__":
    listar_apolices()