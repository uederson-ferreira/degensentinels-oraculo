import os
from pathlib import Path
from multiversx_sdk import Address, Transaction, Account
from multiversx_sdk.wallet import UserPEM
from multiversx_sdk.network_providers import ApiNetworkProvider
from config import CONTRACT_ADDRESS, SENDER_ADDRESS, CHAIN_ID, PROXY

# Caminho do PEM
BASE_DIR = Path(os.getcwd()).parent
PASTA_PEM = os.getenv("PASTA_PEM", "wallets/")
PEM_PATH = BASE_DIR / (PASTA_PEM + "1") / f"{SENDER_ADDRESS}.pem"

# Conexão com a rede
provider = ApiNetworkProvider(PROXY)
sender_address = Address.from_bech32(SENDER_ADDRESS)
account_onchain = provider.get_account(sender_address)

# Inicializa signer e conta local
signer = UserPEM.from_file(PEM_PATH)
sender = Account(secret_key=signer.secret_key)
sender.nonce = account_onchain.nonce

# Payload para chamar o endpoint "receber_fundos"
payload = "receber_fundos"

# Valor a enviar: 1 EGLD (convertido para wei)
value = 1 * 10**18  # 1 EGLD

# Cria a transação
tx = Transaction(
    nonce=sender.nonce,
    sender=sender_address,
    receiver=Address.from_bech32(CONTRACT_ADDRESS),
    value=value,
    gas_limit=6_000_000,
    chain_id=CHAIN_ID,
    data=payload.encode()
)

# Assina e envia a transação
tx.signature = sender.sign_transaction(tx)
tx_hash = provider.send_transaction(tx)

print(f"✅ Valor enviado com sucesso! Hash: {tx_hash.hex()}")
print(f"🔗 Explorer: https://devnet-explorer.multiversx.com/transactions/{tx_hash.hex()}")