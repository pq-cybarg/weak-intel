#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.check_call([sys.executable, os.path.join(ROOT, "models", "graph", "build_graph.py")],
                              cwd=ROOT)
        cls.g = json.load(open(os.path.join(ROOT, "data", "graph.json"), encoding="utf-8"))

    def test_size(self):
        self.assertGreaterEqual(self.g["analysis"]["n_entities"], 200)
        self.assertGreaterEqual(self.g["analysis"]["n_edges"], 200)

    def test_core_is_attack_layer_only(self):
        an = self.g["analysis"]
        self.assertIn("sccs_attack", an)
        self.assertIn("sccs_all", an)
        extra = set(an.get("nodes_only_in_all_edges_scc") or [])
        core = set(an.get("core_scc") or [])
        self.assertTrue(extra.isdisjoint(core))
        # composition fallacy guard: photonic/fab cycle must not be headline core
        fake = {"Modality_Photonic", "PsiQuantum", "GlobalFoundries", "CRQC"}
        self.assertFalse(fake <= core)

    def test_dual_use_nonempty(self):
        self.assertGreaterEqual(len(self.g["analysis"]["dual_use_nodes"]), 1)

    def test_recurring_targets(self):
        ids = {t["id"] for t in self.g["analysis"]["recurring_targets"]}
        self.assertTrue({"Active_Directory", "Edge_VPN", "Microsoft_Exchange"} & ids)

    def test_crqc_split(self):
        self.assertIn("RSA", self.g["analysis"]["crqc_fragile"])
        self.assertTrue(self.g["analysis"]["crqc_survives"])

    def test_facilities_have_coords(self):
        geo = [e for e in self.g["entities"].values() if e.get("lat") is not None]
        self.assertGreaterEqual(len(geo), 5)

    def test_key_nodes_present(self):
        for n in ("CRQC", "HNDL", "TNFL", "Salt_Typhoon", "EternalBlue", "FIDO2_WebAuthn", "LockBit",
                  "IonQ", "PsiQuantum", "Infineon", "TPM2", "ASML", "Helium3", "REvil", "Paragon_Solutions",
                  "Huntress", "Snyk", "xLight", "Substrate",
                  "Anduril", "Shield_AI", "Palantir", "In_Q_Tel",
                  "Keyhole", "Recorded_Future", "CIA",
                  "SACLA", "European_XFEL", "Xarion_Laser_Acoustics"):
            self.assertIn(n, self.g["entities"], n)


if __name__ == "__main__":
    unittest.main()
