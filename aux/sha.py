"""SHA module."""
import hashlib


class SHA():
    """SHA de n bits."""
    def __init__(self, n: int):
        """Inicializa parâmetros."""
        self.n = n

    def encode(self, msg: str) -> str:
        """Encode hash."""
        h = hashlib.sha256(msg).digest()
        h_int = int.from_bytes(h, "big")
        return h_int >> (256 - self.n)

    def decode(self, hash: str) -> bin:
        """Decode hash."""
        return bin(hash)[2:].zfill(self.n)

    def validate(self, hash: str, diff_bits: int):
        """Validate hash."""
        binary_hash = self.decode(hash)
        return binary_hash.startswith('0' * diff_bits)
