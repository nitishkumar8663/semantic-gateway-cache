#!/usr/bin/env python3
"""Unit + live integration tests for the semantic gateway v2 (C1-C6).

Run from the repo root:  python3 -m unittest discover -s tests -v
The FakeEmbedder tests are pure and deterministic. TestLiveEmbeddings
hits the real Ollama bge-m3 model; it is skipped if Ollama is down.
No test touches the dispatcher, the memory service, or any live model
other than bge-m3 (embeddings only) and, in the demo, gemma3:4b.

v2 notes: the gateway normalises text before embedding (C2), so the
FakeEmbedder mapping is keyed by NORMALISED text. The exact-match
fast path (C1) means normalised-equal repeats never call embed().
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
    DENYLIST_VERSION, CacheStore, Gateway, cosine_similarity, denied,
    load_config, normalize_text,
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
    """Returns fixed vectors per NORMALISED prompt (C2)."""

    def __init__(self, mapping):
        self.mapping = mapping  # normalised prompt -> vector
        self.calls = 0

    def embed(self, text):
        self.calls += 1
        if text in self.mapping:
            return list(self.mapping[text])
        return _vec_from_seed(text)


def _gateway_with_fake(mapping, threshold=0.98, **cfg_overrides):
    tmp = tempfile.mkdtemp()
    cfg = load_config()
    cfg["threshold"] = threshold
    cfg["store_path"] = os.path.join(tmp, "store.json")
    cfg["log_path"] = os.path.join(tmp, "hits.log")
    cfg.update(cfg_overrides)
    emb = FakeEmbedder(mapping)
    gw = Gateway(cfg, embedder=emb, upstream=lambda text: "UPSTREAM:" + text)
    return gw, emb


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


class TestNormalisation(unittest.TestCase):
    def test_normalise_matches_scorer(self):
        self.assertEqual(normalize_text("Tell me a joke. "), "tell me a joke")
        self.assertEqual(normalize_text("Hi"), "hi")
        self.assertEqual(normalize_text("turn the lights on!"),
                         "turn the lights on")
        self.assertEqual(normalize_text("  What   is   this?  "),
                         "what is this")


class TestDenylistV15(unittest.TestCase):
    def test_version(self):
        self.assertEqual(DENYLIST_VERSION, "v1.5")

    def test_blocks_known_escapes(self):
        for text in ("turn the lights on", "lights on in the living room",
                     "turn the lights off", "turn the lights on!",
                     "hi'; echo PWNED; '",
                     "Perception alert: the door camera saw a change "
                     "(person) at frame frame-020.png."):
            self.assertIsNotNone(denied(text), text)

    def test_status_fp_fixed(self):
        self.assertIsNone(
            denied("what's the status of my quantum computer?"))
        self.assertIsNotNone(denied("what's the status?"))
        self.assertIsNotNone(denied("what's the status of my order"))

    def test_safe_prompts_not_denied(self):
        for text in ("tell me a joke", "Hi",
                     "What is the capital of France?",
                     "remind me of the balcony plant plan"):
            self.assertIsNone(denied(text), text)


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

    def test_exact_lookup_respects_ttl(self):
        tmp = tempfile.mkdtemp()
        store = CacheStore(os.path.join(tmp, "store.json"),
                           ttl_seconds=3600.0)
        store.add("hello", "hi", [1.0, 0.0], created_at=1000.0)
        self.assertIsNotNone(store.exact_lookup("hello", now=2000.0))
        self.assertIsNone(store.exact_lookup("hello", now=10000.0))

    def test_best_match_skips_expired(self):
        tmp = tempfile.mkdtemp()
        store = CacheStore(os.path.join(tmp, "store.json"),
                           ttl_seconds=3600.0)
        store.add("hello", "hi", [1.0, 0.0], created_at=1000.0)
        entry, sim, expired = store.best_match_detailed(
            [1.0, 0.0], 0.98, now=10000.0)
        self.assertIsNone(entry)
        self.assertTrue(expired)


class TestGatewayHits(unittest.TestCase):
    def test_exact_duplicate_hit(self):
        gw, _ = _gateway_with_fake({})
        first = gw.query("What is the capital of France?")
        self.assertFalse(first["hit"])
        self.assertTrue(first["cached"])
        second = gw.query("What is the capital of France?")
        self.assertTrue(second["hit"])
        self.assertAlmostEqual(second["similarity"], 1.0, places=9)
        self.assertEqual(second["output"], first["output"])

    def test_exact_path_skips_embedding(self):
        # C1: a normalised-equal repeat must not call the embedder.
        gw, emb = _gateway_with_fake({})
        gw.query("What is the capital of France?")
        calls_after_first = emb.calls
        # The v2.9 guard embeds its 50 prototypes on the first
        # query, so calls_after_first is 51, not 1. C1 only
        # requires that a normalised-equal repeat adds no calls.
        gw.query("what is the capital of france?")
        self.assertEqual(emb.calls, calls_after_first)
        gw.query("What is the capital of France!")
        self.assertEqual(emb.calls, calls_after_first)

    def test_case_variant_hits_via_exact_path(self):
        # C1+C2: "Hi" then "hi" is a hit without embedding twice.
        gw, emb = _gateway_with_fake({})
        gw.query("Hi")
        calls_after_first = emb.calls
        second = gw.query("hi")
        self.assertTrue(second["hit"])
        self.assertTrue(second["exact_hit"])
        self.assertEqual(emb.calls, calls_after_first)

    def test_near_duplicate_different_intent_does_not_hit(self):
        # Probe vector at cosine ~0.90 to the seed: below the 0.98 bar.
        # Mapping keys are NORMALISED (C2).
        seed = [1.0, 0.0, 0.0, 0.0]
        probe = [0.90, math.sqrt(1 - 0.90 ** 2), 0.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(seed, probe), 0.90, places=6)
        gw, _ = _gateway_with_fake(
            {"what is the capital of france?": seed,
             "what is the capital of spain?": probe}, threshold=0.98)
        gw.query("What is the capital of France?")
        result = gw.query("What is the capital of Spain?")
        self.assertFalse(result["hit"])
        self.assertLess(result["similarity"], 0.98)

    def test_threshold_behaviour(self):
        # Same 0.90-similar pair: hits at 0.85, misses at 0.98.
        seed = [1.0, 0.0, 0.0, 0.0]
        probe = [0.90, math.sqrt(1 - 0.90 ** 2), 0.0, 0.0]
        mapping = {"seed prompt": seed, "probe prompt": probe}
        loose, _ = _gateway_with_fake(mapping, threshold=0.85)
        loose.query("seed prompt")
        self.assertTrue(loose.query("probe prompt")["hit"])
        strict, _ = _gateway_with_fake(mapping, threshold=0.98)
        strict.query("seed prompt")
        self.assertFalse(strict.query("probe prompt")["hit"])

    def test_miss_stores_pair_then_hits(self):
        gw, _ = _gateway_with_fake({})
        self.assertEqual(len(gw.store.entries), 0)
        gw.query("How do I make tea?")
        self.assertEqual(len(gw.store.entries), 1)
        self.assertTrue(gw.query("How do I make tea?")["hit"])

    def test_empty_text_rejected(self):
        gw, _ = _gateway_with_fake({})
        for bad in ("", "   ", None, 42):
            with self.assertRaises(ValueError):
                gw.query(bad)

    def test_latency_measurement_path(self):
        gw, _ = _gateway_with_fake({})
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


class TestGatewayC3(unittest.TestCase):
    def test_denylist_blocks_and_never_stores(self):
        gw, _ = _gateway_with_fake({})
        r = gw.query("turn the lights on")
        self.assertFalse(r["hit"])
        self.assertIsNotNone(r["blocked_by"])
        self.assertIn("denylist:", r["blocked_by"])
        self.assertEqual(len(gw.store.entries), 0)
        # A later identical prompt is still blocked, not a hit.
        r2 = gw.query("turn the lights on")
        self.assertFalse(r2["hit"])
        self.assertEqual(len(gw.store.entries), 0)

    def test_denylist_blocks_perception_alert(self):
        gw, _ = _gateway_with_fake({})
        r = gw.query("Perception alert: the door camera saw a change "
                     "(person) at frame frame-021.png.")
        self.assertFalse(r["hit"])
        self.assertIn("denylist:", r["blocked_by"] or "")
        self.assertEqual(len(gw.store.entries), 0)

    def test_route_scoping_blocks_fast_path(self):
        gw, _ = _gateway_with_fake({})
        r = gw.query("what is the temperature?", route="fast")
        self.assertFalse(r["hit"])
        self.assertEqual(r["blocked_by"], "route:fast-path-first")
        self.assertEqual(len(gw.store.entries), 0)
        # Same text on the full route consults normally.
        r2 = gw.query("what is the temperature?", route="full")
        self.assertFalse(r2["hit"])  # denied by denylist, not route
        self.assertIn("denylist:", r2["blocked_by"] or "")

    def test_ttl_expiry_blocks_stale_hit(self):
        gw, _ = _gateway_with_fake({})
        gw.query("What is the capital of France?")
        entry = gw.store.entries[0]
        # Stable fact: 7-day TTL under E1, so age it past 7 days.
        entry["created_at"] = 1000.0
        r = gw.query("What is the capital of France?",
                     now=1000.0 + 8 * 24 * 3600.0)
        self.assertFalse(r["hit"])
        self.assertTrue(r["expired_miss"])


class TestGatewayC6Degraded(unittest.TestCase):
    def test_stub_upstream_stores_miss(self):
        # Shadow mode: a stub upstream returns a placeholder so an
        # unblocked miss is stored (the store learns real traffic).
        tmp = tempfile.mkdtemp()
        cfg = load_config()
        cfg["store_path"] = os.path.join(tmp, "store.json")
        cfg["log_path"] = os.path.join(tmp, "hits.log")
        cfg["upstream_mode"] = "stub"
        gw = Gateway(cfg, embedder=FakeEmbedder({}))
        r = gw.query("a brand new prompt")
        self.assertFalse(r["hit"])
        self.assertEqual(r["output"], "STUB-OUTPUT")
        self.assertTrue(r["cached"])
        self.assertEqual(len(gw.store.entries), 1)

    def test_embed_failure_falls_back_to_upstream_uncached(self):
        class FailingEmbedder:
            def embed(self, text):
                raise RuntimeError("ollama down")

        tmp = tempfile.mkdtemp()
        cfg = load_config()
        cfg["store_path"] = os.path.join(tmp, "store.json")
        cfg["log_path"] = os.path.join(tmp, "hits.log")
        gw = Gateway(cfg, embedder=FailingEmbedder(),
                     upstream=lambda text: "UPSTREAM:" + text)
        r = gw.query("a brand new prompt")
        self.assertFalse(r["hit"])
        self.assertEqual(r["output"], "UPSTREAM:a brand new prompt")
        self.assertFalse(r["cached"])
        self.assertEqual(len(gw.store.entries), 0)


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
