import os
import json
import shutil
from rich import print
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table
from pathlib import Path
from blockchain import cancelar_apolice_blockchain  # ✅ Função no seu blockchain.py

console = Console()

APOLICE_DIR = "apolices"
MONITOR_FILE = os.path.join(APOLICE_DIR, "apolices_monitoradas.json")
PASTA_EXCLUIDAS = os.path.join(APOLICE_DIR, "apolices_excluidas")

def barra_progresso(acionamentos, limite):
    if limite == 0:
        return "[green]∞[/green]"
    porcentagem = int((acionamentos / limite) * 10)
    barra = "█" * porcentagem + "░" * (10 - porcentagem)
    return f"[cyan]{barra}[/cyan] {acionamentos}/{limite}"

def exibir_tabela_apolices():
    if not os.path.exists(APOLICE_DIR):
        console.print("[red]❌ Pasta de apólices não encontrada.[/red]")
        return []

    arquivos = [f for f in os.listdir(APOLICE_DIR) if f.startswith("apolice_") and f.endswith(".json")]

    if not arquivos:
        console.print("[yellow]⚠️ Nenhuma apólice registrada.[/yellow]")
        return []

    table = Table(title="📑 Apólices Registradas", show_lines=True)
    table.add_column("ID", style="bold cyan", justify="center")
    table.add_column("Local", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Limite (mm)", justify="center")
    table.add_column("Dias", justify="center")
    table.add_column("Indenização", justify="center")
    table.add_column("Válida até", justify="center")
    table.add_column("Acionamentos", justify="center")
    table.add_column("Tx Hash", overflow="fold", justify="center")

    ids = []

    for arquivo in sorted(arquivos):
        caminho = os.path.join(APOLICE_DIR, arquivo)
        with open(caminho, "r") as f:
            dados = json.load(f)

        policy_id = str(dados.get("policy_id", ""))
        ids.append(policy_id)
        local = dados.get("local", "")
        status = "[green]Ativa[/green]" if dados.get("ativo", False) else "[red]Inativa[/red]"
        limite = str(dados.get("limite_chuva", ""))
        dias = str(dados.get("dias_chuva", ""))
        indenizacao = str(dados.get("valor_indemnizacao", ""))
        expira = str(dados.get("expiration", ""))
        tx_hash = dados.get("tx_hash", "")

        acionamentos = dados.get("acionamentos", 0)
        limite_acionamentos = dados.get("limite_acionamentos", 0)
        progresso = barra_progresso(acionamentos, limite_acionamentos)

        table.add_row(
            policy_id,
            local,
            status,
            limite,
            dias,
            indenizacao,
            expira,
            progresso,
            tx_hash
        )

    console.print(table)
    return ids

def remover_apolice():
    ids_disponiveis = exibir_tabela_apolices()
    if not ids_disponiveis:
        return

    try:
        policy_id = Prompt.ask("\n🗑️ Digite o ID da apólice que deseja remover")
        if policy_id not in ids_disponiveis:
            print(f"[red]❌ Apólice {policy_id} não encontrada nos registros.[/red]")
            return

        nome_arquivo = f"apolice_{policy_id}.json"
        origem = os.path.join(APOLICE_DIR, nome_arquivo)
        destino_pasta = os.path.join(PASTA_EXCLUIDAS)
        destino = os.path.join(destino_pasta, nome_arquivo)

        # ✅ Cancela na blockchain
        cancelar_apolice_blockchain(int(policy_id))

        # ✅ Atualiza localmente como inativa
        with open(origem, "r") as f:
            dados = json.load(f)

        dados["ativo"] = False
        dados["status"] = "cancelada"

        with open(origem, "w") as f:
            json.dump(dados, f, indent=2)

        # ✅ Move para pasta de apólices excluídas
        os.makedirs(destino_pasta, exist_ok=True)
        shutil.move(origem, destino)
        print(f"[green]📦 Apólice movida para: {destino}[/green]")

        # ✅ Remove do monitoramento
        if os.path.exists(MONITOR_FILE):
            with open(MONITOR_FILE, "r") as f:
                monitoradas = json.load(f)
            monitoradas_filtradas = [ap for ap in monitoradas if str(ap["policy_id"]) != policy_id]
            with open(MONITOR_FILE, "w") as f:
                json.dump(monitoradas_filtradas, f, indent=2)

        print(f"[bold green]✅ Apólice {policy_id} cancelada e removida com sucesso.[/bold green]")

    except Exception as e:
        print(f"[red]❌ Erro ao remover a apólice: {e}[/red]")

if __name__ == "__main__":
    remover_apolice()
