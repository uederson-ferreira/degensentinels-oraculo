# main.py

import time
import os
import json
from rich import print
from rich.panel import Panel
from rich.console import Console
from weather import get_accumulated_precipitation
from blockchain import send_trigger_transaction

console = Console()

APOLICE_DIR = "apolices"
MONITOR_FILE = f"{APOLICE_DIR}/apolices_monitoradas.json"
HISTORICO_LOG = f"{APOLICE_DIR}/historico_ativacoes.log"

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

def salvar_historico(policy_id, chuva):
    with open(HISTORICO_LOG, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Apólice {policy_id} acionada - {chuva:.2f} mm\n")

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
                policy_id = apolice["policy_id"]
                limite = apolice["limite_chuva"]
                validade = apolice["expiration"]
                duracao_dias = apolice["dias_chuva"]

                titulo = f"📋 Apólice {policy_id} ({duracao_dias} dias)"
                console.print(Panel.fit(
                    f"🌍 Local: {apolice['local']}\n⏳ Expira em: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(validade))}\n🎯 Limite: {limite} mm",
                    title=titulo
                ))

                if now > validade:
                    console.print(f"[yellow]⏰ Apólice {policy_id} expirada.[/yellow]")
                    continue

                if chuva > limite:
                    console.print(f"[bold red]🚨 Gatilho ativado! Chuva > {limite} mm.[/bold red]")
                    send_trigger_transaction(policy_id, chuva, now)
                    salvar_historico(policy_id, chuva)
                else:
                    console.print(f"[green]✅ Condição não atingida ({chuva:.2f} mm < {limite} mm)[/green]")

        console.print("[dim]⏳ Aguardando 60 segundos...\n[/dim]")
        time.sleep(60)

if __name__ == "__main__":
    main()