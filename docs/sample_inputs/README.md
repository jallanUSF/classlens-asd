# Sample Test Inputs — by student

This folder contains realistic classroom artifacts that would be fed
into ClassLens ASD for testing. Each student has **3 inputs**
chosen to exercise the three IEP goals in that student's docket,
plus (for 7 students) **one PNG photo mockup** of a key artifact —
the kind of image a teacher would actually snap on their phone.

## Structure

    sample_inputs/
    ├── 01_maya/     (3 text + 1 photo)
    ├── 02_jaylen/   (3 text + 1 photo)
    ├── 03_sofia/    (3 text + 1 photo)
    ├── 04_amara/    (3 text + 1 photo)
    ├── 05_ethan/    (3 text + 1 photo)
    ├── 06_lily/     (3 text + 1 photo)
    └── 07_marcus/   (3 text + 1 photo)

## Coverage matrix — which IEP goal each input hits

| Student | Input 1 | Input 2 | Input 3 |
|---------|---------|---------|---------|
| Maya    | G2 (math) + photo | G1 (directions) | G3 (lunch peer) |
| Jaylen  | G1 (AAC) + photo | G2 (fire drill) | G3 (attention) |
| Sofia   | G1 (writing) + photo | G2 (pragmatics) | G3 (flexibility) |
| Amara ⚠ | G1 (inference — strong) | G2 (REGRESSION) + photo | G2 (regression support) |
| Ethan ⚠ | G2 (plateau) + photo | G1 (echolalia%) | G3 (strength/regulation) |
| Lily    | G1 (writing) | G2 (recovery) | G3 (regulation) + photo |
| Marcus  | G1 (toileting) + photo | G2 (pretend play) | G3 (milestone) |

⚠ = the two cases the system needs to handle well: Amara's
regression and Ethan's plateau. Each of those students has at
least one input specifically designed to surface the concerning
pattern.

## Expected system behavior by input type

- **Worksheet / writing sample** → Vision Reader should extract
  handwriting content; IEP Mapper should link to G1 or G2; Progress
  Analyst should score.
- **Para observation log** → skip Vision Reader, IEP Mapper reads
  the structured percentages, Progress Analyst compares to target.
- **Transcript (speech or peer interaction)** → IEP Mapper should
  detect initiation counts and pragmatic language features.
- **Anecdotal note (Marcus slide, Amara cafeteria)** → Progress
  Analyst should treat as qualitative-only and surface as a team
  alert or parent email candidate, not a numerical data point.

## Fixture use

These inputs are safe to commit — all student details are
synthetic. Real names, parents, and schools are not referenced.
Load them via file path and treat them as the pre-OCR / pre-parse
test corpus.
