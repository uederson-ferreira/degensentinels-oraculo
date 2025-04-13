# listar_apolices.py
import os
import json
from rich import print
from rich.console import Console
from rich.table import Table
from pathlib import Path

# Define o caminho da pasta onde estão os arquivos de apólices
APOLICE_DIR = os.path.join(Path(__file__).parent, "apolices")

# Instancia um console do Rich para impressão formatada
console = Console()

def barra_progresso(acionamentos, limite):
    """
    Gera uma barra de progresso textual baseada na razão acionamentos / limite_acionamentos.
    Se o limite for 0, retorna o símbolo de infinito.
    """
    if limite == 0:
        return "[green]∞[/green]"
    porcentagem = int((acionamentos / limite) * 10)  # 10 blocos para barra
    barra = "█" * porcentagem + "░" * (10 - porcentagem)
    return f"[cyan]{barra}[/cyan] {acionamentos}/{limite}"

def listar_apolices():
    """
    Lista as apólices presentes na pasta `apolices`, extraindo os campos relevantes
    e exibindo uma tabela formatada com Rich, incluindo status, progresso e hash.
    """
    if not os.path.exists(APOLICE_DIR):
        console.print("[red]❌ Pasta de apólices não encontrada.[/red]")
        return

    # Coleta todos os arquivos de apólices no formato correto
    arquivos = [f for f in os.listdir(APOLICE_DIR) if f.startswith("apolice_") and f.endswith(".json")]

    if not arquivos:
        console.print("[yellow]⚠️ Nenhuma apólice registrada.[/yellow]")
        return

    # Cria a tabela com colunas bem definidas
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

    # Preenche cada linha da tabela com dados do JSON
    for arquivo in sorted(arquivos):
        caminho = os.path.join(APOLICE_DIR, arquivo)
        with open(caminho, "r") as f:
            dados = json.load(f)

        policy_id = str(dados.get("policy_id", ""))
        local = dados.get("local", "")
        status = "[green]Ativa[/green]" if dados.get("ativo", False) else "[red]Inativa[/red]"
        limite = str(dados.get("limite_chuva", ""))
        dias = str(dados.get("dias_chuva", ""))
        indenizacao = str(dados.get("valor_indemnizacao", ""))
        expira = str(dados.get("expiration", ""))
        tx_hash = dados.get("tx_hash", "")

        # Dados novos com suporte a acionamento
        acionamentos = dados.get("acionamentos", 0)
        limite_acionamentos = dados.get("limite_acionamentos", 0)

        # Gera barra de progresso
        progresso = barra_progresso(acionamentos, limite_acionamentos)

        # Adiciona linha na tabela
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

    # Imprime a tabela no terminal
    console.print(table)

# Executa a função caso o script seja chamado diretamente
if __name__ == "__main__":
    listar_apolices()