"""Blockchain module."""
import hashlib
import time
from grover import GroverAlgorithm
from math import gcd
from sympy import mod_inverse
from qiskit import transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler


def sha_32(msg: bytes) -> int:
    """SHA-32."""
    h = hashlib.sha256(msg).digest()
    h_int = int.from_bytes(h, "big")
    return h_int >> (256 - 32)


class Wallet:
    """Representa a carteira de um usuário, com seu par de chaves."""
    def __init__(self, p: int, q: int, e: int = 5):
        """Inicializa parâmetros."""
        self.p = p
        self.q = q
        self.N = p * q
        phi_N = (p - 1) * (q - 1)
        possible_es = [3, 5, 17, 257, 65537]
        self.e = -1  # Inicializa com valor inválido
        for e_candidate in possible_es:
            if gcd(e_candidate, phi_N) == 1:
                self.e = e_candidate
                break
        self.d = mod_inverse(self.e, phi_N)
        self.public_key = (self.N, self.e)
        self.private_key = (self.N, self.d)
        self.address = (
            f"addr_{sha_32(str(self.public_key).encode())}"
        )

    def sign_transaction(self, to_address: str, amount: float):
        """Cria e assina uma transação com a chave privada."""
        return Transaction(self.address, to_address, amount, self)


class Transaction:
    """Representa uma transição entre membros da cadeia."""
    def __init__(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        wallet: Wallet,
    ):
        """Inicializa parâmetros."""
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.data = f"{from_address}{to_address}{amount}"
        self.hash = sha_32(self.data.encode()) % wallet.N
        self.signature = pow(self.hash, wallet.d, wallet.N)
        self.public_key = wallet.public_key


class Block:
    """Classe do bloco na cadeia."""
    def __init__(
        self,
        index: int,
        transactions: list[Transaction],
        timestamp: time.time,
        previous_hash: str,
        nonce: int = 0
    ):
        """Inicializa parâmetros."""
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """Calcula o hash do bloco, que serve como sua identidade única."""
        block_string = (
            f"{self.index}{self.transactions}{self.timestamp}"
            f"{self.previous_hash}{self.nonce}"
        )
        return sha_32(block_string.encode())


class Blockchain:
    """Classe da blockchain."""
    def __init__(self, difficulty_bits: int = 16, nonce_bits: int = 16):
        """Inicializa parâmetros."""
        self.difficulty_bits = difficulty_bits
        self.nonce_bits = nonce_bits
        self.chain = []
        self.pending_transactions = []

        # Create initial block
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """Retorna o último bloco."""
        return self.chain[-1]

    def is_valid_proof(self, block_hash: str):
        """Verifica se o hash atende aos critérios de dificuldade."""
        binary_hash = bin(block_hash)[2:].zfill(32)
        return binary_hash.startswith('0' * self.difficulty_bits)

    def add_transaction(self, transaction: Transaction):
        """Adiciona uma nova transação à lista de pendentes."""
        self.pending_transactions.append(transaction)

    def mine_classically(self):
        """Minera um bloco usando força bruta clássica."""
        start_time = time.time()
        block = Block(
            self.last_block.index + 1,
            self.pending_transactions,
            time.time(),
            self.last_block.hash
        )

        # Prova de Trabalho por força bruta
        for nonce in range(2**self.nonce_bits):
            block.nonce = nonce
            hash_attempt = block.compute_hash()
            if self.is_valid_proof(hash_attempt):
                end_time = time.time()
                return nonce, end_time - start_time

        return None, time.time() - start_time

    def mine_quantically(self, simulation: bool = True, shots: int = 1024):
        """Simula a mineração de um bloco usando o Algoritmo de Grover."""
        start_time = time.time()

        # Configura o algoritmo de Grover
        grover_alg = GroverAlgorithm(self.nonce_bits, self.difficulty_bits)
        grover_circuit = grover_alg.build_circuit()

        # Executa o algoritmo
        if simulation:
            simulator = AerSimulator()
            grover_circuit = transpile(grover_circuit, simulator)

            # Extrai resultado
            result = simulator.run(
                grover_circuit, shots=shots, memory=True).result()
            measured_nonce_str = result.get_memory()[0]
            run_time = time.time() - start_time

        else:
            # Configurações IBM
            service = QiskitRuntimeService()
            backend = service.least_busy(operational=True, simulator=False)
            pm = generate_preset_pass_manager(
                backend=backend, optimization_level=1)
            grover_circuit = pm.run(grover_circuit)
            sampler = Sampler(backend)

            # Extrai resultado
            job = sampler.run([grover_circuit], shots=shots)
            result = job.result()
            counts = result[0].data.meas.get_counts()
            measured_nonce_str = max(counts, key=counts.get)
            span = result.metadata['execution']['execution_spans'][0]
            run_time = (span.stop - span.start).total_seconds()

        measured_nonce = int(measured_nonce_str.replace(" ", ""), 2)
        return measured_nonce, run_time
