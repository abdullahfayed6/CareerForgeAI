from __future__ import annotations

import hashlib


def _pick(options: list[str], seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(options)
    return options[index]


def generate_task_simulation(company_name: str, task_title: str) -> str:
    overview = _pick(
        [
            "Mid-sized product company with a mix of legacy systems and newer services.",
            "Series B startup scaling fast and shipping weekly with a lean ops team.",
            "Established enterprise vendor with compliance-heavy customers and slow release cycles.",
        ],
        f"overview:{company_name}:{task_title}",
    )
    users = _pick(
        [
            "Customers, internal analytics teams, and a small partner ecosystem.",
            "Enterprise buyers, account managers, and support teams who rely on dashboards.",
            "Internal ops, QA auditors, and external clients with strict SLAs.",
        ],
        f"users:{company_name}:{task_title}",
    )
    problem = _pick(
        [
            "Key workflow is noisy, inconsistent, and slowing down delivery timelines.",
            "Growth metrics stalled after a recent product change and leadership wants answers.",
            "Manual processes are leading to errors and increased support costs.",
        ],
        f"problem:{company_name}:{task_title}",
    )
    trigger = _pick(
        [
            "Spike in customer complaints during the last release cycle.",
            "Leadership noticed a week-over-week drop in a core KPI.",
            "A new partner integration created unexpected operational risk.",
        ],
        f"trigger:{company_name}:{task_title}",
    )
    constraints = _pick(
        [
            "Legacy schemas, partial data coverage, and only one sprint to deliver a demo.",
            "Limited observability, a backlog of tech debt, and compliance review gates.",
            "Short timeline, minimal QA capacity, and a fragile deployment pipeline.",
        ],
        f"constraints:{company_name}:{task_title}",
    )
    role_title = _pick(
        [
            "Backend Engineer",
            "Data Engineer",
            "ML Engineer",
            "Platform Engineer",
        ],
        f"role:{company_name}:{task_title}",
    )
    out_of_scope = _pick(
        [
            "Redesigning the core product UI or rewriting the entire data pipeline.",
            "Changing upstream data contracts owned by other teams.",
            "Full enterprise-scale rollout beyond the pilot cohort.",
        ],
        f"out-of-scope:{company_name}:{task_title}",
    )
    data_issues = _pick(
        [
            "Input data is delayed by hours, missing fields, and inconsistent across regions.",
            "Event tracking has gaps due to ad-blockers and inconsistent client versions.",
            "Historical data is sparse and stored in multiple formats with unclear ownership.",
        ],
        f"data:{company_name}:{task_title}",
    )

    return f"""
==========================================
TASK SIMULATION: {task_title} @ {company_name}
==========================================

1. COMPANY CONTEXT (REALISTIC BUSINESS SETUP)
- Company overview:
  {company_name} is a {overview}
- Users:
  {users}
- Business problem:
  {problem}
- Why this matters:
  The issue is already impacting revenue and renewal conversations, and it is eroding trust with key stakeholders.

2. TASK ORIGIN (HOW THIS ARRIVED AT YOUR DESK)
- Requested by:
  The PM for the core product area, with a strong nudge from the Head of Operations.
- Trigger event:
  {trigger}
- Requirement quality:
  Requirements are incomplete and shifting; the PM has only high-level goals and expects you to fill in the technical details.
- Constraints:
  {constraints}

3. YOUR ROLE IN THE COMPANY
- Job title:
  {role_title}
- What YOU are responsible for:
  Building the MVP implementation, documenting assumptions, and proposing a safe rollout plan.
- What you are NOT responsible for:
  {out_of_scope}
- Who you work with:
  PMs, a senior engineer for review, an ops stakeholder, and a QA partner who is only available part-time.

4. ACTUAL TECHNICAL TASK (REAL WORK VERSION)
Describe what needs to be built or improved:
- High-level system workflow
  - Intake inputs, normalize the key fields, run validation, and generate a structured task simulation output.
- Data inputs and sources (including data quality issues)
  - Inputs are company_name and task_title from an internal tool.
  - {data_issues}
- Expected outputs
  - A single structured task simulation document that follows the required format exactly.
- Edge cases and failure scenarios
  - Empty or overly generic task titles, conflicting company context, or missing input values.
- Performance or scale considerations
  - Must respond within 2 seconds for a single request; batch processing can be deferred.
- Integrations with existing systems or APIs
  - Integrates with the internal education platform and stores outputs for later review.
- Security, reliability, and logging concerns
  - Log request metadata only, avoid storing sensitive customer identifiers, and provide clear error messages.
- Deployment expectations (CI/CD, monitoring, rollback)
  - Ship behind a feature flag, add basic request logging, and ensure rollback is possible with a config toggle.

5. NON-TECHNICAL REALITIES (THIS IS REAL LIFE)
Explicitly describe:
- Ambiguities in the task
  - The PM wants "realistic" output but hasn't defined what quality means beyond a few examples.
- Trade-offs that must be made
  - Template-based output is faster but less flexible than a fully dynamic system.
- Decisions required with incomplete information
  - You need to decide how much randomness to allow and how to validate realism.
- Communication challenges
  - Stakeholders expect progress updates daily, but requirements are still evolving.
- Business pressure vs technical correctness
  - Leadership wants a demo next sprint even if edge cases aren't fully handled.

6. HOW A STUDENT TYPICALLY THINKS (ACADEMIC MODE)
Describe how a student might incorrectly approach this:
- Focus on algorithms only
- Ignore data issues
- Assume perfect requirements
- Over-engineer or under-scope

7. HOW A REAL ENGINEER APPROACHES IT
Describe a professional mindset:
- Breaks the problem into deliverable phases
- Reduces risk early
- Communicates assumptions clearly
- Chooses pragmatic solutions
- Plans for iteration, not perfection

8. SKILLS THIS TASK IS DESIGNED TO TRAIN
Explicitly list:
- Technical skills
  - API design, templating, input validation, logging
- System design thinking
  - Defining workflows, handling edge cases, scaling for future requests
- Decision-making under constraints
  - MVP scope, time-boxed delivery, quality vs speed
- Communication and collaboration
  - Clarifying requirements, setting expectations, documenting assumptions
- Handling unclear or changing requirements
  - Iterative refinement and stakeholder alignment

9. FINAL CHALLENGE TO THE STUDENT
"You have 7 days before a sprint demo.
Explain your approach, justify your technical decisions,
identify risks, and define what success looks like."

==========================================
GOAL OF THIS TASK SIMULATOR
==========================================
- Simulate real company work
- Bridge the gap between academic learning and industry reality
- Train engineers to think, communicate, and decide like professionals
- Show that real work is messy, constrained, and collaborative
==========================================

--------------------------------------------------
IMPORTANT MVP & DUMMY DATA NOTE
--------------------------------------------------
This task is intended for an MVP implementation.

You MUST:
- Assume no access to real production data
- Generate realistic DUMMY / SYNTHETIC DATA
- Clearly state assumptions about the data
- Keep scope MVP-sized (demo-ready, not enterprise-scale)
- Prefer simple, explainable solutions over complex ones

The focus is on:
- Correct thinking
- Clean structure
- Realistic trade-offs
- Ability to explain decisions

NOT on:
- Perfect accuracy
- Full production readiness
- Advanced optimization
""".strip()
