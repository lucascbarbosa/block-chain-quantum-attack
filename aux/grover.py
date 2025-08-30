"""Grover module."""
from math import floor, pi, sqrt
from qiskit import QuantumCircuit
from .sha import SHA


class GroverAlgorithm:
    """Classe com o algoritmo de Grover para achar a hash PoW do bloco."""
    def __init__(self, block, nonce_bits: int, difficulty_bits: int, sha: SHA):
        """Inicializa parâmetros."""
        self.nonce_bits = nonce_bits
        self.difficulty_bits = difficulty_bits
        self.block = block
        self.sha = sha
        self.marked_state = None

    def _find_first_valid_nonce(self):
        for nonce in range(2 ** self.nonce_bits):
            self.block.nonce = nonce
            hash_attempt = self.block.compute_hash()
            if self.sha.validate(hash_attempt, self.difficulty_bits):
                return format(nonce, f'0{self.nonce_bits}b')
        return None

    def oracle(self):
        """Cria o oráculo que marca os estados vencedores.

        Os estados marcados são aquelas strings binárias de nonce_bits bits
        cujos primeiros difficulty_bits bits são zero.

        """
        if self.marked_state is None:
            self.marked_state = self._find_first_valid_nonce()
        if self.marked_state is None:
            raise ValueError("Nenhum estado válido encontrado para o oráculo.")

        qc = QuantumCircuit(self.nonce_bits)

        # X nos bits que são 0 no estado alvo
        for i, b in enumerate(self.marked_state):
            if b == '0':
                qc.x(i)

        # MCZ no último qubit
        qc.h(self.nonce_bits - 1)
        qc.mcx(list(range(self.nonce_bits - 1)), self.nonce_bits - 1)
        qc.h(self.nonce_bits - 1)

        # Desfaz X
        for i, b in enumerate(self.marked_state):
            if b == '0':
                qc.x(i)

        qc.name = "Oráculo"
        return qc.to_gate()

    def diffuser(self):
        """Cria o difusor (inversão sobre a média)."""
        difusor = QuantumCircuit(self.nonce_bits)
        difusor.h(range(self.nonce_bits))
        difusor.x(range(self.nonce_bits))
        difusor.h(self.nonce_bits - 1)
        difusor.mcx(list(range(self.nonce_bits - 1)), self.nonce_bits - 1)
        difusor.h(self.nonce_bits - 1)
        difusor.x(range(self.nonce_bits))
        difusor.h(range(self.nonce_bits))
        difusor.name = "Difusor"
        return difusor.to_gate()

    def build_circuit(self):
        """Monta o circuito de Grover para o valor alvo."""
        grover = QuantumCircuit(self.nonce_bits, self.nonce_bits)
        grover.h(range(self.nonce_bits))

        oracle_gate = self.oracle()
        diffuser_gate = self.diffuser()

        N = 2 ** self.nonce_bits  # Número total de elementos
        iterations = floor(pi / 4 * sqrt(N))

        # Iterações
        for _ in range(iterations):
            grover.append(oracle_gate, range(self.nonce_bits))
            grover.append(diffuser_gate, range(self.nonce_bits))

        # Medidores
        for i in range(self.nonce_bits):
            grover.measure(i, self.nonce_bits - 1 - i)

        return grover
