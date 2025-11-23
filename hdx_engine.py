import hashlib
import time
import random

class Context:
    """
    Represents the user authorization context.
    In a real app, 'auth_token' would be validated against a secure vault.
    """
    def __init__(self, role, auth_token):
        self.role = role
        self.auth_token = auth_token
        # HARDCODED SECRET FOR POC PURPOSES ONLY
        self.is_valid = (auth_token == "SECURE_ROOT_KEY_99X")

class Signal:
    """
    Discrete Binary Field Wrapper.
    """
    def __init__(self, data: bytes):
        self.data = bytearray(data)

    def copy(self):
        return Signal(self.data)

    def xor(self, pattern: bytes):
        """Standard XOR operation used for mixing and honey generation."""
        if not pattern: return
        length = len(self.data)
        for i in range(length):
            self.data[i] ^= pattern[i % len(pattern)]

    def __repr__(self):
        # We show a hash of the data to avoid leaking raw bytes in logs
        return f"<Signal Hash: {hashlib.sha256(self.data).hexdigest()[:8]}>"

class Operator:
    """
    HDX Operator: R o T o K
    Implements the 'Defensive Operator' logic.
    """
    def __init__(self, name, max_depth):
        self.name = name
        self.max_depth = max_depth

    def execute(self, signal: Signal, depth: int, context: Context):
        # --- DEFENSIVE LOGIC ---
        # If context is invalid OR depth exceeded, trigger Decay
        if not context.is_valid or depth > self.max_depth:
            return self._decay(signal, depth)
        
        # --- VALID LOGIC ---
        return self._transform(signal)

    def _transform(self, signal: Signal):
        """
        The Real Mathematical Operation.
        Only runs if Context is Authorized.
        """
        # 1. Kernel (Invert)
        for i in range(len(signal.data)):
            signal.data[i] = ~signal.data[i] & 0xFF
        
        # 2. Twist (Shift/Mix)
        signal.xor(b'\xAA\x55') 
        
        return signal, False # False = Not Honey

    def _decay(self, signal: Signal, depth: int):
        """
        The Decay Chain.
        Generates plausible 'Honey' output to confuse the adversary.
        """
        # Deterministic Honey Pattern based on depth (looks structured, is fake)
        seed = f"HONEY_PATTERN_{depth}_{self.name}".encode()
        honey_pattern = hashlib.sha256(seed).digest()
        
        signal.xor(honey_pattern)
        return signal, True # True = Is Honey

class HDXEngine:
    def __init__(self, operators):
        self.operators = operators
        self.state = "NORMAL"

    def run(self, input_data: bytes, context: Context):
        """
        Main simulation loop.
        """
        sig = Signal(input_data)
        trace = []
        
        # Reset state for new run
        self.state = "NORMAL"

        for i, op in enumerate(self.operators):
            
            # --- KILL SWITCH CHECK ---
            # If we are stuck in honey state too long, block completely.
            if self.state == "HONEY" and i > len(self.operators) - 2:
                self.state = "BLOCKED"
                trace.append("KILL-SWITCH: ENGAGED")
                break

            # Execute Operator
            sig, is_honey = op.execute(sig, i, context)

            if is_honey:
                if self.state == "NORMAL":
                    # Transition from Normal to Honey (Decay Triggered)
                    self.state = "HONEY"
                trace.append(f"Step {i}: DECAY/HONEY")
            else:
                trace.append(f"Step {i}: VALID")

        return sig, self.state, trace
