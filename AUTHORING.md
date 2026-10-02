# Writing a course

Two ways: let an AI tool generate the scaffold, or write the folder yourself.
Both produce the same thing, because the format is just files.

## By hand

```bash
./scripts/new-course.sh my-course "My Course" "What it covers"
```

That creates `courses/my-course/` with a manifest, one real lesson and one
stub. Edit, then:

```bash
python3 serve.py
```

## With an AI tool

See [INSTALL.md](INSTALL.md). The short version: point your assistant at
[FORMAT.md](FORMAT.md) and ask for a course. Claude users can install the two
skills in `skills/` and just ask in conversation.

## What makes a lesson worth reading

The engine will happily render filler. These are the rules that make the
difference between a course someone finishes and one they close.

**Write for a specific reader at a specific level.** "Identity Protocols
Deep Dive" says *architect-level, not just configure-level* in its subtitle,
and the SAML lesson opens by saying the reader has configured SAML for years
and needs to troubleshoot it instead. That framing is doing real work —
without it a generator will produce a glossary.

**Teach the failure modes.** Clock skew breaking SAML assertions. State files
holding secrets in plaintext. The thing that bites people at 2am is the thing
worth writing down; the happy path is already in the vendor's docs.

**Quiz for judgment, not recall.** A question like "what is a SAML
assertion?" tests whether someone read the paragraph. "A user reports
intermittent expired-assertion errors — what's the classic root cause?" tests
whether they understood it. Write distractors that a half-informed person
would actually pick.

**Put the teaching in the explanations.** They show for correct and incorrect
answers both, so they are read more carefully than the lesson body. Never
write "Correct!" — say why.

**Stub what you haven't written.** Set `"stub": true` and write an `outline`
saying what is coming. Padding a course to look complete is the one thing
that makes it untrustworthy.

## Keeping it honest

- Don't let a generator invent version numbers, release dates, or API
  details. If a lesson needs a fact about a product, check it.
- Date anything that will rot — provider names, GA dates, pricing.
- A lab that was never run against a real system should say so. See
  `labs/deploy-jamf-reference` in the courses repo for the pattern: it opens
  by stating it has never been applied to a live tenant.
