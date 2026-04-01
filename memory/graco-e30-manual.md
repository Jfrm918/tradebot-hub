# Graco Reactor² E-30 — Complete FoamDial Knowledge Base
*Compiled from official Graco manuals: 333023EN, 333023F, 312066F*

---

## MACHINE IDENTITY
- **Full Name:** Graco Reactor® 2 E-30 Plural Component Proportioner
- **Type:** Electric, Heated, Plural Component Proportioner
- **Purpose:** Spraying polyurethane foam and polyurea coatings
- **Manual:** 333023EN (current)

---

## SPECS

### Pressure
- **Max working pressure:** 3,500 psi (field operations: 800–1,200 psi typical for SPF)
- **Pressure control:** Electronic (single motor drives both pumps; ADM controls motor speed)
- **A and B pressure** displayed separately on Home screen — BUT controlled by one setpoint
- **Cannot set A and B pressure independently** — single motor drives both 1:1

### Temperature
- **Three independent heat zones:** A-side (ISO), B-side (RES), Hose
- **Each zone set independently** on Targets screen
- **Heater capacity:** 10 kW (standard) or 15 kW (Pro/Elite)
- **Elite model:** Includes fluid inlet sensors + Graco InSite

### Output
- **Per cycle:** 0.0272 gal (A+B combined)
- **Ratio:** 1:1 by volume — A and B pumps mechanically sized equal
- **Max flow:** ~2 lb/min at typical settings

### Motor & Electrical
- **Motor:** Single DC brushed motor — drives BOTH A and B pumps
- **Brush wear alarm:** E29 — replace brushes
- **Voltage options:** 230V 1-phase, 230V 3-phase, 380V 3-phase
- **Breakers:**
  - AAG: Hose | AAH: Motor | AAJ: A Heat | AAK: B Heat | AAL: Transformer | MP: Main Power

---

## ADM DISPLAY (Advanced Display Module)

### LED Status
| LED | Meaning |
|-----|---------|
| Green solid | Run Mode, system ON |
| Green flashing | Setup Mode |
| Yellow solid | System OFF |
| Yellow flashing | Alarm/Error |
| Green + Yellow flashing | Communication issue |

### Power Up Sequence
1. Turn main power switch (MP) to ON
2. Wait for ADM to initialize
3. Press Startup/Shutdown key to activate
4. System enters Run Mode → Home screen

### Home Screen Fields
- Actual A temp | Actual B temp | Actual hose temp
- Actual A pressure | Actual B pressure
- Jog speed | Coolant temp | Cycle counter

---

## TARGETS SCREEN — HOW TO CHANGE PRESSURE AND TEMPS

### Accessing Targets
From Home screen → press soft key next to Targets/setpoint icon (or navigate with arrows)

### Changing Pressure Setpoint
1. Navigate to Targets screen
2. Press soft key next to pressure field → enter edit mode
3. Use **Up/Down arrows** to increase/decrease value
4. Press soft key again or Enter to **confirm**
5. Press Back to exit

**⚠️ ONE setpoint controls BOTH sides** — you cannot set A and B pressure to different values electronically

### Changing Temperature Setpoints
Same procedure — select A, B, or Hose zone independently. **Each zone is fully independent.**

### Setup Mode (Advanced Settings)
- Access: Home → Setup soft key → Enter password (default: **0000**)
- **System 1 screen:** Set pressure imbalance alarm threshold (E24 trigger point)
- **Recipes:** Up to 24 saved presets (pressure + temp combos)

---

## A/B PRESSURE IMBALANCE — DIAGNOSIS & FIX

### Why A and B pressures differ even with one setpoint:
1. **Dirty inlet strainer/filter** on one side (most common) → clean/replace
2. **Check valve wear** on one side → replace check valves
3. **T1 pump wear** on one side → inspect, rebuild, or replace
4. **Viscosity difference** between ISO and RES (temp-related) → check temps are equal
5. **Hose restriction** one side → inspect full hose length
6. **Drum running low** → pickup tube pulling air

### E24 Alarm = Pressure Imbalance
- Fires when A and B pressures differ by more than the threshold set in System 1
- Threshold is configurable — default varies by setup
- Fix the mechanical/material root cause, not a software setting

### Field Diagnosis Steps
1. Check inlet strainer on both sides — clean if dirty
2. Verify both drum pickup tubes are submerged
3. Check that both drum temperatures are within spec
4. Listen to pump strokes — uneven rhythm = one side struggling
5. If pressures still won't balance → check valves or pump wear

---

## WET CUPS — DAILY MAINTENANCE
- Felt washers in packing nut/wet-cup **must stay saturated** with Graco TSL (Throat Seal Liquid, #206995)
- **Check EVERY DAY before spraying**
- Dry wet cups = accelerated pump seal wear = pressure loss

---

## INLET STRAINERS — DAILY MAINTENANCE
- Both A and B inlet strainers must be inspected and cleaned daily
- **ISO (A-side) strainer especially critical** — isocyanate can crystallize from moisture contamination
- Clogged strainer = pressure drop on that side = A/B imbalance

---

## HOSE SYSTEM
- **RTD embedded in hose** — feeds temp data to TCM
- **Alarms:**
  - E02: High hose current (heater drawing too much)
  - E03: No hose current (disconnected or failed)
  - T6DH/T6DT: RTD sensor errors → Manual Hose Heat Mode
- **Manual Hose Heat Mode:** Setup > System 2 → emergency workaround when RTD fails; hose shows current draw instead of temp

---

## COMMON ALARM CODES
| Code | Meaning | Action |
|------|---------|--------|
| E01 | High fluid temperature | Reduce temp setpoint, check material |
| E02 | High hose current | Inspect hose heater |
| E03 | No hose current | Check hose connection |
| E24 | Pressure imbalance A vs B | Check strainers, check valves, pump wear |
| E29 | Motor brush wear | Replace motor brushes |
| T6DH/T6DT | Hose RTD sensor fault | Enable Manual Hose Heat Mode temporarily |

---

## GRACO T1 PUMP
- **Type:** Reciprocating displacement pump, one per side
- **Drive:** Both driven by single DC motor via gear/drive housing
- **Ratio:** 1:1 volumetric (equal output per stroke per side)
- **Key maintenance:** Wet cups (daily TSL), inlet strainers (daily), check valves (inspect on pressure imbalance)

---

## JASON'S RIG SPECIFICS
- **PASSENGER reactor:** 300 ft hose + 10 ft whip (primary, in use)
- **DRIVER reactor:** 300 ft hose + 20 ft whip (not yet in rotation)
- **Guns:** Graco Fusion AP on both
- **Tips in use:** 4242, 4747, 5252 ONLY
- **Typical pressure:** 1,080 psi target
- **Typical temps (Ambit OC):** A: 128–131°F | B: 130–133°F

---

## KNOWLEDGE GAPS (still pending)
- Generator make/model and full specs (need from Jason)
- Compressor make/model (need from Jason)
- 300 ft hose heat retention and pressure drop data
- 10 ft vs 20 ft whip behavior differences
