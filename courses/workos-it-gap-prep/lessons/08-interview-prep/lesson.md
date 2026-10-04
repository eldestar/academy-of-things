# Interview prep for the WorkOS Systems Engineer role

You are not preparing to prove you know Okta. The posting is written so that the Okta, MDM and automation lines are your strengths, and the interview is where the other lines get tested. This lesson maps the posting to your resume without flattery, turns resume facts into story outlines you must fill in yourself, and sets the rule for what you may claim.

## The posting, as of today

Re-read live from WorkOS's public Ashby posting API on 2026-10-03: "Systems Engineer", department IT, remote for the United States and Canada, published 2026-07-23, listed at $190K to $230K with equity. Three lines matter most:

- It is "not a help desk role". An MSP partner handles tier 1; you design the systems the MSP works from, automate upstream, and are the tier 2/3 escalation point.
- Qualifications ask for 7+ years in IT systems, infrastructure or identity engineering, hands-on Terraform, and comfort with REST APIs, webhooks and authentication flows.
- The posting says AI tools may help review applications and resumes, and that humans make the final decisions.

## Requirement by requirement

| Posting line | Evidence on your resume | Rating |
| --- | --- | --- |
| 7+ years of systems, infrastructure or identity engineering | Systems-engineer titles run for roughly the last five years; before that an operations-management role with an IT roadmap, and a military communications tour | Strong on depth. Your summary says 12+ years; the Senior Operations Manager role (2013-2022) is where the counting question lands, so prepare how you count |
| Deep Okta: Workflows, integrations, policy design, SCIM | Classic-to-OIE migration, Workflows JML, FastPass enforcement, Device Trust policy, FedRAMP-aligned tenant | Strong. For Workflows depth beyond the resume, this repo's `okta-workflows` course covers error handling, tables and limits, API endpoints and governance |
| Python and Bash scripting | JML scripts, GAM, Slack API, compliance and device-config scripts | Strong |
| REST APIs, webhooks, auth flows | The words appear in your skills list; no named webhook receiver you built or verified | Thin (lesson 7) |
| Hands-on Terraform | Not mentioned anywhere | Absent |
| macOS fleet, MDM, zero-touch | Jamf Pro, Kandji Passport and Blueprints, Intune, remediation scripting | Strong |
| SAML, OAuth 2.0, SCIM, troubleshoot and architect depth | OIE migration across SAML, SCIM, OIDC, OAuth connections; AI platform with Okta SSO and SCIM attribute sync; SSO/SCIM intake assistant that files to Jira | Strong as IdP admin. Moderate on the service-provider side: the AI platform's SSO and SCIM sync is your best evidence, but the resume does not show an SP, a SCIM endpoint or a webhook receiver you built |
| Google Workspace at scale | Administration at scale, GAM automation, directory-synced tooling | Strong |
| Networking: DNS, HTTP, APIs, VPNs, firewalls | Meraki and UniFi office builds, switch and AP work, military comms; no stated DNS, VPN or firewall work | Thin (lesson 5) |
| Nice: AI/LLM for IT automation | Claude-based onboarding agent, intake assistant, internal AI platform, AI ITSM scale-out | Strong |
| Nice: GitOps or declarative device and identity management | FleetDM and Blueprints are declarative-adjacent; no Git-driven workflow stated | Absent (adjacent only) |
| Nice: GCP or AWS | Identity Center integration only | Thin |
| Nice: SOC 2 or ISO 27001 | ITGC evidence, access certifications, SoD, GRC partnership | Strong |
| Nice: MSP-augmented model | You own tier 2/3 escalation and wrote runbooks to cut tier 1; no MSP named | Thin (lesson 6) |
| Evaluate and enable SaaS, license governance | Vendor evaluation and contracts, SaaS governance tooling | Strong |
| Documentation and runbooks | Knowledge base, runbooks, SOPs and onboarding/offboarding documentation, all from the 2022-2024 role | Moderate; bring a recent example |

The shape: your Strong rows are the first half of the job, and your Absent and Thin rows cluster in the infrastructure-as-code and cloud half. Expect the interview to spend its time there.

## Story outlines (facts from your resume only)

Each outline gives the facts the resume states and what you must supply. Do not invent a number you cannot defend; "I don't have the exact figure, my estimate is X because Y" is a strong answer.

- **Classic to OIE migration.** Facts: roughly 1,300 users, SAML, SCIM, OIDC and OAuth connections across integrated platforms, no user-impacting incidents. Supply: app count, cutover sequencing, rollback plan, the thing that almost broke, what you would change.
- **FastPass, then enforcement.** Facts: about 1,800 users, 80%+ voluntary adoption before enforcing FastPass or YubiKey, no business disruption. Supply: how you measured adoption, comms plan, exception handling, ticket volume during enforcement.
- **Device Trust.** Facts: about 1,700 endpoints, managed-device and Device Assurance conditions, a CrowdStrike score threshold, unmanaged personal-device access surfaced. Supply: the threshold and why, how many unmanaged devices you found, the exception path.
- **Provisioning automation.** Facts: Okta Workflows plus Python, provisioning time cut 70%. Supply: baseline and after in real units, how measured, what happens when step four of nine fails.
- **AI agents in IT.** Facts: an Okta onboarding agent and an SSO/SCIM intake assistant that files to Jira, a stated but unquantified drop in review time. Supply: the actual time saved, guardrails, human approval points, a case where it was wrong.
- **Vendor migrations and a team.** Facts: Kandji to Jamf Pro with Intune, SentinelOne to CrowdStrike, a team of three with two hires by you. Supply: selection criteria, sequencing, what you negotiated, hiring bar.
- **Missing: a failure story.** The resume has none, and interviewers ask. Pick a real one from memory: what you decided, what went wrong, what you changed.

## Likely technical questions

> These are predictions from the posting, not reported questions.

- **Okta and SSO.** "A SAML app works for most users and fails for a few." A strong answer separates IdP configuration from SP validation: captures the actual assertion, checks audience, ACS, NameID format and attribute mapping, certificate rollover, clock skew against validity windows, SP-initiated versus IdP-initiated. "A SCIM deprovision did not take effect": checks push status, whether the SP honours `active=false` or needs DELETE, SP-side soft deletion, rate limits.
- **Endpoint.** "Design zero-touch for a remote hire." Must cover enrollment binding to identity, what is enforced before first access, disk-encryption key escrow, EDR install, the device signal fed to Okta, and failures: unassigned serials, no network at setup, expired tokens.
- **Automation.** "Design offboarding." Must cover the HR trigger, ordering (kill sessions and tokens, then deactivate; lesson 6 says what to test about that order), idempotence, dry run, audit trail, partial failure, and webhook duplicates and disorder (lesson 7).
- **Terraform.** "Okta was configured by hand; how do you bring it under Terraform?" Must cover import, plan-only first to see drift, remote state with locking, secrets in state, small blast radius, PR-reviewed plans. Say what you have done and what you have only read.
- **MSP.** "Design for an MSP doing tier 1." Must cover runbooks as executable steps, least-privilege MSP roles, what they may never do, escalation criteria, a quality feedback loop, and audit evidence of their access.
- **Security and compliance.** "Keep access reviews from becoming a quarterly scramble." Must cover system-generated populations, completeness checks on the report, reviewer sign-off, tracked remediation, SoD.
- **AI in IT.** "When is an agent safe in identity workflows?" Must cover scoped credentials, human approval on writes, ticket text as untrusted input, action logging, an evaluation set, and measured results.

## Questions to ask them

The posting names Okta, an MSP partner and Terraform, but not how they fit together. These ask for facts it leaves out:

- **Dogfooding.** "Which internal apps authenticate through WorkOS and which go through Okta directly, and who owns that boundary?"
- **MSP boundary.** "What can the MSP do today without escalating, in which systems, and who owns and updates the runbooks?"
- **Okta tenant.** "Is there one org or several, is it managed by hand or as code, and who holds super admin?"
- **Terraform maturity.** "What is in Terraform today: cloud only, or Okta and SaaS too? Where is state, and who reviews plans?"

## Honest resume framing

> Rule: never claim hands-on Terraform until you have applied a real change with `terraform plan` and `apply`, and can explain the state file you produced. A lab counts as a lab, and the resume should say so.

- Add a line **only after** the matching lab is done: Terraform with the Okta provider after the tasks in lessons 1 and 2, plan-and-apply in CI after lesson 3's task, GCP federation after lesson 4's task, webhook verification after lesson 7's task. Label them lab or personal-project scale. Never edit an experience bullet to imply you did it at work.
- Do not add MSP experience. Reframe what is true: you own tier 2/3 escalation and runbooks.
- Tighten wording you may be pressed on: your skills list says "FedRAMP" while your experience says "FedRAMP-aligned"; use the experience wording. Your skills list also names webhooks and Zero Trust networking, so expect a request to show one.

## The reported interview process

Low confidence. The posting lists no stages, and no role-specific process was found in research. WorkOS's own blog post "Inside WorkOS" (2025-10-27) says the CEO has personally met with every candidate. Second-hand summaries of candidate reviews describe a recruiter call, a manager call, a take-home, a live technical session and several final interviews, but they concern engineering roles, the source blocked automated access so it was not re-checked, and nothing confirms any of it for IT. Ask the recruiter for the stages on the first call.

Next: lessons 1-4 are where the Absent and Thin rows turn into lab evidence.
