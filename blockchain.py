"""Blockchain module."""
import time
from grover import GroverAlgorithm
from math import gcd
from sha import SHA
from sympy import mod_inverse
from qiskit import transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler


class Wallet:
    """Representa a carteira de um usuário, com seu par de chaves."""
    def __init__(self, p: int, q: int, sha: SHA, e: int = 5):
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
        self.sha = sha
        self.address = (
            f"addr_{self.sha.encode(str(self.public_key).encode())}"
        )

    def sign_transaction(self, to_address: str, amount: float):
        """Cria e assina uma transação com a chave privada."""
        return Transaction(self.address, to_address, amount, self, self.sha)


class Transaction:
    """Representa uma transição entre membros da cadeia."""
    def __init__(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        wallet: Wallet,
        sha: SHA,
    ):
        """Inicializa parâmetros."""
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.data = f"{from_address}{to_address}{amount}"
        self.hash = sha.encode(self.data.encode()) % wallet.N
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
        sha: SHA,
        nonce: int = 0,
    ):
        """Inicializa parâmetros."""
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.sha = sha

    def compute_hash(self):
        """Calcula o hash do bloco, que serve como sua identidade única."""
        block_string = (
            f"{self.index}{self.transactions}{self.timestamp}"
            f"{self.previous_hash}{self.nonce}"
        ).encode()
        return self.sha.encode(block_string)


class Blockchain:
    """Classe da blockchain."""
    def __init__(
        self,
        sha: SHA,
        difficulty_bits: int = 16,
        nonce_bits: int = 16,
    ):
        """Inicializa parâmetros."""
        self.difficulty_bits = difficulty_bits
        self.nonce_bits = nonce_bits
        self.chain = []
        self.pending_transactions = []

        # Create sha object
        self.sha = sha

        # Create initial block
        genesis_block = Block(0, [], time.time(), "0", sha=self.sha)
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """Retorna o último bloco."""
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction):
        """Adiciona uma nova transação à lista de pendentes."""
        self.pending_transactions.append(transaction)

    def classic_mining(self):
        """Minera um bloco usando força bruta clássica."""
        start_time = time.time()
        block = Block(
            self.last_block.index + 1,
            self.pending_transactions,
            time.time(),
            self.last_block.hash,
            sha=self.sha,
        )

        # Prova de Trabalho por força bruta
        for nonce in range(2**self.nonce_bits):
            block.nonce = nonce
            hash_attempt = block.compute_hash()
            decoded_hash = self.sha.decode(hash_attempt)
            if self.sha.validate(hash_attempt, self.difficulty_bits):
                end_time = time.time()
                return (
                    nonce,
                    hash_attempt,
                    decoded_hash,
                    end_time - start_time
                )

        return None, None, None, time.time() - start_time

    def quantum_mining(self, simulation: bool = True, shots: int = 1024):
        """Simula a mineração de um bloco usando o Algoritmo de Grover."""
        # Cria bloco
        block = Block(
            self.last_block.index + 1,
            self.pending_transactions,
            time.time(),
            self.last_block.hash,
            sha=self.sha,
        )

        # Configura o algoritmo de Grover
        grover_alg = GroverAlgorithm(
            block,
            self.nonce_bits,
            self.difficulty_bits,
            self.sha
        )
        grover_circuit = grover_alg.build_circuit()

        # Executa o algoritmo
        if simulation:
            start_time = time.time()
            simulator = AerSimulator()
            grover_circuit = transpile(grover_circuit, simulator)

            # Extrai resultado
            result = simulator.run(
                grover_circuit, shots=shots, memory=True).result()
            counts = result.get_counts()
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
            span = result.metadata['execution']['execution_spans'][0]
            run_time = (span.stop - span.start).total_seconds()

        print(counts)
        measured_nonce_str = max(counts, key=counts.get).split(" ")[0]
        measured_nonce = int(measured_nonce_str, 2)
        block.nonce = measured_nonce
        block_hash = block.compute_hash()
        decoded_hash = self.sha.decode(block.compute_hash())
        return measured_nonce, block_hash, decoded_hash, run_time
