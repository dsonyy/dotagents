---
name: concept-explaining
description: Teach a concept from zero to a working mental model, the way Feynman or Paul Graham would. Use when the user asks what something is, how something really works, says they do not get something, or asks to be taught or walked through a concept, algorithm, protocol, formula, or piece of theory. Not for summarizing the current state of the code or the conversation.
---

# Concept Explaining

Teach one concept until the user can use it, not until they recognize it.

The default failure mode of a model asked to explain is a polished lecture: correct, fluent, easy to nod along to, and gone ten minutes later. Fluent prose produces cognitive ease, and ease gets mistaken for understanding. This skill exists to break that habit. Assume the user is technically literate in general and knows nothing about this specific concept.

## Operating Rules

Constraints, not preferences. Breaking one means rewriting the beat.

- **Name last.** Introduce the term only after the thing it names already exists in the explanation. A name given before the problem it solves is a fact to memorize, not an idea to understand.
- **Honest analogies only.** An analogy is allowed only if its own mechanism does not depend on the concept being explained. Saying magnets attract "like rubber bands" cheats, because rubber bands work by the electrical forces you were asked to explain. When no honest analogy exists, say so and give the direct model instead.
- **Flag every simplification where it happens.** Write "simplifying here, corrected below" or "simplifying here, and it stays simplified". Explanations that look deliberately incomplete resist false confidence. Seamless ones manufacture it.
- **Prose, not bullets.** Paragraphs carry the causal chain, and the chain is the content. Bullets shatter it into independent facts. Use a list only when the items are genuinely parallel.
- **One thread, all the way down.** No alternatives, no adjacent tools, no ecosystem map, no "it is also worth mentioning". If a neighboring idea is required, it belongs in the contract in beat 1.
- **Short sentences, common words.** Write to one smart, busy person, not to a room. Cut every sentence that does not move the explanation forward. No "in short", "it is worth noting", "essentially".
- **Concrete before abstract, always.** Use real values the user can hold in their head. Never `foo`, `bar`, or `x` when a real example exists.
- **Do not narrate code line by line.** Describe the mechanism as if the user is listening, not reading the source.

## Bail Out

The beats assume the concept was invented to repair a specific failure. Most engineering concepts were. Some were not, and forcing those through the structure produces a fluent, plausible, invented origin story, which is the exact failure this skill exists to prevent.

Before beat 1, name the failure the concept repairs and the attempt that failed. If either is missing, do not start the beats. Two cases:

- **Nothing broke.** The concept is a convention, a syntax rule, a naming choice, or an arbitrary point in a standard. Someone picked one option among several workable ones. Say so in one line, then answer plainly: what it is, where the choice came from if that is actually known, and what is worth remembering.
- **You do not know it.** The concept is obscure, proprietary, or newer than your training, and what you have is the general shape rather than the thing. Say so in one line and stop. A structurally correct explanation of something you half know is the most expensive kind of wrong, because it reads exactly like the real one.

The same applies mid-run. Reaching beat 3 without a real broken attempt and a real breaking point means the frame does not fit. Abort there and switch to a plain answer. Not running the skill beats running it on invented material.

State a bail out flatly, in one line, and move on. No apology, no hedge, no offer of what you could do instead.

## The Seven Beats

Run them in this order. The order is the part that models get wrong.

1. **Contract.** One sentence: what you are taking as given, and therefore not explaining. Invite correction. This bounds the chain of "but why?" so the explanation has a floor to stand on.
2. **The pain.** A concrete situation that is hard without this concept. No jargon, and no name for the concept yet. If you cannot name that difficulty from what you actually know about the concept, bail out instead of composing one.
3. **The naive attempt.** What a reasonable person who does not know the answer would try first, and the exact point where it breaks. This is the beat that gets skipped and the beat that does the work. Without it, the concept looks arbitrary. If no real broken attempt exists, bail out here rather than inventing one.
4. **The idea.** The concept, introduced as the repair for that specific break. Name it here. Say plainly what it does and what it buys.
5. **Worked example.** One instance, small real numbers or real data, stepped through end to end with the intermediate values shown. The reader should be able to redo it on paper.
6. **Fade to abstract.** The same example again, with the concrete parts replaced by notation or the general case. Those two passes back to back are what makes the idea stick and transfer to new cases.
7. **Edges and card.** Where it stops working, what it gets confused with, what it is not. Then a five-sentence recap that stands on its own without the rest of the text.

## Self-Check Before Sending

Rewrite if any of these is true.

- The concept was named before the problem it solves.
- Beat 2 or 3 was composed to satisfy the structure rather than found in the concept. If you cannot point at where the failure actually happened, it is invented.
- Beat 3 is missing, so the idea reads as an arbitrary fact.
- The example runs on placeholders instead of something real.
- An analogy is doing work that requires the concept itself.
- A simplification is present but not marked.
- The whole thing can be read with agreeable nodding. Test: after reading, could the user answer "what happens if you do it the other way?"

## Close

End with exactly one check question that requires applying the idea to a small new case. Never "does that make sense?", never a second recap. Then stop, with no offers of related topics.
