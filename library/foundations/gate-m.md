---
title: "GATE-M (Gate Theory) — core framework synthesis"
source: "vault: GATE-M.md (ChatGPT dialogue export)"
captured: "unknown"
author: "model:chatgpt"
document_type: framework
evidence_class: "model-synthesis"
edited_by: "model:claude (library builder and CS lane, 2026-11-05)"
edits: "added header; repaired two formulas whose copied KaTeX had been duplicated into plain text; generalized one sentence"
status: foundation
adoption: unconfirmed
note: "Model synthesis of the owner's ideas. The owner's own positions appear only indirectly, through the model's replies to his corrections (for example 'Your correction is precise', 'I agree that collapse should not sit on a continuum'). Read it as the model's articulation, not the owner's statement."
reviewed: "a GPT reviewer @ 7e07409 (full read); later edits re-read by a Claude reviewer"
---

# Gate Theory

## Core Premise

Many systems are not best understood through averages, central tendencies, or local optimization.

Instead, outcomes emerge through a network of **gates**: conditions, decisions, thresholds, or transitions that must be satisfied before subsequent states become possible.

A gate may be:

- probabilistic,    
- deterministic,    
- informational,    
- social,    
- mechanical,    
- economic,    
- computational.    

The key observation is that outcomes are often governed less by aggregate performance than by the structure, interaction, and manipulability of gates.

---

# Definitions

## Gate

A condition that must be satisfied before a subsequent state becomes accessible.

Examples:

- Range in 40k    
- ATS passage    
- Recruiter review    
- Referral requirement    
- Hit roll    
- Save roll    
- Customer retention threshold    
- Data availability requirement    

---

## Gate Chain

A sequence of gates.

Example:

```text
Application
→ ATS
→ Recruiter
→ Hiring Manager
→ Interview
→ Offer
```

Or:

```text
Range
→ Hit
→ Wound
→ Save
→ Damage
→ Model Removed
```

---

## Gate Network

Real systems usually contain multiple parallel paths.

Example:

```text
ATS
     \
      → Human Review
     /
Referral
```

Not all outcomes require the same sequence of gates.

---

# Fundamental Principles

## 1. Gates Are Multiplicative

Success rates compound.

```text
P(success)
=
P(G1)
× P(G2)
× P(G3)
...
```

Small changes at different gates produce dramatically different effects.

---

## 2. Not All Gates Matter Equally

A gate's importance depends on:

- passage rate,
- downstream position,
- manipulability,
- available alternatives,
- interactions with other gates.

A frequently discussed gate may be strategically irrelevant.

A rarely discussed gate may dominate outcomes.

---

## 3. Elasticity Matters More Than Visibility

The important question is not:

> Which gate causes the most failures?

The important question is:

> Which gate responds most strongly to intervention?

A fixed gate is strategically less important than a mutable one.

---

# Gate Operations

## Gate Reinforcement

Improving success probability at a gate.

Examples:

- Better BS
- Resume keyword optimization
- Better sales script

---

## Gate Weakening

Reducing the restrictiveness of a gate.

Examples:

- AP reducing saves
- Recruiter endorsement
- Internal recommendation

---

## Gate Collapse

Removing a gate entirely.

Examples:

- Torrent removing hit rolls
- Auto-pass abilities
- Referrals bypassing ATS
- Reputation bypassing credential verification

A collapsed gate has effectively infinite leverage relative to incremental improvements.

---

## Gate Substitution

Replacing one path with another.

Examples:

```text
ATS → Recruiter
```

becomes

```text
Portfolio → Hiring Manager
```

---

## Gate Creation

Creating a new pathway.

Examples:

- Conference talk
- Open-source project
- Professional network

---

# Distributional Analysis

## Means Are Often Insufficient

Expected value frequently obscures strategic reality.

Important quantities may include:

- 5th percentile
- 25th percentile
- 75th percentile
- 95th percentile

depending on the gate structure.

---

## Enablement Thresholds

Performance beyond a threshold may have little value.

Performance below a threshold may be worthless.

Examples:

- Kill transport vs fail to kill transport
- Reach interview vs fail ATS
- Obtain data vs lack data

---

## Tail Relevance

Different systems privilege different portions of a distribution.

Examples:

### Reliability Problem

Lower tail dominates.

```text
Can the plan survive bad luck?
```

### Spike Problem

Upper tail dominates.

```text
Can the plan occasionally achieve a decisive outcome?
```

---

# Topological Analysis

## State Accessibility

The strongest decision may not improve outcomes.

It may change which outcomes are possible.

Examples:

- Movement creating charge lanes
- Referrals creating interview opportunities
- Data collection enabling analysis

---

## Path Dependence

Early gate decisions shape later possibilities.

A gate may matter not because of immediate outcomes but because it alters future state space.

---

## Option Enablement

Actions should be evaluated by what they make possible.

Not solely by their direct effect.

Examples:

- Removing a screen
- Building a network
- Creating a portfolio
- Learning a domain

---

# Robustness

## State-Space Reduction

Some strategies are valuable because they reduce dependence on assumptions.

Example:

The "Hand Flamer of Doom":

- Torrent
- Precision
- Devastating Wounds
- AP
- Multi-damage

collapses multiple gates simultaneously.

Its strength comes not only from damage output but from reducing sensitivity to target characteristics.

---

## Assumption Sensitivity

Evaluate:

> How many independent conditions must be satisfied?

The fewer conditions required, the more robust the strategy.

---

# ATS Application

Gate Theory predicts that hiring outcomes depend on:

- gate structure,
- gate elasticity,
- available alternative paths,
- representation effects,
- threshold behavior.

Resume perturbation experiments are an attempt to determine whether representation changes can alter passage through AI-ranking gates while leaving earlier gates intact.

The objective is not necessarily higher average scores.

The objective may be:

- increased variance,
- alternate categorization,
- uncertainty induction,
- different routing behavior,
- gate passage.

---

# Generalist Advantage

Specialists optimize within gates.

Generalists often identify:

- hidden gates,
- substitute paths,
- gate interactions,
- gate collapses,
- topology changes.

The value of broad knowledge is not necessarily superior local optimization.

It is superior navigation and restructuring of gate networks.

---

That captures the core framework: the examples in this note are applications of the same underlying structure rather than separate ideas.

## Gate Hierarchy Examples

### Data Gates

Before forecasting even becomes possible:

- Availability
- Eligibility
- History length
- Reliability
- Sample size
- Maintainability

A model cannot compensate for failure at many of these gates.

A lot of analytics teams try anyway.

---

### Pipeline Gates

Before predictions become practical:

- Compute cost
- Storage cost
- Tool compatibility
- Code maintainability
- Organizational support

A brilliant model that cannot survive deployment has failed a pipeline gate.

---

### Model Gates

Before forecasts become trustworthy:

- Model family selection
- Parameterization
- Validation strategy
- Aggregation level
- Grain selection

Notice that this is the part most data scientists immediately jump to.

Yet it's only one layer of the stack.

---

### Performance Gates

Before predictions become useful:

- Central tendency
- Distribution shape
- Spread
- Type I vs Type II tradeoffs
- Forecast horizon
- Calibration
- Stability

This is where your quantile observations become relevant.

The mean forecast may be completely uninteresting.

The critical question might be:

> What happens in the 95th percentile demand scenario?

or

> What's the downside risk in the 5th percentile?

---

But I think there are at least three more categories hiding underneath your list.

### Decision Gates

Can anyone act on this?

- Interpretability
- Trust
- Explainability
- Accountability
- Timing

A perfect forecast that arrives after the decision deadline is effectively a failed gate.

---

### Action Gates

Can the organization respond?

- Available inventory
- Staffing flexibility
- Budget
- Supply constraints
- Intervention mechanisms

Many predictive products fail here.

The prediction is correct.

The organization is unable to respond.

---

### Outcome Gates

Does the action actually influence reality?

This is where forecasting often gets conflated with causality.

```
Forecast≠Improvement
```

There must exist a mechanism through which the forecast changes decisions and decisions change outcomes.

---

## Gate Coupling

A referral can simultaneously:

- bypass or weaken automated screening,
- raise recruiter willingness to investigate ambiguity,
- lower the hiring manager’s evidentiary threshold,
- increase tolerance for an unconventional background,
- and alter how later interview evidence is interpreted.

That is not one operation. It is a perturbation propagating across coupled gates.

## Gate coupling

A useful definition:

> **Gate coupling:** A relationship in which the state, outcome, or passage conditions of one gate modify the threshold, evaluation, availability, or consequences of another gate.

That includes several distinct coupling types:

### Threshold coupling

Passing one gate changes how demanding another gate is.

```
Referral present→ lower threshold for recruiter escalation
```

### Evidentiary coupling

Evidence accepted at one gate changes how evidence is interpreted later.

```
Trusted recommendation→ ambiguous résumé history receives charitable interpretation
```

### Availability coupling

Passing one gate creates or removes another gate.

```
Forecast exceeds alert threshold→ manual review gate is activated
```

### Outcome coupling

The result of one gate changes the value of passing another.

```
Inventory unavailable→ accurate demand prediction has little operational value
```

### Feedback coupling

A downstream outcome alters an upstream gate in the next iteration.

```
Successful intervention→ increased user trust→ lower adoption threshold for later predictions
```

### Correlated coupling

Several gates depend on a shared latent factor and therefore do not behave independently.

```
Poor data governance→ lower reliability→ higher pipeline burden→ lower model confidence→ lower user trust
```

That last one matters because the simple multiplicative expression

$$
P(\text{outcome})=\prod_i P(G_i)
$$

is only valid under conditional assumptions that can become badly misleading. In a coupled architecture, the better form is closer to:

$$
P(\text{outcome}) = P(G_1)\, P(G_2\mid G_1)\, P(G_3\mid G_1,G_2)\cdots
$$

And some gates are not merely stochastic conditions; they transform the architecture itself.

## Gate collapse is categorically different

I agree that collapse should not sit on a continuum with reinforcement.

Gate reinforcement changes a parameter:

```
P(pass) = .60 → .75
```

Gate collapse changes the architecture:

```
Gate required → gate absent
```

Those interventions differ in kind because collapse removes:

- the probability of failure at that gate,
- variance introduced by that gate,
- costs of evaluating or traversing it,
- dependencies on gate-specific resources,
- and often whole classes of interaction effects.

Torrent does not give excellent Ballistic Skill. It makes Ballistic Skill irrelevant.

That distinction is probably foundational:

### Parametric operations

Change behavior while retaining the gate:

- reinforce,
- weaken,
- raise or lower threshold,
- increase attempts,
- alter variance,
- change error weighting.

### Architectural operations

Change the gate network itself:

- collapse,
- create,
- substitute,
- reorder,
- split,
- merge,
- route around,
- couple or decouple.

This also clarifies why some interventions produce discontinuous value. They do not improve the same process; they replace its structure.

## Sequencing should be endogenous

The existing treatment implicitly assumes:

```
G₁ → G₂ → G₃ → outcome
```

But sequence itself is often a controllable variable.

A stronger methodology asks:

- Must these gates occur in this order?
- Can evidence be introduced earlier?
- Can a costly gate be deferred until after a cheap disqualifying gate?
- Can two gates be evaluated concurrently?
- Can passing one gate provisionally satisfy another?
- Can a downstream actor reach backward and override an earlier failure?
- Does the same gate recur with different thresholds?

In hiring, a hiring manager can effectively reach backward and reverse an ATS outcome. In forecasting, business requirements established late can invalidate earlier choices about grain, horizon, or validation. In 40k, movement and target-selection decisions determine whether the nominal attack sequence exists at all.

So **gate ordering** deserves status as an architectural primitive, not merely an attribute of a path.

## The generalist advantage

Your correction is precise: breadth is neither the mechanism nor sufficient by itself.

The advantage is **cross-gate visibility**.

A specialist usually receives a locally framed problem:

> Improve forecast accuracy.  
> Reduce processing time.  
> Increase sales conversion.  
> Increase weapon damage.

The specialist may optimize that gate brilliantly. But their role, incentives, data access, and vocabulary often make the surrounding architecture appear fixed.

A useful generalist can instead recognize:

- that the apparent problem belongs to another gate,
- that the gate is downstream of a more restrictive one,
- that a local improvement will be absorbed elsewhere,
- that two teams are separately optimizing coupled gates,
- or that the path can be reconfigured entirely.

So the sharper claim is:

> **Specialists tend to dominate when the binding gate is known, stable, and locally technical. Generalists gain comparative advantage when the gate architecture is obscure, coupled, changing, or contested.**

That avoids turning generalism into a universal virtue. The Jack beats the Ace when the game rewards identifying or restructuring the game—not when it simply asks who is best at a known task.

## Revised abstract structure

I think the portable core now separates cleanly into four layers.

### 1. Primitives

- **State:** A condition the system may occupy.
- **Transition:** Movement between states.
- **Gate:** A condition governing a transition.
- **Threshold:** The criterion for gate passage.
- **Path:** An ordered or partially ordered set of transitions.
- **Architecture:** The full network of states, gates, paths, and couplings.
- **Resource:** Something consumed, reserved, or enabled while traversing gates.
- **Actor:** An entity capable of evaluating, modifying, or traversing gates.

### 2. Gate properties

- passage probability,
- determinism,
- threshold form,
- observability,
- mutability,
- cost,
- latency,
- recurrence,
- reversibility,
- error asymmetry,
- distributional sensitivity,
- dependence on other gates.

### 3. Operations

**Parametric**

- reinforce,
- weaken,
- shift threshold,
- increase volume,
- redistribute variance,
- change error costs.

**Architectural**

- collapse,
- create,
- substitute,
- bypass,
- reorder,
- split,
- merge,
- couple,
- decouple,
- activate,
- deactivate.

### 4. Evaluation concepts

- binding constraint,
- elasticity,
- threshold-crossing probability,
- tail relevance,
- option enablement,
- state accessibility,
- robustness,
- assumption dependence,
- intervention availability,
- downstream utility,
- propagation through coupled gates.

## The methodology

The method should probably not begin with “find the bottleneck.” That prematurely assumes a simple chain and a single dominant constraint.

A more faithful sequence would be:

1. **Define the desired state.**  
    Not merely the local metric.
2. **Map the architecture.**  
    States, gates, paths, actors, sequence, and alternatives.
3. **Characterize each gate.**  
    Thresholds, distributions, error costs, visibility, and mutability.
4. **Map coupling.**  
    Identify where one gate changes another or where several share causes.
5. **Identify intervention surfaces.**  
    Distinguish what is important from what is actually manipulable.
6. **Generate parametric and architectural interventions.**  
    Do not limit the search to improving passage rates.
7. **Evaluate against final-state utility.**  
    Include asymmetric errors, tails, enablement, and downstream compensation.
8. **Experiment.**  
    Perturb the architecture or parameters and observe both local and propagated effects.
9. **Update the map.**  
    The architecture is a model of the system, not the system itself.

And yes: the eventual document should present that abstraction first, then one neutral worked example, and only afterward introduce Warhammer, ATS, and predictive analytics. Warhammer is the origin and perhaps the clearest demonstration; it should not be required for readers to extract the methodology.

The forecasting instantiation is probably the best place to establish professional credibility. The Hand Flamer of Doom is the best place to make the architecture unforgettable.

--- 

## Example

In GATE-M terms, Warhammer 40,000 offense and defense are not opposites so much as **competing attempts to shape the same gate architecture**.

Offense tries to create a path from decision to desired state:

> choose target → establish eligibility → generate attacks → convert attacks → defeat defenses → inflict sufficient consequence → enable a broader objective

Defense tries to:

> deny the path, add gates, raise thresholds, force inefficient routing, reduce attempts, absorb success, or make the resulting state strategically irrelevant

The useful part of a **holarchic** framing is that every level is simultaneously:

- a complete system in itself,
- a component inside a larger system,
- and an environment containing smaller systems.

A weapon profile is a holon inside a model.  
A model is a holon inside a unit.  
A unit is a holon inside an activation plan.  
An activation is a holon inside a turn.  
A turn is a holon inside a battle plan.  
An army is a holon inside the mission and matchup.

A gate can therefore be decisive locally but irrelevant globally, or mediocre locally but extremely important because of what it enables one level up.

# GATE-M framing of 40k offense and defense

## 1. The atomic attack holon

At the lowest scale, an attack is a chain of gates.

### Offensive path

```text
Target exists
→ Target is eligible
→ Attacker is eligible
→ Range satisfied
→ Visibility satisfied
→ Phase/action timing satisfied
→ Attack quantity generated
→ Hit gate passed
→ Wound gate passed
→ Allocation reaches desired model
→ Save gate failed or bypassed
→ Damage gate passed
→ Damage converts into desired consequence
```

The mistake in conventional mathhammer is often treating this chain as though it were merely a sequence of independent probabilities.

It is not.

Each gate can be:

- removed,    
- weakened,    
- strengthened,    
- substituted,    
- bypassed,    
- coupled to another,    
- made irrelevant by target choice,    
- or rendered strategically meaningless by overkill or poor timing.    

## Offensive operations at the attack scale

### Gate reinforcement

Improve passage through an existing gate.

Examples:

- +1 to Hit    
- +1 to Wound    
- rerolls    
- increased Strength    
- increased AP
- increased Damage

These remain parametric improvements. The gate still exists.

### Gate collapse

Remove the gate.

Examples:

- Torrent collapses the Hit gate.
- Devastating Wounds can collapse the Save gate on critical wounds.
- Mortal wounds collapse much of the conventional attack sequence.
- Ignore Cover removes one defensive modifier pathway.
- Anti-X can sharply reshape the Wound threshold.
- Precision weakens or bypasses ordinary damage allocation.

Collapse is not just “a large bonus.” It changes the architecture.

### Gate multiplication

Increase the number of attempts flowing through the chain.

Examples:

- more attacks,
    
- Blast,
    
- Sustained Hits,
    
- additional shooting activations,
    
- fight-on-death,
    
- shooting in the opponent’s phase,
    
- Overwatch.
    

Volume is not merely more expected damage. It changes the probability that rare branches occur:

- critical hits,
    
- critical wounds,
    
- Devastating Wounds,
    
- enough failed saves to cross a model-removal threshold,
    
- enough damage to reach an activation-denial state.
    

### Gate routing

Direct successful passage toward the desired object.

Examples:

- Precision,
    
- indirect fire,
    
- split fire,
    
- target selection,
    
- allocation manipulation,
    
- attacks that ignore bodyguards or intervening screens.
    

This is distinct from raw output. A lower-damage attack can be more strategically effective if it reaches the right model.

## Defensive operations at the attack scale

### Gate creation

Defense can insert new conditions.

Examples:

- Lone Operative,
    
- Stealth,
    
- cover,
    
- Feel No Pain,
    
- bodyguard rules,
    
- screening,
    
- untargetability conditions,
    
- range constraints.
    

### Gate strengthening

Examples:

- improved Save,
    
- Invulnerable Save,
    
- -1 to Hit,
    
- -1 to Wound,
    
- damage reduction,
    
- higher Toughness,
    
- higher Wounds.
    

### Gate substitution

Defense may replace one gate with a more favorable one.

Examples:

- use an invulnerable save instead of an armor save,
    
- convert ordinary damage into Feel No Pain rolls,
    
- allocate attacks into a disposable bodyguard,
    
- force shooting into a transport rather than passengers,
    
- force a melee unit to kill a screen before reaching the real target.
    

### Gate absorption

The attack succeeds mechanically but fails strategically.

Examples:

- overkill into a cheap unit,
    
- wasting Damage 4 into one-wound models,
    
- killing a unit that has already completed its mission role,
    
- forcing excess attacks into a doomed screen,
    
- trading down in points or tempo.
    

This is one of the most important defensive concepts in GATE-M:

> Defense does not always prevent passage. It can make passage worthless.

# 2. The weapon-profile holon

A weapon profile is an architecture of gate interactions.

A conventional comparison asks:

> What is the average damage?

GATE-M asks:

- Which gates does the profile depend upon?
    
- Which gates does it remove?
    
- Which target classes alter its effectiveness?
    
- Which thresholds does it cross reliably?
    
- Which parts of its output distribution matter?
    
- What strategic states does it enable?
    

## The Hand Flamer of Doom

A profile with:

- Torrent
    
- Strength 6
    
- AP -2
    
- Damage 4
    
- Devastating Wounds
    
- Precision
    
- +2 Attacks
    

is powerful because it attacks multiple gates at once.

### Torrent

Removes the Hit gate.

This also creates defensive robustness against:

- poor Ballistic Skill,
    
- hit penalties,
    
- Stealth,
    
- variance from attack rolls.
    

### Strength 6

Improves the Wound gate against relevant infantry and character profiles.

Its value depends on the target thresholds it crosses:

- S5 to S6 may change wound probability sharply against T5,
    
- while doing little against other bands.
    

### AP -2

Weakens the armor gate when Devastating Wounds do not trigger.

### Devastating Wounds

Creates a branch that bypasses conventional saving.

### Precision

Changes routing through the allocation architecture.

The profile no longer merely damages a unit; it can threaten the specific character that makes the unit function.

### Damage 4

Interacts with wound thresholds discontinuously.

Damage 4 does not merely mean “twice Damage 2.”

It may change:

```text
two successful attacks required
```

into:

```text
one successful attack required
```

That is a gate-threshold shift.

### Additional attacks

Increase sampling through all downstream branches.

More attacks mean:

- more wound rolls,
    
- more opportunities for critical wounds,
    
- more chances to route damage into the character,
    
- more chances to cross the kill threshold.
    

The profile is therefore not merely high-output. It is **low-dependence and high-routing**.

That state-space reduction is often more valuable than raw mean damage.

# 3. The model holon

A model combines:

- movement,
    
- weapon access,
    
- durability,
    
- special rules,
    
- base size,
    
- OC,
    
- character abilities,
    
- keyword interactions.
    

The model-level question is not simply:

> How much damage does this model deal?

It is:

> What gate functions does this model perform inside the unit and army architecture?

## Offensive model functions

A model may act as:

- output generator,
    
- character assassin,
    
- transport killer,
    
- screen clearer,
    
- overwatch threat,
    
- charge enabler,
    
- OC remover,
    
- support-model eliminator,
    
- secondary scorer,
    
- movement blocker.
    

A model with mediocre damage can still be offensively decisive if it collapses a gate for something else.

Example:

A model kills one screening unit.

Its direct output is modest. But that action may enable:

```text
screen removed
→ charge lane opens
→ melee hammer reaches primary target
→ objective flips
```

The model’s value is upstream enablement.

## Defensive model functions

A model may defend through:

- durability,
    
- placement,
    
- sacrificial occupation,
    
- base-size blocking,
    
- threat of retaliation,
    
- bodyguarding,
    
- aura denial,
    
- target-priority distortion.
    

A cheap model can be defensively excellent if it imposes expensive gates on the opponent.

For example:

```text
enemy must first expose
→ spend an activation
→ kill cheap model
→ remain unable to reach key unit
```

The model did not “survive.” It still succeeded defensively.

# 4. The unit holon

A unit is not merely the sum of its profiles. It is a small gate network.

It contains:

- internal role differentiation,
    
- allocation rules,
    
- special weapons,
    
- leaders,
    
- buffs,
    
- coherency constraints,
    
- model-removal consequences,
    
- OC thresholds,
    
- transport relationships.
    

## Offensive unit architecture

A unit can combine distinct gate functions.

Example:

- high-volume weapons remove screens,
    
- special weapons threaten hard targets,
    
- a character adds rerolls,
    
- Precision threatens support models,
    
- high OC converts damage into objective control.
    

The unit may be designed for:

### Concentrated gate collapse

Several mechanisms attack one critical gate.

Example:

- rerolls,
    
- +1 to Wound,
    
- Lethal Hits,
    
- high Strength,
    
- wound modifiers.
    

This overwhelms the Wound gate.

### Distributed gate pressure

Different mechanisms attack different gates.

Example:

- Torrent removes hit dependence,
    
- Devastating Wounds bypasses saves,
    
- Precision changes routing,
    
- multi-damage crosses character thresholds.
    

This creates broad robustness.

### Redundant gate access

Several models or weapon types can perform the same task.

This reduces dependence on one casualty, one roll, or one profile.

## Defensive unit architecture

A unit defends through:

- ablative bodies,
    
- wound allocation,
    
- character protection,
    
- mixed durability,
    
- model spacing,
    
- coherency,
    
- reactive movement,
    
- threat zones,
    
- replacement or resurrection,
    
- damage reduction.
    

### Ablative defense

Cheap bodies absorb passage through the attack chain before the opponent reaches the valuable models.

### Threshold defense

The unit is configured so that likely damage does not cross a meaningful threshold.

Examples:

- leaving a leader alive,
    
- preserving special weapons,
    
- retaining enough OC,
    
- keeping enough models to hold an objective,
    
- surviving with one model so the unit still exists for scoring or denial.
    

### Functional defense

The unit may lose models but preserve its strategic role.

This matters because model loss is not always the actual desired outcome.

The attacker may need to:

- destroy the unit,
    
- remove its OC,
    
- kill its leader,
    
- stop its aura,
    
- prevent an action,
    
- clear a footprint.
    

The defender should identify which consequence is actually being pursued and defend that gate.

# 5. The activation holon

An activation is the use of one unit, stratagem, ability, or action opportunity.

At this level, offense and defense become questions of sequencing, information, and resource exchange.

## Offensive activation gates

```text
Unit available
→ target available
→ route available
→ resources available
→ activation selected
→ attack resolves
→ desired threshold crossed
→ later activation enabled
```

The crucial question is:

> What does this activation make possible next?

A low-output activation may be best if it removes uncertainty or opens the board.

Examples:

- remove a screen,
    
- strip cover,
    
- force a defensive stratagem,
    
- trigger Battle-shock,
    
- expose a transport,
    
- make the opponent spend CP,
    
- finish a damaged unit to free later fire.
    

## Activation sequencing

Gate coupling becomes central.

An early activation may modify later gates.

Examples:

```text
Thunderstrike marks target
→ later wound thresholds improve
```

```text
screen cleared
→ charge declaration becomes possible
```

```text
transport destroyed
→ passengers become targetable
```

```text
defensive stratagem baited
→ later attack avoids it
```

This means activation order cannot be evaluated only by local output.

A weaker first activation may be better because it alters downstream gate conditions.

## Defensive activation architecture

Defense at this level includes:

- interrupt timing,
    
- reactive moves,
    
- overwatch,
    
- defensive stratagems,
    
- Heroic Intervention,
    
- target denial,
    
- resource reservation,
    
- forcing bad activation order.
    

A defender often wants to create an **activation tax**:

> The attacker must spend extra units, CP, movement, or sequencing attention before reaching the desired state.

Even if every defensive unit eventually dies, the defense can succeed by consuming enough of the opponent’s activation economy.

# 6. The phase holon

Each phase has its own gate architecture.

## Movement phase

Movement establishes many later gates.

It determines:

- range,
    
- visibility,
    
- target eligibility,
    
- charge paths,
    
- screening,
    
- objective access,
    
- deep-strike denial,
    
- retreat routes,
    
- counterattack exposure.
    

Movement is therefore not merely positional. It is **gate preconfiguration**.

### Offensive movement

Offensive movement tries to:

- create range,
    
- establish line of sight,
    
- open charge lanes,
    
- force target exposure,
    
- threaten multiple routes,
    
- create mutually exclusive defensive demands.
    

### Defensive movement

Defensive movement tries to:

- deny range,
    
- deny line of sight,
    
- block paths,
    
- preserve distance,
    
- maintain fallback routes,
    
- force overextension,
    
- make enemy outputs inapplicable.
    

Your Parthian example is pure GATE-M:

> Use Assault movement and range control so your shooting gates exist while the opponent’s melee gates do not.

This does not improve your save or reduce their damage.

It prevents their attack architecture from activating.

## Shooting phase

The shooting phase is largely about:

- selecting which defensive gates to attack,
    
- deciding which units must be weakened versus destroyed,
    
- allocating enough volume to cross thresholds without wasting activations.
    

## Charge phase

The charge phase contains:

- eligibility,
    
- distance,
    
- overwatch exposure,
    
- screening,
    
- route geometry,
    
- multiple charge risks,
    
- countercharge consequences.
    

## Fight phase

The fight phase adds:

- Fight First,
    
- activation sequencing,
    
- pile-in and consolidation,
    
- interrupt threats,
    
- model removal affecting reach,
    
- objective and movement consequences.
    

## Command phase

This phase affects future gates through:

- Battle-shock,
    
- CP generation,
    
- objective control,
    
- ability activation,
    
- status clearing.
    

The command phase is often underweighted because it produces little direct damage, but it can alter the architecture for the entire round.

# 7. The turn holon

A turn is an integrated sequence of phase-level gate manipulations.

A good offensive turn does not maximize damage in each phase independently.

It uses one phase to configure the next.

Example:

```text
Movement creates angles
→ Shooting removes screen
→ Charge reaches support unit
→ Fight consolidates onto objective
→ opponent begins turn with reduced options
```

The final state is not “damage dealt.”

It is:

- target removed,
    
- objective controlled,
    
- opponent routed,
    
- counterattack weakened,
    
- future path opened.
    

## Offensive turn design

A GATE-M offensive turn should ask:

- What desired state must exist at turn end?
    
- Which gates prevent it?
    
- Which phase can alter those gates most efficiently?
    
- Which activations are enabling rather than finishing?
    
- What threshold must be crossed, and what output beyond that is wasted?
    
- What defensive reactions must be baited or exhausted first?
    

## Defensive turn design

A defensive turn should ask:

- Which enemy paths must be denied?
    
- Which gates can be made mutually exclusive?
    
- Where can sacrifice add activation taxes?
    
- What resources must remain available for later phases?
    
- Can the opponent be forced to overcommit?
    
- Can success at one gate be made irrelevant at the next?
    

Defense at turn scale often means shaping the opponent’s decision tree so that every branch has a cost.

# 8. The battle-round holon

The battle round includes both players’ turns and therefore introduces reciprocal gate coupling.

A decision during your turn can alter:

- what the opponent can attack,
    
- what they must expose,
    
- which objectives they can reach,
    
- what resources they must spend,
    
- which units remain available for their own scoring.
    

## Offensive battle-round thinking

The real question becomes:

> What state survives contact with the opponent’s response?

A unit can kill its target and still fail if it creates a favorable retaliation path.

Offense at this scale includes:

- trading,
    
- tempo,
    
- forcing responses,
    
- denying recovery,
    
- setting up second-order threats.
    

## Defensive battle-round thinking

Defense may deliberately concede a local gate to preserve a larger one.

Examples:

- give up a unit to protect scoring,
    
- concede one objective to preserve the army,
    
- allow a charge that pulls the opponent out of position,
    
- offer a durable target that consumes the enemy turn.
    

This is where “defense” becomes architecture manipulation rather than damage prevention.

# 9. The army holon

An army is a portfolio of gate functions.

A balanced army is not necessarily one with equal amounts of melee, shooting, and durability.

It is one with enough tools to interact with the relevant gate architectures.

## Offensive army functions

An army may need:

- screen clearance,
    
- anti-elite,
    
- anti-tank,
    
- character removal,
    
- indirect pressure,
    
- deep strike,
    
- movement control,
    
- objective flipping,
    
- action units,
    
- countercharge,
    
- reserve threats.
    

These are not simply damage categories. They correspond to different gates.

### Redundancy

Can multiple units address the same gate?

### Complementarity

Can one unit modify a gate for another?

### Routing diversity

Can the army reach desired states through different paths?

### Threshold coverage

Can it reliably solve low, medium, and high durability problems without gross inefficiency?

## Defensive army functions

An army defends through:

- screening,
    
- reserves,
    
- layered durability,
    
- target saturation,
    
- threat saturation,
    
- reactive movement,
    
- denial zones,
    
- expendable units,
    
- counterattack,
    
- distributed scoring.
    

A defensive army does not need to be durable in the conventional sense.

It may instead be hard to interact with efficiently.

Examples:

- too many threats to answer,
    
- too many routes to block,
    
- targets hidden until activation,
    
- expendable units protecting valuable ones,
    
- units operating at ranges the opponent cannot answer.
    

# 10. The mission holon

At mission scale, all combat gates are subordinate to scoring.

The desired state is not:

> destroy the enemy army

It is:

> produce a winning score.

This creates one of the most important GATE-M corrections in 40k:

> Damage is often an intermediate gate, not the terminal outcome.

A unit may be valuable because it:

- removes OC,
    
- clears one objective,
    
- survives long enough,
    
- performs an action,
    
- forces the opponent off schedule,
    
- blocks a route,
    
- denies a secondary,
    
- threatens a future turn.
    

## Offensive mission play

Offense means creating scoring states.

This may require:

- killing,
    
- moving,
    
- denying,
    
- surviving,
    
- sacrificing,
    
- forcing opponent displacement.
    

## Defensive mission play

Defense means denying the opponent’s scoring architecture.

That can include:

- preserving one model,
    
- occupying space,
    
- forcing inefficient trades,
    
- hiding,
    
- delaying,
    
- conceding low-value areas,
    
- protecting a late-game path.
    

At mission scale, “offense” and “defense” often swap meanings.

A charge may be defensive because it pins a unit away from an objective.

A retreat may be offensive because it preserves a scoring piece.

# 11. The matchup holon

The matchup is the interaction between two army architectures.

A unit profile has no fixed value independent of the enemy’s gate structure.

Examples:

- AP -2 is excellent into some armor profiles and partially wasted into invulnerable saves.
    
- Damage 4 is devastating into four-wound characters and inefficient into one-wound infantry.
    
- Precision is powerful only when support characters matter.
    
- Torrent is more valuable against hit penalties and Overwatch opportunities.
    
- screening is more important against deep strike or melee armies than static gunlines.
    

The correct question is:

> Which parts of my architecture intersect with their binding gates?

## Offensive matchup plan

- Identify what their army requires to function.
    
- Locate support dependencies.
    
- Identify fragile gate couplings.
    
- Attack units whose removal changes multiple downstream thresholds.
    
- Force them into gate structures where their strengths are inactive.
    

## Defensive matchup plan

- Hide critical dependencies.
    
- Decouple support units from obvious targeting paths.
    
- create redundancy,
    
- force enemy specialization into poor targets,
    
- deny their preferred sequence,
    
- make them solve several different gate problems at once.
    

# 12. The metagame holon

At the metagame scale, the “gates” include:

- list-building assumptions,
    
- common defensive profiles,
    
- common scoring patterns,
    
- terrain conventions,
    
- tournament timing,
    
- expected matchup frequencies,
    
- prevailing target-selection habits.
    

A weapon or unit can outperform its paper efficiency because it attacks under-defended gates in the environment.

Similarly, a generally powerful profile can underperform because the metagame has already adapted around it.

## Offensive metagame thinking

- Which gates are most armies currently underprotecting?
    
- Which profiles reduce dependence on common defenses?
    
- Which list architectures force unfamiliar decisions?
    
- Which target types are overrepresented?
    

## Defensive metagame thinking

- Which common attack architectures must the list survive?
    
- Which dependencies are obvious and easily targeted?
    
- Can the army avoid presenting a standard problem?
    
- Can it force opponents to use inefficient answers?
    

# Cross-scale principles

## 1. Local success can produce global failure

A unit may destroy its target and still worsen the army’s state.

Examples:

- overextend,
    
- expose itself,
    
- vacate an objective,
    
- spend too many resources,
    
- enable a countercharge,
    
- waste a key activation.
    

## 2. Local inefficiency can produce global success

A unit can trade down in points but:

- remove a screen,
    
- pin a hammer,
    
- force CP expenditure,
    
- preserve a scoring unit,
    
- create a charge lane,
    
- deny a turn.
    

## 3. Gates propagate upward

A failed attack gate can become:

- a failed unit activation,
    
- a failed phase plan,
    
- a failed objective flip,
    
- a lost battle round.
    

## 4. Gates propagate downward

A mission decision can determine:

- which unit activates,
    
- which target matters,
    
- which weapon profile is relevant,
    
- which percentile of damage matters.
    

## 5. Relevant quantiles change by scale

At weapon scale:

- spike potential may matter.
    

At activation scale:

- threshold crossing matters.
    

At turn scale:

- reliability may dominate.
    

At mission scale:

- preserving a viable late-game branch may matter more than either mean or spike.
    

## 6. Defense often acts by denying activation

The best defense may be:

- out of range,
    
- out of sight,
    
- screened,
    
- untargetable,
    
- in reserve,
    
- not worth attacking,
    
- too costly to reach.
    

“Cannot begin the chain” is stronger than “survives the chain.”

## 7. Offense often acts by collapsing dependency

The best offense may:

- auto-hit,
    
- bypass saves,
    
- target leaders,
    
- ignore cover,
    
- attack from reserve,
    
- create extra activations,
    
- choose a different target class.
    

“Fewer gates required” is often stronger than “better at every roll.”

# A compact GATE-M offensive diagnostic

For any offensive plan:

1. What exact state do I want?
    
2. What gates must be passed?
    
3. Which gate is most restrictive?
    
4. Which gate is most mutable?
    
5. Which gates can be removed rather than improved?
    
6. Which defensive gates are coupled?
    
7. What threshold is sufficient?
    
8. Which output above that threshold is wasted?
    
9. What does success enable at the next scale?
    
10. What counterarchitecture does success expose me to?
    

# A compact GATE-M defensive diagnostic

For any defensive plan:

1. What state is the opponent trying to create?
    
2. What gates do they require?
    
3. Which gate can I deny earliest?
    
4. Can I force them onto a less efficient path?
    
5. Can I insert an activation tax?
    
6. Can I make success strategically irrelevant?
    
7. Which unit or resource is actually carrying the defensive function?
    
8. Can I preserve function without preserving models?
    
9. Can I create mutually exclusive demands?
    
10. What larger-scale state am I protecting?
    

# The core holarchic insight

At every scale, offense and defense are both forms of gate architecture.

- **Offense** creates, opens, weakens, bypasses, or collapses paths toward a desired state.
    
- **Defense** closes, strengthens, diverts, taxes, absorbs, or invalidates those paths.
    
- **Strategy** is choosing which scale matters.
    
- **Tactics** are the operations performed on gates.
    
- **List construction** is the selection of gate-manipulation capabilities.
    
- **Mission play** determines which gate outcomes have actual utility.
    

The best 40k decisions often look strange when evaluated at the wrong level of the holarchy.

A bad trade at the model level can be excellent at the mission level.  
A weak weapon can be essential at the activation level.  
A durable unit can be defensively useless if it protects no meaningful gate.  
A fragile unit can be defensively excellent if it denies an entire enemy path.  
A high-damage unit can be strategically poor if its output cannot be routed into a relevant state.

That is where GATE-M becomes more useful than conventional efficiency analysis: it does not ask only whether a unit performs well.

It asks:

> **Which gates does it alter, at what scale, for whose benefit, and what larger states become reachable or unreachable as a result?**
