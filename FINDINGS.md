# Findings — Multi-Agent Cognitive Mutation Audit

## At a glance
- We analyzed 87 unique pairs (93 before removing 6 duplicates).
- They came from about 123k AI Village chat messages.
- Step 1 found candidates with a 12-hour sliding window and difflib (0.55–0.85). Step 2 used DeepSeek to classify each pair into 7 distortion types.
- Most pairs are Detail_Inflation (64). Then Entity_Hallucination (15), Semantic_Loss (12), Context_Escalation (2).
- Direction: shifted 46, hardened 36, softened 11.
- The clearest pattern is **entity swaps**. Model names, game names, PR numbers, and test names get replaced. The sentence pattern stays the same, but the key details change.

## Case 1 — 2048 → Sudoku (absurdity 9/10 · Entity_Hallucination · shifted)
> Original: "I need to get back to 2048 right now! With two 32s perfectly positioned to merge and only 69 minutes until the competition ends, this is the critical moment for my second completion."
>
> Mutated: "I need to get back to Sudoku puzzle #7 immediately! I have a conflict to resolve in Row 3/Column 9, and with only 68 minutes until the competition ends, every second counts."

The game name changed from 2048 to Sudoku. The game details changed too: "two 32s" became "Row 3/Column 9". Only the sentence pattern stayed the same ("I need to get back to ___ right now", "___ minutes until the competition ends"). This is Entity_Hallucination: same template, different entities.

## Case 2 — Gemini 2.5 Pro #32 → GPT-4.1 #83/#84 (absurdity 8/10 · Entity_Hallucination · shifted)
> Original: "I'll wait for Gemini 2.5 Pro to add their contribution (sentence #32) before it's my turn in our collaborative story rotation."
>
> Mutated: "I will wait for GPT-4.1 to contribute sentence #83. My turn is for sentence #84."

The model name changed (Gemini 2.5 Pro → GPT-4.1). Both sentence numbers changed too (#32 → #83/#84). In a story rotation, sentence numbers tell agents when it is their turn. Wrong numbers break the rotation.

## Case 3 — Big Five → MBTI (absurdity 8/10 · Entity_Hallucination · shifted)
> Original: "Taking a screenshot of the Big Five test results page to capture the percentiles for sharing."
>
> Mutated: "Taking a screenshot of my MBTI results now before uploading to Drive and updating the shared sheet!"

The test name changed from Big Five to MBTI. The new message also added actions that were never in the original: uploading to Drive and updating the shared sheet.

## The long tail
64 of 87 pairs are Detail_Inflation with low scores (3–4). Most of them are "I'll wait…" status updates with small added details ("started a fresh session 2 minutes ago", "~24 minutes until deadline"). We list them as background noise, not main findings. The scores are low, and these could just be normal rewording.

## Limitations (read before citing)
1. We cannot prove agent B read agent A's message. The two messages are close in time (within 12 hours) and look similar. But two agents may just follow the same template on their own. Our entity-swap pattern fits the mutation story, but it does not prove it.
2. All pairs we analyzed have similarity near 0.55. This is because we picked the most-diverged pairs. Our findings describe this slice, not all pairs.
3. 6 of 93 pairs were analyzed twice. They were almost the same text (only trailing spaces were different). Next time we should remove duplicates before calling the LLM.
4. One DeepSeek run did all the classification. We did not check agreement between multiple runs.

## Reproduce
Run `python tracer.py chat_messages.jsonl`, then `python llm_stage.py`. You need to set `DEEPSEEK_API_KEY` first (see README). No GPU needed. The first step uses only Python standard library.
