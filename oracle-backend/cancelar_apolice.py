# cancelar_apolice.py

import json
from multiversx_sdk import Address, Transaction
from multiversx_sdk.wallet import UserSigner
from multiversx_sdk.network_providers import ApiNetworkProvider
from config import CONTRACT_ADDRESS, PEM_PATH, CHAIN_ID, PROXY, SENDER_ADDRESS

def h(x):
    """Formata valores em hexadecimal com comprimento par."""
    hex_str = hex(x)[2:]
    return hex_str.zfill(len(hex_str) + len(hex_str) % 2)

def cancelar_apolice():
    print("🛑 Cancelamento de Apólice")
    policy_id = int(input("Digite o ID da apólice que deseja cancelar: "))

    payload = f"cancelarApolice@{h(policy_id)}"

    provider = ApiNetworkProvider(PROXY)
    signer = UserSigner.from_pem_file(PEM_PATH)

    sender_address = Address.from_bech32(SENDER_ADDRESS)
    sender_account = provider.get_account(sender_address)

    tx = Transaction(
        nonce=sender_account.nonce,
        sender=sender_address,
        receiver=Address.from_bech32(CONTRACT_ADDRESS),
        gas_limit=12_000_000,
        chain_id=CHAIN_ID,
        data=payload.encode(),
        value=0
    )

    tx.signature = signer.sign(tx.serialize_for_signing().hex())
    tx_hash = provider.send_transaction(tx)

    print(f"✅ Apólice cancelada com sucesso. Hash: {tx_hash.hex()}")
    print(f"🔎 Explorer: https://devnet-explorer.multiversx.com/transactions/{tx_hash.hex()}")

if __name__ == "__main__":
    cancelar_apolice()