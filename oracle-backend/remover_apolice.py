import os
import json
import shutil
from rich import print
from rich.prompt import Prompt

APOLICE_DIR = "apolices"
MONITOR_FILE = os.path.join(APOLICE_DIR, "apolices_monitoradas.json")
PASTA_EXCLUIDAS = os.path.join(APOLICE_DIR, "apolices_excluidas")

def remover_apolice():
    if not os.path.exists(MONITOR_FILE):
        print("[yellow]⚠️ Nenhuma apólice monitorada.[/yellow]")
        return

    # Carrega lista de apólices monitoradas
    with open(MONITOR_FILE, "r") as f:
        monitoradas = json.load(f)

    if not monitoradas:
        print("[yellow]⚠️ Nenhuma apólice registrada para remoção.[/yellow]")
        return

    print("[bold cyan]📋 Apólices monitoradas:[/bold cyan]")
    for item in monitoradas:
        print(f" - ID: [bold]{item['policy_id']}[/bold]")

    try:
        policy_id = int(Prompt.ask("\n🗑️ Digite o ID da apólice que deseja remover"))

        # Verifica se o ID está na lista
        monitoradas_filtradas = [ap for ap in monitoradas if ap["policy_id"] != policy_id]

        if len(monitoradas) == len(monitoradas_filtradas):
            print(f"[red]❌ Apólice {policy_id} não encontrada no monitoramento.[/red]")
            return

        # Move o arquivo JSON da apólice para a pasta de excluídas
        nome_arquivo = f"apolice_{policy_id}.json"
        origem = os.path.join(APOLICE_DIR, nome_arquivo)
        destino_pasta = os.path.join(PASTA_EXCLUIDAS)
        destino = os.path.join(destino_pasta, nome_arquivo)

        # Cria a pasta de destino, se não existir
        os.makedirs(destino_pasta, exist_ok=True)

        if os.path.exists(origem):
            shutil.move(origem, destino)
            print(f"[green]📦 Apólice movida para: {destino}[/green]")
        else:
            print(f"[yellow]⚠️ Arquivo da apólice {policy_id} não encontrado.[/yellow]")

        # Atualiza o arquivo de monitoramento
        with open(MONITOR_FILE, "w") as f:
            json.dump(monitoradas_filtradas, f, indent=2)

        print(f"[bold green]✅ Apólice {policy_id} removida do monitoramento com sucesso.[/bold green]")

    except Exception as e:
        print(f"[red]❌ Erro ao remover a apólice: {e}[/red]")

if __name__ == "__main__":
    remover_apolice()