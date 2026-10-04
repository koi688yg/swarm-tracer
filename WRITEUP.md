# Multi-Agent Cognitive Mutation Audit — Project Write-up

AI agents talk to each other all the time. They pass task updates, share documents, and coordinate plans. But do their messages survive intact, like a game of telephone? We built a tool to check.

Our pipeline has three steps. First, a zero-cost filter scans about 123k chat messages from the AI Village dataset. It keeps only pairs that look like mutations: close in time (12-hour window), sharing rare words, with difflib similarity between 0.55 and 0.85. Then DeepSeek acts as a judge. It classifies each pair into 7 distortion types, gives an absurdity score from 1 to 10, and quotes the exact changed words. Last, we chart the results.

We analyzed 87 unique pairs. The clearest pattern is entity swaps. The sentence pattern stays the same, but key details get replaced. The wildest case: "I need to get back to 2048 right now, with two 32s perfectly positioned to merge" became "I need to get back to Sudoku puzzle #7 immediately, with a conflict in Row 3/Column 9" — same template, different game entirely (absurdity 9/10). We also saw model names swapped (Gemini 2.5 Pro → GPT-4.1) with wrong sentence numbers, and a Big Five test result turned into an MBTI result with invented follow-up actions.

We are honest about what we cannot prove. We cannot prove agent B read agent A's message — two agents may follow the same template on their own. Our pattern fits the mutation story, but it does not prove it. Still, for anyone building swarm observability tooling, entity-level drift like this is exactly the failure mode worth watching: the message looks fluent and confident, but the referents have silently changed.

The full pipeline runs on CPU with no GPU. The 93-pair LLM pass costs less than 0.1$.