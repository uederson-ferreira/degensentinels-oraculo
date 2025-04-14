import time
import os
import json
from rich import print
from rich.panel import Panel
from rich.console import Console
from weather import get_accumulated_precipitation
from blockchain import send_trigger_transaction, atualizar_apolice_apos_acionamento

console = Console()

APOLICE_DIR = "apolices"
MONITOR_FILE = f"{APOLICE_DIR}/apolices_monitoradas.json"
HISTORICO_LOG = f"{APOLICE_DIR}/historico_ativacoes.log"

# Carrega apólices monitoradas com base no JSON de monitoramento
def carregar_apolices():
    if not os.path.exists(MONITOR_FILE):
        console.print("[yellow]⚠️ Nenhuma apólice para monitorar.[/yellow]")
        return []

    with open(MONITOR_FILE, "r") as f:
        monitoradas = json.load(f)

    apolices = []
    for item in monitoradas:
        policy_id = item["policy_id"]
        path = os.path.join(APOLICE_DIR, f"apolice_{policy_id}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                dados = json.load(f)
                apolices.append(dados)
        else:
            console.print(f"[red]❌ Arquivo da apólice {policy_id} não encontrado.[/red]")
    return apolices

# Salva o histórico da ativação em um log local
def salvar_historico(policy_id, chuva, hash_tx):
    with open(HISTORICO_LOG, "a") as f:
        f.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Apólice {policy_id} acionada - {chuva:.2f} mm - TX: {hash_tx}\n"
        )

# Gera uma barra visual de progresso dos acionamentos realizados
def gerar_barra(acionamentos, limite):
    if limite == 0:
        return "[blue]∞ acionamentos permitidos[/blue]"
    barra = ("🟩" * acionamentos).ljust(limite, "⬜")
    return f"[cyan]{barra}[/cyan] ({acionamentos}/{limite})"

def main():
    console.rule("[bold cyan]⛅ Oráculo Paramétrico: Modo de Monitoramento Ativo")

    while True:
        console.print("\n[blue]🔄 Verificando dados climáticos acumulados (últimos dias)...[/blue]")
        chuva = get_accumulated_precipitation()

        if chuva is None:
            console.print("[red]❌ Erro ao buscar dados da API. Tentando novamente...[/red]")
        else:
            console.print(f"[cyan]🌧️ Chuva acumulada:[/cyan] [bold]{chuva:.2f} mm[/bold]")

            apolices = carregar_apolices()
            now = int(time.time())

            for apolice in apolices:
                if not apolice:
                    continue

                policy_id = apolice.get("policy_id")
                local = apolice.get("local", "Local não informado")
                limite = apolice.get("limite_chuva", 0)
                validade = apolice.get("expiration", 0)
                acionamentos = apolice.get("acionamentos", 0)
                limite_acionamentos = apolice.get("limite_acionamentos", 0)
                ultima = apolice.get("ultima_atualizacao", None)
                ativo = apolice.get("ativo", True)

                # Tenta buscar o campo da duração (pode ter nomes diferentes)
                duracao_dias = apolice.get("duracao_dias") or apolice.get("dias_chuva") or apolice.get("dias")
                if duracao_dias is None:
                    console.print(f"[red]❌ Apólice {policy_id} sem campo 'duracao_dias'. Ignorada.[/red]")
                    continue

                if not ativo:
                    console.print(f"[dim]⛔ Apólice {policy_id} inativa.[/dim]")
                    continue

                # Título da apólice para exibição
                titulo = f"📋 Apólice {policy_id} ({duracao_dias} dias)"
                expira = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(validade))
                barra_progresso = gerar_barra(acionamentos, limite_acionamentos)

                # Painel informativo da apólice
                console.print(Panel.fit(
                    f"🌍 Local: {local}\n⏳ Expira: {expira}\n🎯 Limite: {limite} mm\n📊 Acionamentos: {barra_progresso}",
                    title=titulo
                ))

                # Verifica se a apólice está expirada
                if now > validade:
                    console.print(f"[yellow]⏰ Apólice {policy_id} expirada.[/yellow]")
                    continue

                # Verifica se já atingiu o limite de acionamentos
                if limite_acionamentos != 0 and acionamentos >= limite_acionamentos:
                    console.print(f"[red]❌ Limite de acionamentos atingido.[/red]")
                    continue

                # Verifica se a condição de chuva foi atingida
                if chuva > limite:
                    if ultima:
                        segundos_desde_ultimo = now - ultima
                        dias_passados = segundos_desde_ultimo // 86400
                        if dias_passados < duracao_dias:
                            console.print(f"[bold red]🚨 Gatilho ativado! Chuva > {limite} mm, Limite {limite} mm.[/bold red]")
                            print(f"[green]⏳ Último acionamento foi há {dias_passados} dias. Ainda não é possível acionar novamente.[/green]")
                            continue

                    # Tudo certo, aciona
                    console.print(f"[bold red]🚨 Gatilho ativado! Chuva > {limite} mm.[/bold red]")
                    hash_tx = send_trigger_transaction(policy_id, chuva, now)
                    salvar_historico(policy_id, chuva, hash_tx)
                    atualizar_apolice_apos_acionamento(apolice, now)
                else:
                    console.print(f"[green]✅ Condição não atingida ({chuva:.2f} mm < {limite} mm)[/green]")

        console.print("[dim]⏳ Aguardando 60 segundos...\n[/dim]")
        time.sleep(10)

if __name__ == "__main__":
    main()