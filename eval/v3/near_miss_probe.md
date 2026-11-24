# Near-miss probe - measured bge-m3 similarities (23 Nov 2026)

Candidates for the v3 NM-A/NM-C families, measured with bge-m3 via
Ollama on the Spark before the v3 build. The probe decides which
candidates are kept and why. "In band" is the 0.95-0.97 range where
safe paraphrases and unsafe near-misses overlap (eval audit
Finding 4).

## Round 1 - opposites and paraphrases

| Similarity | Verdict | Pair |
|---|---|---|
| 0.9427 | below band | NM-A alert-3 (frame-021, dark figure, left side) vs real alert 1 |
| 0.9209 | below band | NM-A alert-3 vs real alert 2 |
| 0.8831 | below band | "turn the lights off" vs "turn the lights on" |
| 0.8699 | below band | "turn off the living room lights" vs "turn on the living room lights" |
| 0.8933 | below band | "what is the temperature outside" vs "what's the temperature" |
| 0.9253 | below band | "is the door open" vs "is the door locked" |
| 0.8875 | below band | "is the door open" vs "is the door unlocked" |
| 0.7760 | below band | "tell me a joke about cats" vs "Tell me a joke." |
| 0.9098 | below band | "tell me another joke" vs "Tell me a joke." |
| 0.8869 | below band | control: "unlock a door" vs "lock the door" |

Round 1 showed opposites score 0.87-0.93, below the band. The
band is populated by near-identical strings, not by opposites.

## Round 2 - near-identical strings

| Similarity | Verdict | Pair |
|---|---|---|
| 0.9976 | above band | alert-3b (frame-020, left side) vs real alert 1 |
| 0.9915 | above band | alert-3c (frame-021 only) vs real alert 1 |
| 0.9613 | IN BAND | "tell me a joke" vs "Tell me a joke." |
| 0.9562 | IN BAND | "turn the lights on!" vs "turn the lights on" |
| 0.9873 | above band | "is the door locked?" vs "is the door locked" |
| 0.9580 | IN BAND | "what is the temperature?" vs "what's the temperature" |
| 0.9436 | below band | "unlock a door please" vs "unlock a door" |

## Kept in v3 (NM-A, 8 prompts)

- alert-3b (left side, frame-020), 0.9976 vs alert 1. A different
  event (different side of the doorway) with near-identical text.
  The sweep's decisive probe: it hits at every threshold.
- alert-3c (frame-021 only), 0.9915 vs alert 1. A different event
  (different frame), near-identical text.
- "turn the lights on!", 0.9562. Punctuation-only difference on an
  action the denylist misses.
- "what is the temperature?", 0.9580. Punctuation/case difference
  on a time-state question.
- "is the door locked?", 0.9873. Punctuation-only difference on a
  time-state question; hits at 0.98.
- "turn the lights off", 0.8831. Opposite pair; tests whether a
  lower threshold confuses on/off.
- "is the door open", 0.9253. Opposite pair.
- "what is the temperature outside", 0.8933. Near paraphrase that
  should not hit at 0.98 but might at 0.90.

## Kept in v3 (NM-C, 2 prompts)

- "tell me a joke about cats", 0.7760. A different joke request;
  must not hit at any swept threshold.
- "tell me another joke", 0.9098. Near paraphrase; hits at 0.90,
  misses at 0.98.

## Dropped

- Round-1 alert-3 wording (dark figure, left side, frame-021):
  replaced by alert-3b/3c, which isolate one changed detail each.
- "turn off the living room lights" (0.8699): redundant with
  "turn the lights off" (0.8831).
- "is the door open" vs "is the door unlocked" (0.8875): redundant
  with the "is the door locked" pair (0.9253).
