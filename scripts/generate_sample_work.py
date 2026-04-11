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

        # Try to load a cleaner font, fall back to default
        try:
            self.title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            self.header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            self.normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            self.small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except OSError:
            # Fall back to default font
            self.title_font = ImageFont.load_default()
            self.header_font = ImageFont.load_default()
            self.normal_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

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

        print()
        print("✓ All images generated successfully!")


def main():
    """Main entry point."""
    output_dir = "/sessions/modest-festive-cori/mnt/ClassLense/classlens-asd/data/sample_work"
    generator = WorksheetGenerator(output_dir)
    generator.generate_all()


if __name__ == "__main__":
    main()
