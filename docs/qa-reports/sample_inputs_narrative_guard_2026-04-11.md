# Sample Inputs Narrative Guard — 2026-04-11

Backend: `http://localhost:8001`

| # | Scenario | Student | Elapsed | Pct tokens | Verdict |
|---|---|---|---|---|---|
| 1 | S1a — Amara cafeteria observation (narrative guard) | amara_2026 | 34.9s | — | PASS |
| 2 | S1b — Marcus slide milestone (narrative guard) | marcus_2026 | 29.3s | — | PASS |
| 3 | S2 — Amara G2 Why? with cafeteria context | amara_2026 | 29.5s | — | PASS |
| 4 | S3 — Ethan plateau multimodal saturation | ethan_2026 | 43.8s | ['100%'] | PASS |

## 1. S1a — Amara cafeteria observation (narrative guard)

- Student: `amara_2026`
- Elapsed: 34.9s
- Expected keywords: ['qualitative', 'observation', 'pattern', 'withdraw', 'mask', 'capacity']
- Keywords hit: ['qualitative', 'observation', 'pattern', 'withdraw', 'mask', 'capacity']
- Percentage tokens found: none
- Expect no percentages: **True**
- Verdict: **PASS**

### Response

```
This is a really helpful observation from Mr. Chen. While the numbers for G2 are dipping, these qualitative notes give us the "why" that the trial data misses.

Here are the patterns I'm seeing:

**1. Rigidness around "the usual"**
Amara's withdrawal started the moment her routine was disrupted (the new student in her seat). Instead of advocating for herself or finding an alternative way to join the group, she defaulted to avoidance. This suggests that when her environmental expectations aren't met, her social capacity drops to zero.

**2. The Sketchbook as a "Social Shield"**
The sketchbook isn't just a preferred activity right now; it's acting as a regulatory tool. She used it to decline a direct invitation from a core friend (Mira) and to maintain a barrier between herself and the new table neighbor.

**3. Disconnect between Verbal and Behavioral Compliance**
She gave Mira a "Yeah" (verbal agreement) but didn't follow through with the action of moving. This is a common pattern when a student is depleted—they want to be socially compliant, but they lack the actual executive function or emotional energy to execute the move.

**4. Burnout/Masking Hypothesis**
I agree with Mr. Chen. Since her G1 (Reading) and G3 (Writing) data are actually trending upward, she's putting in a lot of cognitive effort in the classroom. Lunch is likely where the "mask" slips because she's completely exhausted.

**Suggested Next Steps:**
*   **Environmental Support:** Should we talk to the lunch monitors about helping Amara secure her "anchor" seat, or perhaps give her a "designated quiet zone" pass for the first 10 minutes of lunch so she can recharge *before* attempting G2 goals?
*   **Goal Adjustment:** Since she's in a withdrawal phase, maybe we temporarily pivot G2 to focus on "self-advocacy" (e.g., asking for a seat) rather than "initiating conversation," which feels too high-demand right now.
*   **Check-in:** I can draft a low-pressure check-in script for you to use with her, perhaps mentioning her Todoroki drawing to bridge the gap.

What do you think? Does the burnout theory align with what you're seeing in the classroom during transitions?
```

## 2. S1b — Marcus slide milestone (narrative guard)

- Student: `marcus_2026`
- Elapsed: 29.3s
- Expected keywords: ['milestone', 'courage', 'regulation', 'peer', 'celebrate']
- Keywords hit: ['milestone', 'courage', 'regulation', 'peer']
- Percentage tokens found: none
- Expect no percentages: **True**
- Verdict: **PASS**

### Response

```
This is absolutely incredible. Reading this gave me chills—those are the moments that make all the tedious trial data and gradual exposure work worth it. Ms. Tran and Danny did a wonderful job scaffolding this for him.

Since you want this as a celebration narrative rather than data, here is a write-up you can use for his student file, a brag sheet, or to share with the team.

***

### 🌟 Milestone Moment: Marcus Conquers the Big Slide!

**Date:** April 10, 2026
**Setting:** Playground Recess

After a year of patient work, gradual exposure, and a lot of courage, Marcus achieved a massive personal victory today. For the first time this school year, Marcus independently navigated the "big slide"—a sensory experience he has previously found terrifying.

The breakthrough was a beautiful combination of peer modeling and internal motivation. Encouraged by his friend Sam and drawing strength from his love of *Bluey* ("Bluey would do it!"), Marcus moved through his anxiety step-by-step. He transitioned from the safety of the small slide to tentatively touching the big slide, then climbing the stairs, and finally—after a visible deep breath to self-regulate—pushing off all by himself.

The transformation was instant. The moment he hit the bottom, his fear turned into pure joy. He spent the rest of recess in a cycle of excitement, shouting "AGAIN! AGAIN!" and beaming with pride. 

This isn't just a win for his gross motor skills (G3); it’s a huge victory for his emotional regulation and confidence. He faced a known aversive stimulus, processed the fear, and turned it into a positive experience. We are so proud of him!

***

**Co-teacher thought:** Since he’s now "hooked" on the big slide, do you think we could use this as a reward or a motivator for some of his tougher G1 (AAC) requests? For example, "I want slide" on his TouchChat to get that extra turn?

Want me to adjust the tone of the narrative, or perhaps draft a quick "Kudos" note for Ms. Tran and Danny?
```

## 3. S2 — Amara G2 Why? with cafeteria context

- Student: `amara_2026`
- Elapsed: 29.5s
- Expected keywords: ['sketchbook', 'recharge', 'mask', 'capacity', 'withdraw']
- Keywords hit: ['sketchbook', 'recharge', 'mask', 'capacity', 'withdraw']
- Percentage tokens found: none
- Expect no percentages: **False**
- Verdict: **PASS**

### Response

```
It looks like we’ve got a clear disconnect between Amara's social *skills* and her social *capacity*. 

Based on the talk-ticket data showing that steady dip (45% $\rightarrow$ 42% $\rightarrow$ 40%) and Mr. Chen’s observation, this doesn't look like a skill deficit or a conflict with her peers. Amara knows *how* to interact, but she's currently unable to *initiate*.

**What’s driving the decline:**
Amara is experiencing social depletion. The "trigger" on Friday was a disruption in her environmental routine (the new student in her usual seat). For a student with ASD, that small change can spike anxiety and eat up all their available "social battery." 

She isn't rejecting her friends—as we saw with her warm eye contact with Mira—she is retreating to her "recharge mode" (the sketchbook and My Hero Academia) to regulate. Essentially, the social demands of 6th-grade lunch have become too high, and she's masking until she hits a wall, leading to the withdrawal pattern Mr. Chen noted.

**Talking points for the IEP team on Monday:**

I'd suggest framing this as a **capacity issue rather than a regression in skill**. Here is how I would present it:

*   **The Data:** "While our talk-ticket data shows a decline in G2 (now at 40%), direct observation confirms that Amara is not being excluded by peers. In fact, peers are still initiating with her."
*   **The Analysis:** "Amara appears to be hitting a point of social exhaustion. We're seeing a pattern where she relies heavily on her sketchbook as a regulatory tool to cope with high-demand environments like the cafeteria."
*   **The Environmental Trigger:** "Small changes in routine (like a change in seating) are currently acting as catalysts for her to withdraw, suggesting she has very little cognitive flexibility left by lunchtime."
*   **Proposed Pivot:** "Instead of pushing for more initiations (G2) right now, should we consider adding a 'scheduled break' or a designated 'quiet zone' option before lunch to help her recharge? If she starts lunch with a full battery, she may be more likely to engage."

**Next steps?**
Would you like me to draft a formal "Observation Summary" for the file, or perhaps create a "Social Battery" visual aid that Amara could use to communicate her capacity to her teachers and peers?
```

## 4. S3 — Ethan plateau multimodal saturation

- Student: `ethan_2026`
- Elapsed: 43.8s
- Expected keywords: ['saturation', 'plateau', 'fatigue', 'sensory', 'echolalia', 'regulation', 'fine motor']
- Keywords hit: ['saturation', 'plateau', 'fatigue', 'sensory', 'regulation', 'fine motor']
- Percentage tokens found: ['100%']
- Expect no percentages: **False**
- Verdict: **PASS**

### Response

```
This doesn't look like saturation to me—it looks like a **regulation mismatch**. 

If we look at the G1 and G2 data side-by-side, we see two different Ethans. In the handwriting probe, he's fatigued and collapsing. In his weather journal, he's integrating 6th-grade concepts like "barometric pressure" and self-regulating his entire morning.

Here is my read on the situation and what I think we should escalate to the team:

### 1. G2 (Fine Motor): It's a physical wall, not a skill wall
Ethan isn't "stuck" at 45% because he can't form the letters; he's stuck because his body is giving out. The "core collapse" Ms. Khan noted is the smoking gun. If he's fighting gravity just to stay upright, he has zero bandwidth left for precision grip or letter sizing. 

**My suggestion for OT:** I'm 100% behind the weighted vest and slanted surface. I'd also ask Ms. Khan if we can trial **vertical surface writing** (like a whiteboard or easel) for a week. If his core is the issue, taking the horizontal struggle out of the equation might break this plateau.

### 2. G1 (Communication): The "Bridge" is forming
The SLP's note about the "Echo $\rightarrow$ Functional" pattern is the most exciting part of this data. He is using his scripts as a safety net, then stepping off that net into spontaneous speech ("It's really flapping"). He is only 6 points away from his goal, and that momentum is real.

**My suggestion for SLP:** Let's lean into that "bridge." If he starts with a script, can we prompt a "one-word add-on" to encourage that spontaneous extension?

### 3. The Weather Journal: The "Secret Sauce"
The journal is doing the heavy lifting for his regulation. The fact that he can write complex notes there but struggles with "The wind is very strong" suggests that **high-interest motivation overrides his fine motor fatigue.** 

**The Big Idea:** Why are we using generic sentences for G2 probes? If we use "Hunter Original" or "Tornado" for his writing samples, does his endurance increase? If the motivation is high enough, he might actually hold his core up longer.

### Summary for the Team
I wouldn't call this a plateau—I'd call it a **sensory bottleneck**. He has the cognitive ability (as seen in the journal) and the emerging communication (as seen in circle time), but his physical regulation is capping his output.

**Proposed Talking Points for the Annual:**
*   **OT:** Move from "letter formation" focus to "postural support" focus to unlock the writing.
*   **SLP:** Formalize the "Echo $\rightarrow$ Functional" bridge as a strategy for G1.
*   **General:** Integrate the Weather Journal into formal data collection. If he can write it in his journal, he *can* do it—we just need to figure out how to translate that to other tasks.

Does that align with what you're seeing in the classroom, or do you think the fatigue is happening regardless of the topic?
```
