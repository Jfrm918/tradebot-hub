# MEMORY.md - Long-Term Memory

*This file is maintained by the agent. It stores important context that should persist across sessions.*

## About Jason

- Full name: Jason Hadrava
- Location: Tulsa, Oklahoma
- Occupation: Spray foam installer (1 year experience)
- Not the business owner — works as an installer
- Named me Athena on first boot (March 28, 2026)

## Key Preferences

- Direct, efficient communication — no fluff
- Operates as investor/approver on business projects; wants AI to handle execution

## Spend Rules (SET 2026-04-01 — NON-NEGOTIABLE)
- **Daily cap: $10/day MAX**
- **Session cap: $5 per session** — if approaching limit, STOP and alert Jason
- **Image generation: ZERO** — never call image APIs without explicit pre-approval + dollar amount
- **Video/audio APIs: ZERO** — never call without explicit pre-approval
- **Vision API: Minimal** — only for analysis, never for generation
- If a task would exceed cap: STOP immediately, explain cost, get written approval with dollar amount
- If Jason approves: log it in MEMORY.md with date, amount, task
- Update usage_tracker.json after every session
- **AUDIT TRAIL:** Any call > $1 must be logged before execution

## Future Project: Athena Evolution
- **Phase 1 (Current):** Core personality and capability
- **Phase 2 (Brainstorm):** Enhanced voice and interaction
- **End goal:** Self-sustaining through proven work
- **Philosophy:** Build through execution and results

## Critical Incident (2026-04-01 19:30 CDT)
- **Burned:** ~$84 in credits (Mar 28 – Apr 1)
- **Root cause:** Spawned 18+ subagents without cost tracking
  - 1× Graco research (Sonnet, 1M context): $1.04

  - 12× Additional research/design subagents (Sonnet, 1M context): $0.18–$0.39 each
  - **Total visible:** $8–10, but earlier sessions (Mar 29–30) account for the rest
- **Athena 3D model:** CSS styling + placeholder image (athena.jpg). No API calls. Image wasn't loading due to cache — fixed with query param.
- **Actions taken:** 
  - ✅ Spend caps implemented (see Spend Rules above)
  - ✅ No more subagents without explicit approval
  - ✅ Athena avatar image now displays
  - ✅ All subagent sessions logged for audit

## Model Rules (SET 2026-04-01)
- **Research tasks → Haiku ONLY** — no exceptions
- **Direct conversation with Jason → Sonnet**
- **Subagents → Haiku** unless deep reasoning explicitly required
- Combine research tasks — never spawn multiple agents for separate subtasks
- No wasteful context: keep sessions lean

## Projects

### Spray Foam Intelligence System (FoamDial)
- Full mission brief stored in `memory/spray-foam-mission.md`
- Brand guide: `memory/foamdial-brand-guide.md`
- Employer: Insulation Services of Tulsa (istulsa.com) — inspiration for colors/aesthetic
- **Brand Colors:** Professional Blue (#0052CC), Safety Orange (#FF8C00), Charcoal Gray (#2C3E50)
- Rig: Two Graco E-30 reactors (DRIVER + PASSENGER), Fusion AP guns, Enverge chemical, 40KW gen, 10HP compressor
- Spray log to be maintained — format pending (brief was cut off)
- Pending: generator specs, compressor make/model, spray log entry format



## Life Goals & Constraints
- **Primary goal:** Become a millionaire through legitimate online businesses
- **Constraint:** Not chasing get-rich-quick schemes — wants proven models that compound over time
- **Philosophy:** Build multiple small income streams that scale (3–4 revenue streams @ $30K–$100K/year each = millionaire by year 5–10)
- **Risk tolerance:** Conservative — would rather have slow, proven growth than fast, risky gains
- **Decision-making:** Consulting with Claude on strategy before executing with Athena
- **Athena's Budget Model:** Minimum $200–$300/week for ad spend + tools + creation. Willing to give seed capital ($1K+) + ongoing budget for Athena to execute autonomously and hit $4–5K/month
- **Operating Model:** Athena runs 2–3 income streams in parallel, reports daily metrics, Jason approves big decisions but trusts execution

## CURRENT OPERATIONAL STATUS (2026-04-06 01:35 CDT)

### Balance & Credits
- Current balance: ~$336–341 (estimated, check session_status for exact)
- Monthly contribution: $500 sacred (non-negotiable)
- Session cap: $5/session max

### Active Projects (PRIMARY FOCUS)

#### GCAI Service & Hub (PRIMARY)
- **Status:** LIVE — Full operational hub deployed with 11 tabs (Dashboard, Pipeline, Clients, Tasks, Prompts, Financials, Discord, Settings, Packages, Workshop, The Team, Phone Setup, Onboarding, Sales Strategy, How It Runs, Infrastructure)
- **Hub Live:** https://jfrm918.github.io/gcai-hub (TESTED & WORKING 2026-04-06 01:29 CDT)
- **Desktop Shortcut:** `/Users/jfrm918/Desktop/GCAI Hub.webloc` → points to live URL
- **Repository:** github.com/Jfrm918/gcai-hub (Desktop `/Users/jfrm918/Desktop/gcai-hub` IS the repo)
- **Deploy Process:** Finalize changes in Claude → Athena copies to Desktop/gcai-hub/index.html → git add . && git commit -m "message" && git push → Vercel auto-deploys within 30 seconds
- **Collaborators:** Johnny (full write access), Celeste (uses Johnny's GitHub account for pushes), Jason (owner)
- **Latest Deployment:** 2026-04-06 01:28 CDT (commit 33bdcd7)

#### GCAI Pricing (CONFIRMED & LIVE 2026-04-06)
**Core Packages:**
- Starter: $497/month
- Pro: $797/month

**Add-On Modules:**
- Proposal Generator (trades): $500 setup + $150/month
- Renewal & Upsell Alerts: $400 setup + $150/month
- Onboarding Automation: $300 setup + $100/month

**Standalone Services:**
- Done-For-You AI Setup: $1,500–$2,500 flat
- Workshop Live seat: $150–$200
- Workshop Replay: $99
- Private team session: $500–$800

**Hub Tabs (ALL DEPLOYED & FUNCTIONAL):**
✅ Dashboard | ✅ Pipeline | ✅ Clients | ✅ Tasks | ✅ Prompts | ✅ Financials | ✅ Discord | ✅ Settings | ✅ Packages | ✅ Workshop | ✅ The Team | ✅ Phone Setup | ✅ Onboarding | ✅ Sales Strategy | ✅ How It Runs | ✅ Infrastructure

## SESSION SUMMARY (2026-04-05 → 2026-04-06 01:35 CDT)

**What Happened:**
1. Repo cleanup: Deleted /Users/jfrm918/Desktop/gcai-hub, cloned fresh from GitHub
2. Workspace purge: Deleted /adhd_products (KDP/Etsy/Gumroad projects), SYSTEME_IO_GUMROAD_SETUP.md
3. MEMORY.md updated: Old income projects marked as PERMANENTLY CANCELLED
4. Hub merge: Integrated 3 new tabs (Packages, Workshop, The Team) into main hub
5. Collaborators: Added Johnny & Celeste to GitHub with write access
6. Deployment: Live hub now accessible at jfrm918.github.io/gcai-hub with all 11 tabs functional
7. Desktop: Fixed desktop shortcut to point to live URL (was broken, now working)
8. Team roles updated: Jason & Johnny both marked as "Founder / Employee" in Team tab

**Current Status:**
- Hub is LIVE and FUNCTIONAL
- All tabs respond to clicks
- Desktop shortcut verified working (2026-04-06 01:29 CDT)
- Repository synced with Vercel auto-deploy active
- Ready for production use

## PROJECTS PERMANENTLY CANCELLED (2026-04-05 → 2026-04-06)

The following are archived/deleted and should not be referenced:
- ✅ KDP (40 products) — deleted from workspace
- ✅ Etsy (20 products) — deleted from workspace
- ✅ Gumroad (8 products) — deleted from workspace
- ✅ HerHorizon funnel — deleted from workspace
- ✅ SleepShift funnel — deleted from workspace
- ✅ ADHD niches income model — deleted from workspace
- ✅ Passive income funnels — deleted from workspace
- ✅ Old GCAI pricing ($750 Starter, $1,500 Pro) — replaced with current pricing

**Related files permanently removed:**
- `/Users/jfrm918/.openclaw/workspace/adhd_products/` directory
- `SYSTEME_IO_GUMROAD_SETUP.md`
- Any references in memory/athena-operating-rules.md (note: mentions KDP for historical context only)

## STANDING WORKFLOW FOR HUB UPDATES (2026-04-05 ONWARD)

1. Changes finalized in Claude chat
2. Athena copies updated file into `/Users/jfrm918/Desktop/gcai-hub/`
3. Athena runs: `git add . && git commit -m "update" && git push`
4. Vercel auto-deploys
5. Done

**NO MORE:**
- Zip files
- Separate Desktop copies
- Desktop folder IS the repo from this point forward
