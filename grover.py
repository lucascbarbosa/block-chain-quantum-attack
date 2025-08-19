"""Grover module."""
from math import floor, pi, sqrt
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate


class GroverAlgorithm:
    """Classe com o algoritmo de Grover para achar a hash PoW do bloco."""
    def __init__(self, n_qubits: int):
        """Inicializa parâmetros."""
        self.n_qubits = n_qubits

    def oracle(self, winner_state: int):
        """Cria o oráculo que marca um único estado vencedor."""
        # A diagonal é -1 no estado vencedor e 1 nos outros.
        diagonal = [1] * (2**self.n_qubits)
        diagonal[winner_state] = -1
        oracle_gate = DiagonalGate(diagonal)
        oracle_gate.name = "Oráculo"
        return oracle_gate

    def diffuser(self):
        """Cria o difusor (inversão sobre a média)."""
        difusor = QuantumCircuit(self.n_qubits)
        difusor.h(range(self.n_qubits))
        difusor.x(range(self.n_qubits))
        difusor.h(self.n_qubits - 1)
        difusor.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
        difusor.h(self.n_qubits - 1)
        difusor.x(range(self.n_qubits))
        difusor.h(range(self.n_qubits))
        difusor.name = "Difusor"
        return difusor.to_gate()

    def build_circuit(self, winner_state: int):
        """Monta o circuito de Grover para o valor alvo."""
        N = 2**self.n_qubits  # Número total de elementos
        M = 1                 # Número de soluções (apenas uma)
        iterations = floor(pi / 4 * sqrt(N / M))

        grover = QuantumCircuit(self.n_qubits, self.n_qubits)
        grover.h(range(self.n_qubits))

        oracle_gate = self.oracle(winner_state)
        diffuser_gate = self.diffuser()

        for _ in range(iterations):
            grover.append(oracle_gate, range(self.n_qubits))
            grover.append(diffuser_gate, range(self.n_qubits))
        grover.measure_all()
        return grover
