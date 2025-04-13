import os
import json
import shutil
from rich import print
from rich.table import Table
from rich.prompt import Prompt, Confirm

APOLICE_DIR = "apolices"
PASTA_EXCLUIDAS = os.path.join(APOLICE_DIR, "apolices_excluidas")
MONITOR_FILE = os.path.join(APOLICE_DIR, "apolices_monitoradas.json")

def exibir_dados_apolice(path):
    try:
        with open(path, "r") as f:
            dados = json.load(f)

        table = Table(title="📋 Dados da Apólice", show_lines=True)
        table.add_column("Campo", style="bold cyan")
        table.add_column("Valor", style="bold green")

        campos = {
            "ID": dados.get("policy_id"),
            "Local": dados.get("local", "N/A"),
            "Dias de Chuva": str(dados.get("dias_chuva", "")),
            "Limite de Chuva (mm)": str(dados.get("limite_chuva", "")),
            "Indenização (wei)": str(dados.get("valor_indemnizacao", "")),
            "Expiração": str(dados.get("expiration", "")),
            "Ativo": "✅ Sim" if dados.get("ativo") else "❌ Não",
            "Acionamentos": str(dados.get("acionamentos", 0)),
            "Limite de Acionamentos": str(dados.get("limite_acionamentos", 0)),
            "Última Atualização": str(dados.get("ultima_atualizacao", "N/A")),
            "Tx Hash": dados.get("tx_hash", "N/A"),
            "Criada em": str(dados.get("timestamp_criacao", "N/A")),
        }

        for chave, valor in campos.items():
            table.add_row(chave, str(valor))

        print(table)
    except Exception as e:
        print(f"[red]Erro ao ler dados da apólice: {e}[/red]")

def restaurar_apolice():
    if not os.path.exists(PASTA_EXCLUIDAS):
        print("[yellow]⚠️ Nenhuma apólice excluída encontrada.[/yellow]")
        return

    arquivos = [f for f in os.listdir(PASTA_EXCLUIDAS) if f.startswith("apolice_") and f.endswith(".json")]
    if not arquivos:
        print("[yellow]⚠️ Nenhuma apólice excluída encontrada.[/yellow]")
        return

    print("[bold cyan]📦 Apólices excluídas disponíveis para restauração:[/bold cyan]")
    ids_disponiveis = []
    for arq in arquivos:
        policy_id = arq.replace("apolice_", "").replace(".json", "")
        ids_disponiveis.append(policy_id)
        print(f" - ID: [bold]{policy_id}[/bold]")

    try:
        id_escolhido = Prompt.ask("\n♻️ Digite o ID da apólice que deseja restaurar").strip()

        if id_escolhido not in ids_disponiveis:
            print(f"[red]❌ Apólice ID {id_escolhido} não está na lista de excluídas.[/red]")
            return

        nome_arquivo = f"apolice_{id_escolhido}.json"
        origem = os.path.join(PASTA_EXCLUIDAS, nome_arquivo)
        destino = os.path.join(APOLICE_DIR, nome_arquivo)

        # Exibe os dados da apólice antes de restaurar
        exibir_dados_apolice(origem)

        if not Confirm.ask("[cyan]Deseja realmente restaurar esta apólice?[/cyan]"):
            print("[yellow]❌ Restauração cancelada pelo usuário.[/yellow]")
            return

        shutil.move(origem, destino)
        print(f"[green]✅ Apólice {id_escolhido} restaurada para {destino}[/green]")

        # Atualiza o monitoramento
        policy_id_int = int(id_escolhido)
        if os.path.exists(MONITOR_FILE):
            with open(MONITOR_FILE, "r") as f:
                monitoradas = json.load(f)
        else:
            monitoradas = []

        if any(item["policy_id"] == policy_id_int for item in monitoradas):
            print("[yellow]⚠️ Apólice já estava na lista de monitoramento.[/yellow]")
        else:
            monitoradas.append({"policy_id": policy_id_int})
            with open(MONITOR_FILE, "w") as f:
                json.dump(monitoradas, f, indent=2)
            print("[bold green]✅ Apólice adicionada novamente ao monitoramento.[/bold green]")

    except Exception as e:
        print(f"[red]❌ Erro ao restaurar a apólice: {e}[/red]")

if __name__ == "__main__":
    restaurar_apolice()