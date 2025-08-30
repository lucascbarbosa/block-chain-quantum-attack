"""Main script."""
import argparse
from aux.blockchain import Blockchain, Wallet
from aux.sha import SHA
from math import floor, pi, sqrt

parser = argparse.ArgumentParser(
    description="Simulação de Blockchain com mineração clássica e quântica."
)
parser.add_argument(
    "--difficulty-bits",
    type=int,
    default=8,
    help="Número de bits de dificuldade para mineração."
)
parser.add_argument(
    "--nonce-bits",
    type=int,
    default=10,
    help="Número de bits do nonce."
)
parser.add_argument(
    "--sha-bits",
    type=int,
    default=10,
    help="Número de bits do SHA."
)
parser.add_argument(
    "--shots",
    type=int,
    default=1024,
    help="Número de execuções (shots) para a simulação quântica."
)
parser.add_argument(
    "--simulation",
    action="store_true",
    default=True,
    help="Simular mineração quântica (padrão: True)."
)
parser.add_argument(
    "--no-simulation",
    action="store_false",
    dest="simulation",
    help="Desabilitar simulação de mineração quântica."
)

args = parser.parse_args()

print("--- 1. INICIANDO SIMULAÇÃO DA BLOCKCHAIN ---")
print(
    f"DIFFICULTY_BITS={args.difficulty_bits}, "
    f"NONCE_BITS={args.nonce_bits}, "
    f"SHA_BITS={args.sha_bits}, "
    f"SIMULATION={args.simulation}"
)
# Cria SHA
sha = SHA(n=args.sha_bits)

# Cria blockchain
blockchain = Blockchain(
    difficulty_bits=args.difficulty_bits,
    nonce_bits=args.nonce_bits,
    sha=sha
)

# Cria carteiras
alice_wallet = Wallet(p=5, q=7, sha=sha)
bob_wallet = Wallet(p=11, q=3, sha=sha)
attacker_wallet = Wallet(p=5, q=11, sha=sha)
print(f"Carteira da Alice: {alice_wallet.address} (e={alice_wallet.e})")
print(f"Carteira do Bob: {bob_wallet.address} (e={bob_wallet.e})")
print(
    f"Carteira do Atacante: {attacker_wallet.address} (e={attacker_wallet.e})"
)

print("\n--- 2. ALICE ENVIA 10 MOEDAS PARA BOB ---")
tx = alice_wallet.sign_transaction(bob_wallet.address, 10.0)
blockchain.add_transaction(tx)
print("Transação adicionada à lista de pendentes.")

(
    classical_nonce,
    classical_hash,
    classical_decoded_hash,
) = blockchain.classic_mining()
print("\n--- 3. TENTANDO MINERAR COM MÉTODO CLÁSSICO ---")
if classical_nonce is None:
    print("Mineração clássica falhou em encontrar um nonce.")
else:
    print(
        f"Nonce: {classical_nonce} "
        f"Iterations: {classical_nonce} "
        f"Hash (encoded): {classical_hash} "
        f"Hash (decoded): {classical_decoded_hash}"
    )

print("\n--- 4. TENTANDO MINERAR COM MÉTODO QUÂNTICO ---")
(
    quantum_nonce,
    quantum_hash,
    quantum_decoded_hash
) = blockchain.quantum_mining(simulation=args.simulation, shots=args.shots)
quantum_iterations = floor(pi / 4 * sqrt(2 ** args.nonce_bits))
if quantum_nonce is None:
    print("Mineração quântica falhou em encontrar um nonce.")
else:
    print(
        f"Nonce: {quantum_nonce} "
        f"Iterations: {quantum_iterations} "
        f"Hash (encoded): {quantum_hash} "
        f"Hash (decoded): {quantum_decoded_hash}"
    )
