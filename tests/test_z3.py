#!/usr/bin/env python3
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(script):
    p = subprocess.run([sys.executable, os.path.join(ROOT, "models", "z3", script)],
                       cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Z3Tests(unittest.TestCase):
    def test_shared_substrate(self):
        try:
            import z3  # noqa: F401
        except ImportError:
            self.skipTest("z3-solver not installed")
        code, out = run("shared_substrate.py")
        self.assertEqual(code, 0, out)
        self.assertIn("PROVED", out)
        self.assertNotIn("UNEXPECTED", out)

    def test_crqc_unwind(self):
        try:
            import z3  # noqa: F401
        except ImportError:
            self.skipTest("z3-solver not installed")
        code, out = run("crqc_unwind.py")
        self.assertEqual(code, 0, out)
        self.assertIn("PROVED", out)
        self.assertNotIn("UNEXPECTED", out)


if __name__ == "__main__":
    unittest.main()
