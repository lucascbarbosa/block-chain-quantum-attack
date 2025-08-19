"""Grover module."""
from math import floor, pi, sqrt
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate


class GroverAlgorithm:
    """Classe com o algoritmo de Grover para achar a hash PoW do bloco."""
    def __init__(self, nonce_bits: int, difficulty_bits: int):
        """Inicializa parâmetros."""
        self.nonce_bits = nonce_bits
        self.difficulty_bits = difficulty_bits

    def oracle(self):
        """Cria o oráculo que marca os estados vencedores.

        Os estados marcados são aquelas strings binárias de nonce_bits bits
        cujos primeiros difficulty_bits bits são zero.

        """
        diagonal = [1] * (2**self.nonce_bits)
        # Marca os estados que possuem os primeiros bits de dificuldade zerados
        for i in range(2**self.nonce_bits):
            if i >> (self.nonce_bits - self.difficulty_bits) == 0:
                diagonal[i] = -1
        oracle_gate = DiagonalGate(diagonal)
        oracle_gate.name = "Oráculo"
        return oracle_gate

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
        N = 2**self.nonce_bits  # Número total de elementos
        M = 1                 # Número de soluções (apenas uma)
        iterations = floor(pi / 4 * sqrt(N / M))

        grover = QuantumCircuit(self.nonce_bits, self.nonce_bits)
        grover.h(range(self.nonce_bits))

        oracle_gate = self.oracle()
        diffuser_gate = self.diffuser()

        for _ in range(iterations):
            grover.append(oracle_gate, range(self.nonce_bits))
            grover.append(diffuser_gate, range(self.nonce_bits))
        grover.measure_all()
        return grover
