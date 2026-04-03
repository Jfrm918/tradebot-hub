# Systeme.io + Gumroad Setup Guide

**Last Updated:** 2026-04-03  
**For:** Jason (HerHorizon + SleepShift Funnels)

---

## PART 1: SYSTEME.IO SETUP INSTRUCTIONS

### Overview
You'll create **two identical funnel structures** in Systeme.io—one for HerHorizon, one for SleepShift. Each follows the same 10-step process.

### Funnel Architecture
```
Landing Page → Email Capture → $7 Tripwire → $97/mo Core Offer → $47 Upsell → Thank You
```

---

### STEP 1: Landing Page Template Selection

**Action:**
1. Log into Systeme.io dashboard
2. Click **Funnels** → **Create New Funnel**
3. Name it: `HerHorizon - Awareness Funnel` (or `SleepShift - Awareness Funnel`)
4. Choose a **high-converting landing page template**:
   - Look for templates with: email capture field, clear CTA button, testimonial section
   - Recommended style: Clean, minimalist (healthcare/wellness positioning)

**Customize:**
- Headline: Match your funnel (e.g., "The Hormone Reset System Women Actually Use")
- Subheadline: Benefit-driven (e.g., "Feel like yourself again in just 5 days")
- Image: Use professional product/lifestyle photo
- Email capture field: Single field for email (no gatekeeping fields yet)
- CTA button: "Get Instant Access" or "Start My Reset Challenge"
- Add 2-3 bullet points (benefits, not features)

---

### STEP 2: Connect Landing Page to Email Automation

**Action:**
1. In the funnel builder, click **Settings** → **Email Provider**
2. Connect your email service:
   - If using Systeme.io's native email: **Skip to next step**
   - If using external (ConvertKit, ActiveCampaign, etc.): Authenticate and select
3. Create a **new email automation list** named:
   - `HerHorizon_Subscribers` or `SleepShift_Subscribers`
4. Set the **trigger action**: Email capture on landing page = **auto-add to list**
5. Enable **auto-responder**: First email sends immediately after signup

**First Email Trigger:**
- Subject: "Your Free [Magnet Name] is Ready — Access It Here"
- Delay: Send immediately (0 seconds)
- Content: Include download link to free lead magnet PDF (from Gumroad)

---

### STEP 3: Set Up Tripwire Checkout ($7)

**Action:**
1. In funnel builder, add **new page** after lead magnet delivery (or thank you page)
2. Page type: **Sales/Checkout Page**
3. Name: `HerHorizon_Tripwire` or `SleepShift_Tripwire`
4. Create a simple sales page:
   - Headline: "Ready to Go Deeper? Start Here"
   - Price: **$7** (displayed prominently)
   - CTA: "Unlock My 5-Day Challenge" or "Start My 3-Day Detox"
   - Include: 2-3 benefit bullets, single testimonial if available
5. **Payment Integration**:
   - Connect Stripe (see Step 9)
   - Select product type: **Digital Course/Video**
   - Upload/link video content delivery URL (from Gumroad or your hosting)

**Email Trigger:**
- Tripwire purchase → Auto-email: "Your 5-Day Challenge is Ready — Login Here"
- Include: Access link, welcome video, Day 1 instructions

---

### STEP 4: Core Offer Checkout ($97/month Recurring)

**Action:**
1. Add **new sales page** after tripwire conversion/thank you
2. Page type: **Membership/Subscription Checkout**
3. Name: `HerHorizon_Core` or `SleepShift_Core`
4. Sales page layout:
   - Headline: "Join the [HerHorizon/SleepShift] Lifestyle Program"
   - Pricing options (use table or toggle):
     - Monthly: $97/mo (recurring)
     - 3-Month Bundle: $297 (pay-once, better deal positioning)
   - Include: 5-7 key benefits (weekly coaching, community access, meal plans, etc.)
   - Add testimonials (2-3 success stories)
   - Urgency element: Limited spots, money-back guarantee
   - CTA: "Join the Program Today" or "Start My Transformation"
5. **Payment Setup**:
   - Configure as **recurring subscription** (Stripe)
   - Billing cycle: Monthly (default) or custom for 3-month
   - Include retry logic for failed payments

**Email Trigger:**
- Purchase confirmation → "Welcome to [Program Name] — Your First Week Roadmap"
- Include: Dashboard login, first training module, community invite

---

### STEP 5: Upsell Flow ($47 Upsell After Core Purchase)

**Action:**
1. In funnel settings, enable **One-Click Upsell** (Systeme.io feature)
2. Add new sales page: `HerHorizon_Upsell` or `SleepShift_Upsell`
3. Configure upsell trigger:
   - **If core offer purchased**: Show upsell page immediately (same session, no redirect needed)
   - OR create separate **Upsell Email** (sent 24 hours after core purchase)
4. Upsell sales page:
   - Headline: "Triple Your Results With [Supplement Stack/Advanced Protocol]"
   - Price: **$47** (one-time)
   - Emphasis: "Advanced layer, 10x your progress" or "The missing piece"
   - Benefits: 3-4 specific outcomes
   - CTA: "Add to My Program" or "Get the Stack"
5. **Decline path**:
   - Users who skip upsell → Thank you page (no friction)
   - No hard sell

---

### STEP 6: Thank You Page Configuration

**Action:**
1. Create **thank you page** after all purchases (both core & upsell paths lead here)
2. Content:
   - Headline: "You're In! Here's What Happens Next"
   - Checklist: 3 immediate actions (check email, join community, schedule intro call)
   - Next steps: Timeline (e.g., "Day 1: Intro video, Day 3: First group call")
   - Add: Calendar link to schedule 1:1 kickoff (if applicable)
   - CTA: "Join Our Private Community" (link to Slack/Facebook/Circle)
3. **Email follow-up**:
   - Triggered at thank you page view
   - Subject: "Your [Program] Starts Tomorrow — Here's Your Onboarding"
   - Include: Video welcome, login credentials, FAQ, support contact

---

### STEP 7: Email Sequence Setup (Map Emails to Automations)

**Action:**
1. Go to **Emails** section in Systeme.io
2. Create email sequences for each funnel:

**Sequence: HerHorizon (or SleepShift)**

| Trigger | Email | Delay | Content |
|---------|-------|-------|---------|
| Landing page signup | Welcome + Free Magnet | Immediate | Deliver PDF, set expectations |
| Email 2 | Social proof | 1 day | Success story, overcome objections |
| Email 3 | Tripwire offer | 2 days | Limited-time $7 offer, urgency |
| Tripwire purchase | Tripwire access | Immediate | Video course access, instructions |
| Email 4 | Core offer intro | 3 days post-tripwire | Case study, core program benefits |
| Email 5 | Core offer deadline | 5 days post-tripwire | FOMO, limited spots, call-to-action |
| Core purchase | Core welcome | Immediate | Dashboard access, first week guide |
| Email 6 | Upsell pitch | 2 days post-core | Social proof for supplement stack |
| Upsell purchase | Upsell delivery | Immediate | Delivery link, implementation guide |
| No action (5+ days) | Re-engagement | Day 7 | Personal outreach, demo video |

**Email Best Practices:**
- Subject lines: Curiosity + benefit (not clickbait)
- Length: 100-150 words (mobile-first)
- CTA per email: One clear button, one link
- Segmentation: Tag users by stage (see Step 8)

---

### STEP 8: Tag Subscribers by Funnel Stage

**Action:**
1. In automation settings, create **tags** for each stage:
   - `HH_LeadMagnet_Downloaded` (all landing page captures)
   - `HH_Tripwire_Purchased` (paid $7)
   - `HH_Tripwire_Did_NOT_Purchase` (skipped tripwire)
   - `HH_Core_Purchased` (active members)
   - `HH_Core_Monthly` (monthly subscribers)
   - `HH_Core_3Month` (3-month bundle buyers)
   - `HH_Upsell_Purchased` (supplement stack buyers)
   - `HH_Upsell_Declined` (skipped upsell)

2. **Auto-tagging rules**:
   - Trigger tags **automatically** at each conversion point
   - Example: When $7 charge succeeds → add `HH_Tripwire_Purchased` tag
   - Use tags to segment emails (different sequences per stage)

3. **Reporting benefit**:
   - Track conversion rates: `LeadMagnet → Tripwire → Core → Upsell`
   - Identify stalled customers (e.g., `HH_Tripwire_Did_NOT_Purchase`)

---

### STEP 9: Connect to Payment Processor (Stripe)

**Action:**
1. Go to **Settings** → **Payment Methods**
2. Click **Connect Stripe**
3. Authenticate with your Stripe account
4. Choose: **Live mode** (production payments) or **Test mode** (do NOT use in production)
5. Configure payment settings:
   - Currency: USD
   - Tax handling: Enable if applicable (varies by location)
   - Recurring billing: Enable for $97/mo core offer
   - Decline email: Set auto-email for failed payments (optional)

**Stripe Setup (if new):**
- Stripe account: https://dashboard.stripe.com (create if needed)
- Verify bank account for payouts
- Test mode: Use card `4242 4242 4242 4242` for testing
- Live mode: Only activate after testing complete

**Product Mapping in Stripe:**
- Create products in Stripe matching Systeme.io prices:
  - `HerHorizon Tripwire ($7)` — One-time charge
  - `HerHorizon Core ($97)` — Monthly recurring
  - `HerHorizon Core Bundle ($297)` — One-time
  - `HerHorizon Upsell ($47)` — One-time charge
  - *(Repeat for SleepShift)*

---

### STEP 10: Test Entire Flow End-to-End

**Action:**

#### Test Mode Setup
1. In Systeme.io: Settings → **Test Mode** (ON)
2. In Stripe: Use test card `4242 4242 4242 4242`
3. Expiry: Any future date (e.g., 12/27)
4. CVC: Any 3 digits

#### Run Full Test Path
1. **Test as new user:**
   - Visit landing page URL
   - Enter test email (e.g., `test1@example.com`)
   - Verify: Email arrives with magnet download link
   - Download PDF successfully
2. **Test tripwire flow:**
   - Click tripwire CTA from email
   - Proceed to $7 checkout
   - Enter test card → Complete purchase
   - Verify: Tripwire access email arrives within 2 min
   - Access video course (if stored on Gumroad, test the link works)
3. **Test core offer:**
   - From tripwire thank you page, click core offer CTA
   - Choose pricing option (monthly or 3-month)
   - Complete $97 (or $297) charge with test card
   - Verify: Core welcome email with dashboard link
   - Log in to dashboard with test credentials
4. **Test upsell:**
   - From core thank you page, see upsell offer
   - Click "Add to My Program"
   - Confirm $47 charge
   - Verify: Upsell delivery email
5. **Test decline path:**
   - Repeat but skip upsell CTA
   - Verify: Thank you page displays (no error)
   - No upsell delivery email sent
6. **Verify email sequence:**
   - Check all follow-up emails arrive in sequence
   - Verify: All CTA links are live and working
   - Check: Tags applied correctly (check Systeme.io or email provider)

#### Check Points
- [ ] Lead magnet PDF downloads work
- [ ] All emails arrive within expected time
- [ ] Payment success messages display
- [ ] Checkout doesn't double-charge
- [ ] Failed payment emails trigger correctly (test by declining card `4000 0000 0000 0002`)
- [ ] Recurring billing shows on Stripe dashboard (monthly charge)
- [ ] Tags applied to test subscribers
- [ ] Upsell page appears only for core buyers
- [ ] Decline path doesn't trigger upsell emails

#### Launch Checklist
- [ ] Switch Systeme.io from **Test Mode → Live Mode**
- [ ] Confirm Stripe is in **Live mode** (real payments)
- [ ] Double-check all email copy for typos
- [ ] Verify: Lead magnet, tripwire course, core training, upsell PDF are live
- [ ] Test once more with real email (not test email)
- [ ] Set funnel URL as primary link (or use landing page direct URL)
- [ ] Notify Jason: "Funnel is live and ready for traffic"

---

---

## PART 2: GUMROAD PRODUCT DESCRIPTIONS

### Overview
You'll create **8 products total**: 4 per funnel (HerHorizon + SleepShift).  
Each product has: **Title**, **50-word benefit-focused description**, **What Buyer Gets** (deliverables), **Pricing Explanation**.

**Store URL Format:** `gumroad.com/[yourname]/l/[product-slug]`

---

## HERHORIZON FUNNEL (4 Products)

### Product 1: Lead Magnet (Free)

**Title:**  
The Perimenopause Survival Guide — What Your Doctor Isn't Telling You

**50-Word Description (Benefit-Focused):**  
Stop guessing about your hormones. This no-fluff guide reveals exactly what's happening in your body during perimenopause, why your doctor missed it, and the three immediate lifestyle shifts that calm hot flashes, mood swings, and brain fog—before you spend money on anything else.

**What Buyer Gets:**
- 28-page PDF guidebook (formatted, printable)
- Hormone timeline chart (understand your cycle)
- 3 quick-start protocols (immediate relief)
- Symptom tracker worksheet
- Bonus: 5-min daily routine (do at home, no equipment)

**Pricing Explanation:**
Free lead magnet. Purpose: Build email list, establish trust, pre-sell into tripwire.  
*Monetization:* This converts cold traffic into qualified leads; $7 tripwire converts 15-25% of readers.

---

### Product 2: Tripwire ($7)

**Title:**  
5-Day Hormone Reset Challenge — Video Course

**50-Word Description (Benefit-Focused):**  
Five days. Five videos. One transformation. This micro-course walks you through the exact daily practices that rebalance cortisol, serotonin, and estrogen without supplements or doctors. Women report sleeping better, clearer heads, and stable moods by Day 3. It's a proof-of-concept for what's possible in the core program.

**What Buyer Gets:**
- 5 daily video lessons (8-12 min each, downloadable)
- Printable daily action sheet (one per day)
- Private community access (72 hours)
- Email support during challenge (1 question per day)
- Bonus: "After the Challenge" email sequence (3 emails mapping next steps)

**Pricing Explanation:**
$7 entry point. Low friction, high perceived value. Goal: 15-25% of leads → $97/mo core offer.  
*Psychology:* $7 feels like "let me try it," not "let me commit." Builds social proof + confidence for core upsell.

---

### Product 3: Core Offer ($97/month or $297/3-month)

**Title:**  
HerHorizon Lifestyle Program — The Complete Hormone Mastery System

**50-Word Description (Benefit-Focused):**  
The all-in-one program: weekly 1-on-1 coach calls, daily live group sessions, meal plans built for your cycle, supplement protocols, and our private community of 500+ women. Members report feeling like themselves again in 4-6 weeks. Recurring access means you're never stuck figuring it out alone again.

**What Buyer Gets:**

**Core Training:**
- 12-week progressive video course (hormones, nutrition, movement, sleep, stress)
- Printable workbooks per module (goals, tracking, meal plans)
- Weekly group coaching calls (Zoom, live Q&A, recorded for async viewing)
- Monthly 1-on-1 strategy call (30 min, schedule anytime)
- Private Slack community (500+ members, peer support 24/7)

**Recurring Access:**
- New module released every 2 weeks
- Monthly live challenge (focus area varies)
- Exclusive podcast: "Ask a Hormone Specialist" (bi-weekly)
- Supplement vendor discount codes (30-50% off)
- Email support: 48-hour response time

**Deliverables Format:**
- Videos: On-demand (streaming + downloadable MP4)
- Docs: Printable PDFs (meal plans, protocols, trackers)
- Calls: Zoom links emailed 24 hours prior
- Community: Private Slack workspace

**Pricing Explanation:**
$97/month or $297 for 3 months (saves $194 vs. monthly).  
*Strategy:* Monthly removes commitment friction; 3-month bundle creates urgency + better unit economics.  
*Goal:* 80%+ conversion from $7 tripwire. Recurring revenue supports ongoing support.

---

### Product 4: Upsell ($47, One-Time)

**Title:**  
Supplement Stack Protocol Guide — The Complete Hormone Optimization Stack

**50-Word Description (Benefit-Focused):**  
You can feel 80% better with lifestyle alone. This advanced guide is the final 20%: the exact supplement stack that closes hormone gaps, the labs to order before you buy anything, timing strategies for max absorption, and brand recommendations (and what to avoid). Used by 90% of program members. This is premium health optimization.

**What Buyer Gets:**
- 32-page protocol PDF (download instantly)
- Supplement sourcing guide (best brands, price benchmarks)
- Lab test recommendations (which tests to order, where to order)
- Absorption timing chart (when to take what, with/without food)
- 3 customizable stacks (light, standard, advanced levels)
- Bonus video: "Read Your Bloodwork" (15 min, demystified)
- Bonus: Quarterly protocol updates (included for 1 year)

**Pricing Explanation:**
$47 one-time. Upsell trigger: After core purchase (high intent).  
*Positioning:* "The missing layer" — supplements alone don't work; lifestyle first, this as the accelerant.  
*Goal:* 10-15% upsell rate from core buyers. Low commitment, high perceived value.

---

## SLEEPSHIFT FUNNEL (4 Products)

### Product 1: Lead Magnet (Free)

**Title:**  
The 7-Night Sleep Reset — Fall Asleep In Under 20 Minutes

**50-Word Description (Benefit-Focused):**  
Insomnia isn't your fault—your nervous system just forgot how to shut down. This 7-night PDF guide shows you the exact order of practices (breathing, light, temperature, sound) that reset your sleep architecture without melatonin or prescriptions. Most people see results by Night 3. No equipment. No cost.

**What Buyer Gets:**
- 22-page PDF guidebook (printable, mobile-friendly)
- 7-night nightly checklist (one page per night)
- Pre-sleep breathing technique video (5 min)
- Sleep environment audit worksheet (optimize your bedroom)
- Bonus: "Sleep Myths Debunked" infographic (common mistakes explained)
- Bonus: Circadian rhythm tracker template (understand your natural timing)

**Pricing Explanation:**
Free lead magnet. Purpose: Prove the system works fast, build trust, qualify leads.  
*Conversion metric:* Expect 18-22% of leads → $7 tripwire (proof builds confidence).

---

### Product 2: Tripwire ($7)

**Title:**  
3-Day Sleep Detox — Video Course

**50-Word Description (Benefit-Focused):**  
Three days of guided sleep restoration. Watch three short videos, follow the exact nightly protocol, and reset your sleep cycle. No more lying awake. By Day 2, most people report falling asleep naturally. By Day 3, sleeping deeper. It's a guaranteed preview of what the full program can do—or your money back.

**What Buyer Gets:**
- 3 daily video lessons (10-15 min each, downloadable)
- Printable night-by-night action sheet
- Private Slack group access (72 hours, active community)
- Daily email check-in (AM: reflection, PM: prep for night)
- Bonus: "Sleep Food & Timing" quick guide (1 page, actionable)
- Money-back guarantee: If you don't sleep better by Day 3, full refund (no questions)

**Pricing Explanation:**
$7 entry point. Low-risk trial for cold traffic.  
*Psychology:* Money-back guarantee removes objection; most people don't refund once they see results.  
*Goal:* Convert 20-25% → $97/mo core offer.

---

### Product 3: Core Offer ($97/month or $297/3-month)

**Title:**  
SleepShift Coaching Program — The Complete Sleep Mastery System

**50-Word Description (Benefit-Focused):**  
The comprehensive 12-week program: video training (sleep science, environment optimization, nutrition timing), weekly group coaching, personalized sleep protocol design, and our community of 400+ people beating insomnia together. Members average 7-8 hours of deep sleep within 4 weeks. Sleep better, feel unstoppable. Recurring access, forever support.

**What Buyer Gets:**

**Core Training:**
- 12-week progressive video curriculum (sleep science, nervous system reset, chronotype optimization, travel sleep, aging sleep)
- Printable workbooks: Sleep audit, environment design, supplement timing, stress protocols
- Weekly group coaching calls (live Zoom, recorded for on-demand)
- Bi-weekly 1-on-1 sleep consultations (15 min each, personalized protocol design)
- Private community (400+ members, 24/7 peer support)

**Ongoing Support (Recurring):**
- New module every 2 weeks (advanced topics, seasonal adjustments)
- Monthly live challenge: "Sleep Tracking Week" or "Blue Light Reset"
- Bi-weekly podcast: "Ask the Sleep Coach" (member questions answered)
- Exclusive vendor partnerships (sleep tech discounts: 30-50% off pillows, blue-light glasses, white noise machines)
- Sleep tracking integration guide (Oura Ring, Fitbit, Apple Watch analysis)
- Email support: 24-hour response

**Deliverables Format:**
- Videos: Streaming + MP4 download
- Docs: Printable workbooks, checklists, trackers
- Calls: Zoom, calendar links sent 48 hours prior
- Community: Private Slack workspace + daily digest email

**Pricing Explanation:**
$97/month or $297 for 3 months (saves $194).  
*Strategy:* Monthly removes barrier; 3-month incentivizes commitment.  
*Goal:* 80%+ tripwire→core conversion. Recurring revenue funds 1-on-1 support.

---

### Product 4: Upsell ($47, One-Time)

**Title:**  
Sleep Supplement Stack Protocol — The Advanced Sleep Optimization Guide

**50-Word Description (Benefit-Focused):**  
Lifestyle alone gives you 80% of the results. This advanced guide is the final 20%: the exact supplement stack (magnesium types, timing, quality brands), lab tests that reveal why you can't sleep, meal timing for melatonin production, and advanced hacks (light therapy timing, temperature variation). For sleep optimization beyond good sleep—for elite recovery.

**What Buyer Gets:**
- 28-page protocol PDF (instant download)
- 3 supplement stacks: Foundation (budget), Standard, Advanced (premium)
- Brand recommendations + sourcing guide (vetted vendors only)
- Lab test checklist (which tests reveal sleep barriers: cortisol, iron, thyroid, etc.)
- Timing protocol (what to take when, food interactions, half-lives)
- Bonus video: "Read Your Sleep Labs" (17 min, demystified interpretation)
- Bonus: Quarterly protocol updates (1-year included)
- Bonus: "Sleep Tech Buyer's Guide" (Oura, WHOOP, Fitbit analysis)

**Pricing Explanation:**
$47 one-time. Upsell trigger: Shown after core purchase.  
*Positioning:* "The missing catalyst" — for members who want next-level sleep architecture optimization.  
*Goal:* 10-15% upsell conversion from core buyers.

---

---

## SUMMARY: CONVERSION TARGETS

### Funnel Economics (Per 100 Landing Page Visitors)

| Stage | HerHorizon | SleepShift |
|-------|-----------|-----------|
| **Landing Page** | 100 | 100 |
| **Lead Magnet** | 25-30 | 25-30 |
| **Tripwire ($7)** | 3-5 ($21-35 revenue) | 3-5 ($21-35 revenue) |
| **Core ($97/mo)** | 2-4 ($194-388 revenue) | 2-4 ($194-388 revenue) |
| **Upsell ($47)** | 0.3-0.5 ($14-24 revenue) | 0.3-0.5 ($14-24 revenue) |
| **Total Revenue (Per 100)** | ~$230-450 | ~$230-450 |

**Key Metrics:**
- Lead magnet → Tripwire: 12-17% conversion
- Tripwire → Core: 40-50% conversion
- Core → Upsell: 10-15% conversion
- **Overall funnel (visitor → paying member): 2-4%**

---

## NEXT STEPS FOR JASON

1. **Systeme.io Setup**: Follow Steps 1-10 above (duplicate for both funnels)
2. **Create Gumroad Products**: Copy descriptions above, upload files/videos
3. **Connect Stripe**: Ensure live account, test mode first
4. **Email Sequences**: Map the email sequence table from Step 7
5. **Test Everything**: Run full end-to-end test (Step 10) before launching
6. **Launch**: Flip to live mode, start driving traffic

---

**Questions?** Ask in Slack. This doc stays updated.

---

*Generated: 2026-04-03 | Subagent Task Complete*
