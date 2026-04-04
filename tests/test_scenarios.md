# ClassLens ASD Test Scenarios

Comprehensive test coverage for all four agents in the ClassLens pipeline. Each test case specifies inputs, expected outputs, pass criteria, and priority levels (P0 = critical for demo, P1 = should work, P2 = nice to have).

---

## Agent 1: Vision Reader (OCR + Behavior Recognition)

### VR-01: Maya's Math Worksheet Transcription
- **Test ID**: VR-01
- **Agent**: Vision Reader
- **Input**: Photo of Maya's completed math worksheet (single-digit addition: 3+4, 2+5, 7+1, 6+2, 5+3, 8+0, 4+4, 1+6, 9+0, 3+2)
- **Expected Output**:
  - Correctly transcribed 10 math problems
  - Identified answers: 7 correct (70%), 2 incorrect (20%), 1 skipped (10%)
  - Notes showing "skipped problem #4" and "incorrect problem #7 (wrote 8 instead of 12)"
- **Pass Criteria**: Transcription accuracy 95%+, correct count of correct/incorrect/skipped with ±1 tolerance
- **Priority**: P0 (core demo functionality)

### VR-02: Maya's Behavior Tally (Greeting Behavior)
- **Test ID**: VR-02
- **Agent**: Vision Reader
- **Input**: Photo of teacher tally sheet with date columns (Mon-Fri) and row labels: "Greets peer", "Follows direction", "Calming strategy used"
  - Example tally: Mon=3, Tue=4, Wed=2 (fire drill), Thu=5, Fri=6 (greetings per day)
- **Expected Output**:
  - Extracted tally marks per behavior per day
  - Calculated daily average for "Greets peer": 4.0/day
  - Flagged low day (Wed) with note about fire drill
- **Pass Criteria**: Tally count accuracy 90%+, correctly identified all 5 days, correctly calculated averages
- **Priority**: P0

### VR-03: Maya's Visual Schedule Checklist
- **Test ID**: VR-03
- **Agent**: Vision Reader
- **Input**: Photo of visual schedule with 6 items: (1) Morning meeting ✓, (2) Math ✓, (3) Snack, (4) Reading ✓, (5) Specials, (6) Pack up ✓
- **Expected Output**:
  - Identified 4 items with checkmarks, 2 items without
  - Correctly listed unchecked items: "Snack", "Specials"
  - Structured output: `{"completed": 4, "pending": 2, "percent_complete": 67}`
- **Pass Criteria**: Checkmark detection 100%, correct completion percentage, correct item identification
- **Priority**: P1

### VR-04: Jaylen's Task Checklist (7 steps)
- **Test ID**: VR-04
- **Agent**: Vision Reader
- **Input**: Photo of Jaylen's morning routine checklist with 7 steps: (1) Hands-on sensory bin ✓, (2) Morning snack ✓, (3) AAC warm-up ✓, (4) Visual schedule review ✓, (5) Transition song, (6) Work task ✓, (7) Clean-up
- **Expected Output**:
  - Identified 5 completed steps, 2 incomplete
  - Listed as: `[1,2,3,4,6]` (completed indices)
  - Progress: 71% (5 of 7)
- **Pass Criteria**: All 7 steps recognized, completion count accurate to ±1, correct percentage
- **Priority**: P0

### VR-05: Jaylen's PECS Communication Log
- **Test ID**: VR-05
- **Agent**: Vision Reader
- **Input**: Photo of PECS log with 5 recorded requests:
  - 9:00 AM - "Train" (AAC device) ✓
  - 10:15 AM - "Water" (gesture + picture) ✓
  - 11:00 AM - "Break" (picture card) ✓
  - 12:30 PM - "Snack" (AAC device) ✓
  - 1:45 PM - "More" (gesture only)
- **Expected Output**:
  - 5 total communication attempts extracted
  - Methods: AAC device (2), picture card (1), gesture + picture (1), gesture only (1)
  - Success rate: 4/5 = 80% (gesture-only = prompted/not independent)
- **Pass Criteria**: All 5 attempts recognized, method classification 80%+ accurate, success calculation correct
- **Priority**: P0

### VR-06: Sofia's Writing Sample (Transcription)
- **Test ID**: VR-06
- **Agent**: Vision Reader
- **Input**: Photo of Sofia's handwritten paragraph about Presidents:
  - "George Washington was the first president. He lived in Virginia. The Constitution was created in 1787. Washington was an army leader before he was president."
  - (Note: 2 spelling errors intentionally included: "creaded" instead of "created", "Washinton" instead of "Washington")
- **Expected Output**:
  - Faithful transcription including original spelling errors
  - 4 sentences identified
  - Flag note: "2 spelling errors detected"
  - Word count: 38 words
- **Pass Criteria**: Transcription 95%+ accurate, spelling errors flagged, sentence count correct
- **Priority**: P1

### VR-07: Sofia's Transition Log
- **Test ID**: VR-07
- **Agent**: Vision Reader
- **Input**: Photo of Sofia's transition tracking log with 4 recorded transitions:
  - 9:45 AM - Math to Reading (5-minute warning given) ✓ Smooth
  - 11:00 AM - Reading to Lunch (announced day before) ✓ Smooth
  - 12:15 PM - Lunch to Science (unexpected: scheduled change) ✗ Anxious
  - 1:30 PM - Science to Pack-up (standard transition) ✓ Smooth
- **Expected Output**:
  - 4 transitions extracted with timestamps
  - 3 smooth transitions, 1 with anxiety flag
  - Identified unannounced change as trigger
  - Notes: "Warning effectiveness: planned transitions 100%, unplanned 0%"
- **Pass Criteria**: All 4 transitions recognized, emotional flags correct, trigger identification accurate
- **Priority**: P1

---

## Agent 2: IEP Mapper (Goal Alignment)

### IM-01: Maya's Math Worksheet → Goal Mapping
- **Test ID**: IM-01
- **Agent**: IEP Mapper
- **Input**: Vision Reader output from VR-01 (Maya's math worksheet: 7/10 correct)
- **Expected Output**:
  - Primary mapping: **G2 (Following Directions)** - worksheet represents multi-step task execution
  - Secondary mapping: **G1 (Greetings)** - low confidence, not applicable
  - Confidence: 85% (clear alignment to direction-following domain)
  - Trial data: 7 successes, 10 trials, 70% (within G2 measurement window)
- **Pass Criteria**: Primary goal correctly identified as G2, confidence >80%, secondary goals marked low-confidence
- **Priority**: P0

### IM-02: Maya's Behavior Tally → Multi-Goal Mapping
- **Test ID**: IM-02
- **Agent**: IEP Mapper
- **Input**: Vision Reader output from VR-02 (behavior tally: greetings 4/day, calming 2/day, directions 5/8)
- **Expected Output**:
  - Greeting row → **G1 (Peer Greetings)**: 4 successes per day average, trending upward
  - Calming strategy row → **G3 (Self-Regulation)**: 2 uses/day indicates 1 outburst reduction
  - Following directions row → **G2 (Following Directions)**: 5/8 = 63% (on track toward 75% target)
  - Integrated note: "Multiple goals improving in parallel; fire drill spike noted on Wed"
- **Pass Criteria**: All 3 goals identified, correct row-to-goal mapping, trend detection working
- **Priority**: P0

### IM-03: Jaylen's PECS Log → AAC Communication Goal
- **Test ID**: IM-03
- **Agent**: IEP Mapper
- **Input**: Vision Reader output from VR-05 (PECS log: 5 attempts, 4 successful/AAC-based)
- **Expected Output**:
  - Primary mapping: **G1 (AAC Communication)**: 4/5 = 80% (met target!)
  - Independent calculation: AAC device method = 2/5 = 40% truly independent (gestures + pictures = prompted)
  - Note: "4/5 successes if we count picture+gesture hybrid; 2/5 if we require AAC-only independence"
  - Recommendation: "AAC device increasing; monitor gesture-reliance"
- **Pass Criteria**: Goal G1 correctly identified, dual success-rate calculation provided, independence assessment accurate
- **Priority**: P0

### IM-04: Sofia's Writing Sample → G3 Mapping
- **Test ID**: IM-04
- **Agent**: IEP Mapper
- **Input**: Vision Reader output from VR-06 (Sofia's paragraph about Presidents - facts only, no opinion/emotion)
- **Expected Output**:
  - Primary mapping: **G3 (Written Expression)**:
    - Content analysis: "All-facts, no-opinion" structure
    - Rubric estimate: 2/4 (meets 50% of expectations - accurate facts but lacks voice/emotion)
    - Trend vs. baseline (40%): "No improvement yet; still heavily factual"
  - Coaching note: "Ready for opinion-insertion prompts; consider: 'Why do YOU think Washington was important?'"
- **Pass Criteria**: Goal G3 identified, rubric scoring accurate to within ±0.5, coaching recommendations aligned
- **Priority**: P1

### IM-05: Sofia's Transition Log → Executive Function + Anxiety Flag
- **Test ID**: IM-05
- **Agent**: IEP Mapper
- **Input**: Vision Reader output from VR-07 (transition log: 3 smooth, 1 anxious from unannounced change)
- **Expected Output**:
  - Primary mapping: **G2 (Managing Transitions & Schedule Changes)**: 3/4 = 75% (below 85% target)
  - Secondary alert: **G1 (Social Communication)** - low confidence, anxiety may impact peer initiation
  - Critical flag: "Unannounced changes = 0% success; recommend 5-minute warning protocol"
  - Trend note: "Approaching target; consistency of announcement protocol critical"
- **Pass Criteria**: Goal G2 identified, anxiety incident flagged, trigger analysis correct, alert generated
- **Priority**: P0

---

## Agent 3: Progress Analyst (Trend Detection & Alerts)

### PA-01: Maya's G1 (Greetings) - Improving Trend
- **Test ID**: PA-01
- **Agent**: Progress Analyst
- **Input**: Maya's G1 trial history (30% → 40% → 60% → 70% → 80%, dates 3/15 to 4/03)
- **Expected Output**:
  - Trend detection: **"improving"** (5-point upward trajectory, R² > 0.95)
  - Status: "On track; target met as of 4/3"
  - Alert: `false` (no intervention needed)
  - Confidence: "high" (5 data points, clear linear improvement)
  - Days to mastery: "Already mastered as of 4/3"
  - Teacher note: "Peer buddy program + reinforcer stickers highly effective"
- **Pass Criteria**: Trend correctly identified as "improving", alert = false, confidence high, mastery detection accurate
- **Priority**: P0

### PA-02: Maya's G2 (Directions) - Plateau Then Breakthrough
- **Test ID**: PA-02
- **Agent**: Progress Analyst
- **Input**: Maya's G2 trial history (50% → 38% → 50% → 63% → 75%, dates 3/15 to 4/03)
- **Expected Output**:
  - Trend detection: **"improving"** (despite plateau, recent breakthrough evident)
  - Plateau identified: 3/15-3/22 (days 1-8) at ~45% baseline
  - Breakthrough date: ~3/29 with verbal cueing added
  - Status: "Met target on 4/3; intervention effective"
  - Alert: `false` (breakthrough occurred; no escalation needed)
  - Notes: "Intervention: visual checklist prompts + verbal cueing ('listen with your whole body'). Replicate across contexts."
- **Pass Criteria**: Plateau detection correct, breakthrough identified, trend correctly labeled, alert false, intervention noted
- **Priority**: P0

### PA-03: Jaylen's G1 (AAC Requesting) - Steady Climb
- **Test ID**: PA-03
- **Agent**: Progress Analyst
- **Input**: Jaylen's G1 trial history (33% → 47% → 60% → 73% → 80%, dates 3/15 to 4/03)
- **Expected Output**:
  - Trend detection: **"on_track"** (steady 12-15% weekly gains)
  - Linear growth pattern identified
  - Mastery projection: "Target (80%) reached 4/3; estimated continued growth to 90%+ by end of month"
  - Confidence: "very high" (5 data points, consistent slope)
  - Alert: `false`
  - Coaching note: "AAC device reinforcement via Thomas stickers working; recommend continuation"
- **Pass Criteria**: Trend "on_track", mastery projection accurate, confidence "very high", growth trajectory calculated
- **Priority**: P1

### PA-04: Sofia's G3 (Written Expression) - Plateaued (Alert!)
- **Test ID**: PA-04
- **Agent**: Progress Analyst
- **Input**: Sofia's G3 trial history (40% → 40% → 40% → 60% → 80%, dates 3/15 to 4/03)
- **Expected Output**:
  - Trend detection: **"plateaued"** with recent spike (last 2 data points show breakthrough)
  - Initial plateau: 3/15-3/29 (15 days) at 40% baseline
  - Breakthrough point: ~4/1 with personal narrative + reflective essay assignments
  - Status: "Just met target (80%) on 4/3; BUT plateau was long"
  - Alert: `true` (escalate if this reverts; monitor closely)
  - Recommendation: "Current instruction (personal narrative + reflection prompts) IS effective. Continue this approach. If plateau recurs, shift to mentor-based peer feedback."
- **Pass Criteria**: Plateau correctly identified, breakthrough noted, alert = true (given long plateau history), recommendation provided
- **Priority**: P0

### PA-05: Low Data Point Scenario (Confidence Flag)
- **Test ID**: PA-05
- **Agent**: Progress Analyst
- **Input**: Hypothetical new goal with only 2 data points: 45% on 3/29, 50% on 4/03 (one week)
- **Expected Output**:
  - Trend: "unclear" or "insufficient_data"
  - Confidence: **"low"**
  - Alert: `false` (no alert without confidence)
  - Notes: "Only 2 data points available. Continue monitoring for 3+ weeks before trend analysis. Current direction: slight improvement, but <3 data points = unreliable."
- **Pass Criteria**: Confidence flagged as "low", trend marked "insufficient_data", no false alerts generated
- **Priority**: P2

---

## Agent 4: Material Forge (Instructional Design & Parent Communication)

### MF-01: Lesson Plan for Maya's G1 (Greetings) - Dinosaur Theme
- **Test ID**: MF-01
- **Agent**: Material Forge
- **Input**:
  - Student: Maya (3rd grade, verbal, dinosaur enthusiast)
  - Goal: G1 (Peer Greetings, 80% target)
  - Current performance: 80% (just met)
  - Context: Morning arrival, lunch, specials, free play
- **Expected Output**: Lesson plan document including:
  - Title: "Maya's Dinosaur Greeting Adventures"
  - 3-4 activities:
    1. "Blue the Raptor Greeting Game" (greet toy raptor as daily warm-up)
    2. "Dinosaur Handshake" (peer greeting variation themed to dino movements)
    3. "Dino Sticker Chart" (7-day challenge: earn stickers for greetings across 3+ settings)
  - Visual supports: clipart of Blue raptor, 3-color behavior chart
  - Reinforcers: dinosaur stickers, 5 min water table time
  - Implementation notes: "Use 3-4 word phrases aligned to Maya's communication level"
- **Pass Criteria**: All 3 activities included, dinosaur theme consistently applied, reinforcers match student profile, visual supports present
- **Priority**: P0

### MF-02: Lesson Plan for Jaylen's G1 (AAC Communication) - Train Theme
- **Test ID**: MF-02
- **Agent**: Material Forge
- **Input**:
  - Student: Jaylen (1st grade, non-verbal AAC, Thomas the Tank Engine enthusiast)
  - Goal: G1 (AAC Requesting, just met 80%)
  - Focus: Sustain AAC use, prevent gesture regression
  - Context: Snack requests, activity choice, sensory breaks
- **Expected Output**: Lesson plan including:
  - Title: "Jaylen's AAC Express: All Aboard for Communication!"
  - 3 activities:
    1. "Thomas Station Requests" (AAC device practice at designated "station" with train imagery)
    2. "Ticket Trading Game" (exchange train cards for AAC phrases: "I want trains", "More trains")
    3. "Sensory Express Chart" (visual schedule with AAC prompts for: snack, break, sensory input, activity)
  - AAC-specific supports: large picture buttons, pre-programmed phrases, sensory wheel integration
  - Reinforcers: 2 min Thomas trains play, spinning top
  - Notes: "Reduce gesture acceptance; redirect to AAC device every request"
- **Pass Criteria**: All 3 activities included, train theme applied, AAC-specific supports, sensory integration, reinforcers correct
- **Priority**: P0

### MF-03: Tracking Sheet for Maya's G2 (Following Directions) - Clipboard-Friendly
- **Test ID**: MF-03
- **Agent**: Material Forge
- **Input**:
  - Student: Maya
  - Goal: G2 (Following Directions, just met 75%)
  - Measurement method: 8 trials per session, need tracking sheet
  - Format: teacher can print & carry on clipboard
- **Expected Output**: Tracking sheet with:
  - Header: "Maya's Direction-Following Progress" + 2-week calendar grid
  - Columns: Date | Trial # | Direction (2-step description) | Success (Y/N) | Notes
  - Footer: Weekly % calculation, space for visual checklist sketches
  - Dimensions: half-page (fits on clipboard sideways)
  - Materials: includes small dinosaur sticker icon in corners for reinforcement reference
  - Format: simple grid, large font for quick marking during class
- **Pass Criteria**: All 8 trials fit on one sheet, date grid present, success % calculation built-in, clipboard-friendly layout
- **Priority**: P1

### MF-04: Social Story for Maya (Transition Anxiety) - Carol Gray Format
- **Test ID**: MF-04
- **Agent**: Material Forge
- **Input**:
  - Student: Maya (3rd grade, dinosaur enthusiast, sensory-seeking)
  - Situation: Anxiety during transitions (especially to lunch, specials)
  - Format: Carol Gray (first person, 2:1 ratio: descriptive:coaching sentences)
  - Length: 1 page
  - Theme: dinosaur/Blue raptor
- **Expected Output**: Social story with:
  - Title: "I Am Brave Like Blue the Raptor"
  - Opening: "My name is Maya. I like dinosaurs. Blue the raptor is brave. Blue knows how to move from one place to another."
  - Body sections (2:1 ratio enforced):
    1. Description (2): "Transitions mean we move from one activity to another. Everyone in our class has transitions." / Coaching (1): "I can be brave during transitions like Blue."
    2. Description (2): "Sometimes transitions feel bumpy or loud. My body might feel worried." / Coaching (1): "I can use my noise-canceling headphones to help."
    3. Description (2): "I have special tools to help me: fidget cube, weighted lap pad, water table time." / Coaching (1): "These tools help me feel calm like Blue feels safe in her den."
  - Closing: "I am learning to be brave during transitions. I am like Blue the raptor."
  - Visual supports: Blue raptor image, transition icons, calming strategy boxes
- **Pass Criteria**: 2:1 ratio maintained, first-person perspective, dinosaur theme consistent, all 3 calming strategies included, Carol Gray format correct
- **Priority**: P0

### MF-05: Social Story for Sofia (Schedule Changes) - Carol Gray Format
- **Test ID**: MF-05
- **Agent**: Material Forge
- **Input**:
  - Student: Sofia (5th grade, advanced reader, map/president enthusiast)
  - Situation: Anxiety from unannounced schedule changes
  - Format: Carol Gray (first person, 2:1 ratio, full sentences for reading level)
  - Length: 1-1.5 pages
  - Theme: maps/presidents (predictability theme)
- **Expected Output**: Social story including:
  - Title: "My Schedule Is Like a Map: Sometimes the Route Changes"
  - Opening: "My name is Sofia. I like maps and Presidents. Maps help me understand where places are. My schedule is like a map for my day."
  - Body sections (2:1 ratio, full sentences for 7th-grade reader):
    1. Description (2): "Presidents had to make plans for the country. Sometimes their plans changed because of new information or events. This was normal." / Coaching (1): "Schedule changes happen at school too, and that is normal."
    2. Description (2): "I feel worried when I don't know about schedule changes ahead of time. My body feels confused, like I'm on an old map with new roads." / Coaching (1): "When I feel confused, I can use deep breathing and count to make myself feel better."
    3. Description (2): "I can use my coping tools: making a list of the new plan, doing 4-count breathing, or asking for a 5-minute warning." / Coaching (1): "Using these tools helps me adjust to new schedules."
  - Closing: "I am learning that changes are like exploring new maps. I can use my tools to stay calm."
  - Visual supports: map graphic showing "original route" vs "new route", breathing illustration
- **Pass Criteria**: 2:1 ratio, full sentences appropriate to 7th-grade reader, map/president theme, all 3 coping strategies, anxiety specifically named
- **Priority**: P0

### MF-06: Visual Schedule for Jaylen (Morning Routine) - Concrete & Train-Themed
- **Test ID**: MF-06
- **Agent**: Material Forge
- **Input**:
  - Student: Jaylen (1st grade, non-verbal AAC, train enthusiast, needs concrete steps)
  - Goal: G2 (Visual schedule independence, 90% achieved)
  - Context: Morning routine (arrival through reading)
  - Format: Photo-based with train imagery
- **Expected Output**: Visual schedule including:
  - 5-7 concrete steps with photos of Jaylen + each activity:
    1. [Photo of Jaylen at sensory bin] "Hands-on time" + Thomas train sticker
    2. [Photo of snack] "Morning snack" + train track image
    3. [Photo of AAC device] "Say it! (AAC warm-up)" + speaking mouth icon
    4. [Photo of visual schedule board] "Check schedule" + pointer finger
    5. [Photo of transition song video] "Sing & move" + musical notes
    6. [Photo of work task] "Work time" + train whistle icon
    7. [Photo of cleanup bin] "Clean up" + sweeping icon
  - Layout: 2x4 grid, large photos (5"x5" each), minimal text (single words)
  - Reinforcement: small train sticker for each completed step
  - Material: laminated, positioned at Jaylen's eye level (36" high), Velcro-backed steps for removal
- **Pass Criteria**: All 5-7 steps included, photos of Jaylen present, train theme applied, concrete labels, eye-level positioning specified
- **Priority**: P1

### MF-07: Parent Communication for Maya (Math Performance + Home Activity)
- **Test ID**: MF-07
- **Agent**: Material Forge
- **Input**:
  - Student: Maya
  - Date: 4/3/2026
  - Context: Just completed math worksheet (7/10), G1 at 80%, G2 at 75%
  - Tone: warm, collaborative, growth-focused
- **Expected Output**: Parent letter including:
  - Greeting: "Hi [Parent Name], Maya had another great day!"
  - Math performance: "Today Maya completed a math worksheet with 7 out of 10 correct (70%). This is showing she's getting better at following multi-step directions!"
  - Progress note: "Maya is now greeting classmates 80% of the time — we met her goal! And she's doing really well following two-step directions (75%)."
  - Home activity: "Here's something fun to try at home: practice 2-step directions during play. For example: 'Get your dinosaur and put it in the purple box.' Maya loves dinosaurs, so this might be a great reinforcer!"
  - Sensory note: "The weighted lap pad is really helping Maya feel calm during transitions. Thanks for supporting our plan!"
  - Closing: "Keep up the great work, Maya! We're celebrating your progress every day."
  - Signature: Teacher name + date
  - Visual: small dinosaur clip-art in corner
- **Pass Criteria**: Math result referenced (7/10), warm tone, home activity specific & practical, sensory strategy acknowledged, no jargon
- **Priority**: P0

### MF-08: Parent Communication for Jaylen (AAC Success Celebration)
- **Test ID**: MF-08
- **Agent**: Material Forge
- **Input**:
  - Student: Jaylen
  - Date: 4/3/2026
  - Context: Just met G1 target (80% AAC requesting), PECS log showing success
  - Tone: celebratory, AAC-focused, acknowledging non-verbal strengths
- **Expected Output**: Parent letter including:
  - Greeting: "Hi [Parent Name], Big celebration this week!"
  - AAC achievement: "Jaylen met his communication goal! He is now using his AAC device to request what he wants 80% of the time. This is a huge step toward independence!"
  - Specific wins: "This week Jaylen asked for snack time using the AAC, asked for a break, and requested the sensory swing. These are all things he communicated with gestures before."
  - Thomas reinforcement: "The Thomas the Tank Engine stickers are really motivating Jaylen. Seeing his favorite character helps him stay excited about using AAC."
  - Home practice: "At home, you can practice by giving Jaylen choices (snack vs. drink, trains vs. books) and waiting for him to touch the AAC buttons. Let him lead with what he wants!"
  - Note on methods: "We're celebrating AAC use and gently reducing gesture responses. This helps Jaylen build stronger communication skills."
  - Closing: "Jaylen is an amazing communicator. We're so proud of him!"
  - Visual: train clip-art
- **Pass Criteria**: AAC focus clear, specific behaviors listed, home activity parent-friendly, non-verbal strengths affirmed, celebratory tone
- **Priority**: P0

### MF-09: Administrative Report for Maya (3-Goal Summary + Trends)
- **Test ID**: MF-09
- **Agent**: Material Forge
- **Input**:
  - Student: Maya
  - IEP goals: G1 (Greetings), G2 (Directions), G3 (Self-Regulation)
  - All three at/near target as of 4/3
  - Format: 1-page progress summary for IEP team
- **Expected Output**: Admin report with:
  - Header: "Maya — Progress Summary (Period: 3/15–4/3/2026)"
  - G1 (Greetings):
    - Baseline: 20%, Current: 80%, Target: 80% ✓ MET
    - Trend: Consistent improvement across all settings
    - Intervention: Peer buddy program + dinosaur reinforcer stickers
    - Recommendation: Maintain current supports; consider fading reinforcer frequency
  - G2 (Directions):
    - Baseline: 45%, Current: 75%, Target: 75% ✓ MET
    - Trend: Plateau 3/15–3/22, improvement 3/29 onward
    - Intervention: Visual checklist + verbal cueing ("listen with your whole body")
    - Recommendation: Generalize visual checklist to novel contexts (specials, transitions)
  - G3 (Self-Regulation):
    - Baseline: 3.2 outbursts/day, Current: 1.0/day, Target: 1.0/day ✓ MET
    - Trend: Steady decline; significant improvement post-fire drill adaptation
    - Intervention: Weighted lap pad + noise-canceling headphones + fidget cube routine
    - Recommendation: Continue current sensory supports; monitor for fatigue with reinforcer stickers
  - Summary statement: "Maya has met all three IEP goals through consistent sensory support, visual structuring, and peer relationship building. She demonstrates emerging self-regulation and communication skills across multiple settings."
  - Next steps: "Schedule IEP review to celebrate progress and set new goals for next year."
- **Pass Criteria**: All 3 goals with baseline/current/target, trends identified, interventions specific, recommendations actionable, professional language
- **Priority**: P0

### MF-10: Administrative Report for Sofia (Plateau Alert + Intervention Recommendation)
- **Test ID**: MF-10
- **Agent**: Material Forge
- **Input**:
  - Student: Sofia
  - IEP goals: G1 (Social Communication), G2 (Transitions), G3 (Written Expression)
  - G1: 80% (met), G2: 87% (exceeded), G3: 80% (met, but after long plateau)
  - Flag: G3 had 3-week plateau (40% → 40% → 40%) before breakthrough
  - Format: 1-page report with intervention recommendation
- **Expected Output**: Admin report with:
  - Header: "Sofia — Progress Summary with Intervention Monitoring (Period: 3/15–4/3/2026)"
  - G1 (Social Communication):
    - Baseline: 45%, Current: 80%, Target: 80% ✓ MET
    - Trend: Steady improvement; peer group project accelerated progress
    - Intervention: Social skills coaching + structured peer project
    - Recommendation: Maintain small-group social opportunities; consider peer mentor pairing
  - G2 (Transitions & Schedule Changes):
    - Baseline: 55%, Current: 87%, Target: 85% ✓ EXCEEDED
    - Trend: Consistent improvement; written transition lists + deep breathing highly effective
    - Intervention: 5-minute warning protocol + transition list templates + breathing exercises
    - Recommendation: Fade verbal warnings; monitor for increased independence with self-initiation
  - G3 (Written Expression):
    - Baseline: 40%, Current: 80%, Target: 80% ✓ MET
    - **⚠ ALERT**: Significant plateau noted 3/15–3/29 (3 weeks at 40%)
    - Breakthrough: Shifted to personal narrative + reflective essay assignments (~4/1)
    - Current intervention: Peer feedback + guided reflection prompts
    - **RECOMMENDATION**: "Sofia's 3-week plateau suggests she required explicit instruction in opinion-forming and emotional language. Current approach (personal narrative + reflection) is working. **Monitor closely**: If performance reverts below 75%, escalate to mentor-based peer writing feedback or 1:1 coaching sessions."
  - Summary statement: "Sofia has met all three IEP goals with strong, consistent progress in social communication and executive function. Written expression reached target after instructional pivot; maintain current approach and monitor for sustainability."
  - Risk note: "Long initial plateau in G3 suggests Sofia may benefit from proactive instructional design changes to prevent future plateaus in new goals."
- **Pass Criteria**: All 3 goals reported, plateau explicitly flagged, alert mechanism activated, intervention recommendation specific, risk identified for future planning
- **Priority**: P0

---

## End-to-End Pipeline Tests

### E2E-01: Maya Math Worksheet Photo → Full Pipeline → Dashboard + Lesson Plan + Parent Comm
- **Test ID**: E2E-01
- **Agent**: Full pipeline (Vision → Mapper → Analyst → Forge)
- **Input**: Photo of Maya's math worksheet (7/10 correct, as in VR-01)
- **Expected Output Sequence**:
  1. **Vision Reader**: Transcription (10 items, 7 correct, 2 wrong, 1 skipped)
  2. **IEP Mapper**: Goal mapping (primary G2 "Following Directions" 70%)
  3. **Progress Analyst**: Trend check (G2 now at 75% as of 4/3 from previous data)
  4. **Material Forge Output 1**: Dashboard update
     - G2 progress card: "Following Directions: 75% (NEAR TARGET) ✓"
     - Intervention status: Visual checklist helping
     - Next step: generalize to specials
  5. **Material Forge Output 2**: Lesson plan (MF-01 style, dinosaur-themed, for G1 maintenance)
  6. **Material Forge Output 3**: Parent communication (MF-07 style, math + home activity)
- **Pass Criteria**: All 3 outputs generated, sequence flows logically, no contradictions between agents, parent comm references exact math score (7/10)
- **Priority**: P0

### E2E-02: Jaylen Task Checklist Photo → Full Pipeline → Dashboard + Social Story
- **Test ID**: E2E-02
- **Agent**: Full pipeline (Vision → Mapper → Analyst → Forge)
- **Input**: Photo of Jaylen's task checklist (5/7 completed, as in VR-04)
- **Expected Output Sequence**:
  1. **Vision Reader**: Task recognition (7 steps, 5 completed, 2 pending = 71%)
  2. **IEP Mapper**: Goal alignment (G2 "Visual Schedule Independence"; Jaylen at 90% from previous data; this checklist = 71%, slight dip likely due to disruption)
  3. **Progress Analyst**: Trend analysis (G2 stable at 90%; this one checklist not enough for trend change; confidence = medium)
  4. **Material Forge Output 1**: Dashboard update
     - G2 status: "Visual Schedule Independence: 90% (TARGET MET) ✓"
     - This-checklist note: "71% (within normal variance); investigate if disruption occurred"
  5. **Material Forge Output 2**: Social story for transitions (MF-06 style, train-themed morning routine)
  6. **Material Forge Output 3**: Parent comm (MF-08 style, celebrating AAC wins from parallel tracking)
- **Pass Criteria**: All outputs connected, trend analysis recognizes day-to-day variance, no false alerts
- **Priority**: P1

### E2E-03: Sofia Writing Sample Photo → Full Pipeline → Plateau Alert + Admin Report
- **Test ID**: E2E-03
- **Agent**: Full pipeline (Vision → Mapper → Analyst → Forge) with alert escalation
- **Input**: Photo of Sofia's writing sample (essay-style, post-breakthrough as in VR-06 transcript)
- **Expected Output Sequence**:
  1. **Vision Reader**: Transcription with rubric pre-estimate (realistic essay format, includes feelings/opinions, ~70 words)
  2. **IEP Mapper**: Goal alignment (G3 "Written Expression"; maps to rubric 3/4 = 75% estimate)
  3. **Progress Analyst**: Trend analysis (G3 has history of plateau 3/15–3/29 at 40%; recent breakthrough to 60%–80%; **alert = true** due to plateau history; confidence = high)
  4. **Material Forge Output 1**: Dashboard update with alert banner
     - G3 status: "Written Expression: 80% (TARGET MET) ✓"
     - Alert: "⚠ History of plateau detected. Monitor next 5 data points closely. Current instruction effective; escalate if performance <75%."
  5. **Material Forge Output 2**: Admin report (MF-10 style, full 3-goal summary with G3 plateau alert + intervention recommendation)
- **Pass Criteria**: Plateau history flagged, alert generated, admin report includes monitoring protocol, recommendation actionable
- **Priority**: P0

---

## Test Execution Notes

### Priority Breakdown
- **P0 (Must work for demo)**: VR-01, VR-02, VR-04, VR-05, IM-01, IM-02, IM-03, IM-05, PA-01, PA-02, PA-04, MF-01, MF-02, MF-04, MF-05, MF-07, MF-08, MF-09, MF-10, E2E-01, E2E-03
- **P1 (Should work)**: VR-03, VR-06, VR-07, IM-04, MF-03, MF-06, E2E-02
- **P2 (Nice to have)**: PA-05

### Gold Standard Baseline
These scenarios match the exact student profiles and current performance data (as of 4/3/2026). For demo purposes, use these as the "answer key" until real classroom data is available from Sarah.

### Automation Testing Checklist
- [ ] All Vision Reader OCR outputs match expected transcriptions (±1 item)
- [ ] All IEP Mapper goal assignments use correct student profiles (G1/G2/G3)
- [ ] All Progress Analyst trends match trial history slopes (R² > 0.90 for linear trends)
- [ ] All Material Forge outputs follow respective formats (lesson plan, social story, tracking sheet, parent comm, admin report)
- [ ] End-to-end pipeline flows produce coherent, non-contradictory outputs
- [ ] Alert mechanisms fire at correct thresholds (plateau detection, confidence scoring)
- [ ] Student interests/themes accurately incorporated (Maya=dinosaurs, Jaylen=trains, Sofia=presidents/maps)
