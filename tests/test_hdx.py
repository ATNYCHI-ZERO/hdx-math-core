import unittest
import sys
import os

# Allow importing from src folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from hdx_engine import HDXEngine, Operator, Context

class TestHDXSystem(unittest.TestCase):
    
    def setUp(self):
        # Setup a chain of 5 operators
        self.ops = [Operator(f"Op_{i}", max_depth=10) for i in range(5)]
        self.engine = HDXEngine(self.ops)
        self.data = b"CONFIDENTIAL_DATA_PACKET"

    def test_authorized_traversal(self):
        """Authorized user should get VALID state and real output."""
        ctx = Context("Admin", "SECURE_ROOT_KEY_99X")
        result, state, trace = self.engine.run(self.data, ctx)
        
        print(f"\n[TEST AUTH] State: {state} | Result: {result}")
        self.assertEqual(state, "NORMAL")
        self.assertTrue(all("VALID" in t for t in trace))

    def test_unauthorized_decay(self):
        """Unauthorized user should get HONEY state and fake output."""
        ctx = Context("Hacker", "WRONG_PASSWORD")
        result, state, trace = self.engine.run(self.data, ctx)
        
        print(f"\n[TEST HACK] State: {state} | Result: {result}")
        # The system should switch to honey or block
        self.assertIn(state, ["HONEY", "BLOCKED"])
        # The trace should indicate decay
        self.assertTrue(any("DECAY" in t for t in trace))

    def test_outputs_are_different(self):
        """The Honey output must not match the Valid output."""
        ctx_auth = Context("Admin", "SECURE_ROOT_KEY_99X")
        res_auth, _, _ = self.engine.run(self.data, ctx_auth)

        ctx_bad = Context("Hacker", "WRONG_PASSWORD")
        res_bad, _, _ = self.engine.run(self.data, ctx_bad)

        # The outputs must be mathematically distinct
        self.assertNotEqual(res_auth.data, res_bad.data)

if __name__ == '__main__':
    unittest.main()
