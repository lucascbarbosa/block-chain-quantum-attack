"""Main script."""
from blockchain import Blockchain, Wallet


DIFFICULTY_BITS = 3
NONCE_BITS = 5
MAX_NONCE = int(
    '0' * DIFFICULTY_BITS + '1' * (NONCE_BITS - DIFFICULTY_BITS), 2
)
SIMULATION = True
print("--- 1. INICIANDO SIMULAÇÃO DA BLOCKCHAIN ---")
# Cria blockchain
blockchain = Blockchain(difficulty_bits=DIFFICULTY_BITS, nonce_bits=NONCE_BITS)
# Cria carteiras
alice_wallet = Wallet(p=5, q=7)
bob_wallet = Wallet(p=11, q=3)
attacker_wallet = Wallet(p=5, q=11)
print(f"NONCE MÁXIMA VÁLIDA: {MAX_NONCE}")
print(f"Carteira da Alice: {alice_wallet.address} (e={alice_wallet.e})")
print(f"Carteira do Bob: {bob_wallet.address} (e={bob_wallet.e})")
print(
    f"Carteira do Atacante: {attacker_wallet.address} (e={attacker_wallet.e})"
)

print("\n--- 2. ALICE ENVIA 10 MOEDAS PARA BOB ---")
tx = alice_wallet.sign_transaction(bob_wallet.address, 10.0)
blockchain.add_transaction(tx)
print("Transação adicionada à lista de pendentes.")

# Um minerador (o próprio atacante, neste caso) minera o bloco
print("\n--- 3. TENTANDO MINERAR COM MÉTODO CLÁSSICO ---")
classical_nonce, classical_time = blockchain.mine_classically()
if classical_nonce is None:
    print("Mineração clássica falhou em encontrar um nonce.")
else:
    print(f"Nonce {classical_nonce} encontrada em {classical_time} segundos")

print("\n--- 4. TENTANDO MINERAR COM MÉTODO QUÂNTICO ---")
quantum_nonce, quantum_time = blockchain.mine_quantically(simulation=True)
if quantum_nonce is None:
    print("Mineração quântica falhou em encontrar um nonce.")
else:
    print(f"Nonce {quantum_nonce} encontrada em {quantum_time} segundos")
