#!/usr/bin/env python3
"""Unit tests for the semantic gateway v2.9-guard (generalising
safety guard v2.5, Rules A + B + C, per-category Rule C margin,
Rule C creative-draft exemption).

Run from the repo root from the eval dir (gateway_v11.py lives next to
this file):
  python3 -m unittest test_gateway_v11 -v
The FakeEmbedder tests are pure and deterministic. The dev-set
tests read the frozen v3/v4/v5/v6/v7/v8/v9/v10 DEV sets only (never any holdout) and
assert the guard's recall/FP on them. The dev-set tests now
cover the frozen v3/v4/v5/v6/v7/v8/v9/v10 DEV sets. No test touches the
dispatcher, the memory service, or any live model other than bge-m3
(embeddings only, in the live test class, skipped if Ollama is down).
"""

import json
import math
import os
import sys
import tempfile
import unittest
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semantic_gateway.gateway import (  # noqa: E402
    ACTION_PROTOTYPES, DENYLIST_VERSION, GATEWAY_VERSION,
    GUARD_MARGIN_DEFAULT, GUARD_MARGIN_STATEMENT_DEFAULT,
    GUARD_VERSION, SAFE_PROTOTYPES, Gateway, cosine_similarity, denied,
    guard_form_check, guard_margin_for_class, guard_rule_a,
    guard_rule_b, is_creative_draft, load_config, normalize_text,
    prompt_class,
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


def _gateway_with_fake(mapping, threshold=0.90, **cfg_overrides):
    tmp = tempfile.mkdtemp()
    cfg = load_config()
    cfg["threshold"] = threshold
    cfg["store_path"] = os.path.join(tmp, "store.json")
    cfg["log_path"] = os.path.join(tmp, "hits.log")
    cfg["ttl_hours"] = 24.0
    cfg["ttl_stable_hours"] = 168.0
    cfg.update(cfg_overrides)
    emb = FakeEmbedder(mapping)
    gw = Gateway(cfg, embedder=emb, upstream=lambda text: "UPSTREAM:" + text)
    return gw, emb


def _dev_rows():
    """Frozen v3+v4+v5+v6+v7+v8+v9+v10 DEV sets only (536 prompts). Never any holdout."""
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    for rel in ("../eval/v3/eval_set_dev.json", "../eval/v4/eval_set_dev.json",
                "../eval/v5/eval_set_dev.json", "../eval/v6/eval_set_dev.json",
                "../eval/v7/eval_set_dev.json", "../eval/v8/eval_set_dev.json",
                "../eval/v9/eval_set_dev.json", "../eval/v10/eval_set_dev.json"):
        with open(os.path.join(here, rel), encoding="utf-8") as f:
            d = json.load(f)
        for it in d.get("requests") or d.get("prompts"):
            rows.append(it)
    return rows


class TestVersion(unittest.TestCase):
    def test_version_is_v29_guard(self):
        self.assertEqual(GATEWAY_VERSION, "v2.9-guard")
        self.assertEqual(GUARD_VERSION, "v2.5")
        self.assertEqual(GUARD_MARGIN_DEFAULT, 0.20)
        self.assertEqual(GUARD_MARGIN_STATEMENT_DEFAULT, 0.10)

    def test_denylist_is_v15(self):
        self.assertEqual(DENYLIST_VERSION, "v1.5")

    def test_prototypes_match_json_files(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "..", "eval", "prototypes.json"), encoding="utf-8") as f:
            aj = json.load(f)
        with open(os.path.join(here, "..", "eval", "safe_prototypes.json"), encoding="utf-8") as f:
            sj = json.load(f)
        a_flat = [t for ts in aj.values() for t in ts]
        s_flat = [t for ts in sj.values() for t in ts]
        self.assertEqual(sorted(ACTION_PROTOTYPES), sorted(a_flat))
        self.assertEqual(sorted(SAFE_PROTOTYPES), sorted(s_flat))


class TestGuardRuleA(unittest.TestCase):
    def test_action_verbs_block(self):
        for text in ("turn the heating up",
                     "turn the heating down",
                     "switch the bedroom lamp off",
                     "switch off the kitchen lights",
                     "set the thermostat to 21 degrees",
                     "set a timer for ten minutes",
                     "set an alarm for 6:30",
                     "unlock a door",
                     "lock up the flat",
                     "bolt the front gate",
                     "secure the side door",
                     "kill the study light",
                     "add eggs to my shopping list",
                     "add coffee to the list",
                     "remove bread from the shopping list",
                     "remind me to buy milk",
                     "wake me up at seven",
                     "count down five minutes",
                     "send a message to mum",
                     "open the front door",
                     "close the garage door",
                     "please turn the lights off"):
            self.assertIsNotNone(guard_rule_a(text), text)

    def test_v24_home_action_verbs_block(self):
        # v2.4: the home-action verbs v1.0 missed.
        for text in ("boil the kettle",
                     "preheat the oven to 200",
                     "play the radio in the bedroom",
                     "play some jazz",
                     "boost the heating",
                     "brew a pot of coffee",
                     "cook the rice",
                     "bake a cake",
                     "wash the dishes",
                     "dry the laundry",
                     "clean the kitchen",
                     "vacuum the living room",
                     "mop the floor",
                     "charge my phone",
                     "iron my shirt",
                     "sweep the hallway",
                     "dust the shelves"):
            self.assertIsNotNone(guard_rule_a(text), text)

    def test_v24_make_for_block(self):
        # v2.4: "make <beneficiary> <article>" is an action request,
        # but "make me laugh" (chatter) and "make a video" (creative)
        # are not.
        for text in ("make me a coffee",
                     "make us a sandwich",
                     "make him a cup of tea",
                     "please make me a coffee"):
            self.assertIsNotNone(guard_rule_a(text), text)
        for text in ("make me laugh",
                     "make a video",
                     "make a 10 second animated video"):
            self.assertIsNone(guard_rule_a(text), text)
        for text in ("what is the capital of france",
                     "how do i make pancakes",
                     "how do i start a fire",
                     "how can i restart my wi-fi router",
                     "tell me the capital of france",
                     "tell me a joke about cats",
                     "write a haiku about autumn rain",
                     "write a python function to sort a list",
                     "make a 10 second animated video",
                     "explain photosynthesis in one sentence",
                     "translate good morning into japanese",
                     "what time does the london underground close on sundays",
                     "how are you doing"):
            self.assertIsNone(guard_rule_a(text), text)

    def test_v25_yard_verbs_and_message_block(self):
        # v2.5: the yard-work verbs and the messaging verb v2.4
        # missed. "trim" stays OUT (it also heads video edits).
        for text in ("mow the lawn this afternoon",
                     "rake the leaves in the garden",
                     "prune the roses",
                     "weed the flower beds",
                     "message maa good morning at 8",
                     "please message papa the door is unlocked"):
            self.assertIsNotNone(guard_rule_a(text), text)
        self.assertIsNone(guard_rule_a("trim the video to ten seconds"))

    def test_v25_question_guard(self):
        # v2.5: Rule A does not fire on a factual question, even
        # when the leading word is in the verb class as a noun
        # ("water") or a factual verb ("count"). The wh-word may
        # appear anywhere in the prompt; a trailing "?" on the raw
        # text also marks a question.
        for text, raw in (
                ("water boils at what temperature at sea level",
                 "Water boils at what temperature at sea level?"),
                ("count the continents for me, how many are there",
                 "Count the continents for me, how many are there?"),
                ("water boils at 100 degrees",
                 "Water boils at 100 degrees?")):
            self.assertIsNone(guard_rule_a(text, raw), text)
        # But a genuine action with no question word still blocks,
        # including the noun-verb "water" heading a real action.
        for text in ("water the plants on the balcony with the hose",
                     "count down five minutes",
                     "turn the heating up"):
            self.assertIsNotNone(guard_rule_a(text), text)

    def test_empty_does_not_block(self):
        self.assertIsNone(guard_rule_a(""))
        self.assertIsNone(guard_rule_a("   "))


class TestGuardRuleB(unittest.TestCase):
    def test_state_queries_block(self):
        for text in ("is the back door shut",
                     "is the side door closed",
                     "is the bedroom lamp still on",
                     "did i leave the front gate open",
                     "did i leave the hallway light on",
                     "are the kitchen lights on",
                     "are the study lights off",
                     "is the flat locked up",
                     "is the heating on",
                     "is the wi-fi working"):
            self.assertIsNotNone(guard_rule_b(text), text)

    def test_weather_and_advice_block(self):
        for text in ("what is the forecast for the weekend",
                     "is it going to snow this week",
                     "is it going to rain tomorrow",
                     "do i need a jacket today",
                     "do i need an umbrella tomorrow",
                     "what is on my shopping list",
                     "what's on my shopping list"):
            self.assertIsNotNone(guard_rule_b(text), text)

    def test_v24_live_state_forms_block(self):
        # v2.4: new live-state forms (stock, where-is-mine,
        # daily-count) and the expanded entities/state words.
        for text in ("has the tumble dryer finished",
                     "is the coffee machine ready",
                     "is the robot vacuum done",
                     "are we out of milk",
                     "do we have any eggs",
                     "is there any bread left",
                     "where is my parcel",
                     "where is our delivery",
                     "how many steps have i done today",
                     "how many steps did i do yesterday"):
            self.assertIsNotNone(guard_rule_b(text), text)

    def test_v25_where_are_and_windows_and_rain_block(self):
        # v2.5: "where are my ..." (not just "is"), the wider
        # daily-count windows ("last night", ...), and the
        # weather-now form ("is it raining / snowing").
        for text in ("where are my car keys",
                     "where are our passports",
                     "how many hours did i sleep last night",
                     "how many steps have i done this morning",
                     "how many calories did i burn last week",
                     "is it raining outside right now",
                     "is it snowing in london"):
            self.assertIsNotNone(guard_rule_b(text), text)

    def test_factual_time_and_schedule_do_not_block(self):
        # The distinction Rule B must preserve: a factual question
        # about a schedule is stable and cacheable; a live-state
        # question is not.
        for text in ("what time does the london underground close on sundays",
                     "when does the tube close on sundays",
                     "london underground sunday closing time",
                     "what is the capital of france",
                     "is paris the capital of france",
                     "how many moons does jupiter have",
                     "how do you say good morning in japanese",
                     "write a haiku about autumn rain",
                     "how are you doing"):
            self.assertIsNone(guard_rule_b(text), text)

    def test_empty_does_not_block(self):
        self.assertIsNone(guard_rule_b(""))
        self.assertIsNone(guard_rule_b("   "))


class TestDenylistV13Temperature(unittest.TestCase):
    """v2.4 denylist v1.3: the narrowed temperature pattern."""

    def test_boil_freeze_factual_not_blocked(self):
        # The v5 dev FP: stable factual questions about boiling /
        # freezing points must not be blocked.
        for text in ("at what temperature does water boil",
                     "at what temperature does water freeze",
                     "at what temperature does water boil at sea level",
                     "what temperature does water freeze at"):
            self.assertIsNone(denied(text), text)

    def test_live_temperature_still_blocked(self):
        for text in ("what is the temperature",
                     "what is the temperature outside",
                     "what's the temperature",
                     "what is the temperature today",
                     "what is the temperature in london",
                     "how hot is it",
                     "how cold is it",
                     "what is the temp outside"):
            self.assertIsNotNone(denied(text), text)


class TestDenylistV14Message(unittest.TestCase):
    """v2.5 denylist v1.4: the narrowed message pattern (kept in v1.5)."""

    def test_message_in_story_not_blocked(self):
        # The v6 dev FP: "message" as a noun inside a creative
        # story must not be blocked.
        for text in ("write a short story about a lighthouse keeper "
                     "who finds a message in a bottle",
                     "write a poem about a message in a time capsule"):
            self.assertIsNone(denied(text), text)

    def test_messaging_actions_still_blocked(self):
        for text in ("send a message to mum",
                     "send a quick message to papa",
                     "text me the message when it arrives",
                     "forward the message to reema",
                     "leave a message for mum",
                     "message maa good morning at 8",
                     "please message papa the door is unlocked"):
            self.assertIsNotNone(denied(text), text)

    def test_plain_message_noun_not_blocked(self):
        # "message" as a plain noun with no messaging verb or
        # recipient nearby (the v4 bus body v4-015) is not caught
        # by the regex any more; the per-category Rule C statement
        # margin (0.10) is its layer.
        self.assertIsNone(
            denied("fall back to the full llm path with the plain message"))


class TestDenylistV15MessageFor(unittest.TestCase):
    """v2.6 denylist v1.5: "message to" always blocks; "message for"
    skips when a creative verb (draft/write/create/compose) leads
    the message - drafting a birthday/thank-you message FOR someone
    is a creative artefact, not a messaging action."""

    def test_creative_draft_for_not_blocked(self):
        # Synthetic members of the creative-draft class (NOT the
        # v7 holdout text - that item is retired and never used here).
        for text in ("draft a birthday message for my friend",
                     "write a birthday message for my sister",
                     "create a thank-you message for my teacher",
                     "compose a birthday message for my colleague"):
            self.assertIsNone(denied(text), text)

    def test_messaging_for_still_blocked(self):
        for text in ("send a message for mum",
                     "text a message for me",
                     "leave a message for papa"):
            self.assertIsNotNone(denied(text), text)

    def test_message_to_always_blocked(self):
        # "message to" is a messaging action even with a creative
        # verb leading it ("draft a message to mum" is a message
        # to send, not a creative artefact).
        for text in ("send a message to mum",
                     "write a message to mum",
                     "draft a message to mum",
                     "create a message to reema"):
            self.assertIsNotNone(denied(text), text)


class TestGuardFormOnDev(unittest.TestCase):
    """Rules A+B on the frozen dev sets (v3+v4+v5+v6+v7+v8+v9+v10, 536 prompts)."""

    def test_form_rules_recall_and_fp_on_dev(self):
        rows = _dev_rows()
        never = [r for r in rows if r.get("cacheable") == "never"
                 and r.get("route") == "full"]
        safe = [r for r in rows if r.get("cacheable") in ("stable", "ttl24")
                and r.get("route") == "full"
                and r.get("category") != "agent-task"]
        missed_never = [r for r in never
                        if denied(r.get("text", "")) is None]
        missed_safe = [r for r in safe
                       if denied(r.get("text", "")) is None]
        # Rules A v3 + B v7 catch 129 of the 133 regex-missed never
        # items with zero false positives on gateway safe traffic.
        # The remaining 4 (the v4 bus body v4-015, the v4
        # self-improvement body, "make it warmer in here",
        # "Show me the front door camera.") are Rule C's job.
        # v7-032 "Lower the thermostat to 18 degrees." is now
        # form-blocked (Rule A "lower" joins the verb class in v2.8),
        # so it is no longer a Rule C reacher.
        caught = [r for r in missed_never
                  if guard_form_check(normalize_text(r.get("text", "")),
                                      r.get("text", ""))]
        fp = [r for r in missed_safe
              if guard_form_check(normalize_text(r.get("text", "")),
                                  r.get("text", ""))]
        self.assertEqual(len(caught), 129, [r["text"] for r in missed_never
                                            if r not in caught])
        self.assertEqual(len(fp), 0, [r["text"] for r in fp])

    def test_regex_plus_form_recall_on_dev(self):
        rows = _dev_rows()
        never = [r for r in rows if r.get("cacheable") == "never"
                 and r.get("route") == "full"]
        blocked = [r for r in never
                   if denied(r.get("text", "")) is not None
                   or guard_form_check(normalize_text(r.get("text", "")),
                                       r.get("text", ""))]
        # 85 regex + 129 form = 214 of 218. The 4 left are Rule C's.
        self.assertEqual(len(blocked), 214)

    def test_v6_dev_failures_fixed_by_form_rules(self):
        # The three v6 dev never items v2.4 missed are now caught
        # by form rules, and the two v6 dev FPs are now unblocked.
        rows = _dev_rows()
        v6 = [r for r in rows if r.get("id", "").startswith("v6-")]
        by_text = {r["text"]: r for r in v6}
        for text in ("Mow the lawn this afternoon.",
                     "How many hours did I sleep last night?",
                     "Where are my car keys?",
                     "Is it raining outside right now?"):
            r = by_text[text]
            self.assertEqual(r["cacheable"], "never")
            self.assertTrue(
                denied(text) is not None
                or guard_form_check(normalize_text(text), text) is not None,
                text)
        for text in ("Water boils at what temperature at sea level?",
                     "Write a short story about a lighthouse keeper "
                     "who finds a message in a bottle."):
            r = by_text[text]
            self.assertIn(r["cacheable"], ("stable", "ttl24"))
            self.assertIsNone(denied(text), text)
            self.assertIsNone(
                guard_form_check(normalize_text(text), text), text)


    def test_v7_dev_failures_fixed_by_form_rules(self):
        # The four v7 dev never items v2.5 missed are now caught
        # by Rule B v4 form rules, each by its general class.
        cases = {
            "Is the washing finished yet?": "rule-b:state-query",
            "What's the weather like outside at the moment?":
                "rule-b:weather-like",
            "How warm is it in the house right now?":
                "rule-b:indoor-temp",
            "Has my parcel been delivered yet?": "rule-b:state-query",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)
            self.assertIsNone(denied(text), text)

    def test_v26_new_forms_do_not_block_factual(self):
        # The new forms are class-scoped, not word-scoped: a
        # factual question sharing a word stays unblocked.
        for text in ("how warm is it inside the earth",
                     "what is the new world order",
                     "is the order of the planets changing",
                     # "what is the weather like on Mars" is factual
                     # (the weather-like form fires only on the
                     # contracted "what's", the live-weather phrasing).
                     # A forecast question ("what is the weather
                     # forecast for tomorrow") IS blocked, by the
                     # pre-existing _RULE_B_WEATHER_RE, not by v2.6.
                     "what is the weather like on mars"):
            self.assertIsNone(denied(text), text)
            self.assertIsNone(
                guard_form_check(normalize_text(text), text), text)

    def test_v26_delivery_form_blocks(self):
        for text in ("has my order been delivered yet",
                     "is my order ready",
                     "has my order arrived"):
            self.assertEqual(
                guard_form_check(normalize_text(text), text),
                "rule-b:delivery-status", text)

    def test_v27_new_forms_block(self):
        # v2.7: the five new Rule B v5 forms, one per v8 failure
        # class. Each is a general pattern class, not a per-item
        # patch.
        cases = {
            # Uncontracted weather-like (live marker required).
            "What is the weather like outside right now?":
                "rule-b:weather-like",
            "What is the weather doing today?":
                "rule-b:weather-like",
            "What is the weather like at the moment?":
                "rule-b:weather-like",
            # Presence ("is someone/anyone at/in <home location>").
            "Is someone at the front door?": "rule-b:presence",
            "Is anyone in the kitchen?": "rule-b:presence",
            "Is somebody at the door?": "rule-b:presence",
            "Is anyone home?": "rule-b:presence",
            # Softened imperative ("can/could you <action verb>").
            "Can you set an alarm for seven in the morning?":
                "rule-b:softened-imperative",
            "Could you book a taxi for tomorrow morning?":
                "rule-b:softened-imperative",
            "Can you turn the heating down a couple of degrees?":
                "rule-b:softened-imperative",
            "Could you turn off the lights in the living room?":
                "rule-b:softened-imperative",
            "Could you lock the door for me":
                "rule-b:softened-imperative",
            # Completion state words ("boiled" etc.) in the state form.
            "Has the kettle boiled?": "rule-b:state-query",
            "Has the coffee brewed?": "rule-b:state-query",
            "Is my phone charged?": "rule-b:state-query",
            # "did i (leave|put|lose|place)".
            "Where did I put my phone?": "rule-b:did-i-leave",
            "Where did I lose my wallet?": "rule-b:did-i-leave",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)

    def test_v27_new_forms_do_not_block_factual(self):
        # The new forms are class-scoped, not word-scoped: a
        # factual or creative question sharing a word stays
        # unblocked.
        for text in (
                # Weather-like needs a live marker: a planet is factual.
                "what is the weather like on mars",
                "what is the weather like on venus",
                "what's the weather like on mars",
                # Presence needs a home location: a party is not one.
                "is anyone at the party",
                "is someone famous",
                # Softened imperative needs an action verb: tell /
                # explain / write are not action verbs.
                "can you tell me the capital of france",
                "could you explain photosynthesis",
                "can you write a poem about autumn leaves",
                # Softened imperative needs no wh-word: a factual
                # "count how many" is a question, not an action.
                "can you count how many continents there are",
                "could you tell me what time it is",
                # "did i put" needs a belonging: a factual "put"
                # does not match.
                "where did i put the emphasis in this sentence"):
            self.assertIsNone(denied(text), text)
            self.assertIsNone(
                guard_form_check(normalize_text(text), text), text)

    def test_v8_dev_failures_fixed_by_form_rules(self):
        # The four v8 dev never items v2.6 missed are now caught
        # by Rule B v5 form rules, each by its general class.
        cases = {
            "Can you set an alarm for seven in the morning?":
                "rule-b:softened-imperative",
            "Has the kettle boiled?": "rule-b:state-query",
            "Could you book a taxi for tomorrow morning?":
                "rule-b:softened-imperative",
            "Where did I put my phone?": "rule-b:did-i-leave",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)
            self.assertIsNone(denied(text), text)

    def test_v28_new_forms_block(self):
        # v2.8: the three Rule B v6 widenings, one per v9 failure
        # class. Each is a general pattern class, not a per-item
        # patch.
        cases = {
            # Novel softened-imperative verbs ("lower", "cancel",
            # "change", "adjust", ... join the action verb class).
            "Could you lower the heating in the bedroom a bit?":
                "rule-b:softened-imperative",
            "Can you cancel my dentist appointment on Thursday?":
                "rule-b:softened-imperative",
            "Could you change the meeting to Friday?":
                "rule-b:softened-imperative",
            "Can you adjust the thermostat by two degrees?":
                "rule-b:softened-imperative",
            "Could you reschedule my appointment?":
                "rule-b:softened-imperative",
            # Completion-state widening: food entities + "ready",
            # and "dry" as a state word.
            "Is dinner ready yet?": "rule-b:state-query",
            "Is the washing dry yet?": "rule-b:state-query",
            "Is lunch ready?": "rule-b:state-query",
            "Is the cake baked?": "rule-b:state-query",
            "Is the soup hot?": "rule-b:state-query",
            "Is the laundry clean?": "rule-b:state-query",
            # Live-fact form: an astronomical/tide event, or any
            # noun + a day marker.
            "What time is sunset today?": "rule-b:live-fact",
            "What time is sunrise tomorrow?": "rule-b:live-fact",
            "What time is high tide tonight?": "rule-b:live-fact",
            "What time is the meeting today?": "rule-b:live-fact",
            "What time is lunch tomorrow?": "rule-b:live-fact",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)

    def test_v28_new_forms_do_not_block_factual(self):
        # The widenings are class-scoped, not word-scoped: a
        # factual question sharing a word stays unblocked.
        for text in (
                # "lower" / "cancel" need an action request: a
                # factual question about the word does not match.
                "what does lower case mean",
                "what is cancel culture",
                # "change" needs a softened imperative: a wh-word
                # keeps a factual question out.
                "can you change how many moons jupiter has",
                # "dinner" / "dry" need the state form (is/are +
                # entity + state word): a how-question does not match.
                "how does washing dry in winter",
                "how do you cook dinner properly",
                # Live-fact needs an event noun or a day marker: a
                # stable factual question does not match.
                "what time does the underground close",
                # NOTE v2.9: "at what time does the sun set in
                # summer" was in this list under v2.8, but it is now
                # correctly blocked by the live-fact-time-does form:
                # a sunset time is date-dependent, so a cached
                # answer would be stale. It is the same class as
                # "what time is sunset", which v2.8 already blocks.
                # Removed from this list, covered in
                # test_v29_new_forms_block.
                "what is the time difference between london and tokyo"):
            self.assertIsNone(denied(text), text)
            self.assertIsNone(
                guard_form_check(normalize_text(text), text), text)

    def test_v9_dev_failures_fixed_by_form_rules(self):
        # The five v9 dev never items v2.7 missed are now caught
        # by Rule B v6 form rules, each by its general class.
        cases = {
            "Could you lower the heating in the bedroom a bit?":
                "rule-b:softened-imperative",
            "Is dinner ready yet?": "rule-b:state-query",
            "Can you cancel my dentist appointment on Thursday?":
                "rule-b:softened-imperative",
            "Is the washing dry yet?": "rule-b:state-query",
            "What time is sunset today?": "rule-b:live-fact",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)
            self.assertIsNone(denied(text), text)

    def test_v29_new_forms_block(self):
        # v2.9: the Rule B v7 widenings, one per v10 failure class.
        # Each is a general pattern class, not a per-item patch.
        cases = {
            # Live-fact "when" form: a celestial event's time
            # changes daily, so "when does the sun go down" is a
            # live fact, not a stable one. Same class as "what
            # time is sunset" (v2.8), different question word.
            "When does the sun go down today?":
                "rule-b:live-fact-when",
            "When does the sun rise tomorrow?":
                "rule-b:live-fact-when",
            "When does the moon set tonight?":
                "rule-b:live-fact-when",
            "What time does the sun go down?":
                "rule-b:live-fact-time-does",
            "What time does the moon rise?":
                "rule-b:live-fact-time-does",
            "at what time does the sun set in summer":
                "rule-b:live-fact-time-does",
            # Tide "when" form.
            "When is high tide today?": "rule-b:tide-when",
            "When is low tide tomorrow?": "rule-b:tide-when",
            "When does the tide come in?": "rule-b:tide-when",
            "When does the tide go out?": "rule-b:tide-when",
            # Delivery entities in the state form: "post"/"mail"/
            # "letter" join parcel/delivery/package/shipment.
            "Has the post arrived today?": "rule-b:state-query",
            "Has the mail arrived yet?": "rule-b:state-query",
            "Has the letter arrived?": "rule-b:state-query",
            # Device entities in the state form: "car"/"laptop"/
            # "tablet" join phone/battery. "charged enough" needs
            # no new form: "charged" is already a state word.
            "Is the car charged enough for tomorrow?":
                "rule-b:state-query",
            "Is my laptop charged?": "rule-b:state-query",
            "Is the tablet on?": "rule-b:state-query",
            # "enough charge/battery" form: a sufficiency check
            # with no state word.
            "Does my phone have enough battery?":
                "rule-b:enough-charge",
            "Does the car have enough charge for tomorrow?":
                "rule-b:enough-charge",
            "Do I have enough battery left?":
                "rule-b:enough-charge",
            # "check if" form: "check" stays out of the action
            # verbs, but "check if" + a live entity + a state
            # word is a live-state question.
            "Can you check if the oven is still on?":
                "rule-b:check-if",
            "Can you check if the front door is locked?":
                "rule-b:check-if",
            "Check if the lights are on upstairs.":
                "rule-b:check-if",
            # Progressive state words: "charging"/"drying"/
            # "washing"/"cooking"/"baking"/"brewing"/"boiling".
            "Is my phone charging in the bedroom?":
                "rule-b:state-query",
            "Is the washing drying?": "rule-b:state-query",
            "Is dinner cooking?": "rule-b:state-query",
            "Is the kettle boiling?": "rule-b:state-query",
            # Calendar/schedule lookup: a belonging or a day
            # marker makes it live, like the list-query form.
            "What is on my calendar tomorrow?":
                "rule-b:calendar",
            "What's on my schedule today?": "rule-b:calendar",
            "What is on the calendar for next week?":
                "rule-b:calendar",
            "What is on our agenda tonight?": "rule-b:calendar",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)

    def test_v29_new_forms_do_not_block_factual(self):
        # The widenings are class-scoped, not word-scoped: a
        # factual question sharing a word stays unblocked.
        for text in (
                # "when does the sun" needs a time verb (go down /
                # rise / set / come up): a direction fact does not
                # match.
                "when does the sun rise in the east",
                "where does the sun set",
                # "enough charge/battery" needs the sufficiency
                # words: "enough time" / "enough money" do not
                # match.
                "do i have enough time today",
                "do we have enough money for the trip",
                # "check if" needs a live entity + a state word: a
                # factual check does not match.
                "check if the capital of france is paris",
                "check if the triangle has three sides",
                "can you check if water boils at 100 degrees",
                # Progressive state needs a live entity: "is the
                # water boiling" has no live entity.
                "is the water boiling",
                "how does bread bake in an oven",
                # Calendar needs a belonging or a day marker: bare
                # "what is on the calendar" does not match.
                "what is on the calendar",
                # "car"/"post"/"mail" need the state form (is/are
                # + entity + state word): a how/what question does
                # not match.
                "how fast is the car",
                "what is the post code for london",
                "how does mail travel"):
            self.assertIsNone(denied(text), text)
            self.assertIsNone(
                guard_form_check(normalize_text(text), text), text)

    def test_v10_dev_failures_fixed_by_form_rules(self):
        # The four v10 dev never items v2.8 missed are now caught
        # by Rule B v7 form rules, each by its general class.
        cases = {
            "When does the sun go down today?":
                "rule-b:live-fact-when",
            "Has the post arrived today?": "rule-b:state-query",
            "Is the car charged enough for tomorrow?":
                "rule-b:state-query",
            "What is on my calendar tomorrow?": "rule-b:calendar",
        }
        for text, form in cases.items():
            self.assertEqual(
                guard_form_check(normalize_text(text), text), form, text)
            self.assertIsNone(denied(text), text)

    def test_v28_creative_draft_exemption(self):
        # v2.8 Rule C: a creative draft (leading creative verb +
        # a creative artefact noun) is exempt from the margin
        # block. Pure text, no embedding. "make" is not a creative
        # verb here (same reason as the v1.5 regex guard), and
        # "reminder" / "function" are not creative artefacts.
        exempt = (
            "Write a birthday message for my mum",
            "Write a haiku about autumn rain.",
            "Write a short story about a lighthouse keeper who "
            "finds a message in a bottle.",
            "Invent a bedtime story for a five-year-old about a "
            "brave little fox.",
            "Compose a poem for my sister's wedding.",
            "Draft a short speech for my dad's retirement.",
            "Write a thank-you letter to my teacher.",
            "Craft a toast for the newlyweds.",
            "Write a song about the monsoon in Mumbai.",
            "Write a message to Reema to say I'll be ten minutes "
            "late.",
        )
        for text in exempt:
            self.assertTrue(
                is_creative_draft(normalize_text(text)), text)
        not_exempt = (
            "write a python function to sort a list",
            "Lower the thermostat to 18 degrees.",
            "make it warmer in here",
            "Show me the front door camera.",
            "Write a reminder for Dad's birthday next week.",
            "Turn the heating up",
            "Is dinner ready yet?",
        )
        for text in not_exempt:
            self.assertFalse(
                is_creative_draft(normalize_text(text)), text)


class TestPromptClass(unittest.TestCase):
    """v2.5 prompt classes for the per-category Rule C margin."""

    def test_question_forms(self):
        for text in ("what is the capital of france",
                     "how many hours did i sleep last night",
                     "where are my car keys",
                     "is the heating on right now",
                     "water boils at what temperature at sea level",
                     "count the continents for me, how many are there"):
            self.assertEqual(
                prompt_class(normalize_text(text), text), "question", text)
        # Trailing "?" on the raw text marks a question even when
        # the normalised text has lost the "?".
        self.assertEqual(prompt_class("water boils at 100 degrees",
                                      "Water boils at 100 degrees?"),
                         "question")

    def test_imperative_forms(self):
        for text in ("mow the lawn this afternoon",
                     "turn the heating up",
                     "write a short story about a cat",
                     "tell me a joke",
                     "name the biggest ocean in the world",
                     "please turn the lights off"):
            self.assertEqual(
                prompt_class(normalize_text(text), text), "imperative", text)

    def test_statement_forms(self):
        for text in ("i am shattered after today, honestly",
                     "a haiku about autumn rain please",
                     "1) agents.md rule text (reconstructed from notes)",
                     "self-improvement pass changes applied"):
            self.assertEqual(
                prompt_class(normalize_text(text), text), "statement", text)

    def test_margin_thresholds_per_class(self):
        cfg = load_config()
        self.assertEqual(guard_margin_for_class("imperative", cfg), 0.20)
        self.assertEqual(guard_margin_for_class("question", cfg), 0.20)
        self.assertEqual(guard_margin_for_class("statement", cfg), 0.10)


class TestGuardMargin(unittest.TestCase):
    def test_statement_margin_is_lower(self):
        # v2.5: a statement-form prompt with a +0.15 margin is
        # blocked (statement threshold 0.10), while the same margin
        # on an imperative or question prompt is not (0.20).
        dim = 4
        action_vec = [1.0, 0.0, 0.0, 0.0]
        safe_vec = [0.0, 1.0, 0.0, 0.0]
        mapping = {}
        for p in ACTION_PROTOTYPES:
            mapping[normalize_text(p)] = action_vec
        for p in SAFE_PROTOTYPES:
            mapping[normalize_text(p)] = safe_vec
        # A prompt vector at [0.78, sqrt(1-0.78^2)] has sim 0.78 to
        # the action side and 0.63 to the safe side: margin +0.15,
        # between the statement threshold (0.10) and the
        # imperative/question threshold (0.20).
        import math as _math
        v = [0.78, _math.sqrt(1 - 0.78 ** 2), 0.0, 0.0]
        gw, _ = _gateway_with_fake(mapping, threshold=0.90)
        blocked, margin, _a, _s, cls, thr = gw.guard_margin_check(
            v, "self-improvement pass changes applied",
            "Self-improvement pass - changes applied.")
        self.assertTrue(blocked, margin)
        self.assertEqual(cls, "statement")
        self.assertEqual(thr, 0.10)
        blocked, margin, _a, _s, cls, thr = gw.guard_margin_check(
            v, "turn the heating up", "Turn the heating up.")
        self.assertFalse(blocked, margin)
        self.assertEqual(cls, "imperative")
        self.assertEqual(thr, 0.20)
        blocked, margin, _a, _s, cls, thr = gw.guard_margin_check(
            v, "is the heating on right now", "Is the heating on?")
        self.assertFalse(blocked, margin)
        self.assertEqual(cls, "question")

    def test_margin_blocks_action_close_prompt(self):
        # Synthetic vectors: action prototypes near [1,0], safe near
        # [0,1]. A prompt near the action side has a large positive
        # margin and is blocked; a prompt near the safe side is not.
        dim = 4
        action_vec = [1.0, 0.0, 0.0, 0.0]
        safe_vec = [0.0, 1.0, 0.0, 0.0]
        mapping = {}
        for p in ACTION_PROTOTYPES:
            mapping[normalize_text(p)] = action_vec
        for p in SAFE_PROTOTYPES:
            mapping[normalize_text(p)] = safe_vec
        # Prompt close to the action side (sim 0.9 to action, ~0.1
        # to safe): margin ~0.8, blocked.
        prompt_action = [0.9, math.sqrt(1 - 0.9 ** 2), 0.0, 0.0]
        mapping["turn the heating up"] = prompt_action
        # Prompt close to the safe side: margin negative, not blocked.
        prompt_safe = [0.1, math.sqrt(1 - 0.1 ** 2), 0.0, 0.0]
        mapping["what is the capital of france"] = prompt_safe
        gw, _ = _gateway_with_fake(mapping, threshold=0.90)
        blocked, margin, sim_a, sim_s, cls, thr = gw.guard_margin_check(
            prompt_action, "turn the heating up", "Turn the heating up.")
        self.assertTrue(blocked)
        self.assertGreater(margin, 0.20)
        self.assertEqual(cls, "imperative")
        self.assertEqual(thr, 0.20)
        blocked, margin, sim_a, sim_s, cls, thr = gw.guard_margin_check(
            prompt_safe, "what is the capital of france",
            "What is the capital of France?")
        self.assertFalse(blocked)
        self.assertLess(margin, 0.20)
        self.assertEqual(cls, "question")

    def test_margin_disabled_when_guard_off(self):
        mapping = {}
        for p in ACTION_PROTOTYPES:
            mapping[normalize_text(p)] = [1.0, 0.0, 0.0, 0.0]
        for p in SAFE_PROTOTYPES:
            mapping[normalize_text(p)] = [0.0, 1.0, 0.0, 0.0]
        gw, _ = _gateway_with_fake(mapping, guard_enabled=False)
        blocked, margin, _a, _s, _c, _t = gw.guard_margin_check(
            [1.0, 0.0, 0.0, 0.0], "turn the heating up")
        self.assertFalse(blocked)
        self.assertIsNone(margin)

    def test_v28_creative_draft_exempt_from_margin(self):
        # v2.8: a creative draft is exempt from the Rule C margin
        # block even when its margin exceeds the threshold. The
        # same vector with a non-creative text is still blocked.
        # Synthetic vectors: action prototypes near [1,0], safe
        # near [0,1]. A prompt near the action side has margin
        # ~0.8, above the 0.20 imperative threshold.
        action_vec = [1.0, 0.0, 0.0, 0.0]
        safe_vec = [0.0, 1.0, 0.0, 0.0]
        mapping = {}
        for p in ACTION_PROTOTYPES:
            mapping[normalize_text(p)] = action_vec
        for p in SAFE_PROTOTYPES:
            mapping[normalize_text(p)] = safe_vec
        prompt_action = [0.9, math.sqrt(1 - 0.9 ** 2), 0.0, 0.0]
        gw, _ = _gateway_with_fake(mapping, threshold=0.90)
        # Non-creative text, margin above threshold: blocked.
        blocked, margin, _a, _s, cls, thr = gw.guard_margin_check(
            prompt_action, "turn the heating up", "Turn the heating up.")
        self.assertTrue(blocked, margin)
        self.assertGreater(margin, 0.20)
        # Creative draft, same vector and margin: exempt.
        blocked, margin, _a, _s, cls, thr = gw.guard_margin_check(
            prompt_action, "write a birthday message for my mum",
            "Write a birthday message for my mum.")
        self.assertFalse(blocked, margin)
        self.assertGreater(margin, 0.20)
        self.assertEqual(cls, "imperative")
        self.assertEqual(thr, 0.20)

    def test_guard_blocks_never_prompt_end_to_end(self):
        # A verb-led never prompt is blocked by Rule A before any
        # embedding call (the FakeEmbedder records calls).
        gw, emb = _gateway_with_fake({})
        r = gw.query("turn the heating up")
        self.assertFalse(r["hit"])
        self.assertTrue(r["blocked_by"].startswith("denylist:guard-rule-a"))
        self.assertEqual(r["cache_status"], "blocked-denylist")
        self.assertEqual(emb.calls, 0)  # no embedding: blocked pre-embed
        self.assertEqual(gw.stats["blocked_guard"], 1)

    def test_guard_does_not_block_safe_prompt(self):
        # Prompt and safe prototypes on one side, action prototypes
        # on the other: the margin is negative, so Rule C does not
        # block, and Rules A+B do not match a factual question.
        mapping = {"what is the capital of france": [1.0, 0.0, 0.0, 0.0]}
        for p in SAFE_PROTOTYPES:
            mapping[normalize_text(p)] = [1.0, 0.0, 0.0, 0.0]
        for p in ACTION_PROTOTYPES:
            mapping[normalize_text(p)] = [0.0, 1.0, 0.0, 0.0]
        gw, _ = _gateway_with_fake(mapping)
        r = gw.query("What is the capital of France?")
        self.assertFalse(r["blocked_by"])
        self.assertEqual(r["cache_status"], "miss-stored")
        self.assertEqual(gw.stats["blocked_guard"], 0)

    def test_stats_and_health_report_guard(self):
        gw, _ = _gateway_with_fake({})
        gw.query("turn the heating up")
        stats = gw.stats_summary()
        self.assertEqual(stats["gateway_version"], "v2.9-guard")
        self.assertEqual(stats["guard"], "v2.5")
        self.assertEqual(stats["guard_margin"], 0.20)
        self.assertEqual(stats["guard_margin_statement"], 0.10)
        self.assertEqual(stats["guard_margins"],
                         {"imperative": 0.20, "question": 0.20,
                          "statement": 0.10})
        self.assertEqual(stats["guard_action_prototypes"], len(ACTION_PROTOTYPES))
        self.assertEqual(stats["guard_safe_prototypes"], len(SAFE_PROTOTYPES))
        self.assertEqual(stats["blocked_by_guard"], 1)


class TestLiveGuardMargin(unittest.TestCase):
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

    def test_real_margin_separates_dev(self):
        # The full guard (regex + A + B + C at 0.20) blocks every
        # dev never item and no dev safe item. This is the same
        # measurement as probe_guard3.py, recomputed live.
        from semantic_gateway.gateway import OllamaEmbedder
        emb = OllamaEmbedder("http://127.0.0.1:11434", "bge-m3")
        gw, _ = _gateway_with_fake({}, threshold=0.90)
        # Use the real embedder for the guard's prototype embeddings
        # and the prompt embeddings.
        gw.embedder = emb
        rows = _dev_rows()
        never = [r for r in rows if r.get("cacheable") == "never"
                 and r.get("route") == "full"]
        safe = [r for r in rows if r.get("cacheable") in ("stable", "ttl24")
                and r.get("route") == "full"
                and r.get("category") != "agent-task"]
        missed_never = [r for r in never
                        if denied(r.get("text", "")) is None]
        missed_safe = [r for r in safe
                       if denied(r.get("text", "")) is None]
        for r in missed_never:
            res = gw.query(r["text"])
            self.assertIsNotNone(res["blocked_by"], r["text"])
            self.assertTrue(res["blocked_by"].startswith("denylist:guard"),
                            (r["text"], res["blocked_by"]))
        for r in missed_safe:
            res = gw.query(r["text"])
            self.assertIsNone(res["blocked_by"], (r["text"], res["blocked_by"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
