"""Grover module."""
from math import floor, pi, sqrt
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from sha import SHA


class GroverAlgorithm:
    """Classe com o algoritmo de Grover para achar a hash PoW do bloco."""
    def __init__(self, block, nonce_bits: int, difficulty_bits: int, sha: SHA):
        """Inicializa parâmetros."""
        self.nonce_bits = nonce_bits
        self.difficulty_bits = difficulty_bits
        self.block = block
        self.sha = sha

    def oracle(self):
        """Cria o oráculo que marca os estados vencedores.

        Os estados marcados são aquelas strings binárias de nonce_bits bits
        cujos primeiros difficulty_bits bits são zero.

        """
        self.marked_states = []
        for nonce in range(2 ** self.nonce_bits):
            self.block.nonce = nonce
            hash_attempt = self.block.compute_hash()
            if self.sha.validate(hash_attempt, self.difficulty_bits):
                self.marked_states.append(
                    format(nonce, f'0{self.nonce_bits}b')
                )

        diagonal = [1] * 2 ** self.nonce_bits
        for state in self.marked_states:
            idx = int(state, 2)
            diagonal[idx] = -1  # aplica fase -1 nos válidos

        oracle = QuantumCircuit(self.nonce_bits)
        oracle.append(DiagonalGate(diagonal), range(self.nonce_bits))
        oracle.name = "Oráculo"
        return oracle.to_gate()

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

        N = 2**self.nonce_bits  # Número total de elementos
        M = len(self.marked_states)
        iterations = floor(pi / 4 * sqrt(N / M))
        print(iterations)
        for _ in range(iterations):
            grover.append(oracle_gate, range(self.nonce_bits))
            grover.append(diffuser_gate, range(self.nonce_bits))
        grover.measure_all()
        return grover
