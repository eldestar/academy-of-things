# Writing Quizzes That Teach

The quiz is not an assessment. Nobody is grading you, the score is not
reported anywhere, and you can retake it immediately. Its only job is to make
you retrieve something you just read, and then tell you why you were wrong.

That changes how the questions should be written.

## Test judgment, not recall

Compare these two questions about the same paragraph:

> What is a SAML assertion?

> A user reports their SAML login intermittently fails with an "expired
> assertion" error, even though it just happened. What is a classic root
> cause?

The first is answerable by anyone who read the sentence thirty seconds ago
and forgotten by tomorrow. The second requires knowing that assertions carry
a narrow `NotBefore`/`NotOnOrAfter` window, and that clock skew between two
systems is the usual culprit. One of those is worth a reader's time.

A useful heuristic: if the question can be answered by string-matching the
lesson text, rewrite it.

## Distractors are the hard part

The wrong options have to be plausible to someone who half-understands the
material. Three bad distractors turn a four-option question into a one-option
question.

Bad:

```
What is a SAML assertion?
  A. A REST API call requesting user data
  B. A signed XML document stating who the user is
  C. A pizza
  D. A password reset token
```

The reader picks B without thinking. Good distractors come from real
confusions: things people genuinely mix up, adjacent concepts from the same
domain, or the answer that was true in an older version of the product.

## correct_index is zero-based

```json
{
  "stem": "...",
  "options": ["first", "second", "third"],
  "correct_index": 1,
  "explanation": "..."
}
```

`correct_index: 1` is `"second"`. This is the single most common authoring
bug in this format, and it is invisible until someone takes the quiz and gets
marked wrong for the right answer. Check it.

## Explanations carry the lesson

Explanations render for every question after the reader checks their answers,
whether they got it right or not. Readers who got a question wrong read them
closely — this is the highest-attention moment in the whole course.

So never write "Correct!" or "That's right." Write the reason:

> Okta authenticates the user and issues the signed assertion vouching for
> their identity — that's the Identity Provider role.

An explanation that merely confirms the answer wastes the one moment the
reader is paying full attention.

## Set a threshold you mean

`pass_threshold_pct` defaults to 80. Pair it with a `passing_note` that does
the arithmetic out loud — "4 of 5 correct to pass" — so the reader knows the
bar before they start rather than discovering it in a failure message.

Four to six questions per lesson is the useful range. Past that, people start
pattern-matching to finish rather than thinking.
