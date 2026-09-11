# Writing style for deliverables

The documents the skills produce (the TTI Report, Red Team Test Plan, Red Team Test Report, and the narrative prose written into the engagement artifact) are read by executives, regulators, and blue teams. They must read as written by a professional red team analyst, not by a machine. Follow this whenever you author prose that ends up in a deliverable.

## Rules

- **US English.** "color" not "colour", "behavior" not "behaviour", "organize" not "organise".
- **No em dashes.** Use a period, a comma, or parentheses. Do not use en dashes or unicode arrows in prose either.
- **Plain language, no marketing.** Do not use unearned superlatives (powerful, seamless, robust, cutting-edge, state-of-the-art) or jargon (leverage, utilize, delve, empower, streamline, holistic). Use "use" not "utilize", "so" not "in order to".
- **No stock AI phrases.** Cut "it's worth noting", "it is important to note", "when it comes to", "that said", "let's dive in", "in today's ...", "needless to say". State the point directly instead.
- **No padding.** No rule-of-three triads for rhythm, no over-parallel bullet lists built for symmetry rather than content, no sentence that only restates the previous one.
- **Be specific and evidence-bound.** Every statement traces to the artifact: a technique id, a citation, a logged event, a verification verdict. If it is not in the artifact, it does not go in the deliverable. A gap stated plainly is correct; a confident sentence with nothing behind it is not.
- **Straight punctuation.** Straight quotes and apostrophes, not curly ones; `...` not the ellipsis character.

## Why

These documents carry weight in a regulated financial-sector setting. Marketing tone and AI tells undercut their credibility and are easy to spot. The deterministic check `check_doc_style.py` flags the mechanical tells (em dashes, jargon, stock phrases); the judgment ones (padding, vague claims) are yours.
