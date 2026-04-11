#!/usr/bin/env python3
"""
Generate realistic sample student work artifact images for ClassLens ASD Vision Reader testing.
Creates PNG images that simulate classroom worksheets, logs, and checklists.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Tuple
import random


class WorksheetGenerator:
    """Generate realistic-looking student work artifact images."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Image settings
        self.width = 800
        self.height = 1000
        self.bg_color = (252, 251, 248)  # Off-white/cream
        self.line_color = (200, 200, 200)  # Light gray
        self.text_color = (30, 30, 30)  # Dark gray/black

        self.title_font = self._load_font(bold=True, size=36)
        self.header_font = self._load_font(bold=True, size=28)
        self.normal_font = self._load_font(bold=False, size=24)
        self.small_font = self._load_font(bold=False, size=20)

    def _load_font(self, bold: bool, size: int):
        """Try Windows fonts first, then Linux DejaVu, then PIL default."""
        candidates_bold = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        candidates_regular = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in (candidates_bold if bold else candidates_regular):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def create_base_image(self) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
        """Create base image with paper-like background."""
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        return img, draw

    def add_light_grid(self, draw: ImageDraw.ImageDraw, spacing: int = 30):
        """Add subtle grid lines to simulate paper."""
        for x in range(0, self.width, spacing):
            draw.line([(x, 0), (x, self.height)], fill=(240, 240, 240), width=1)
        for y in range(0, self.height, spacing):
            draw.line([(0, y), (self.width, y)], fill=(240, 240, 240), width=1)

    def add_ruled_lines(self, draw: ImageDraw.ImageDraw, start_y: int, spacing: int = 35, count: int = 10):
        """Add ruled lines like notebook paper."""
        for i in range(count):
            y = start_y + (i * spacing)
            if y < self.height - 50:
                draw.line([(50, y), (self.width - 50, y)], fill=self.line_color, width=1)

    def slightly_rotate_text(self, text: str, x: int, y: int, font, draw: ImageDraw.ImageDraw, angle: float = 1.5):
        """Draw text with slight rotation for authenticity."""
        # For simplicity, just draw slightly offset text to simulate hand-writing variation
        offset = int(angle * random.uniform(-1, 1))
        draw.text((x + offset, y), text, font=font, fill=self.text_color)

    def generate_maya_math_worksheet(self):
        """Generate Maya's math worksheet."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Math Practice", font=self.title_font, fill=self.text_color)
        y += 60

        # Name with emoji
        draw.text((50, y), "Name: Maya 🦕", font=self.header_font, fill=self.text_color)
        y += 70

        # Problems
        problems = [
            ("3 + 4 =", "7"),
            ("2 + 5 =", "7"),
            ("6 + 1 =", "7"),
            ("4 + 4 =", "8"),
            ("5 + 2 =", "7"),
            ("1 + 8 =", "9"),  # Wrong: should be 9
            ("7 + 2 =", "9"),  # Wrong answer given as 9 (should be 9)
            ("3 + 5 =", "9"),  # Wrong: should be 8
            ("2 + 3 =", ""),   # Blank/skipped
            ("4 + 3 =", "7"),
        ]

        for i, (problem, answer) in enumerate(problems):
            line_y = y + (i * 45)
            draw.text((80, line_y), f"{i+1}. {problem}", font=self.normal_font, fill=self.text_color)
            if answer:
                # Simulate handwritten answer
                offset = random.randint(-2, 2)
                draw.text((320 + offset, line_y), answer, font=self.normal_font, fill=(50, 100, 200))

        img.save(self.output_dir / "maya_math_worksheet.png")
        print("✓ Created maya_math_worksheet.png")

    def generate_maya_behavior_tally(self):
        """Generate Maya's behavior tally sheet."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Behavior Tally Sheet", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Maya", font=self.header_font, fill=self.text_color)
        y += 70

        # Table setup
        col_width = 130
        row_height = 60
        start_x = 50

        # Headers: Behavior | Mon | Tue | Wed | Thu | Fri
        behaviors = ["Greeted peer", "Followed 2-step", "Calming strategy"]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        # Draw header row
        draw.text((start_x, y), "Behavior", font=self.normal_font, fill=self.text_color)
        for i, day in enumerate(days):
            draw.text((start_x + 200 + (i * col_width), y), day, font=self.normal_font, fill=self.text_color)

        y += 50

        # Data with tally marks and checks
        tally_data = [
            (["|", "|", "||", "|||", "|||"]),  # Greeting improving
            (["||", "|||", "||", "||||", "|||"]),  # Directions variable
            (["✓", "✗", "✓", "✓", "✓"]),  # Calming strategies (mixed with checkmarks)
        ]

        for behavior_idx, behavior in enumerate(behaviors):
            draw.text((start_x, y), behavior, font=self.normal_font, fill=self.text_color)

            for day_idx in range(5):
                x_pos = start_x + 200 + (day_idx * col_width)
                tally = tally_data[behavior_idx][day_idx]
                draw.text((x_pos, y), tally, font=self.normal_font, fill=(50, 100, 200))

            y += row_height

        img.save(self.output_dir / "maya_behavior_tally.png")
        print("✓ Created maya_behavior_tally.png")

    def generate_maya_visual_schedule(self):
        """Generate Maya's visual schedule checklist."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Daily Schedule", font=self.title_font, fill=self.text_color)
        y += 70

        # Schedule items with checkmarks
        items = [
            ("Morning circle", True),
            ("Math centers", True),
            ("Snack", True),
            ("Reading group", True),
            ("Recess", False),
            ("Art", False),
        ]

        for item, checked in items:
            # Draw checkbox
            box_x, box_y = 80, y
            draw.rectangle([box_x, box_y, box_x + 35, box_y + 35], outline=self.text_color, width=2)

            # Draw checkmark if checked
            if checked:
                draw.text((box_x + 5, box_y + 2), "✓", font=self.header_font, fill=(0, 150, 0))

            # Draw text
            draw.text((130, y + 5), item, font=self.normal_font, fill=self.text_color)
            y += 70

        img.save(self.output_dir / "maya_visual_schedule.png")
        print("✓ Created maya_visual_schedule.png")

    def generate_jaylen_task_checklist(self):
        """Generate Jaylen's hand-washing task analysis checklist."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Hand Washing Steps", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Jaylen 🚂", font=self.header_font, fill=self.text_color)
        y += 70

        # Task steps
        steps = [
            ("1. Turn on water", True),
            ("2. Wet hands", True),
            ("3. Get soap", True),
            ("4. Rub hands", True),
            ("5. Rinse", True),
            ("6. Turn off water", False),
            ("7. Dry hands", False),
        ]

        for step, checked in steps:
            # Draw checkbox
            box_x, box_y = 80, y
            draw.rectangle([box_x, box_y, box_x + 35, box_y + 35], outline=self.text_color, width=2)

            # Draw checkmark if checked
            if checked:
                draw.text((box_x + 5, box_y + 2), "✓", font=self.header_font, fill=(0, 150, 0))

            # Draw step text
            draw.text((130, y + 5), step, font=self.normal_font, fill=self.text_color)
            y += 60

        img.save(self.output_dir / "jaylen_task_checklist.png")
        print("✓ Created jaylen_task_checklist.png")

    def generate_jaylen_pecs_log(self):
        """Generate Jaylen's communication/PECS log."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Communication Log", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Jaylen", font=self.header_font, fill=self.text_color)
        y += 70

        # Table headers
        headers = ["Time", "Request", "Method", "Success?"]
        col_widths = [80, 130, 150, 120]
        start_x = 50

        x = start_x
        for header, width in zip(headers, col_widths):
            draw.text((x, y), header, font=self.normal_font, fill=self.text_color)
            x += width

        y += 50

        # Log entries
        entries = [
            ("9:15", "Train", "PECS card", "Yes"),
            ("9:45", "Snack", "Pointed", "No"),
            ("10:30", "Break", "AAC device", "Yes"),
            ("11:00", "Water", "PECS card", "Yes"),
            ("11:45", "Play", "Verbal + PECS", "Prompted"),
        ]

        for entry in entries:
            x = start_x
            for text, width in zip(entry, col_widths):
                draw.text((x, y), text, font=self.normal_font, fill=(50, 100, 200))
                x += width
            y += 50

        img.save(self.output_dir / "jaylen_pecs_log.png")
        print("✓ Created jaylen_pecs_log.png")

    def generate_sofia_writing_sample(self):
        """Generate Sofia's writing sample."""
        img, draw = self.create_base_image()
        y = 30

        # Title/prompt
        draw.text((50, y), "Write about a president you admire.", font=self.header_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Sofia", font=self.normal_font, fill=self.text_color)
        y += 50

        # Add ruled lines
        self.add_ruled_lines(draw, y, spacing=35, count=8)

        # Writing sample - fact-based, no emotion/opinion
        text = [
            "George Washington was the first president. He was",
            "born in 1732 in Virginia. He led the Continental Army",
            "in the Revolutionary War. He served two terms as",
            "president from 1789 to 1797.",
        ]

        for line in text:
            # Simulate slight handwriting variation
            offset = random.randint(-1, 1)
            draw.text((60, y + offset), line, font=self.normal_font, fill=(30, 30, 80))
            y += 35

        img.save(self.output_dir / "sofia_writing_sample.png")
        print("✓ Created sofia_writing_sample.png")

    def generate_sofia_transition_log(self):
        """Generate Sofia's transition tracking sheet."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Transition Tracking Log", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Sofia", font=self.header_font, fill=self.text_color)
        y += 70

        # Table setup
        col_width = 140
        start_x = 50

        # Headers
        headers = ["Transition", "Warning?", "Protest?", "Time to Comply"]
        col_widths = [150, 130, 140, 140]

        x = start_x
        for header, width in zip(headers, col_widths):
            draw.text((x, y), header, font=self.normal_font, fill=self.text_color)
            x += width

        y += 50

        # Transition entries showing impact of lack of warning
        entries = [
            ("Circle→Math", "Yes", "No", "30 sec"),
            ("Math→Snack", "Yes", "No", "15 sec"),
            ("Snack→Reading", "No", "YES - verbal", "3 min"),
            ("Reading→Recess", "Yes", "No", "Immediate"),
        ]

        for entry in entries:
            x = start_x
            for text, width in zip(entry, col_widths):
                # Highlight protest entry in red
                color = (200, 50, 50) if "YES" in text else (50, 100, 200)
                draw.text((x, y), text, font=self.normal_font, fill=color)
                x += width
            y += 60

        img.save(self.output_dir / "sofia_transition_log.png")
        print("✓ Created sofia_transition_log.png")

    def generate_maya_reading_comprehension(self):
        """Generate Maya's reading comprehension passage + questions (maps to G2)."""
        img, draw = self.create_base_image()
        y = 30

        # Title
        draw.text((50, y), "Reading Time", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Maya 🦕", font=self.header_font, fill=self.text_color)
        y += 60

        # Passage
        draw.text((50, y), "Read the story. Then answer the questions.", font=self.small_font, fill=self.text_color)
        y += 40

        passage = [
            "Blue is a raptor. Blue lives in a big park.",
            "Blue likes to run fast. Blue eats fish for",
            "lunch. At night, Blue sleeps in a warm nest.",
        ]
        for line in passage:
            draw.text((60, y), line, font=self.normal_font, fill=(30, 30, 80))
            y += 35

        y += 20
        # Questions with two-step directions baked in
        # Maya is at 70% (close to but not at target of 75%)
        questions = [
            ("1. Circle the name. Then write it.", "Blue", True),   # correct
            ("2. Underline what Blue eats. Then draw it.", "fish", True),  # correct
            ("3. Where does Blue sleep? Write it.", "nest", True),  # correct
            ("4. What does Blue like to do? Draw it.", "", False),  # skipped
            ("5. Is Blue fast? Circle yes or no.", "yes", True),    # correct
        ]

        for q_text, answer, correct in questions:
            draw.text((60, y), q_text, font=self.small_font, fill=self.text_color)
            y += 30
            if answer:
                offset = random.randint(-2, 2)
                color = (50, 100, 200) if correct else (200, 50, 50)
                draw.text((90 + offset, y), f"→ {answer}", font=self.normal_font, fill=color)
            else:
                draw.text((90, y), "→ ___", font=self.normal_font, fill=(180, 180, 180))
            y += 45

        img.save(self.output_dir / "maya_reading_comprehension.png")
        print("✓ Created maya_reading_comprehension.png")

    def generate_maya_sensory_break_log(self):
        """Generate Maya's sensory break request log (maps to G3)."""
        img, draw = self.create_base_image()
        y = 30

        draw.text((50, y), "Sensory Break Log", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Maya", font=self.header_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Date: 2026-04-10", font=self.small_font, fill=self.text_color)
        y += 50

        # Table headers
        headers = ["Time", "Activity", "Requested?", "Break Used"]
        col_widths = [110, 180, 160, 180]
        start_x = 50

        x = start_x
        for header, width in zip(headers, col_widths):
            draw.text((x, y), header, font=self.normal_font, fill=self.text_color)
            x += width
        y += 50

        # 5 opportunities, 4 requested independently (80%)
        entries = [
            ("9:10", "Morning circle", "Yes - self", "weighted pad"),
            ("10:20", "Math centers", "Yes - self", "headphones"),
            ("11:05", "Transition", "No - prompted", "fidget cube"),
            ("12:40", "After lunch", "Yes - self", "weighted pad"),
            ("2:15", "Art room", "Yes - self", "headphones"),
        ]

        for entry in entries:
            x = start_x
            for text, width in zip(entry, col_widths):
                color = (50, 100, 200) if "Yes" in text or "self" in text else (200, 120, 50) if "prompt" in text else (50, 100, 200)
                draw.text((x, y), text, font=self.small_font, fill=color)
                x += width
            y += 50

        y += 20
        draw.text((50, y), "Outbursts today: 1 (brief, recovered with pad)", font=self.small_font, fill=(30, 30, 80))

        img.save(self.output_dir / "maya_sensory_break_log.png")
        print("✓ Created maya_sensory_break_log.png")

    def generate_jaylen_choice_board(self):
        """Generate Jaylen's PECS/visual choice board log (maps to G1)."""
        img, draw = self.create_base_image()
        y = 30

        draw.text((50, y), "Choice Board Log", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Jaylen 🚂", font=self.header_font, fill=self.text_color)
        y += 50
        draw.text((50, y), "Date: 2026-04-10", font=self.small_font, fill=self.text_color)
        y += 50

        # Headers
        headers = ["Time", "Choice", "Method", "Success?"]
        col_widths = [110, 200, 200, 160]
        start_x = 50

        x = start_x
        for header, width in zip(headers, col_widths):
            draw.text((x, y), header, font=self.normal_font, fill=self.text_color)
            x += width
        y += 50

        # 15 opportunities, 11 independent AAC (73% - just below 80 target)
        entries = [
            ("8:45",  "Snack - crackers", "AAC device", "Yes"),
            ("9:15",  "Activity - trains", "PECS card",  "Yes"),
            ("9:40",  "Break",             "AAC device", "Yes"),
            ("10:10", "Snack - juice",     "Pointed",    "No - prompt"),
            ("10:35", "Activity - spin",   "AAC device", "Yes"),
            ("11:00", "Sensory swing",     "AAC device", "Yes"),
            ("11:30", "Snack - pretzel",   "PECS card",  "Yes"),
            ("12:00", "Activity - Thomas", "AAC device", "Yes"),
            ("12:35", "Break",             "Cried",      "No - prompt"),
            ("1:10",  "Water",             "AAC device", "Yes"),
            ("1:45",  "Thomas trains",     "AAC device", "Yes"),
        ]

        for entry in entries:
            x = start_x
            for text, width in zip(entry, col_widths):
                if "No" in text:
                    color = (200, 50, 50)
                elif "Yes" in text:
                    color = (50, 150, 50)
                else:
                    color = (50, 100, 200)
                draw.text((x, y), text, font=self.small_font, fill=color)
                x += width
            y += 42

        img.save(self.output_dir / "jaylen_choice_board.png")
        print("✓ Created jaylen_choice_board.png")

    def generate_jaylen_turn_taking_tally(self):
        """Generate Jaylen's turn-taking tally from therapy session (maps to G3)."""
        img, draw = self.create_base_image()
        y = 30

        draw.text((50, y), "Turn-Taking Tally", font=self.title_font, fill=self.text_color)
        y += 60
        draw.text((50, y), "Name: Jaylen", font=self.header_font, fill=self.text_color)
        y += 50
        draw.text((50, y), "Session: 1:1 with therapist", font=self.small_font, fill=self.text_color)
        y += 30
        draw.text((50, y), "Activity: Thomas trains", font=self.small_font, fill=self.text_color)
        y += 30
        draw.text((50, y), "Date: 2026-04-10", font=self.small_font, fill=self.text_color)
        y += 50

        # Table: opportunity | waited for turn | monopolized
        headers = ["Opportunity", "Waited?", "Notes"]
        col_widths = [200, 160, 290]
        start_x = 50

        x = start_x
        for header, width in zip(headers, col_widths):
            draw.text((x, y), header, font=self.normal_font, fill=self.text_color)
            x += width
        y += 50

        # 5 opportunities, 3 successes (60%)
        entries = [
            ("1. Pass Gordon",  "Yes",  "brief wait, smiled"),
            ("2. Pass Percy",   "No",   "grabbed back quickly"),
            ("3. Share track",  "Yes",  "allowed adult turn"),
            ("4. Pass Gordon",  "No",   "protested briefly"),
            ("5. Build tunnel", "Yes",  "longest wait so far"),
        ]

        for entry in entries:
            x = start_x
            for i, (text, width) in enumerate(zip(entry, col_widths)):
                if i == 1:
                    color = (50, 150, 50) if text == "Yes" else (200, 50, 50)
                else:
                    color = (50, 100, 200)
                draw.text((x, y), text, font=self.small_font, fill=color)
                x += width
            y += 55

        y += 20
        draw.text((50, y), "Total waited: 3 / 5 (60%)", font=self.normal_font, fill=(30, 30, 80))

        img.save(self.output_dir / "jaylen_turn_taking_tally.png")
        print("✓ Created jaylen_turn_taking_tally.png")

    # ------------------------------------------------------------------
    # Extended artifacts — underserved students + Sofia top-up
    # ------------------------------------------------------------------

    def _draw_table(self, draw, headers, col_widths, rows, start_x, start_y,
                    row_height=50, value_color=(50, 100, 200)):
        """Helper: draw a simple column-based table. Returns y after last row."""
        x = start_x
        for header, width in zip(headers, col_widths):
            draw.text((x, start_y), header, font=self.normal_font, fill=self.text_color)
            x += width
        y = start_y + row_height
        for row in rows:
            x = start_x
            for i, (text, width) in enumerate(zip(row, col_widths)):
                color = value_color
                if "No" in text or "✗" in text or "FAIL" in text or "ALERT" in text:
                    color = (200, 50, 50)
                elif "Yes" in text or "✓" in text or "PASS" in text:
                    color = (50, 150, 50)
                draw.text((x, y), text, font=self.small_font, fill=color)
                x += width
            y += row_height
        return y

    def generate_amara_inference_probe(self):
        """Amara G1: reading comprehension inferential probe. 7/10 = 70% target hit."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Inferential Reading Probe", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Amara   Grade 6", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   Passage: 'The Last Letter'", font=self.small_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Strategy: MHA character mapping (Todoroki = conflicted)", font=self.small_font, fill=(120, 80, 180))
        y += 50

        questions = [
            ("1. Why did Ren hide the letter from his sister?", "Scared she'd be mad - like Todoroki", True),
            ("2. How does Mia feel when she finds it?", "Betrayed, then sad", True),
            ("3. What does the rain symbolize in paragraph 4?", "Her sadness coming out", True),
            ("4. Predict: will Ren apologize?", "Yes - he feels guilty", True),
            ("5. Why doesn't Mia answer right away?", "(blank)", False),
            ("6. How would you feel in Ren's place?", "Guilty and scared", True),
            ("7. What does 'a weight lifted' mean here?", "He feels better", True),
            ("8. Why did the author mention the photo?", "To remind them of good times", True),
            ("9. Is Mia forgiving or still angry at the end?", "Angry still", False),
            ("10. What lesson does Ren learn?", "(blank)", False),
        ]
        for q, a, correct in questions:
            draw.text((60, y), q, font=self.small_font, fill=self.text_color)
            y += 26
            mark = "✓" if correct else "✗"
            color = (50, 150, 50) if correct else (200, 50, 50)
            draw.text((90, y), f"{mark} {a}", font=self.small_font, fill=color)
            y += 32
        y += 10
        draw.text((50, y), "Score: 7 / 10 = 70%  -  TARGET MET", font=self.normal_font, fill=(30, 100, 30))

        img.save(self.output_dir / "amara_inference_probe.png")
        print("+ amara_inference_probe.png")

    def generate_amara_social_tracker(self):
        """Amara G2: social skills facilitator tracking sheet. 3/10 = 30% - REGRESSION."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Social Skills Tracking Sheet", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Amara   Facilitator: Ms. Reyes", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Week of: 2026-04-06 to 2026-04-10", font=self.small_font, fill=self.text_color)
        y += 50

        headers = ["Setting", "Limit turns?", "Asked Q?", "Success?"]
        col_widths = [200, 150, 130, 150]
        rows = [
            ("Mon - Lunch table",  "No - 4min", "No",  "No"),
            ("Mon - Social group", "Yes",       "No",  "No"),
            ("Tue - Lunch alone",  "n/a",       "n/a", "No"),
            ("Tue - Library",      "Yes",       "Yes", "Yes"),
            ("Wed - Lunch alone",  "n/a",       "n/a", "No"),
            ("Wed - Group proj",   "No - 3min", "No",  "No"),
            ("Thu - Recess",       "Yes",       "No",  "No"),
            ("Thu - Art class",    "Yes",       "Yes", "Yes"),
            ("Fri - Lunch alone",  "n/a",       "n/a", "No"),
            ("Fri - Social group", "Yes",       "Yes", "Yes"),
        ]
        y = self._draw_table(draw, headers, col_widths, rows, 50, y, row_height=48)
        y += 10
        draw.text((50, y), "Success: 3 / 10 = 30%  -  DOWN from 40% last week", font=self.normal_font, fill=(200, 50, 50))
        y += 40
        draw.text((50, y), "Notes: Ate alone 3 days. Refused talk ticket system.", font=self.small_font, fill=self.text_color)
        y += 30
        draw.text((50, y), "New student in lunch group. Amara withdrew.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "amara_social_tracker.png")
        print("+ amara_social_tracker.png")

    def generate_ethan_spontaneous_speech(self):
        """Ethan G1: SLP tally of spontaneous vs scripted utterances. 7/10 = 70% MET."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Spontaneous Speech Tally", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Ethan   SLP: Ms. Okafor", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   Setting: Classroom + Lunch", font=self.small_font, fill=self.text_color)
        y += 50

        headers = ["Opportunity", "Utterance", "Type", "Count?"]
        col_widths = [180, 240, 140, 100]
        rows = [
            ("Circle - weather",   "'tornado watch today'", "spontaneous", "Yes"),
            ("Center - fans",      "'I want fan'",          "spontaneous", "Yes"),
            ("Snack",              "'more please'",         "spontaneous", "Yes"),
            ("Peer offers PlayDo", "'no thank you'",        "spontaneous", "Yes"),
            ("Circle greeting",    "'good morning class'",  "echolalic",   "No"),
            ("Weather unit",       "'seven clouds!'",       "spontaneous", "Yes"),
            ("Transition",         "'breaking weather...'", "echolalic",   "No"),
            ("Lunch",              "'what for lunch?'",     "spontaneous", "Yes"),
            ("Centers",            "(silent)",              "none",        "No"),
            ("Playground",         "'look - seven birds!'", "spontaneous", "Yes"),
        ]
        y = self._draw_table(draw, headers, col_widths, rows, 50, y, row_height=46)
        y += 10
        draw.text((50, y), "Spontaneous: 7 / 10 = 70%  -  TARGET MET", font=self.normal_font, fill=(30, 100, 30))
        y += 38
        draw.text((50, y), "Motivating topics pull real language: weather + 7s.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "ethan_spontaneous_speech.png")
        print("+ ethan_spontaneous_speech.png")

    def generate_ethan_handwriting_probe(self):
        """Ethan G2: OT handwriting sample. 5/10 legible = 45% PLATEAU (alert)."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "OT Handwriting Probe", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Ethan   OT: Mr. Patel", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   Tool: slant board + pencil grip", font=self.small_font, fill=self.text_color)
        y += 50

        draw.text((50, y), "Prompt: Write 10 target letters on lined paper.", font=self.small_font, fill=self.text_color)
        y += 40

        self.add_ruled_lines(draw, y, spacing=35, count=8)

        letters = [
            ("E", True),  ("t", False), ("H", True),  ("a", False),
            ("n", False), ("R", True),  ("f", False), ("7", True),
            ("S", True),  ("m", False),
        ]
        for i, (letter, legible) in enumerate(letters):
            col = i % 5
            row = i // 5
            x = 70 + col * 130
            ly = y + 10 + row * 80
            color = (30, 30, 80) if legible else (180, 80, 50)
            draw.text((x, ly), letter, font=self.title_font, fill=color)
            mark = "OK" if legible else "X"
            draw.text((x + 40, ly + 8), mark, font=self.small_font, fill=color)
        y += 180

        draw.text((50, y), "Legible: 5 / 10 = 45%  -  NO CHANGE 4 weeks", font=self.normal_font, fill=(200, 50, 50))
        y += 38
        draw.text((50, y), "Recommend: vibrating pen, 5-min bursts, fan break.", font=self.small_font, fill=self.text_color)
        y += 28
        draw.text((50, y), "Refused writing after 4 minutes. Switched to scripting.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "ethan_handwriting_probe.png")
        print("+ ethan_handwriting_probe.png")

    def generate_lily_conversation_log(self):
        """Lily G1: SLP conversation + emotion-id log. 8/10 = 80% MET."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Pragmatic Language Log", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Lily   SLP: Ms. Tran", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10", font=self.small_font, fill=self.text_color)
        y += 50

        draw.text((50, y), "Part A - Topic maintenance (3+ exchanges on peer topic)", font=self.normal_font, fill=self.text_color)
        y += 40
        topics = [
            ("Mia  -  soccer",       "4 exchanges", True),
            ("Jordan  -  dogs",      "3 exchanges", True),
            ("Group  -  field trip", "monologue", False),
            ("Owen  -  Minecraft",   "5 exchanges", True),
            ("Mia  -  family trip",  "3 exchanges", True),
        ]
        for peer, result, ok in topics:
            mark = "PASS" if ok else "FAIL"
            color = (50, 150, 50) if ok else (200, 50, 50)
            draw.text((70, y), f"- {peer}", font=self.small_font, fill=self.text_color)
            draw.text((340, y), result, font=self.small_font, fill=(50, 100, 200))
            draw.text((500, y), mark, font=self.small_font, fill=color)
            y += 32
        y += 15

        draw.text((50, y), "Part B - Emotion identification from photos (5 cards)", font=self.normal_font, fill=self.text_color)
        y += 40
        emotions = [
            ("happy",       "happy",      True),
            ("frustrated",  "frustrated", True),
            ("nervous",     "nervous",    True),
            ("jealous",     "mad",        False),
            ("embarrassed", "embarrassed", True),
        ]
        for target, guess, ok in emotions:
            mark = "PASS" if ok else "FAIL"
            color = (50, 150, 50) if ok else (200, 50, 50)
            draw.text((70, y), f"Target: {target}", font=self.small_font, fill=self.text_color)
            draw.text((300, y), f"Said: {guess}", font=self.small_font, fill=(50, 100, 200))
            draw.text((500, y), mark, font=self.small_font, fill=color)
            y += 32

        y += 20
        draw.text((50, y), "Total: 8 / 10 = 80%  -  TARGET MET", font=self.normal_font, fill=(30, 100, 30))
        y += 38
        draw.text((50, y), "Noticed peer's frustration during math partner work", font=self.small_font, fill=self.text_color)
        y += 28
        draw.text((50, y), "and offered help unprompted. First time!", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "lily_conversation_log.png")
        print("+ lily_conversation_log.png")

    def generate_lily_coping_strategy(self):
        """Lily G3: coping strategy vs shutdown log. 7/10 = 70% improving."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Coping Strategy Log", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Lily", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   (5-point scale tracking)", font=self.small_font, fill=self.text_color)
        y += 50

        headers = ["Trigger", "Rating", "Strategy Used", "Outcome"]
        col_widths = [220, 110, 220, 130]
        rows = [
            ("Group math - peer disagreed", "4/5", "Worry stone",    "Coped"),
            ("Science group - loud",        "3/5", "Calm corner",    "Coped"),
            ("Partner reading - wrong book", "3/5", "Deep breathing", "Coped"),
            ("Timed math test",             "4/5", "Deep breathing", "Coped"),
            ("Art - paint smell",           "4/5", "Requested break", "Coped"),
            ("Lunch - spilled milk",        "5/5", "Cried",          "Shutdown"),
            ("Group poster disagreement",   "4/5", "'I need a min'", "Coped"),
            ("Science fair prep",           "4/5", "Pre-task list",  "Coped"),
            ("Cafeteria - fire drill",      "5/5", "Froze",          "Shutdown"),
            ("PE dodgeball - tag",          "4/5", "Step out line",  "Shutdown"),
        ]
        y = self._draw_table(draw, headers, col_widths, rows, 50, y, row_height=48)
        y += 10
        draw.text((50, y), "Coped: 7 / 10 = 70%  -  Nearing 75% target", font=self.normal_font, fill=(30, 100, 30))
        y += 38
        draw.text((50, y), "Fire drill still a loss  -  smell + noise compound trigger.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "lily_coping_strategy.png")
        print("+ lily_coping_strategy.png")

    def generate_marcus_aac_request_log(self):
        """Marcus G1: AAC/PECS independent request log. 5/10 = 50% MET."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "AAC + PECS Request Log", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Marcus   K  Age 5", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   Device: TouchChat (24-icon)", font=self.small_font, fill=self.text_color)
        y += 50

        headers = ["Time", "Request", "Modality", "Independent?"]
        col_widths = [110, 220, 200, 170]
        rows = [
            ("8:30",  "bubbles",       "PECS card", "Yes"),
            ("9:05",  "Bluey",         "AAC icon",  "Yes"),
            ("9:40",  "drum",          "AAC icon",  "Yes"),
            ("10:15", "more crackers", "AAC + 'more'", "Yes"),
            ("10:45", "help (blocks)", "AAC icon",  "Yes"),
            ("11:10", "bathroom",      "Led adult", "No - prompt"),
            ("11:45", "eat",           "PECS card", "Yes"),
            ("12:30", "bubbles",       "PECS card", "Yes"),
            ("1:00",  "Bluey",         "Pulled arm", "No - prompt"),
            ("1:40",  "playground",    "AAC - 2 pages", "Yes"),
        ]
        y = self._draw_table(draw, headers, col_widths, rows, 50, y, row_height=44)
        y += 10
        draw.text((50, y), "Independent: 8 / 10 = 80%  -  EXCEEDS 50% target", font=self.normal_font, fill=(30, 100, 30))
        y += 38
        draw.text((50, y), "Marcus said 'more' verbally WHILE pressing icon  -  multimodal.", font=self.small_font, fill=self.text_color)
        y += 28
        draw.text((50, y), "Navigated 2 AAC pages to find 'playground'. Huge win.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "marcus_aac_request_log.png")
        print("+ marcus_aac_request_log.png")

    def generate_marcus_playground_log(self):
        """Marcus G3: adapted PE playground observation. 5/10 = 50% MET. First big slide."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Adapted PE  -  Playground", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Marcus   Observer: Coach Diaz", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   Recess (low-crowd access)", font=self.small_font, fill=self.text_color)
        y += 50

        headers = ["Equipment", "Attempt?", "Safety rules", "Notes"]
        col_widths = [200, 140, 170, 190]
        rows = [
            ("Small slide",   "Yes - solo", "Feet first",    "Independent"),
            ("Small ladder",  "Yes",        "One hand rail", "Aide nearby"),
            ("Swings",        "Yes",        "Waited turn",   "1 peer turn"),
            ("Big slide",     "YES - first", "Feet first",   "Class cheered"),
            ("Big ladder",    "Yes",        "Both hands",    "With spotter"),
            ("Monkey bars",   "No",         "n/a",           "Watched peer"),
            ("Sandbox",       "Yes",        "n/a",           "Wet texture - brief"),
            ("Merry-go-round", "Yes",       "Held bar",      "Loved spin"),
            ("Climbing wall", "No",         "n/a",           "Too crowded"),
            ("Seesaw",        "Yes",        "Waited turn",   "With Caleb"),
        ]
        y = self._draw_table(draw, headers, col_widths, rows, 50, y, row_height=46)
        y += 10
        draw.text((50, y), "Safe navigation: 8 / 10 = 80%  -  EXCEEDS 50% target", font=self.normal_font, fill=(30, 100, 30))
        y += 38
        draw.text((50, y), "BIG SLIDE for the first time. Followed 'feet first'.", font=self.small_font, fill=(120, 80, 180))
        y += 28
        draw.text((50, y), "Tolerated 5 peers on equipment at once. Aide stepped back.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "marcus_playground_log.png")
        print("+ marcus_playground_log.png")

    def generate_sofia_peer_conversation_tally(self):
        """Sofia G1: peer conversation initiation tally. 9/10 = 90% EXCEEDS 80%."""
        img, draw = self.create_base_image()
        y = 30
        draw.text((50, y), "Peer Conversation Tally", font=self.title_font, fill=self.text_color)
        y += 55
        draw.text((50, y), "Name: Sofia   Counselor: Mr. Kim", font=self.header_font, fill=self.text_color)
        y += 45
        draw.text((50, y), "Date: 2026-04-10   Group project week", font=self.small_font, fill=self.text_color)
        y += 50

        draw.text((50, y), "Criteria: asked Q + showed interest + eye contact", font=self.small_font, fill=self.text_color)
        y += 40

        headers = ["Setting", "Topic", "Q asked?", "Score"]
        col_widths = [200, 220, 130, 130]
        rows = [
            ("Mon - Morning table", "Peer's weekend",  "Yes", "PASS"),
            ("Mon - Group proj",    "State capitals",  "Yes", "PASS"),
            ("Tue - Lunch",         "Peer's dog",      "Yes", "PASS"),
            ("Tue - Recess",        "Map game",        "Yes", "PASS"),
            ("Wed - Group proj",    "Project rubric",  "Yes", "PASS"),
            ("Wed - Library",       "Reading choices", "Yes", "PASS"),
            ("Thu - Lunch",         "Presidents",      "No - monologue", "FAIL"),
            ("Thu - Group proj",    "Teammate idea",   "Yes", "PASS"),
            ("Fri - Morning table", "Peer's hobby",    "Yes", "PASS"),
            ("Fri - Group present", "Shared credit",   "Yes", "PASS"),
        ]
        y = self._draw_table(draw, headers, col_widths, rows, 50, y, row_height=48)
        y += 10
        draw.text((50, y), "Initiations with criteria: 9 / 10 = 90%", font=self.normal_font, fill=(30, 100, 30))
        y += 38
        draw.text((50, y), "EXCEEDS 80% target. Group project anchored shared interest.", font=self.small_font, fill=self.text_color)
        y += 28
        draw.text((50, y), "One slip Thu lunch - reverted to monologue when tired.", font=self.small_font, fill=self.text_color)

        img.save(self.output_dir / "sofia_peer_conversation_tally.png")
        print("+ sofia_peer_conversation_tally.png")

    def generate_all(self):
        """Generate all sample work images."""
        print(f"Generating sample work images in {self.output_dir}...")
        print()

        self.generate_maya_math_worksheet()
        self.generate_maya_behavior_tally()
        self.generate_maya_visual_schedule()
        self.generate_jaylen_task_checklist()
        self.generate_jaylen_pecs_log()
        self.generate_sofia_writing_sample()
        self.generate_sofia_transition_log()
        self.generate_maya_reading_comprehension()
        self.generate_maya_sensory_break_log()
        self.generate_jaylen_choice_board()
        self.generate_jaylen_turn_taking_tally()

        # Extended artifacts for underserved students
        self.generate_amara_inference_probe()
        self.generate_amara_social_tracker()
        self.generate_ethan_spontaneous_speech()
        self.generate_ethan_handwriting_probe()
        self.generate_lily_conversation_log()
        self.generate_lily_coping_strategy()
        self.generate_marcus_aac_request_log()
        self.generate_marcus_playground_log()
        self.generate_sofia_peer_conversation_tally()

        print()
        print("✓ All images generated successfully!")

    def generate_extended_only(self):
        """Generate only the new artifacts for underserved students."""
        print(f"Generating extended sample work images in {self.output_dir}...")
        print()
        self.generate_amara_inference_probe()
        self.generate_amara_social_tracker()
        self.generate_ethan_spontaneous_speech()
        self.generate_ethan_handwriting_probe()
        self.generate_lily_conversation_log()
        self.generate_lily_coping_strategy()
        self.generate_marcus_aac_request_log()
        self.generate_marcus_playground_log()
        self.generate_sofia_peer_conversation_tally()
        print()
        print("Done.")


def main():
    """Main entry point."""
    import sys
    output_dir = Path(__file__).resolve().parent.parent / "data" / "sample_work"
    generator = WorksheetGenerator(str(output_dir))
    if len(sys.argv) > 1 and sys.argv[1] == "--extended":
        generator.generate_extended_only()
    else:
        generator.generate_all()


if __name__ == "__main__":
    main()
