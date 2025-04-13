import os
import json
import time
from rich import print
from rich.console import Console
from rich.table import Table
from pathlib import Path

APOLICE_DIR = os.path.join(Path(__file__).parent, "apolices")
MONITOR_FILE = os.path.join(APOLICE_DIR, "apolices_monitoradas.json")

console = Console()

def formatar_timestamp(timestamp):
    try:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    except:
        return "Data inválida"

def remover_apolice():
    if not os.path.exists(MONITOR_FILE):
        console.print("[red]❌ Nenhuma apólice monitorada.[/red]")
        return

    with open(MONITOR_FILE, "r") as f:
        monitoradas = json.load(f)

    if not monitoradas:
        console.print("[yellow]⚠️ Nenhuma apólice registrada para monitoramento.[/yellow]")
        return

    # Montar tabela
    table = Table(title="📑 Apólices Monitoradas", show_lines=True)
    table.add_column("ID", style="bold cyan", justify="center")
    table.add_column("Local", style="green", justify="center")
    table.add_column("Dias de Chuva", justify="center")
    table.add_column("Limite de Chuva (mm)", justify="center")
    table.add_column("Indenização (wei)", justify="center")
    table.add_column("Criada em", justify="center")
    table.add_column("Expiração", justify="center")
    table.add_column("Tx Hash", overflow="fold", justify="center")

    for item in monitoradas:
        policy_id = item.get("policy_id")
        caminho_apolice = os.path.join(APOLICE_DIR, f"apolice_{policy_id}.json")

        if not os.path.exists(caminho_apolice):
            console.print(f"[red]❌ Arquivo da apólice {policy_id} não encontrado.[/red]")
            continue

        try:
            with open(caminho_apolice, "r") as f:
                dados = json.load(f)

            table.add_row(
                str(dados.get("policy_id", "")),
                dados.get("local", ""),
                str(dados.get("dias_chuva", "")),
                str(dados.get("limite_chuva", "")),
                str(dados.get("valor_indemnizacao", "")),
                formatar_timestamp(dados.get("timestamp_criacao")),
                formatar_timestamp(dados.get("expiration")),
                dados.get("tx_hash", "")
            )
        except Exception as e:
            console.print(f"[red]❌ Erro ao ler apólice {policy_id}: {e}[/red]")

    console.print(table)

    # Remoção
    try:
        policy_id = int(console.input("\n[bold red]🗑️ Digite o ID da apólice que deseja remover: [/bold red]"))

        novas_apolices = [a for a in monitoradas if a.get("policy_id") != policy_id]

        if len(novas_apolices) == len(monitoradas):
            console.print("[yellow]❌ ID não encontrado na lista de apólices monitoradas.[/yellow]")
            return

        with open(MONITOR_FILE, "w") as f:
            json.dump(novas_apolices, f, indent=2)

        caminho_apolice = os.path.join(APOLICE_DIR, f"apolice_{policy_id}.json")
        if os.path.exists(caminho_apolice):
            os.remove(caminho_apolice)
            console.print(f"[dim]🗑️ Arquivo apolice_{policy_id}.json removido.[/dim]")

        console.print(f"[bold green]✅ Apólice {policy_id} removida com sucesso.[/bold green]")

    except Exception as e:
        console.print(f"[red]❌ Erro ao remover: {e}[/red]")

if __name__ == "__main__":
    remover_apolice()