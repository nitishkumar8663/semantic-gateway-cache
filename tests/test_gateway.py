#!/usr/bin/env python3
"""Unit + live integration tests for the semantic gateway.

Run from the repo root:  python3 -m unittest discover -s tests -v
The FakeEmbedder tests are pure and deterministic. TestLiveEmbeddings
hits the real Ollama bge-m3 model; it is skipped if Ollama is down.
No test touches the dispatcher, the memory service, or any live model
other than bge-m3 (embeddings only) and, in the demo, gemma3:4b.
"""

import json
import math
import os
import sys
import tempfile
import time
import unittest
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_gateway.gateway import (  # noqa: E402
    CacheStore, Gateway, cosine_similarity, load_config,
)


def _vec_from_seed(seed, dim=8):
    """Deterministic pseudo-vector from a string seed (test use only)."""
    out = []
    x = sum(ord(c) * (i + 1) for i, c in enumerate(seed)) % 97 + 3
    for i in range(dim):
        x = (x * 31 + 17) % 101
        out.append(((x % 21) - 10) / 10.0)
    return out


class FakeEmbedder:
    """Returns fixed vectors per prompt so similarity is controllable."""

    def __init__(self, mapping):
        self.mapping = mapping  # prompt -> vector

    def embed(self, text):
        if text in self.mapping:
            return list(self.mapping[text])
        return _vec_from_seed(text)


def _gateway_with_fake(mapping, threshold=0.98):
    tmp = tempfile.mkdtemp()
    cfg = load_config()
    cfg["threshold"] = threshold
    cfg["store_path"] = os.path.join(tmp, "store.json")
    cfg["log_path"] = os.path.join(tmp, "hits.log")
    return Gateway(cfg, embedder=FakeEmbedder(mapping),
                   upstream=lambda text: "UPSTREAM:" + text)


class TestCosineSimilarity(unittest.TestCase):
    def test_identical_vectors_score_one(self):
        v = [1.0, 2.0, -3.0, 0.5]
        self.assertAlmostEqual(cosine_similarity(v, v), 1.0, places=9)

    def test_orthogonal_vectors_score_zero(self):
        self.assertAlmostEqual(
            cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0, places=9)

    def test_opposite_vectors_score_minus_one(self):
        self.assertAlmostEqual(
            cosine_similarity([1.0, 2.0], [-1.0, -2.0]), -1.0, places=9)

    def test_zero_vector_scores_zero(self):
        self.assertEqual(cosine_similarity([0.0, 0.0], [1.0, 2.0]), 0.0)

    def test_mismatched_lengths_score_zero(self):
        self.assertEqual(cosine_similarity([1.0], [1.0, 2.0]), 0.0)


class TestCacheStoreRoundTrip(unittest.TestCase):
    def test_store_retrieve_round_trip(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "store.json")
        store = CacheStore(path)
        vec = [0.1, 0.9, -0.3]
        store.add("What is the capital of France?", "Paris.", vec)
        # Reload from disk in a fresh object.
        store2 = CacheStore(path)
        self.assertEqual(len(store2.entries), 1)
        self.assertEqual(store2.entries[0]["prompt"],
                         "What is the capital of France?")
        self.assertEqual(store2.entries[0]["output"], "Paris.")
        self.assertEqual(store2.entries[0]["embedding"], vec)
        entry, sim = store2.best_match(vec, 0.98)
        self.assertIsNotNone(entry)
        self.assertAlmostEqual(sim, 1.0, places=9)

    def test_empty_store_returns_no_match(self):
        tmp = tempfile.mkdtemp()
        store = CacheStore(os.path.join(tmp, "store.json"))
        entry, sim = store.best_match([1.0, 0.0], 0.98)
        self.assertIsNone(entry)
        self.assertEqual(sim, -1.0)


class TestGatewayHits(unittest.TestCase):
    def test_exact_duplicate_hit(self):
        gw = _gateway_with_fake({})
        first = gw.query("What is the capital of France?")
        self.assertFalse(first["hit"])
        self.assertTrue(first["cached"])
        second = gw.query("What is the capital of France?")
        self.assertTrue(second["hit"])
        self.assertAlmostEqual(second["similarity"], 1.0, places=9)
        self.assertEqual(second["output"], first["output"])

    def test_near_duplicate_different_intent_does_not_hit(self):
        # Probe vector at cosine ~0.90 to the seed: below the 0.98 bar.
        seed = [1.0, 0.0, 0.0, 0.0]
        probe = [0.90, math.sqrt(1 - 0.90 ** 2), 0.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(seed, probe), 0.90, places=6)
        gw = _gateway_with_fake(
            {"What is the capital of France?": seed,
             "What is the capital of Spain?": probe}, threshold=0.98)
        gw.query("What is the capital of France?")
        result = gw.query("What is the capital of Spain?")
        self.assertFalse(result["hit"])
        self.assertLess(result["similarity"], 0.98)

    def test_threshold_behaviour(self):
        # Same 0.90-similar pair: hits at 0.85, misses at 0.98.
        seed = [1.0, 0.0, 0.0, 0.0]
        probe = [0.90, math.sqrt(1 - 0.90 ** 2), 0.0, 0.0]
        mapping = {"seed prompt": seed, "probe prompt": probe}
        loose = _gateway_with_fake(mapping, threshold=0.85)
        loose.query("seed prompt")
        self.assertTrue(loose.query("probe prompt")["hit"])
        strict = _gateway_with_fake(mapping, threshold=0.98)
        strict.query("seed prompt")
        self.assertFalse(strict.query("probe prompt")["hit"])

    def test_miss_stores_pair_then_hits(self):
        gw = _gateway_with_fake({})
        self.assertEqual(len(gw.store.entries), 0)
        gw.query("How do I make tea?")
        self.assertEqual(len(gw.store.entries), 1)
        self.assertTrue(gw.query("How do I make tea?")["hit"])

    def test_empty_text_rejected(self):
        gw = _gateway_with_fake({})
        for bad in ("", "   ", None, 42):
            with self.assertRaises(ValueError):
                gw.query(bad)

    def test_latency_measurement_path(self):
        gw = _gateway_with_fake({})
        r1 = gw.query("latency probe one")
        r2 = gw.query("latency probe one")
        for r in (r1, r2):
            self.assertIn("latency_ms", r)
            self.assertGreaterEqual(r["latency_ms"], 0.0)
            self.assertLess(r["latency_ms"], 60_000.0)
        stats = gw.stats_summary()
        self.assertEqual(stats["queries"], 2)
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)
        self.assertIsNotNone(stats["median_hit_ms"])
        self.assertIsNotNone(stats["median_miss_ms"])
        self.assertAlmostEqual(stats["hit_rate"], 0.5)

    def test_hit_log_written(self):
        tmp = tempfile.mkdtemp()
        cfg = load_config()
        cfg["store_path"] = os.path.join(tmp, "store.json")
        cfg["log_path"] = os.path.join(tmp, "hits.log")
        gw = Gateway(cfg, embedder=FakeEmbedder({}),
                     upstream=lambda text: "UPSTREAM:" + text)
        gw.query("probe log entry")
        gw.query("probe log entry")
        with open(os.path.join(tmp, "hits.log"), encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        self.assertEqual(len(lines), 2)
        self.assertFalse(lines[0]["hit"])
        self.assertTrue(lines[1]["hit"])


class TestLiveEmbeddings(unittest.TestCase):
    """Real bge-m3 via Ollama. Skipped if Ollama is unreachable."""

    @classmethod
    def setUpClass(cls):
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                names = [m["name"] for m in json.load(resp)["models"]]
            if not any(n.startswith("bge-m3") for n in names):
                raise unittest.SkipTest("bge-m3 not in Ollama model list")
        except Exception as exc:  # noqa: BLE001 - skip, do not fail suite
            raise unittest.SkipTest(f"Ollama unreachable: {exc}")

    def test_real_exact_duplicate_scores_one(self):
        from semantic_gateway.gateway import OllamaEmbedder
        emb = OllamaEmbedder("http://127.0.0.1:11434", "bge-m3")
        a = emb.embed("What is the capital of France?")
        b = emb.embed("What is the capital of France?")
        self.assertEqual(len(a), 1024)
        self.assertAlmostEqual(cosine_similarity(a, b), 1.0, places=6)

    def test_real_different_intent_below_threshold(self):
        from semantic_gateway.gateway import OllamaEmbedder
        emb = OllamaEmbedder("http://127.0.0.1:11434", "bge-m3")
        fr = emb.embed("What is the capital of France?")
        es = emb.embed("What is the capital of Spain?")
        sim = cosine_similarity(fr, es)
        self.assertLess(sim, 0.98,
                        f"different-intent probe scored {sim:.4f}, >= 0.98")


if __name__ == "__main__":
    unittest.main(verbosity=2)
