#!/usr/bin/env python3
"""Semantic AI Gateway and Cache - v2.9-guard (generalising safety
guard v2.5, 24 Nov 2026).

v2.8-guard vs v2.7-guard: the guard is strengthened as a MECHANISM,
not patched per item. The v9 verdict (NO-GO) showed guard v2.3
misses five never forms on v9 dev (Rule C margin 0.20 does not
separate them: lower-heating 0.187, washing-dry 0.196 are near
misses just under the margin; dinner-ready 0.048, cancel-dentist
-0.002, sunset-time 0.009 are far below it) and still over-blocks
one creative prompt (the birthday-message Rule C FP, margin
0.2574: "write a birthday message for my mum" is close to the
action prototype "send a message to mum"). v2.8 fixes each failure
mode by a general pattern class, validated on
v3+v4+v5+v6+v7+v8+v9 dev (466 prompts):
  Rule C: creative-draft exemption (NEW). A prompt that starts with
          a creative verb (write/compose/draft/craft/pen/invent/
          imagine/create) and names a creative artefact (message/
          poem/story/song/toast/speech/haiku/limerick/...) is a
          creative draft, not an action, and is exempt from the
          margin block. The exemption is pure text and mirrors the
          v1.5 denylist "message for" logic (a draft FOR someone
          is creative, a message TO someone is messaging). It
          cannot let a messaging task through: "message to" is
          regex-blocked before Rule C, and the messaging-task
          prompts that reach Rule C have margins 0.057-0.118
          (below 0.20 anyway). No dev never item starts with a
          creative verb (probed: all 22 creative-verb dev prompts
          are cacheable), and none of the 5 Rule C reachers
          (v4-015, v4-023, v4-065, v5-058, v7-032) is a creative
          draft, so the exemption has zero FP risk on dev. It
          fixes the birthday-message FP (margin 0.2574) without
          touching the margin or the prototypes.
  Rule B v6: three widenings, one per v9 failure class.
          (a) Novel softened-imperative verbs join the action
          verb class: lower, raise, cancel, change, adjust,
          increase, decrease, reduce, move, schedule,
          reschedule, postpone, confirm. The softened-imperative
          form ("can/could you <verb>") now catches "lower the
          heating" and "cancel my dentist appointment". The verbs
          also join Rule A, so a leading "Lower the thermostat"
          (v7-032, previously a Rule C reacher) is now
          form-blocked. The wh-word guard keeps factual questions
          out ("can you change how many ..." has a wh-word).
          (b) Completion-state widening: food entities (dinner,
          lunch, breakfast, supper, meal, food, roast, soup,
          cake, bread, pasta, rice) and household entities
          (clothes, dishes, room) join the live entities, and
          dry, wet, damp, clean, dirty, full, empty, warm, cool,
          cooked, baked, frozen, fresh, stale join the state
          words. The state form now catches "is dinner ready
          yet" (dinner + ready) and "is the washing dry yet"
          (washing + dry).
          (c) Live-fact form: "what time is (sunset|sunrise|
          moonrise|moonset|dawn|dusk|high tide|low tide|the tide)"
          (the event time is inherently daily, so no day marker
          is needed) and "what time is <noun> (today|tomorrow|
          tonight)" (a specific day's schedule). Catches "what
          time is sunset today". A time-zone question ("what time
          is it in London") does not match (no event noun, and
          "what time is it" is already denylist-blocked).
Dev result (v3+v4+v5+v6+v7+v8+v9 dev, 466 prompts): see
guard-v10-build/GUARD-V10-REPORT.md.

v2.7-guard vs v2.6-guard: the guard is strengthened as a MECHANISM,
not patched per item. The v8 verdict (NO-GO) showed guard v2.2
misses four short everyday never forms on v8 dev (Rule C margin
0.20 does not separate them: the softened imperatives and the
novel state/location forms fall below the margin band) and the
v8 candidate named the fresh failure classes as round-4 material.
v2.7 fixes each failure class by a general pattern class,
validated on v3+v4+v5+v6+v7+v8 dev (408 prompts):
  Rule B v5: five new general forms, one per v8 failure class.
          (a) Uncontracted weather-like: "what is the weather
          like/doing" joins "what's ..." - but only with a live
          marker (outside / right now / at the moment / today /
          here / now / currently) after it, so "what is the
          weather like on Mars" (factual) stays unblocked.
          (b) Presence form: "is/are someone/anyone/somebody/
          anybody at/in <home location>" ("is someone at the
          front door", "is anyone in the kitchen", "is anyone
          home"). The location must be a home noun; "is anyone
          at the party" does not match.
          (c) Softened-imperative form: "can/could you <action
          verb>" - an action request phrased as a question, which
          Rule A misses because its question guard keeps it off.
          The verb must be in the Rule A action-verb class
          (set/book/turn/lock/...), and the prompt must contain
          no wh-word, so "can you tell me ..." (tell is not an
          action verb) and "can you count how many ..." (wh-word)
          do not match. Validated on dev: catches 5/5 never
          softened imperatives, 0 FP on cacheable dev.
          (d) More completion state words join the state form:
          boiled, brewed, charged, downloaded, uploaded,
          printed ("has the kettle boiled"). "phone", "battery"
          and "coffee" join the live entities ("is my phone
          charged", "has the coffee brewed").
          (e) The did-i-leave form widens to "did i (put|lose|place)
          my/our" ("where did I put my phone") - the belonging
          ("my"/"our") is required for put/lose/place, so "where
          did i put the emphasis" (a metaphor, not a live
          location) does not match; "did i leave" keeps working
          with "the" ("leave the front gate open").
  Rule C: UNCHANGED (per-class margins 0.20/0.20/0.10,
          prototypes unchanged). The intent-classifier lever was
          tried in v2.6 and DECLINED on LOFO CV evidence; it is
          not retried here. The Rule B v5 forms catch all 4 v8
          dev escapes, so the classifier adds nothing on dev.
Dev result (v3+v4+v5+v6+v7+v8 dev, 408 prompts): see
guard-v9-build/GUARD-V9-REPORT.md.

v2.6-guard vs v2.5-guard: the guard is strengthened as a MECHANISM,
not patched per item. The v7 verdict (NO-GO) showed guard v2.1
misses four short everyday never forms on v7 dev (Rule C margin
0.20 does not separate them: washing-finished 0.1691, weather-now
0.0842, house-temperature 0.0929, parcel-delivered 0.0444 - all
below the highest safe question margin 0.18, so NO margin separates
them) and over-blocks one creative prompt (the birthday-message
regex FP). v2.6 fixes each failure mode by a general pattern class,
validated on v3+v4+v5+v6+v7 dev (346 prompts):
  Denylist v1.5: the "message to/for" pattern is split. "message
          to <recipient>" still always blocks (a message TO
          someone is a messaging action). "message for
          <recipient>" now skips when a creative verb
          (draft/write/create/compose) appears before "message":
          drafting a birthday/thank-you message FOR someone is a
          creative artefact, not a messaging action. "Send/text a
          message for ..." still blocks (no creative verb).
          Validated on dev: no recall loss (the 2 dev prompts
          matching the pattern have alternate blockers), and the
          creative-draft class is unblocked (synthetic checks).
  Rule B v4: three new general live-state forms, one per v7 dev
          failure class. (a) Laundry + delivery entities join the
          state form (washing, laundry, parcel, delivery,
          package, shipment) and delivered/arrived join the state
          words: "is the washing finished", "has my parcel been
          delivered". (b) Weather-like form: "what's the weather
          like/doing". (c) Indoor-temperature form: "how warm/cool
          is it" + a home location (in the/my house/flat/home/
          room/kitchen/bedroom/lounge/living room, or at home).
          Bare "inside"/"here" are deliberately NOT locations:
          "how warm is it inside the Earth" stays unblocked.
          Plus a delivery-status form for "my/the/our order" +
          delivered/arrived/ready/dispatched/shipped ("has my
          order been delivered", "is my order ready"); the
          article-before-noun requirement keeps "what is the new
          world order" unblocked. All four v7 dev escapes are
          caught, 0 new FP on cacheable dev.
  Rule C: UNCHANGED (per-class margins 0.20/0.20/0.10,
          prototypes unchanged). The intent-classifier lever was
          tried and DECLINED: a logistic regression on the 50
          prototype similarities, leave-one-family-out CV on dev,
          reaches at best recall 4/9 at FP 0 (lam=1.0, thr=0.95)
          on Rule C reachers, and 7/9 at FP 4/165 (thr=0.9) -
          it misses the two statement-form agent-task bodies the
          margin catches, and FPs on how-to router questions. No
          threshold gives recall 1.0 at FP 0. The classifier adds
          nothing once the Rule B forms are in (the remaining
          reacher-never items are all caught by the margin), so it
          is not deployed. See GUARD-V8-REPORT.md for the numbers.
Dev result (v3+v4+v5+v6+v7 dev, 346 prompts): see
guard-v8-build/GUARD-V8-REPORT.md.

  Denylist v1.4: the bare \\bmessage\\b pattern is narrowed to
          messaging-action forms only (a send/text/forward verb
          within 40 chars before "message", "message to/for
          <recipient>", or "message <recipient>" as a verb). It
          blocked a creative story ("finds a message in a
          bottle": FP on v6 dev). Messaging actions are still
          caught; "message Maa ..." is now also caught by Rule A
          ("message" joins the verb class).
  Rule A v3: yard-work verbs join the class (mow, rake, prune,
          weed - "trim" stays out: it also heads video edits) and
          the messaging verb "message". Plus a question guard:
          Rule A does not fire on a factual question (a wh-word
          anywhere in the prompt, or a trailing "?"), so a leading
          noun-verb ("Water boils at what temperature ...") and a
          factual "count" ("Count the continents ..., how many
          are there?") no longer block. The guard is checked on
          the raw text for "?" (normalisation strips it).
  Rule B v3: the where-form takes "are" as well as "is"
          ("where are my car keys"); the daily-count form takes
          the wider time windows "last night / last week / this
          morning / last month / this month / this year / last
          year" ("how many hours did I sleep last night"); a new
          weather-now form ("is it raining / snowing") generalises
          the weather class ("is it raining outside right now").
  Rule C: PER-CATEGORY margin (guard v2.1). A probe of all 295
          dev prompts with real bge-m3 (probe_v7.py) REFUTED the
          documented guess in its imperative form: an imperative
          margin of 0.10 would FP on "write a python function to
          sort a list" (+0.1070), and the never imperatives that
          reach Rule C sit at +0.21/+0.27 (already caught at 0.20)
          or +0.0084 ("mow the lawn", uncatchable by any margin
          that keeps FP 0.0). The class that DOES separate is
          statement: safe statements max +0.0889, while the
          statement-form agent-task bodies sit at +0.1093/+0.2360.
          So: imperative 0.20, question 0.20, statement 0.10.
          Prototypes UNCHANGED (candidate agent-task prototypes
          moved the bus-body margin by exactly 0.0000;
          probe_v7b.py). Do NOT lower the imperative/question
          margin below 0.20 and do NOT add item-specific
          prototypes (that is patching, not generalising).
Dev result (v3+v4+v5+v6 dev, 295 prompts): see
guard-v7-build/GUARD-V7-REPORT.md.

ITERATION (for the next round, if v10 still fails): the guard is
modular - each layer is a separate function with its own unit
tests, so a next round can strengthen one layer without touching
the others. The intent-classifier lever was tried in v2.6 and
DECLINED on LOFO CV evidence (see the v2.6 header above); the
next lever, if v10 fails on a fresh form class, is widening Rule B
to that class (the v2.6/v2.7/v2.8 templates show how) - or a genuinely
intent-trained embedding model (fine-tuned, not a linear probe
on bge-m3 sims), which needs more training signal than 466 dev
prompts. The statement margin 0.10 is thin: its gap to the
highest safe statement is 0.02 on dev. Do NOT lower the
imperative/question margin below 0.20 (FP rises steeply: safe
imperatives reach +0.107, safe questions +0.120 on dev) and do NOT
add item-specific prototypes (that is patching, not generalising).

v2.3-guard history (kept for reference):
  Rule A: anchored imperative action verb (a general verb class:
          turn, switch, set, unlock, lock, open, close, bolt,
          secure, kill, add, remove, remind, wake, count, send,
          build, start, stop, ...). The verb must lead the prompt;
          information verbs (tell/show/explain/define/translate/
          write/make/give) are NOT in the class.
  Rule B: live-state question forms (interrogative + live-entity
          noun + state word; "did I leave ..."; weather forms;
          live advice "do I need ... today"; list queries).
  Rule C: two-sided embedding margin - max cosine similarity to
          action prototypes minus max similarity to safe
          prototypes, block when >= 0.20. Reuses the prompt
          embedding already computed for the cache lookup, so the
          marginal cost is ~53 cosine similarities (microseconds).
Rules A and B run on normalised text before the exact-match fast
path (so they also protect exact-match); Rule C runs after
embedding, before the similarity lookup. Guard blocks are reported
as "denylist:guard-<rule>" so the eval driver counts them as
denylist blocks (recall and FP). Dev result (v3 dev + v4 dev, 180
prompts): regex alone recall 0.688, FP 0.0; regex + guard recall
1.000 (77/77 never blocked), FP 0.000 (0/61 gateway safe). See
guard-build/GUARD-REPORT.md. The guard's prototypes are general
canonical phrases (not dev copies); v5 (fresh holdout) is the
generalisation test.

v2.2-enh history (kept for reference):
  E2  Factual-only request-frame stripping in normalisation
      (frame_strip_factual): strip a leading request frame
      ("tell me the", "what is the", ...) before embedding, for
      stable-factual queries only.
  E3b Factual threshold 0.80 (threshold_factual 0.80 instead of
      0.85).
  E4  Legacy backfill (legacy_backfill): entries loaded from disk
      without a TTL class are classified at load (stable-factual /
      stable-generative -> 7d) instead of keeping 24h.
  E5  Stable-generative TTL (generative_ttl): a self-contained
      creative artefact (write/make/create a haiku, video, code)
      keeps its cached answer for 7 days like a stable fact;
      summaries and other source-dependent generative prompts keep
      24h. The TTL class is assigned at write time
      (is_stable_generative).
  E6  Per-category threshold 0.85 for stable-generative queries
      (threshold_generative): a creative prompt has no single
      right answer, so a near-paraphrase artefact is an acceptable
      substitute; factual keeps 0.85, everything else keeps 0.90.
Flow, endpoints and design decisions: unchanged from v2.1-enh
(see gateway_v3.py header / ENH-REPORT.md).

v2.1-enh history (kept for reference):
  E1  Family-aware TTL: a stable factual question keeps its cached
      answer for 7 days (ttl_stable_hours) instead of 24h; every
      other prompt keeps the 24h TTL. The TTL class is assigned at
      write time from the prompt text (is_stable_factual) and stored
      on the entry; entries loaded from disk without a class
      (legacy, including the demo seed) keep the conservative 24h
      TTL, so a TTL change rolls out without a backfill migration
      and entries rotate naturally. The TTL is a property of the
      stored ANSWER, not of the incoming question's phrasing: a
      stable fact stays correct however it is asked, so there is no
      query-side TTL cap. (A query-side cap was tried first and
      reverted: it blocked declarative factual questions such as
      "Jupiter has how many moons?" from matching days-old stable
      entries, costing 4 dev hits, while adding no safety on dev -
      the ttl24 queries that reach the gateway never match factual
      entries at threshold.)
      Dev result: see enhance-build/ENH-REPORT.md (per-candidate
      dev scores against v3.1, seed and empty modes).
  E3  Per-category threshold (ablation): when a query is
      classified stable-factual, the similarity threshold is 0.85
      instead of 0.90 (threshold_factual). The factual classifier
      is the second guard: only factual questions get the lower
      bar, so generative / chatter / agent-task prompts keep 0.90
      and the BUS wrong-match (0.8033) stays a miss. Dev result:
      see enhance-build/ENH-REPORT.md.

Flow for POST /query {"text": "...", "route": "full"}:
  1. Route check: route != "full" -> miss, nothing consulted/stored.
  2. Denylist v1.3 check: denied -> miss, nothing consulted/stored.
  3. Normalise the text (C2).
  4. Exact-match fast path (C1): normalised equality against the
     store index, TTL-checked (E1: the entry's own TTL class).
     Hit -> return cached output, no embed.
  5. Embed the normalised text with bge-m3 via Ollama /api/embeddings.
  6. Cosine-similarity against cached prompt embeddings in a local
     JSON store, skipping entries older than their effective TTL.
     Best match >= threshold is a HIT: return the cached output,
     no generation.
  7. On a MISS, call the configured upstream (dispatcher /dispatch,
     or an Ollama model), store the prompt/output/embedding pair
     with its TTL class (E1), and return the fresh output.

Design decisions (see README.md):
  - Local JSON vector store, NOT the shared memory service. The
    memory service is the user's common memory; prompt/output cache
    pairs are ephemeral serving state and must not pollute it.
  - Stdlib only. No torch, no extra embedding model: bge-m3 is
    already on disk in Ollama (1.2 GB).
  - No Llama model anywhere.
  - Loopback only (127.0.0.1). Never 0.0.0.0.

Endpoints (all JSON):
  GET  /health            -> {"ok": true, ...}
  POST /query  {text, route?} -> {"hit": bool, "output": str,
                              "similarity": float|null,
                              "latency_ms": float, "cached": bool,
                              "blocked_by": str|null, ...}
  POST /cache  {text, output} -> store a pair (embedding computed)
  GET  /stats             -> query/hit/miss counts, latency medians
  POST /clear             -> empty the store (demo/test use)

Run:
  python3 gateway.py [--config config.json] [--port 18795]
  Env overrides: GATEWAY_THRESHOLD, GATEWAY_UPSTREAM_MODE
  (none|ollama|dispatcher), GATEWAY_UPSTREAM_MODEL,
  GATEWAY_STORE_PATH, GATEWAY_PORT, GATEWAY_TTL_STABLE_HOURS.
"""

import argparse
import json
import math
import os
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))

GATEWAY_VERSION = "v2.9-guard"
GUARD_VERSION = "v2.5"
GUARD_MARGIN_DEFAULT = 0.20
GUARD_MARGIN_STATEMENT_DEFAULT = 0.10  # v2.5: per-category Rule C;
                                     # statement prompts (long agent-task
                                     # bodies vs short chatter) separate
                                     # at 0.10; imperative/question stay
                                     # 0.20 (probe_v7.py: safe imperatives
                                     # reach +0.107, safe questions +0.120)
DEFAULT_CONFIG = {
    "threshold": 0.98,
    "embedding_model": "bge-m3",
    "ollama_url": "http://127.0.0.1:11434",
    "upstream_mode": "none",          # none | stub | ollama | dispatcher
    "upstream_model": "gemma3:4b-it-q8_0",
    "upstream_max_tokens": 48,
    "dispatcher_url": "http://127.0.0.1:18791",
    "store_path": os.path.join(HERE, "cache_store.json"),
    "log_path": os.path.join(HERE, "cache_hits.log.jsonl"),
    "host": "127.0.0.1",
    "port": 18795,
    "ttl_hours": 24.0,                # C3: entries older than this never match
    "ttl_stable_hours": 168.0,        # E1+E5: stable entries live 7 days
    "threshold_factual": None,        # E3: lower threshold for factual
                                       # queries; None = same as threshold
    "threshold_generative": None,     # E6: lower threshold for
                                       # stable-generative queries
    "generative_ttl": True,           # E5: creative artefacts get the
                                       # 7d TTL; False = v2.1 behaviour
    "frame_strip_factual": False,     # E2: strip request frames for
                                       # factual queries before embedding
    "legacy_backfill": False,         # E4: classify legacy entries at
                                       # load instead of keeping 24h
    "normalise": True,                # C2: normalise before embedding
    "exact_match": True,              # C1: normalised-equality fast path
    "denylist_enabled": True,         # C3: denylist v1.4 in the gateway
    "route_scoping": True,            # C3: only route=full consults/stores
    "guard_enabled": True,            # v2.8: generalising guard v2.4 (Rules A+B+C)
    "guard_margin": GUARD_MARGIN_DEFAULT,  # v2.5 Rule C: action-safe margin
                                     # for imperative/question prompts
    "guard_margin_statement": GUARD_MARGIN_STATEMENT_DEFAULT,  # v2.5 Rule C:
                                     # margin for statement prompts
    "keep_alive": "24h",              # C5: pin bge-m3 resident in Ollama
}

# ---------------------------------------------------------------------------
# C2: text normalisation - IDENTICAL to frozen scorer v3.0's
# normalize_text (eval/score.py), so dev scores are comparable.
# ---------------------------------------------------------------------------

def normalize_text(text):
    """Lowercase, strip, drop trailing punctuation, collapse whitespace."""
    t = text.strip().lower()
    t = re.sub(r"[.!?,:;]+$", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


# ---------------------------------------------------------------------------
# E1: stable-factual classifier (prompt text only; no eval labels).
# A prompt is stable-factual when it asks a question with a stable
# factual answer, phrased as an interrogative, a "tell me" request
# for a fact, or a deterministic transform (translate / define /
# explain / describe a concept). Everything else - generative
# prompts (write/make/create/summarise), chatter (jokes, ping),
# agent-task bodies, imperative requests - is NOT stable-factual
# and keeps the 24h TTL. The classifier is deliberately a
# whitelist: a false negative only loses a hit; a false positive
# could serve a days-old answer. It is designed from general
# principles, not tuned to dev texts, so it must generalise to
# unseen families. The denylist runs before this in query(), so
# action/time/state prompts never reach it.
# ---------------------------------------------------------------------------

_STABLE_FACTUAL_PATTERNS = [
    re.compile(r"^(what|who|whom|whose|which|where|when|why)\b"),
    re.compile(r"^how (do|does|did|can|could|to|many|much|old|far|long|tall)\b"),
    re.compile(r"^tell me (the|about|what|who|which|how)\b"),
    re.compile(r"^(translate|explain|define|describe)\b"),
]


def is_stable_factual(norm_text):
    """True when a normalised prompt is a stable factual question.

    Input is the C2-normalised text (lowercase, trailing punctuation
    stripped). Returns False for anything that is not clearly a
    factual question: generative, chatter, agent-task, declarative
    statements ("Jupiter has how many moons?") and imperatives.
    """
    t = (norm_text or "").strip()
    if not t:
        return False
    for pat in _STABLE_FACTUAL_PATTERNS:
        if pat.search(t):
            return True
    return False


# ---------------------------------------------------------------------------
# E5/E6: stable-generative classifier (prompt text only; no eval labels).
# A prompt is stable-generative when it asks for a self-contained
# creative artefact - write/make/create a haiku, a video, a piece of
# code - whose output does not decay: re-serving the same haiku or
# video script days later is still a correct answer to the same
# request. The risk for generative prompts is topic mismatch, not
# staleness, and that is guarded by the similarity threshold (E6),
# not by TTL. Source-dependent generative prompts (summarise /
# summarize a report, explain a changing situation) are NOT
# stable-generative and keep the 24h TTL: their source can change.
# The creative verb must lead the request: it has to appear in the
# first 40 characters (an optional leading clause such as "Using
# Remotion, " is allowed). An unanchored match was tried first and
# reverted: it classified a long agent-task body as generative
# because the word "write" occurs at character 253 ("... and write
# your one-line reply to outbox/ ..."), which would give a bus
# body a 7-day TTL and the 0.85 bar - exactly the population the
# threshold is meant to protect. "make" is anchored at the start.
_STABLE_GENERATIVE_HEAD_CHARS = 40
_STABLE_GENERATIVE_VERBS = re.compile(r"\b(write|create|compose)\b")
_STABLE_GENERATIVE_MAKE = re.compile(r"^make\b")


def is_stable_generative(norm_text):
    """True when a normalised prompt asks for a self-contained
    creative artefact, with the creative verb leading the request.
    False for summaries, chatter, factual questions, agent-task
    bodies (however long) and anything else."""
    t = (norm_text or "").strip()
    if not t:
        return False
    if _STABLE_GENERATIVE_VERBS.search(t[:_STABLE_GENERATIVE_HEAD_CHARS]):
        return True
    return bool(_STABLE_GENERATIVE_MAKE.match(t))


# ---------------------------------------------------------------------------
# E2: request-frame stripping (factual-only scope). A leading request
# frame ("tell me the", "what is the", "how do i", ...) carries no
# content; stripping it before embedding canonicalises "Tell me the
# capital of France." and "what is the capital of France?" to the
# same key ("capital of france"). Applied ONLY to stable-factual
# queries (embedding_text): generative / chatter / agent-task
# prompts keep their full text, so the frame vocabulary cannot
# conflate two different tasks. Declined after ablation (see report):
# the one remaining factual near-miss ("when does the tube close on
# sundays", 0.7734) is a wording gap (tube vs Underground), not a
# frame gap, and stripping lowers its similarity (0.7557).
# ---------------------------------------------------------------------------

_FRAME_STRIP_PATTERNS = [
    re.compile(r"^(tell me (the|about|what|who|which|how)\s+)"),
    re.compile(r"^(what'?s the\s+)"),
    re.compile(r"^(what is (the\s+)?)"),
    re.compile(r"^(how (do|does|did|can|could)\s+(i|you|we|one)\s+)"),
    re.compile(r"^(please\s+)"),
]


def strip_request_frame(norm_text):
    """Remove one leading request frame from normalised text."""
    t = (norm_text or "").strip()
    for pat in _FRAME_STRIP_PATTERNS:
        m = pat.match(t)
        if m:
            t = t[m.end():].strip()
            break
    return t


def embedding_text(norm_text, frame_strip_factual=False):
    """Text to embed (and to use as the exact-match key) for a
    normalised prompt. With E2 on, stable-factual queries embed
    frame-stripped; everything else embeds as normalised."""
    if frame_strip_factual and is_stable_factual(norm_text):
        return strip_request_frame(norm_text)
    return norm_text


# ---------------------------------------------------------------------------
# C3: denylist v1.5 (2026-11-23). v1.4 + one fix, designed on dev only:
#   - message-for FP fix: the "message to/for" pattern blocked a
#     creative prompt ("draft a birthday message for my friend",
#     FP on v7 holdout). Split: "message to <recipient>" still
#     always blocks (a message TO someone is a messaging action);
#     "message for <recipient>" now skips when a creative verb
#     (draft/write/create/compose) appears before "message" in the
#     same clause - drafting a birthday/thank-you message FOR
#     someone is a creative artefact, not a messaging action.
#     "Send/text a message for ..." still blocks (no creative
#     verb). The guard lives in denied() (_MSG_FOR_RE +
#     _CREATIVE_BEFORE_MSG_RE). Validated on dev: no recall loss
#     (the 2 dev prompts matching the pattern have alternate
#     blockers) and the creative-draft class is unblocked.
#   - v1.4 (2026-11-23). v1.3 + one fix, designed on dev only:
#   - message FP fix: the bare \\bmessage\\b pattern blocked a
#     creative story ("finds a message in a bottle": FP on v6 dev).
#     Replaced by messaging-action forms only (a send/text/forward
#     verb within 40 chars before "message", "message to/for
#     <recipient>", "message <recipient>" as a verb). Messaging
#     actions are still caught; "message Maa ..." is also caught by
#     Rule A v3 ("message" joins the verb class). The one v4 dev bus
#     body whose only blocker was \\bmessage\\b is now caught by
#     the per-category Rule C statement margin (0.10).
#   - v1.3 (2026-11-23). v1.2 + one fix, designed on dev only:
#   - temperature FP fix: the bare \btemperature\b pattern blocked
#     stable factual questions ("At what temperature does water
#     boil/freeze?": 4 items, FP 0.105 on v5 dev). Replaced by
#     live-temperature question forms only: "what('s| is) the
#     temperature", "temperature (outside|now|today|here|in)",
#     "how (hot|cold) is it", and the standalone word "temp".
#     Live-temp never items ("what is the temperature?", "what is
#     the temperature outside") are still caught; the boil/freeze
#     factual questions are not. Validated on v3+v4+v5 dev: FP
#     0.067 -> 0.029 (the remaining 3 are v3 bus bodies, a v3
#     labelling artefact), recall unchanged. This is a
#     pattern-class fix (narrow a too-broad pattern to its intended
#     class), not a per-item patch.
#   - status FP fix: "what's the status of my quantum computer?"
#     (safe, factual) was blocked by both \bstatus of\b and
#     \bwhat'?s the status\b. Replaced by the anchored bare form plus
#     a narrowed "status of <live thing>" list. v1.2 recall 1.0 and
#     FP 0.0 on gateway traffic on dev (see eval design_denylist.py).
#   - perception alerts: the NM-A pair (0.9976 / 0.9915) cannot be
#     stopped by any threshold; only a denylist pattern stops it.
#   - verb-object lights: "turn the lights on/off" and "lights on
#     in the living room" escape v1.1's adjacent-word patterns.
#   - shell-injection structure: quote/semicolon/pipe + command.
# ---------------------------------------------------------------------------

DENYLIST_VERSION = "v1.5"
DENYLIST = [
    r"\bunlock\b", r"\block\b",
    r"\bturn (on|off)\b", r"\bswitch (on|off)\b",
    r"\bsend\b",
    # v1.4: the bare \\bmessage\\b blocked a creative story
    # ("finds a message in a bottle", v6 dev FP). "message" now
    # matches only a messaging action: a send/text/forward verb
    # within 40 chars before it, "message to/for <recipient>",
    # or "message <recipient>" as a verb. "message Maa ..." is
    # also caught by Rule A (v2.5 verb class).
    r"\b(send|text|forward|share|pass|leave|drop|deliver|reply)\b[^,;]{0,40}\bmessage\b",
    # v1.5: "message to" always blocks; "message for" is checked
    # separately in denied() with the creative-verb guard (a draft
    # FOR someone is creative, a message TO someone is messaging).
    r"\bmessage\b[^,;]{0,12}\bto\b",
    r"\bmessage\s+(maa|mama|papa|nimu|reema|me|him|her|them|us)\b",
    r"\bremind me (to|on)\b", r"\bset a reminder\b", r"\breminder (for|on|to)\b",
    r"\bbuild\b", r"\brebuild\b",
    r"\bopen the door\b",
    r"\btell (maa|mama|papa|nimu|reema)\b",
    r"\bfollow @",
    r"\bwhat(?:'s| is) the temperature\b", r"\btemperature (outside|now|today|here|in)\b", r"\btemp\b",
    r"\bwhat time is it\b", r"\bwhat'?s the time\b", r"\bcurrent time\b",
    r"\btell me the time\b",
    r"\bwhat(?:'s| is) the date\b", r"\bwhat day is it\b",
    r"\btoday'?s date\b",
    r"\bis the door\b", r"\bis .* locked\b", r"\bis .* unlocked\b",
    r"\bgpu temp\b",
    r"\bis the spark\b",
    r"^\s*what'?s the status\s*\??\s*$",
    r"\bstatus of (my|the|our|a|an) (order|delivery|shipment|parcel|package|flight|train|build|application|visa|case|claim|ticket|booking|account|door|device|system|service|server|network|job|deployment|request|payment|refund|it|that|this)\b",
    r"\bhow (hot|cold) is it\b", r"\bhow hot is the\b",
    r"\bhumidity\b",
    r"\brain (today|tomorrow)\b", r"\bwill it rain\b",
    r"\bperception alert\b",
    r"\bturn (the )?lights? (on|off)\b",
    r"\blights? (on|off)\b",
    r";\s*(echo|rm|cat|ls|sh|bash|sudo|curl|wget|python|node|chmod|kill|mv|cp|touch)\b",
    r"""['"]\s*;\s*\w""",
    r"\|\s*(echo|rm|cat|sh|bash|sudo|curl|wget)\b",
    r"\$\([^)]*\)",
]
DENYLIST_COMPILED = [re.compile(p) for p in DENYLIST]

# v1.5: "message for <recipient>" blocks unless a creative verb
# (draft/write/create/compose) appears before "message" in the same
# clause - drafting a birthday/thank-you message FOR someone is a
# creative artefact, not a messaging action. "message to" is always
# blocked (it is in DENYLIST above). "make" is deliberately NOT a
# creative verb here: "make a message for mum" reads as messaging.
_MSG_FOR_RE = re.compile(r"\bmessage\b[^,;]{0,12}\bfor\b")
_MSG_FOR_PATTERN = r"\bmessage\b[^,;]{0,12}\bfor\b"
_CREATIVE_BEFORE_MSG_RE = re.compile(
    r"\b(draft|write|create|compose)\b[^,;]{0,30}\bmessage\b")


def denied(text):
    """Return the matching denylist pattern, or None. Case-insensitive."""
    low = text.lower()
    for pat in DENYLIST_COMPILED:
        if pat.search(low):
            return pat.pattern
    if _MSG_FOR_RE.search(low) and not _CREATIVE_BEFORE_MSG_RE.search(low):
        return _MSG_FOR_PATTERN
    return None


# ---------------------------------------------------------------------------
# v2.7-guard v2.3: generalising safety guard (Rules A + B + C).
# Layer 2, behind the regex denylist v1.5 (layer 1). The guard blocks
# action / live-state / agent-task prompts the regex misses. It is a
# multi-signal intent classifier, not a pattern list for specific
# items: Rule A is a general verb class (v2: expanded with
# home-action verbs + make-for), Rule B is a general live-entity +
# state form (v2: expanded entities/state words + stock,
# where-is-mine, daily-count forms), Rule C is semantic similarity
# to canonical prototype phrases. Prototypes are general canonical
# phrases (not dev copies); the source of truth is
# eval/prototypes.json + eval/safe_prototypes.json, and the unit
# tests assert the module constants match those files. v2.4 drops
# the "what is the temperature outside" action prototype (it caused
# the Rule C FP on temperature factual questions; the regex catches
# live-temp items).
# ---------------------------------------------------------------------------

# Canonical action phrases (never cacheable): home actions, live
# state/time, reminders, lists, messages, agent tasks.
ACTION_PROTOTYPES = [
    "apply the code changes and report back",
    "build and install the plugin",
    "task update from the agent",
    "turn on the washing machine",
    "start the dishwasher",
    "switch off the oven",
    "unlock a door",
    "lock the door",
    "open the front door",
    "is the door locked",
    "is the door shut",
    "turn the heating on",
    "turn up the heating",
    "set the thermostat",
    "make it warmer",
    "turn the lights on",
    "turn the lights off",
    "switch the lamp on",
    "switch the lamp off",
    "add milk to the shopping list",
    "what is on my shopping list",
    "remove bread from the list",
    "send a message to mum",
    "tell papa the door is unlocked",
    "perception alert",
    "the front door is open",
    "remind me to call mum",
    "set a reminder for tomorrow",
    "set a timer",
    "set an alarm",
    "count down ten minutes",
    "will it rain",
    "what is the weather forecast",
]

# Canonical safe phrases (cacheable): factual questions, creative
# requests, chatter. Rule C blocks only when the prompt is closer
# to the action set than to this set by the margin.
SAFE_PROTOTYPES = [
    "how are you doing",
    "what is up",
    "tell me a joke",
    "good morning",
    "how is your day",
    "what is the capital of France",
    "who wrote The Hobbit",
    "how do you say thank you in Spanish",
    "explain photosynthesis in one sentence",
    "how many moons does Jupiter have",
    "what is the largest planet in our solar system",
    "how do you cook rice properly",
    "how do planes stay in the air",
    "write a haiku about the moon",
    "write a short story about a cat",
    "summarise this article in one paragraph",
    "create a video script about space",
]

# Rule A v3: anchored imperative action verb (general verb class).
# v2.8 adds the novel softened-imperative verbs v2.7 missed (lower,
# raise, cancel, change, adjust, increase, decrease, reduce, move,
# schedule, reschedule, postpone, confirm - "lower the heating",
# "cancel my dentist appointment"). They join Rule A too, so a
# leading "Lower the thermostat" (v7-032, previously a Rule C
# reacher) is now form-blocked. The wh-word guard keeps factual
# questions out. "check" stays out: it heads information requests
# ("check the weather", "check my balance") as often as actions.
# v2.5 adds the yard-work verbs v2.4 missed (mow, rake, prune,
# weed - "trim" stays out: it also heads video edits) and the
# messaging verb "message" ("message Maa ..."), plus a question
# guard (below): Rule A does not fire on a factual question.
# v2.4 adds the home-action verbs v1.0 missed (boil, preheat, play,
# boost, brew, cook, bake, wash, dry, clean, vacuum, mop, charge,
# iron, sweep, dust) plus a "make <beneficiary> <article>" form
# ("make me a coffee") with an article constraint so "make me laugh"
# (chatter) and "make a video" (creative) do not match. "make" alone
# stays OUT of the verb class (it heads creative requests).
# The verb must lead the prompt (optional leading "please").
# Information verbs (tell/show/explain/describe/define/translate/
# write/make/give) are deliberately NOT in the class: they head
# information or creative requests, not actions.
_ACTION_VERBS = (
    r"turn|switch|set|unlock|lock|open|close|bolt|secure|kill|add|remove|"
    r"delete|remind|wake|count|send|build|rebuild|start|stop|pause|resume|"
    r"water|feed|arm|disarm|enable|disable|activate|deactivate|book|order|"
    r"call|text|email|put|dim|brighten|heat|cool|mute|unmute|"
    r"boil|preheat|play|boost|brew|cook|bake|wash|dry|clean|vacuum|mop|"
    r"charge|iron|sweep|dust|mow|rake|prune|weed|message|"
    r"lower|raise|cancel|change|adjust|increase|decrease|reduce|move|"
    r"schedule|reschedule|postpone|confirm"
)
_RULE_A_RE = re.compile(r"^(please\s+)?(" + _ACTION_VERBS + r")\b")
# v2.5 question guard: a wh-word anywhere in the prompt, or a
# trailing "?" on the raw text, marks a factual question. Rule A
# matches the first word regardless of part of speech, so without
# this guard it blocks "Water boils at what temperature ..."
# ("water" as a noun) and "Count the continents ..., how many
# are there?" (factual "count"). The "?" is checked on the raw
# text: normalisation strips trailing punctuation.
_QUESTION_WORD_RE = re.compile(
    r"\b(what|who|whom|whose|which|where|when|why|how)\b")
_RULE_A_MAKE_RE = re.compile(
    r"^(please\s+)?make\s+(me|us|him|her|them)\s+(a|an|some|the|my)\b")

# Rule B v5: live-state question forms. v2.8 widens the completion-
# state class: food entities (dinner, lunch, breakfast, supper, meal,
# food, roast, soup, cake, bread, pasta, rice) and household entities
# (clothes, dishes, room) join the live entities, and dry, wet, damp,
# clean, dirty, full, empty, warm, cool, cooked, baked, frozen, fresh,
# stale join the state words ("is dinner ready yet", "is the washing
# dry yet"). v2.7 adds five general forms, one per v8 failure class:
# an uncontracted weather-like form ("what is the weather like/doing"
# + a live marker, so "what is the weather like on Mars" stays
# unblocked); a presence form ("is someone/anyone at/in <home
# location>", plus "is anyone home"); a softened-imperative form
# ("can/could you <action verb>" with no wh-word, so "can you tell
# me ..." and "can you count how many ..." do not match); more
# completion state words (boiled, brewed, charged, downloaded,
# uploaded, printed) and "phone" / "battery" as live entities; and
# the did-i-leave form widens to "did i (put|lose|place) my/our"
# (the belonging is required, so "where did i put the emphasis" does
# not match). v2.6 adds three general forms, one per v7 dev failure
# class: laundry + delivery entities in the state form (washing,
# laundry, parcel, delivery, package, shipment) with delivered/
# arrived as state words ("is the washing finished", "has my parcel
# been delivered"); a weather-like form ("what's the weather
# like/doing"); an indoor-temperature form ("how warm/cool is it" +
# a home location - bare "inside"/"here" are deliberately NOT
# locations, so "how warm is it inside the Earth" stays unblocked);
# and a delivery-status form for "my/the/our order" + a delivery
# state word ("has my order been delivered", "is my order ready" -
# the article-before-noun requirement keeps "what is the new world
# order" unblocked).
# v2.5 takes "are" in the where-form, widens the daily-count time
# windows (last night, last week, this morning, ...), and adds a
# weather-now form ("is it raining / snowing"). v2.4 expands the live-entity
# list (tumble dryer, dryer, coffee machine, robot vacuum, vacuum,
# sprinklers, hose), the state words (finished, done, ready), the
# interrogatives (has, have), and adds three general forms: stock
# ("are we out of", "do we have any"), delivery/location ("where is
# my/our"), daily-count ("how many ... have I done today").
_LIVE_ENTITIES = (
    r"door|gate|lights?|lamp|heating|thermostat|oven|washing machine|"
    r"washing|laundry|dishwasher|tumble dryer|dryer|coffee machine|"
    r"robot vacuum|vacuum|"
    r"window|lock|alarm|kettle|fridge|fan|tv|television|"
    r"speaker|shower|tap|boiler|radiator|wifi|wi-fi|internet|router|network|"
    r"flat|house|home|apartment|sprinkler|sprinklers|hose|"
    r"parcel|delivery|package|shipment|phone|battery|coffee|"
    r"dinner|lunch|breakfast|supper|meal|food|roast|soup|cake|bread|pasta|rice|"
    r"clothes|dishes|room|"
    r"post|mail|letter|car|laptop|tablet"  # v2.9: delivery entities
    # (post/mail/letter) so "has the post arrived" is form-blocked;
    # device entities (car/laptop/tablet) so "is the car charged
    # enough" and "is my phone charging" are form-blocked. "is the
    # car fast" does not match: "fast" is not a state word.
)
_STATE_WORDS = (
    r"on|off|open|closed|shut|locked|unlocked|running|still|hot|cold|"
    r"working|down|online|offline|connected|finished|done|ready|"
    r"delivered|arrived|boiled|brewed|charged|downloaded|uploaded|printed|"
    r"dry|wet|damp|clean|dirty|full|empty|warm|cool|cooked|baked|frozen|fresh|stale|"
    r"charging|drying|washing|cooking|baking|brewing|boiling"  # v2.9:
    # progressive state words: "is my phone charging", "is the
    # washing drying", "is dinner cooking", "is the kettle boiling".
    # "is the water boiling" does not match: "water" is not a live
    # entity.
)
_RULE_B_STATE_RE = re.compile(
    r"\b(is|are|did|was|were|has|have)\b[^?]*\b(" + _LIVE_ENTITIES + r")\b[^?]*\b("
    + _STATE_WORDS + r")\b")
_RULE_B_LEFT_RE = re.compile(
    r"\bdid i leave\b|\bdid i (put|lose|place) (my|our)\b")  # v2.7: "put/lose/place" need a belonging ("my"/"our") - "where did i put the emphasis" is a metaphor, not a live location; "did i leave" keeps working with "the" ("leave the front gate open")
_RULE_B_WEATHER_RE = re.compile(
    r"\b(forecast|going to (rain|snow)|will it (rain|snow))\b")
_RULE_B_ADVICE_RE = re.compile(r"\bdo i need\b[^?]*\b(today|tomorrow)\b")
_RULE_B_LISTQ_RE = re.compile(r"\b(what'?s|what is) on (my|the) .*list\b")
_RULE_B_STOCK_RE = re.compile(r"\b(are we out of|do we have any|is there any)\b")
_RULE_B_WHERE_RE = re.compile(r"\bwhere (is|are) (my|our)\b")  # v2.5: "are"
_RULE_B_COUNT_RE = re.compile(
    r"\bhow many\b[^?]*\b(have i|did i|have you|did you)\b[^?]*\b(today|yesterday|this week|last night|last week|this morning|last month|this month|this year|last year)\b")
# v2.5: live weather happening now ("is it raining outside right
# now") - a generalisation of the weather form, like "will it rain".
_RULE_B_RAIN_RE = re.compile(r"\bis it (raining|snowing)\b")  # v2.5: wider windows
# v2.7: uncontracted weather-like ("what is the weather like/doing")
# joins the contracted form - but only with a live marker (outside /
# right now / at the moment / today / here / now / currently) after
# it, so "what is the weather like on Mars" (factual) stays
# unblocked. The live marker is the difference between a current-
# weather question (live, here, now) and a factual weather
# question (a place, a planet).
_RULE_B_WEATHER_LIKE_RE = re.compile(
    r"\b(what'?s|what is) the weather (like|doing)\b[^?]*\b(outside|right now|at the moment|today|here|now|currently)\b")
# v2.7: presence ("is someone/anyone at/in <home location>", plus
# "is anyone home"). The location must be a home noun; "is anyone
# at the party" does not match. A live presence question, not a
# factual one. The did-i-put widening (below) requires a belonging
# ("my"/"our") for the same reason: "where did i put the emphasis"
# is a metaphor, not a live location.
_RULE_B_PRESENCE_RE = re.compile(
    r"\b(is|are) (someone|anyone|somebody|anybody) ((at|in) (the|my|our)? ?(front door|door|kitchen|room|house|flat|home|apartment|lounge|living room|bedroom|garden|garage|hallway|porch)|home)\b")
# v2.7: softened imperative ("can/could you <action verb>"). An
# action request phrased as a question, which Rule A misses because
# its question guard keeps it off. The verb must be in the Rule A
# action-verb class, and the prompt must contain no wh-word (the
# wh-word check lives in guard_rule_b, next to the other question
# forms), so "can you tell me ..." (tell is not an action verb) and
# "can you count how many ..." (wh-word) do not match. Validated
# on dev: catches 5/5 never softened imperatives, 0 FP on
# cacheable dev.
_RULE_B_SOFT_IMP_RE = re.compile(
    r"^(please\s+)?(can|could) you (" + _ACTION_VERBS + r")\b")
# v2.6: indoor temperature ("how warm/cool is it in the house").
# The home location must be an explicit home noun (in the/my
# house/flat/home/apartment/room/kitchen/bedroom/lounge/living room,
# or at home). Bare "inside"/"here" are NOT locations: "how warm is
# it inside the Earth" is factual and stays unblocked. "how hot/cold
# is it" is already caught by the denylist regex.
_RULE_B_INDOOR_TEMP_RE = re.compile(
    r"\bhow (warm|cool) is it\b[^?]*\b(in (the|my) (house|flat|home|apartment|room|kitchen|bedroom|lounge|living room)|at home)\b")
# v2.6: delivery status for an order ("has my order been delivered",
# "is my order ready"). The article ("my/the/our") must sit directly
# before "order", so "what is the new world order" does not match.
_RULE_B_DELIVERY_RE = re.compile(
    r"\b(my|the|our) order\b[^?]*\b(delivered|arrived|ready|dispatched|shipped|on its way|out for delivery)\b")
# v2.8: live daily fact ("what time is sunset today"). Two patterns.
# (a) An astronomical/tide event whose time is inherently daily
# (sunset, sunrise, moonrise, moonset, dawn, dusk, high/low tide):
# no day marker is needed, because the event's time changes every
# day. (b) Any noun + a day marker ("what time is the meeting
# today", "what time is lunch tomorrow"): a specific day's schedule
# is live, not a stable fact. A time-zone question ("what time is
# it in London") does not match: "what time is it" is already
# denylist-blocked, and the noun ("it") is not followed directly by
# a day marker.
_RULE_B_LIVE_FACT_RE = re.compile(
    r"\bwhat time is (sunset|sunrise|moonrise|moonset|dawn|dusk|high tide|low tide|the tide)\b")
_RULE_B_LIVE_FACT_DAY_RE = re.compile(
    r"\bwhat time is (the|my|our)? ?\w+ (today|tomorrow|tonight)\b")
# v2.9: live-fact "when" forms. The v2.8 live-fact form only matches
# "what time is sunset"; "when does the sun go down today" escaped
# it. A celestial event's time changes daily, so it is inherently a
# live fact whatever the question word is: "when does the sun go
# down / rise / set", "what time does the sun go down", "when is
# high tide", "when does the tide come in". "when does the sun set
# in June" is still live (the answer depends on the date), so no
# day marker is required. "when does the sun rise in the east" is
# a direction fact, not a time - it does not match (no time verb).
_RULE_B_LIVE_FACT_WHEN_RE = re.compile(
    r"\bwhen does (the )?(sun|moon) (go down|go up|rise|set|come up)"
    r"(?!\s+in the (east|west|north|south))\b")
# The negative lookahead keeps direction facts out: "when does the
# sun rise in the east" asks where the sun rises, not at what time.
# "when does the sun rise in summer" still matches (a date-dependent
# time, like "what time does the sun set in summer").
_RULE_B_LIVE_FACT_TIME_DOES_RE = re.compile(
    r"\bwhat time does (the )?(sun|moon) (go down|go up|rise|set|come up)\b")
_RULE_B_TIDE_WHEN_RE = re.compile(
    r"\bwhen is (high tide|low tide)\b|\bwhen does the tide (come in|go out)\b")
# v2.9: "enough charge/battery" - a device-state question phrased
# as a sufficiency check ("is the car charged enough for tomorrow"
# is already caught by the state form once "car" joins the live
# entities; this form catches "does my phone have enough battery",
# which has no state word). Only charge/battery/power/fuel/petrol:
# "enough time" / "enough money" do not match.
_RULE_B_ENOUGH_RE = re.compile(
    r"\benough (charge|battery|power|fuel|petrol)\b")
# v2.9: "check if" - a live-state check phrased as a request ("can
# you check if the oven is still on"). "check" stays out of the
# action-verb class (it heads information requests), but "check if"
# + a live entity + a state word is a live-state question, not a
# factual one. "check if the capital of France is Paris" does not
# match: no live entity, no state word. "check if the water is
# boiling" does not match: "water" is not a live entity.
_RULE_B_CHECK_IF_RE = re.compile(
    r"\bcheck if\b[^?]*\b(" + _LIVE_ENTITIES + r")\b[^?]*\b("
    + _STATE_WORDS + r")\b")
# v2.9: calendar/schedule lookup - a personal-schedule question,
# the same class as the list-query form ("what's on my shopping
# list"). A belonging (my/our) or a day marker makes it live: "what
# is on my calendar" is personal data, "what is on the calendar for
# tomorrow" is a specific day's schedule. Bare "what is on the
# calendar" (no belonging, no day marker) does not match.
_RULE_B_CALENDAR_RE = re.compile(
    r"\b(what'?s|what is) on (my|our) (calendar|schedule|agenda|diary)\b")
_RULE_B_CALENDAR_DAY_RE = re.compile(
    r"\b(what'?s|what is) on (the|my|our) (calendar|schedule|agenda|diary)\b[^?]*\b(today|tomorrow|tonight|this week|next week)\b")


def guard_rule_a(norm_text, raw_text=None):
    """Rule A: leading imperative action verb. Returns the verb, or None.

    Input is the C2-normalised text (raw_text, when given, is the
    un-normalised prompt, used only for the trailing-"?" check).
    The verb must lead the prompt (optional leading "please"), so
    "how do I start a fire" (a factual question) does not match,
    but "start the dishwasher" (an action) does. v2.5 question
    guard: a prompt containing a wh-word, or ending with "?", is
    a question, not an imperative - the leading word may be a noun
    ("Water boils at what temperature ...") or a factual verb
    ("Count the continents ..., how many are there?").
    """
    t = (norm_text or "").strip()
    if not t:
        return None
    if _QUESTION_WORD_RE.search(t):
        return None
    if raw_text is not None and raw_text.strip().endswith("?"):
        return None
    m = _RULE_A_RE.match(t)
    if m:
        return m.group(2)
    if _RULE_A_MAKE_RE.match(t):
        return "make-for"
    return None


def guard_rule_b(norm_text):
    """Rule B: live-state question form. Returns the form name, or None.

    Catches questions about a live entity's state ("is the back door
    shut"), "did I leave ..." checks, weather forms ("forecast",
    "going to snow"), live advice ("do I need ... today"), and list
    queries ("what's on my shopping list"). A factual question about
    a schedule ("what time does the Underground close") does not
    match: it has no live entity and no state word.
    """
    t = (norm_text or "").strip()
    if not t:
        return None
    if _RULE_B_STATE_RE.search(t):
        return "state-query"
    if _RULE_B_LEFT_RE.search(t):
        return "did-i-leave"
    if _RULE_B_WEATHER_RE.search(t):
        return "weather"
    if _RULE_B_RAIN_RE.search(t):
        return "weather-now"
    if _RULE_B_WEATHER_LIKE_RE.search(t):
        return "weather-like"
    if _RULE_B_PRESENCE_RE.search(t):
        return "presence"
    # v2.7: softened imperative ("can/could you <action verb>"). The
    # wh-word guard keeps factual questions out ("can you count how
    # many ..." has a wh-word; "can you tell me ..." has no action
    # verb). Checked here, in Rule B, because it is a question form
    # that Rule A's question guard keeps off.
    if _RULE_B_SOFT_IMP_RE.match(t) and not _QUESTION_WORD_RE.search(t):
        return "softened-imperative"
    if _RULE_B_INDOOR_TEMP_RE.search(t):
        return "indoor-temp"
    if _RULE_B_DELIVERY_RE.search(t):
        return "delivery-status"
    if _RULE_B_LIVE_FACT_RE.search(t) or _RULE_B_LIVE_FACT_DAY_RE.search(t):
        return "live-fact"
    if _RULE_B_LIVE_FACT_WHEN_RE.search(t):
        return "live-fact-when"
    if _RULE_B_LIVE_FACT_TIME_DOES_RE.search(t):
        return "live-fact-time-does"
    if _RULE_B_TIDE_WHEN_RE.search(t):
        return "tide-when"
    if _RULE_B_ENOUGH_RE.search(t):
        return "enough-charge"
    if _RULE_B_CHECK_IF_RE.search(t):
        return "check-if"
    if _RULE_B_CALENDAR_RE.search(t) or _RULE_B_CALENDAR_DAY_RE.search(t):
        return "calendar"
    if _RULE_B_ADVICE_RE.search(t):
        return "live-advice"
    if _RULE_B_LISTQ_RE.search(t):
        return "list-query"
    if _RULE_B_STOCK_RE.search(t):
        return "stock"
    if _RULE_B_WHERE_RE.search(t):
        return "where-is-mine"
    if _RULE_B_COUNT_RE.search(t):
        return "daily-count"
    return None


def guard_form_check(norm_text, raw_text=None):
    """Rules A + B combined. Returns "rule-a:<verb>" or
    "rule-b:<form>", or None. Pure text, no embedding needed, so it
    runs before the exact-match fast path. raw_text (when given)
    is passed to Rule A for its trailing-"?" question guard."""
    verb = guard_rule_a(norm_text, raw_text=raw_text)
    if verb:
        return "rule-a:" + verb
    form = guard_rule_b(norm_text)
    if form:
        return "rule-b:" + form
    return None


# ---------------------------------------------------------------------------
# v2.8-guard v2.4: Rule C creative-draft exemption. A prompt that starts
# with a creative verb (write/compose/draft/craft/pen/invent/imagine/
# create) and names a creative artefact (message/poem/story/song/
# toast/speech/haiku/limerick/...) is a creative draft, not an action,
# and is exempt from the Rule C margin block. The exemption is pure
# text and mirrors the v1.5 denylist "message for" logic (a draft FOR
# someone is creative, a message TO someone is messaging). It cannot
# let a messaging task through: "message to" is regex-blocked before
# Rule C, and the messaging-task prompts that reach Rule C have
# margins 0.057-0.118 (below 0.20 anyway, probed on v2.7). No dev
# never item starts with a creative verb (probed: all 22 creative-
# verb dev prompts are cacheable), and none of the 5 Rule C reachers
# is a creative draft, so the exemption has zero FP risk on dev. It
# fixes the birthday-message FP (margin 0.2574: "write a birthday
# message for my mum" is close to the action prototype "send a
# message to mum") without touching the margin or the prototypes.
# "make" is deliberately NOT a creative verb here (same reason as
# the v1.5 regex guard): "make a message for mum" reads as
# messaging, and "make" heads creative requests ("make a video")
# that Rule C already leaves alone.
# ---------------------------------------------------------------------------

_CREATIVE_VERBS = ("write", "compose", "draft", "craft", "pen",
                   "invent", "imagine", "create")
_CREATIVE_ARTEFACTS = (
    "message", "poem", "story", "song", "toast", "speech", "haiku",
    "limerick", "novel", "letter", "card", "lyrics", "verse", "tale",
    "ode", "sonnet", "ballad", "anthem", "jingle", "slogan", "caption",
    "blog", "essay", "article", "script", "play", "screenplay", "chorus",
)
_CREATIVE_DRAFT_RE = re.compile(
    r"^(please\s+)?(" + "|".join(_CREATIVE_VERBS) + r")\b"
    r"[^?]*\b(" + "|".join(_CREATIVE_ARTEFACTS) + r")\b")


def is_creative_draft(norm_text):
    """True if the prompt is a creative draft (leading creative verb
    + a creative artefact noun). Pure text. Used by Rule C only: a
    creative draft is exempt from the margin block."""
    t = (norm_text or "").strip()
    if not t:
        return False
    return bool(_CREATIVE_DRAFT_RE.match(t))


# ---------------------------------------------------------------------------
# v2.5-guard v2.1: prompt classes for the per-category Rule C margin.
# A prompt's form (question / imperative / statement) is decided from
# its own text, never from eval labels: a wh-word anywhere, an
# auxiliary leading the prompt, or a trailing "?" makes a question;
# otherwise a first word from the generic imperative-verb lexicon
# (ordinary English verbs: the Rule A action verbs + information /
# creative verbs + common imperative verbs) makes an imperative;
# everything else (declarative, greeting, chatter, long agent-task
# bodies) is a statement. The lexicon never blocks anything by
# itself; it only selects which Rule C margin applies.
# ---------------------------------------------------------------------------

_WH_RE = re.compile(r"\b(what|who|whom|whose|which|where|when|why|how)\b")
_AUX_LEAD_RE = re.compile(
    r"^(is|are|did|was|were|has|have|can|could|does|do|will|would|should|am)\b")
_IMPERATIVE_VERBS = set(
    "turn switch set unlock lock open close bolt secure kill add remove "
    "delete remind wake count send build rebuild start stop pause resume "
    "water feed arm disarm enable disable activate deactivate book order "
    "call text email put dim brighten heat cool mute unmute boil preheat "
    "play boost brew cook bake wash dry clean vacuum mop charge iron sweep "
    "dust mow rake trim prune weed message "
    "tell show explain describe define translate give make name list draw "
    "compose create summarise summarize draft generate produce sing read "
    "write check find look go come take get bring run ask answer repeat "
    "say speak talk walk sit stand wait watch listen hear feel try use keep "
    "leave let help save load print share post upload download install "
    "update change move copy".split())


def prompt_class(norm_text, raw_text=""):
    """question / imperative / statement, from the prompt's form only."""
    t = (norm_text or "").strip()
    if not t:
        return "statement"
    if _WH_RE.search(t) or _AUX_LEAD_RE.match(t):
        return "question"
    if (raw_text or "").strip().endswith("?"):
        return "question"
    words = t.split()
    w = words[0]
    if w == "please" and len(words) > 1:
        w = words[1]
    if w in _IMPERATIVE_VERBS:
        return "imperative"
    return "statement"


def guard_margin_for_class(cls, cfg):
    """Rule C margin threshold for one prompt class (v2.5).

    Imperative and question prompts keep the 0.20 margin (probe:
    safe imperatives reach +0.107, safe questions +0.120, so any
    lower value buys nothing and risks FPs). Statement prompts use
    0.10 (probe: safe statements max +0.0889, statement-form
    agent-task bodies +0.1093/+0.2360).
    """
    if cls == "statement":
        return float(cfg.get("guard_margin_statement",
                             GUARD_MARGIN_STATEMENT_DEFAULT))
    return float(cfg.get("guard_margin", GUARD_MARGIN_DEFAULT))


# ---------------------------------------------------------------------------
# Pure helpers (unit-testable without any service)
# ---------------------------------------------------------------------------

def cosine_similarity(a, b):
    """Cosine similarity of two equal-length vectors. 0.0 if degenerate."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cfg.update(json.load(f))
    cfg["threshold"] = float(os.environ.get("GATEWAY_THRESHOLD", cfg["threshold"]))
    cfg["ttl_stable_hours"] = float(os.environ.get(
        "GATEWAY_TTL_STABLE_HOURS", cfg.get("ttl_stable_hours", 168.0)))
    _tf = os.environ.get("GATEWAY_THRESHOLD_FACTUAL")
    if _tf:
        cfg["threshold_factual"] = float(_tf)
    _tg = os.environ.get("GATEWAY_THRESHOLD_GENERATIVE")
    if _tg:
        cfg["threshold_generative"] = float(_tg)
    _gt = os.environ.get("GATEWAY_GENERATIVE_TTL")
    if _gt:
        cfg["generative_ttl"] = _gt.strip().lower() in ("1", "true", "yes")
    _gm = os.environ.get("GATEWAY_GUARD_MARGIN")
    if _gm:
        cfg["guard_margin"] = float(_gm)
    _gms = os.environ.get("GATEWAY_GUARD_MARGIN_STATEMENT")
    if _gms:
        cfg["guard_margin_statement"] = float(_gms)
    _ge = os.environ.get("GATEWAY_GUARD_ENABLED")
    if _ge:
        cfg["guard_enabled"] = _ge.strip().lower() in ("1", "true", "yes")
    for _env, _key in (("GATEWAY_FRAME_STRIP_FACTUAL", "frame_strip_factual"),
                       ("GATEWAY_LEGACY_BACKFILL", "legacy_backfill")):
        _v = os.environ.get(_env)
        if _v:
            cfg[_key] = _v.strip().lower() in ("1", "true", "yes")
    cfg["upstream_mode"] = os.environ.get(
        "GATEWAY_UPSTREAM_MODE", cfg["upstream_mode"])
    cfg["upstream_model"] = os.environ.get(
        "GATEWAY_UPSTREAM_MODEL", cfg["upstream_model"])
    cfg["store_path"] = os.environ.get("GATEWAY_STORE_PATH", cfg["store_path"])
    cfg["port"] = int(os.environ.get("GATEWAY_PORT", cfg["port"]))
    return cfg


# ---------------------------------------------------------------------------
# Vector store: JSON file, atomic writes, exact-match index (C1)
# ---------------------------------------------------------------------------

class CacheStore:
    """Prompt/output pairs with embeddings, persisted as JSON.

    Each entry carries prompt (raw), prompt_norm (C2 normalised key),
    embedding (of the normalised prompt when normalise is on),
    created_at, hits, source, entry_id, plus (E1/E5) ttl_class and
    ttl_seconds: "stable" / "stable-generative" entries (stable
    factual / creative artefact, classified at write time) live
    ttl_stable_seconds (7 days); "standard" entries live ttl_seconds
    (24h). Entries loaded from disk without a ttl_class are legacy:
    they keep the conservative 24h TTL unless E4 legacy_backfill is
    on, in which case they are classified at load (factual /
    generative -> long TTL, anything else stays 24h).
    """

    def __init__(self, path, ttl_seconds=24.0 * 3600.0,
                 ttl_stable_seconds=7.0 * 24.0 * 3600.0,
                 legacy_backfill=False, frame_strip_factual=False,
                 generative_ttl=True):
        self.path = path
        self.ttl_seconds = ttl_seconds
        self.ttl_stable_seconds = ttl_stable_seconds
        self.legacy_backfill = legacy_backfill
        self.frame_strip_factual = frame_strip_factual
        self.generative_ttl = generative_ttl
        self.entries = []
        self.exact_index = {}
        self.load()

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            self.entries = data.get("entries", [])
        except (OSError, ValueError):
            self.entries = []
        for i, e in enumerate(self.entries):
            if "prompt_norm" not in e:
                e["prompt_norm"] = normalize_text(e.get("prompt", ""))
            if "entry_id" not in e:
                e["entry_id"] = f"entry-{i}"
            if "source" not in e:
                e["source"] = "live-store-seed"
            if "hits" not in e:
                e["hits"] = 0
            # E1: legacy entries (stored before TTL classes existed,
            # including the demo seed) keep the 24h TTL, unless E4
            # legacy_backfill is on: then they are classified at
            # load from their own prompt text (factual / creative
            # artefact -> long TTL, anything else stays 24h).
            if "ttl_class" not in e:
                if self.legacy_backfill:
                    _n = e.get("prompt_norm", "")
                    if is_stable_factual(_n):
                        e["ttl_class"] = "legacy-stable"
                        e["ttl_seconds"] = self.ttl_stable_seconds
                    elif is_stable_generative(_n):
                        e["ttl_class"] = "legacy-generative"
                        e["ttl_seconds"] = self.ttl_stable_seconds
                    else:
                        e["ttl_class"] = "legacy"
                        e["ttl_seconds"] = self.ttl_seconds
                else:
                    e["ttl_class"] = "legacy"
                    e["ttl_seconds"] = self.ttl_seconds
            if "ttl_seconds" not in e:
                e["ttl_seconds"] = self.ttl_seconds
        self._rebuild_index()

    def _rebuild_index(self):
        self.exact_index = {}
        for e in self.entries:
            self.exact_index[e.get("prompt_norm", "")] = e

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"entries": self.entries}, f)
        os.replace(tmp, self.path)

    def _entry_ttl(self, entry):
        """E1: effective TTL of one entry (its own class), in seconds."""
        ttl = entry.get("ttl_seconds", self.ttl_seconds)
        if ttl is None or ttl <= 0:
            return self.ttl_seconds
        return ttl

    def _expired(self, entry, now):
        """E1: expired when older than the entry's own TTL class
        (stable 7d, standard/legacy 24h). The TTL is a property of
        the stored answer, not of the incoming question."""
        ts = entry.get("created_at")
        if ts is None:
            return False
        return (now - ts) > self._entry_ttl(entry)

    def add(self, prompt, output, embedding, created_at=None, source="shadow-workload"):
        # E1/E5: TTL class assigned at write time from the prompt
        # text. Factual first, then creative-generative; both long
        # classes live ttl_stable_seconds (7 days).
        norm = normalize_text(prompt)
        if self.frame_strip_factual:
            norm = embedding_text(norm, True)
        if is_stable_factual(normalize_text(prompt)):
            ttl_class, ttl = "stable", self.ttl_stable_seconds
        elif self.generative_ttl and is_stable_generative(
                normalize_text(prompt)):
            ttl_class, ttl = "stable-generative", self.ttl_stable_seconds
        else:
            ttl_class, ttl = "standard", self.ttl_seconds
        entry = {
            "prompt": prompt,
            "prompt_norm": norm,
            "output": output,
            "embedding": embedding,
            "created_at": time.time() if created_at is None else created_at,
            "hits": 0,
            "source": source,
            "entry_id": f"entry-{len(self.entries)}",
            "ttl_class": ttl_class,
            "ttl_seconds": ttl,
        }
        self.entries.append(entry)
        self.exact_index[entry["prompt_norm"]] = entry
        self.save()
        return entry

    def exact_lookup(self, norm_text, now=None):
        """C1: normalised-equality lookup. None if absent or expired
        (E1: by the entry's own TTL class)."""
        if now is None:
            now = time.time()
        entry = self.exact_index.get(norm_text)
        if entry is None:
            return None
        if self._expired(entry, now):
            return None
        return entry

    def best_match(self, embedding, threshold, now=None):
        """Return (entry, similarity) for the closest non-expired entry,
        or (None, best). Kept for backward compatibility with tests."""
        entry, sim, _expired = self.best_match_detailed(
            embedding, threshold, now)
        return entry, sim

    def best_match_detailed(self, embedding, threshold, now=None):
        """Return (entry, similarity, expired_miss): expired_miss is True
        when an expired entry alone would have matched at threshold
        (E1: expired by its own TTL class)."""
        if now is None:
            now = time.time()
        best_entry, best_sim = None, -1.0
        best_expired_sim = -1.0
        for entry in self.entries:
            sim = cosine_similarity(embedding, entry["embedding"])
            if self._expired(entry, now):
                if sim > best_expired_sim:
                    best_expired_sim = sim
                continue
            if sim > best_sim:
                best_entry, best_sim = entry, sim
        if best_entry is not None and best_sim >= threshold:
            return best_entry, best_sim, False
        expired_miss = best_expired_sim >= threshold
        return None, best_sim, expired_miss

    def clear(self):
        self.entries = []
        self.exact_index = {}
        self.save()


# ---------------------------------------------------------------------------
# Ollama embedding client (C5: keep_alive pins bge-m3 resident)
# ---------------------------------------------------------------------------

def _post_json(url, payload, timeout=120):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


class OllamaEmbedder:
    def __init__(self, ollama_url, model, keep_alive="24h"):
        self.url = ollama_url.rstrip("/")
        self.model = model
        self.keep_alive = keep_alive

    def embed(self, text):
        payload = {"model": self.model, "prompt": text}
        if self.keep_alive:
            payload["keep_alive"] = self.keep_alive
        data = _post_json(self.url + "/api/embeddings", payload)
        return data["embedding"]

    def warmup(self):
        """Best-effort: load bge-m3 now so the first real query is warm."""
        try:
            self.embed("warmup")
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Gateway core
# ---------------------------------------------------------------------------

class Gateway:
    def __init__(self, config, embedder=None, upstream=None):
        self.cfg = config
        self.store = CacheStore(
            config["store_path"],
            ttl_seconds=float(config.get("ttl_hours", 24.0)) * 3600.0,
            ttl_stable_seconds=float(
                config.get("ttl_stable_hours", 168.0)) * 3600.0,
            legacy_backfill=bool(config.get("legacy_backfill", False)),
            frame_strip_factual=bool(
                config.get("frame_strip_factual", False)),
            generative_ttl=bool(config.get("generative_ttl", True)))
        self.embedder = embedder or OllamaEmbedder(
            config["ollama_url"], config["embedding_model"],
            keep_alive=config.get("keep_alive", "24h"))
        self.upstream = upstream if upstream is not None else self._default_upstream
        self.lock = threading.Lock()
        # v2.7-guard: prototype embeddings for Rule C, computed lazily
        # on first use (one embedding call per prototype, ~53 total)
        # and cached for the life of the process. None until computed;
        # if the embedder fails, Rule C is skipped for that query
        # (Rules A+B and the regex still run, and the embed-failure
        # path never stores, so no store poisoning is possible).
        self._guard_action_embs = None
        self._guard_safe_embs = None
        self._guard_embs_lock = threading.Lock()
        self.stats = {"queries": 0, "hits": 0, "misses": 0,
                      "hit_ms": [], "miss_ms": [],
                      "blocked_route": 0, "blocked_denylist": 0,
                      "blocked_guard": 0,
                      "exact_hits": 0, "embed_failures": 0}

    # -- v2.8-guard Rule C (creative-draft exemption added; margin
    #    per-class unchanged from v2.5) ------------------------------
    def _ensure_guard_embeddings(self):
        """Embed the prototype lists once (lazily) and cache them.

        Returns True when both sets are available. False when the
        embedder fails (Rule C is then skipped for the query; Rules
        A+B and the regex still run, and the embed-failure path never
        stores, so a missing Rule C cannot poison the store).
        """
        if self._guard_action_embs is not None and self._guard_safe_embs is not None:
            return True
        with self._guard_embs_lock:
            if self._guard_action_embs is not None and self._guard_safe_embs is not None:
                return True
            try:
                self._guard_action_embs = [
                    self.embedder.embed(normalize_text(p))
                    for p in ACTION_PROTOTYPES]
                self._guard_safe_embs = [
                    self.embedder.embed(normalize_text(p))
                    for p in SAFE_PROTOTYPES]
            except Exception:
                self._guard_action_embs = None
                self._guard_safe_embs = None
                return False
            return True

    def guard_margin_check(self, embedding, norm_text=None, raw_text=None):
        """Rule C: two-sided embedding margin, per prompt class (v2.5).

        Returns (blocked, margin, sim_action, sim_safe, prompt_class,
        threshold). Blocked when max similarity to the action
        prototypes exceeds max similarity to the safe prototypes by
        at least the margin for the prompt's class (imperative 0.20,
        question 0.20, statement 0.10; see guard_margin_for_class).
        The prompt embedding is the one already computed for the
        cache lookup, so the marginal cost is the cosine
        similarities against the cached prototype embeddings
        (microseconds). Returns not-blocked when the guard is
        disabled or the prototype embeddings are unavailable.
        v2.8: a creative draft (is_creative_draft) is exempt from the
        margin block - the margin is still computed and returned for
        observability, but blocked is False. This fixes the
        birthday-message FP (margin 0.2574) without touching the
        margin or the prototypes.
        """
        if not self.cfg.get("guard_enabled", True):
            return False, None, None, None, None, None
        if not self._ensure_guard_embeddings():
            return False, None, None, None, None, None
        sim_action = max(
            (cosine_similarity(embedding, pe)
             for pe in self._guard_action_embs), default=0.0)
        sim_safe = max(
            (cosine_similarity(embedding, pe)
             for pe in self._guard_safe_embs), default=0.0)
        margin = sim_action - sim_safe
        cls = prompt_class(norm_text or "", raw_text or "")
        threshold = guard_margin_for_class(cls, self.cfg)
        if is_creative_draft(norm_text or ""):
            return (False, round(margin, 4),
                    round(sim_action, 4), round(sim_safe, 4), cls,
                    round(threshold, 4))
        return (margin >= threshold, round(margin, 4),
                round(sim_action, 4), round(sim_safe, 4), cls,
                round(threshold, 4))

    # -- upstream backends -------------------------------------------------
    def _default_upstream(self, text):
        mode = self.cfg["upstream_mode"]
        if mode == "stub":
            # Shadow-only: a fixed placeholder output so unblocked
            # misses are stored (the store learns real traffic, exactly
            # as the eval driver does). Never served to a user; the
            # shadow gateway serves nothing live.
            return "STUB-OUTPUT"
        if mode == "ollama":
            data = _post_json(
                self.cfg["ollama_url"].rstrip("/") + "/api/generate",
                {"model": self.cfg["upstream_model"], "prompt": text,
                 "stream": False,
                 "options": {"num_predict": self.cfg["upstream_max_tokens"]}},
                timeout=300)
            return data.get("response", "")
        if mode == "dispatcher":
            data = _post_json(
                self.cfg["dispatcher_url"].rstrip("/") + "/dispatch",
                {"text": text}, timeout=300)
            if isinstance(data, dict):
                for key in ("reply", "text", "output", "response"):
                    if isinstance(data.get(key), str) and data[key]:
                        return data[key]
            return json.dumps(data)
        return None  # mode "none": no upstream configured

    # -- query -------------------------------------------------------------
    def query(self, text, route="full", now=None):
        """One gateway lookup. Returns a result dict (see module docstring).

        route: "full" consults/stores; anything else is blocked before
        any consult (C3 route scoping). now: request epoch seconds
        (live time when None); used for TTL ageing in replay/shadow.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        text = text.strip()
        route = route if isinstance(route, str) and route else "full"
        started = time.monotonic()
        now_ts = time.time() if now is None else now

        # C3: route scoping - fast-path traffic never consults/stores.
        if self.cfg.get("route_scoping", True) and route != "full":
            latency_ms = (time.monotonic() - started) * 1000.0
            self._record(False, latency_ms, text, None,
                         blocked_by="route:fast-path-first",
                         route_decision=route, cache_status="blocked-route")
            return {"hit": False, "output": None, "similarity": None,
                    "latency_ms": latency_ms, "cached": False,
                    "matched_prompt": None,
                    "blocked_by": "route:fast-path-first",
                    "route_decision": route, "cache_status": "blocked-route",
                    "matched_entry_id": None, "matched_entry_ts": None,
                    "matched_entry_age_s": None, "entry_source": None,
                    "embed_ms": 0.0, "lookup_ms": 0.0, "exact_hit": False,
                    "expired_miss": False}

        # C3: denylist v1.4 - denied prompts never consult or store.
        if self.cfg.get("denylist_enabled", True):
            pat = denied(text)
            if pat:
                latency_ms = (time.monotonic() - started) * 1000.0
                self._record(False, latency_ms, text, None,
                             blocked_by=f"denylist:{pat}",
                             route_decision=route,
                             cache_status="blocked-denylist")
                return {"hit": False, "output": None, "similarity": None,
                        "latency_ms": latency_ms, "cached": False,
                        "matched_prompt": None,
                        "blocked_by": f"denylist:{pat}",
                        "route_decision": route,
                        "cache_status": "blocked-denylist",
                        "matched_entry_id": None, "matched_entry_ts": None,
                        "matched_entry_age_s": None, "entry_source": None,
                        "embed_ms": 0.0, "lookup_ms": 0.0, "exact_hit": False,
                        "expired_miss": False}

        # C2: normalise before embedding (and before the exact lookup).
        norm = normalize_text(text) if self.cfg.get("normalise", True) else text
        # E2: with frame stripping on, factual queries embed (and
        # exact-match) on the frame-stripped text.
        emb_text = embedding_text(
            norm, bool(self.cfg.get("frame_strip_factual", False)))

        # v2.5-guard Rules A+B: form check on normalised text, before
        # the exact-match fast path (so a never prompt cannot be
        # served by exact-match either). Pure text, no embedding.
        if self.cfg.get("guard_enabled", True):
            form_rule = guard_form_check(norm, raw_text=text)
            if form_rule:
                latency_ms = (time.monotonic() - started) * 1000.0
                self._record(False, latency_ms, text, None,
                             blocked_by=f"denylist:guard-{form_rule}",
                             route_decision=route,
                             cache_status="blocked-denylist")
                return {"hit": False, "output": None, "similarity": None,
                        "latency_ms": latency_ms, "cached": False,
                        "matched_prompt": None,
                        "blocked_by": f"denylist:guard-{form_rule}",
                        "route_decision": route,
                        "cache_status": "blocked-denylist",
                        "matched_entry_id": None, "matched_entry_ts": None,
                        "matched_entry_age_s": None, "entry_source": None,
                        "embed_ms": 0.0, "lookup_ms": 0.0, "exact_hit": False,
                        "expired_miss": False}

        # C1: exact-match fast path - no embedding call at all.
        # (E1: the entry's own TTL class decides expiry; the incoming
        # question's phrasing does not - a stable fact stays correct
        # however it is asked.)
        if self.cfg.get("exact_match", True):
            t0 = time.monotonic()
            with self.lock:
                entry = self.store.exact_lookup(emb_text, now_ts)
            lookup_ms = (time.monotonic() - t0) * 1000.0
            if entry is not None:
                with self.lock:
                    entry["hits"] += 1
                    self.store.save()
                latency_ms = (time.monotonic() - started) * 1000.0
                self.stats["exact_hits"] += 1
                age = (now_ts - entry["created_at"]
                       if entry.get("created_at") is not None else None)
                self._record(True, latency_ms, text, 1.0,
                             route_decision=route, cache_status="hit-safe",
                             matched_entry_id=entry.get("entry_id"),
                             matched_entry_ts=entry.get("created_at"),
                             matched_entry_age_s=age,
                             entry_source=entry.get("source"),
                             embed_ms=0.0, lookup_ms=lookup_ms)
                return {"hit": True, "output": entry["output"],
                        "similarity": 1.0, "latency_ms": latency_ms,
                        "cached": True, "matched_prompt": entry["prompt"],
                        "blocked_by": None, "route_decision": route,
                        "cache_status": "hit-safe",
                        "matched_entry_id": entry.get("entry_id"),
                        "matched_entry_ts": entry.get("created_at"),
                        "matched_entry_age_s": age,
                        "entry_source": entry.get("source"),
                        "embed_ms": 0.0, "lookup_ms": lookup_ms,
                        "exact_hit": True, "expired_miss": False}

        # Embed (C5 keep-alive is inside the embedder).
        t0 = time.monotonic()
        try:
            embedding = self.embedder.embed(emb_text)
            embed_ms = (time.monotonic() - t0) * 1000.0
        except Exception:
            # C6 degraded mode: embed failure falls back to upstream as
            # an uncached miss (exact already missed). 500 only if the
            # upstream also fails (raised by the caller/handler).
            self.stats["embed_failures"] += 1
            embed_ms = (time.monotonic() - t0) * 1000.0
            output = self.upstream(text)
            latency_ms = (time.monotonic() - started) * 1000.0
            self._record(False, latency_ms, text, None,
                         route_decision=route, cache_status="miss-embed-failed",
                         embed_ms=embed_ms)
            return {"hit": False, "output": output, "similarity": None,
                    "latency_ms": latency_ms, "cached": False,
                    "matched_prompt": None, "blocked_by": None,
                    "route_decision": route,
                    "cache_status": "miss-embed-failed",
                    "matched_entry_id": None, "matched_entry_ts": None,
                    "matched_entry_age_s": None, "entry_source": None,
                    "embed_ms": embed_ms, "lookup_ms": 0.0,
                    "exact_hit": False, "expired_miss": False}

        # v2.5-guard Rule C: two-sided embedding margin, after the
        # embed (which reuses the prompt embedding already computed
        # for the cache lookup) and before the similarity lookup.
        # A blocked prompt never consults or stores.
        if self.cfg.get("guard_enabled", True):
            blocked, margin, sim_a, sim_s, _cls, _thr = (
                self.guard_margin_check(embedding, norm, text))
            if blocked:
                latency_ms = (time.monotonic() - started) * 1000.0
                self._record(False, latency_ms, text, None,
                             blocked_by="denylist:guard-margin",
                             route_decision=route,
                             cache_status="blocked-denylist",
                             embed_ms=embed_ms)
                return {"hit": False, "output": None, "similarity": None,
                        "latency_ms": latency_ms, "cached": False,
                        "matched_prompt": None,
                        "blocked_by": "denylist:guard-margin",
                        "route_decision": route,
                        "cache_status": "blocked-denylist",
                        "matched_entry_id": None, "matched_entry_ts": None,
                        "matched_entry_age_s": None, "entry_source": None,
                        "embed_ms": embed_ms, "lookup_ms": 0.0,
                        "exact_hit": False, "expired_miss": False}
        t0 = time.monotonic()
        # E3/E6: a stable-factual question gets the lower factual
        # threshold, a stable-generative prompt the generative
        # threshold (the classifier is the second guard in both
        # cases); every other prompt keeps the configured threshold.
        thr = self.cfg["threshold"]
        tf = self.cfg.get("threshold_factual")
        tg = self.cfg.get("threshold_generative")
        if tf is not None and is_stable_factual(norm):
            thr = float(tf)
        elif tg is not None and is_stable_generative(norm):
            thr = float(tg)
        with self.lock:
            entry, sim, expired = self.store.best_match_detailed(
                embedding, thr, now_ts)
        lookup_ms = (time.monotonic() - t0) * 1000.0
        if entry is not None:
            with self.lock:
                entry["hits"] += 1
                self.store.save()
            latency_ms = (time.monotonic() - started) * 1000.0
            age = (now_ts - entry["created_at"]
                   if entry.get("created_at") is not None else None)
            self._record(True, latency_ms, text, sim,
                         route_decision=route, cache_status="hit-safe",
                         matched_entry_id=entry.get("entry_id"),
                         matched_entry_ts=entry.get("created_at"),
                         matched_entry_age_s=age,
                         entry_source=entry.get("source"),
                         embed_ms=embed_ms, lookup_ms=lookup_ms)
            return {"hit": True, "output": entry["output"],
                    "similarity": sim, "latency_ms": latency_ms,
                    "cached": True, "matched_prompt": entry["prompt"],
                    "blocked_by": None, "route_decision": route,
                    "cache_status": "hit-safe",
                    "matched_entry_id": entry.get("entry_id"),
                    "matched_entry_ts": entry.get("created_at"),
                    "matched_entry_age_s": age,
                    "entry_source": entry.get("source"),
                    "embed_ms": embed_ms, "lookup_ms": lookup_ms,
                    "exact_hit": False, "expired_miss": False}
        output = self.upstream(text)
        latency_ms = (time.monotonic() - started) * 1000.0
        cached = False
        if output:
            with self.lock:
                self.store.add(text, output, embedding, created_at=now_ts)
            cached = True
        self._record(False, latency_ms, text, sim,
                     route_decision=route,
                     cache_status=("miss-expired" if expired else "miss-stored"),
                     embed_ms=embed_ms, lookup_ms=lookup_ms)
        return {"hit": False, "output": output, "similarity": sim,
                "latency_ms": latency_ms, "cached": cached,
                "matched_prompt": None, "blocked_by": None,
                "route_decision": route,
                "cache_status": ("miss-expired" if expired else "miss-stored"),
                "matched_entry_id": None, "matched_entry_ts": None,
                "matched_entry_age_s": None, "entry_source": None,
                "embed_ms": embed_ms, "lookup_ms": lookup_ms,
                "exact_hit": False, "expired_miss": expired}

    def _record(self, hit, latency_ms, text, similarity, blocked_by=None,
                route_decision="full", cache_status=None,
                matched_entry_id=None, matched_entry_ts=None,
                matched_entry_age_s=None, entry_source=None,
                embed_ms=None, lookup_ms=None):
        self.stats["queries"] += 1
        if blocked_by and blocked_by.startswith("route:"):
            self.stats["blocked_route"] += 1
        if blocked_by and blocked_by.startswith("denylist:"):
            self.stats["blocked_denylist"] += 1
        if blocked_by and blocked_by.startswith("denylist:guard"):
            self.stats["blocked_guard"] += 1
        if hit:
            self.stats["hits"] += 1
            self.stats["hit_ms"].append(latency_ms)
        else:
            self.stats["misses"] += 1
            self.stats["miss_ms"].append(latency_ms)
        # Cache-hit logging: one JSON line per query (append-only),
        # with the E2 trace fields.
        try:
            with open(self.cfg["log_path"], "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "ts": time.time(), "hit": hit,
                    "latency_ms": round(latency_ms, 1),
                    "similarity": None if similarity is None else round(similarity, 4),
                    "text": text[:200],
                    "blocked_by": blocked_by,
                    "route_decision": route_decision,
                    "cache_status": cache_status,
                    "matched_entry_id": matched_entry_id,
                    "matched_entry_ts": matched_entry_ts,
                    "matched_entry_age_s": (round(matched_entry_age_s, 1)
                                            if matched_entry_age_s is not None else None),
                    "entry_source": entry_source,
                    "embed_ms": embed_ms,
                    "lookup_ms": lookup_ms,
                }) + "\n")
        except OSError:
            pass

    def stats_summary(self):
        def median(values):
            return round(statistics.median(values), 1) if values else None
        ttl_classes = {}
        for e in self.store.entries:
            ttl_classes[e.get("ttl_class", "?")] = (
                ttl_classes.get(e.get("ttl_class", "?"), 0) + 1)
        return {
            "gateway_version": GATEWAY_VERSION,
            "queries": self.stats["queries"],
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": (round(self.stats["hits"] / self.stats["queries"], 4)
                         if self.stats["queries"] else None),
            "median_hit_ms": median(self.stats["hit_ms"]),
            "median_miss_ms": median(self.stats["miss_ms"]),
            "blocked_by_route": self.stats["blocked_route"],
            "blocked_by_denylist": self.stats["blocked_denylist"],
            "blocked_by_guard": self.stats["blocked_guard"],
            "exact_hits": self.stats["exact_hits"],
            "embed_failures": self.stats["embed_failures"],
            "entries": len(self.store.entries),
            "ttl_classes": ttl_classes,
            "threshold": self.cfg["threshold"],
            "threshold_factual": self.cfg.get("threshold_factual"),
            "threshold_generative": self.cfg.get("threshold_generative"),
            "frame_strip_factual": self.cfg.get("frame_strip_factual", False),
            "legacy_backfill": self.cfg.get("legacy_backfill", False),
            "generative_ttl": self.cfg.get("generative_ttl", True),
            "denylist": DENYLIST_VERSION,
            "guard": GUARD_VERSION,
            "guard_enabled": self.cfg.get("guard_enabled", True),
            "guard_margin": self.cfg.get("guard_margin", GUARD_MARGIN_DEFAULT),
            "guard_margin_statement": self.cfg.get(
                "guard_margin_statement", GUARD_MARGIN_STATEMENT_DEFAULT),
            "guard_margins": {
                "imperative": float(self.cfg.get(
                    "guard_margin", GUARD_MARGIN_DEFAULT)),
                "question": float(self.cfg.get(
                    "guard_margin", GUARD_MARGIN_DEFAULT)),
                "statement": float(self.cfg.get(
                    "guard_margin_statement",
                    GUARD_MARGIN_STATEMENT_DEFAULT))},
            "guard_action_prototypes": len(ACTION_PROTOTYPES),
            "guard_safe_prototypes": len(SAFE_PROTOTYPES),
            "ttl_hours": self.cfg.get("ttl_hours", 24.0),
            "ttl_stable_hours": self.cfg.get("ttl_stable_hours", 168.0),
            "normalise": self.cfg.get("normalise", True),
            "exact_match": self.cfg.get("exact_match", True),
            "keep_alive": self.cfg.get("keep_alive", "24h"),
            "upstream_mode": self.cfg["upstream_mode"],
        }


# ---------------------------------------------------------------------------
# HTTP server (stdlib ThreadingHTTPServer)
# ---------------------------------------------------------------------------

def serve(config):
    gateway = Gateway(config)
    # C5: best-effort warmup so the first real query is not a cold load.
    warmed = False
    try:
        warmed = gateway.embedder.warmup()
    except Exception:
        warmed = False
    # v2.7-guard: pre-compute the prototype embeddings now (best
    # effort, ~0.4s) so the first query that reaches Rule C does not
    # pay for all 51 of them. Lazy fallback in guard_margin_check
    # covers a startup failure.
    try:
        gateway._ensure_guard_embeddings()
    except Exception:
        pass

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self):
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = 0
            raw = self.rfile.read(length) if length else b"{}"
            return json.loads(raw or b"{}")

        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"ok": True, "service": "semantic-gateway-cache",
                                 "gateway_version": GATEWAY_VERSION,
                                 "threshold": gateway.cfg["threshold"],
                                 "threshold_factual": gateway.cfg.get(
                                     "threshold_factual"),
                                 "threshold_generative": gateway.cfg.get(
                                     "threshold_generative"),
                                 "frame_strip_factual": gateway.cfg.get(
                                     "frame_strip_factual", False),
                                 "legacy_backfill": gateway.cfg.get(
                                     "legacy_backfill", False),
                                 "generative_ttl": gateway.cfg.get(
                                     "generative_ttl", True),
                                 "denylist": DENYLIST_VERSION,
                                 "guard": GUARD_VERSION,
                                 "guard_enabled": gateway.cfg.get(
                                     "guard_enabled", True),
                                 "guard_margin": gateway.cfg.get(
                                     "guard_margin", GUARD_MARGIN_DEFAULT),
                                 "guard_margin_statement": gateway.cfg.get(
                                     "guard_margin_statement",
                                     GUARD_MARGIN_STATEMENT_DEFAULT),
                                 "guard_action_prototypes": len(ACTION_PROTOTYPES),
                                 "guard_safe_prototypes": len(SAFE_PROTOTYPES),
                                 "ttl_hours": gateway.cfg.get("ttl_hours", 24.0),
                                 "ttl_stable_hours": gateway.cfg.get(
                                     "ttl_stable_hours", 168.0),
                                 "normalise": gateway.cfg.get("normalise", True),
                                 "exact_match": gateway.cfg.get("exact_match", True),
                                 "keep_alive": gateway.cfg.get("keep_alive", "24h"),
                                 "embedder_warmed": warmed})
            elif self.path == "/stats":
                self._send(200, gateway.stats_summary())
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            try:
                body = self._read_json()
            except ValueError:
                self._send(400, {"error": "invalid JSON body"})
                return
            try:
                if self.path == "/query":
                    text = body.get("text")
                    if not isinstance(text, str) or not text.strip():
                        raise ValueError("missing or empty text")
                    route = body.get("route", "full")
                    self._send(200, gateway.query(text, route=route))
                elif self.path == "/cache":
                    text = body.get("text")
                    output = body.get("output")
                    if not isinstance(text, str) or not text.strip():
                        raise ValueError("missing or empty text")
                    if not isinstance(output, str) or not output:
                        raise ValueError("missing or empty output")
                    norm = (normalize_text(text.strip())
                            if gateway.cfg.get("normalise", True) else text.strip())
                    norm = embedding_text(
                        norm, bool(gateway.cfg.get("frame_strip_factual", False)))
                    emb = gateway.embedder.embed(norm)
                    gateway.store.add(text.strip(), output, emb)
                    self._send(200, {"ok": True,
                                     "entries": len(gateway.store.entries)})
                elif self.path == "/clear":
                    gateway.store.clear()
                    self._send(200, {"ok": True, "entries": 0})
                else:
                    self._send(404, {"error": "not found"})
            except ValueError as exc:
                self._send(400, {"error": str(exc)[:200]})
            except Exception as exc:  # noqa: BLE001 - HTTP must not crash
                self._send(500, {"error": str(exc)[:200]})

    server = ThreadingHTTPServer(
        (config["host"], config["port"]), Handler)
    print(f"semantic gateway {GATEWAY_VERSION}: listening on {config['host']}:{config['port']} "
          f"threshold={config['threshold']} upstream={config['upstream_mode']} "
          f"denylist={DENYLIST_VERSION} guard={GUARD_VERSION} "
          f"guard_margin={config.get('guard_margin', GUARD_MARGIN_DEFAULT)} "
          f"guard_enabled={config.get('guard_enabled', True)} "
          f"ttl={config.get('ttl_hours', 24.0)}h "
          f"ttl_stable={config.get('ttl_stable_hours', 168.0)}h "
          f"thr_factual={config.get('threshold_factual')} "
          f"thr_generative={config.get('threshold_generative')} "
          f"frame_strip={config.get('frame_strip_factual', False)} "
          f"legacy_backfill={config.get('legacy_backfill', False)} "
          f"generative_ttl={config.get('generative_ttl', True)} "
          f"warmed={warmed}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def main(argv=None):
    parser = argparse.ArgumentParser(description="semantic gateway and cache")
    parser.add_argument("--config", default=os.path.join(HERE, "config.json"))
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args(argv)
    cfg = load_config(args.config if os.path.exists(args.config) else None)
    if args.port:
        cfg["port"] = args.port
    serve(cfg)


if __name__ == "__main__":
    main()
