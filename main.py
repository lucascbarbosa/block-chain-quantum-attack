"""Main script."""
from blockchain import Blockchain, Wallet
from sha import SHA


DIFFICULTY_BITS = 3
NONCE_BITS = 5
SHA_BITS = 8
SIMULATION = True
print("--- 1. INICIANDO SIMULAÇÃO DA BLOCKCHAIN ---")
print(
    f"DIFFICULTY_BITS={DIFFICULTY_BITS}, "
    f"NONCE_BITS={NONCE_BITS}, "
    f"SHA_BITS={SHA_BITS}, "
    f"SIMULATION={SIMULATION}"
)
# Cria SHA
sha = SHA(n=SHA_BITS)

# Cria blockchain
blockchain = Blockchain(
    difficulty_bits=DIFFICULTY_BITS,
    nonce_bits=NONCE_BITS,
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

print("\n--- 3. TENTANDO MINERAR COM MÉTODO CLÁSSICO ---")
(
    classical_nonce,
    classical_hash,
    classical_decoded_hash,
    classical_time
) = blockchain.classic_mining()
if classical_nonce is None:
    print("Mineração clássica falhou em encontrar um nonce.")
else:
    print(
        f"Nonce {classical_nonce} encontrada em {classical_time} segundos, "
        f"hash: {classical_hash}, hash decodificado: {classical_decoded_hash}"
    )

print("\n--- 4. TENTANDO MINERAR COM MÉTODO QUÂNTICO ---")
(
    quantum_nonce,
    quantum_hash,
    quantum_decoded_hash,
    quantum_time
) = blockchain.quantum_mining()
if quantum_nonce is None:
    print("Mineração quântica falhou em encontrar um nonce.")
else:
    print(
        f"Nonce {quantum_nonce} encontrada em {quantum_time} segundos, "
        f"hash: {quantum_hash}, hash decodificado: {quantum_decoded_hash}"
    )
