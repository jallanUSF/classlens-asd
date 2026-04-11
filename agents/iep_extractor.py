"""
Agent: IEP Extractor
PDF or image of an IEP document -> structured IEP goals, accommodations, and
student demographic fields.

Uses Gemma 4 multimodal + function calling. Renders PDF pages to high-DPI PNGs
via pymupdf so the multimodal model can see them. Merges per-page extractions
into a single result dict.

Schema-compatible with schemas/student_profile.StudentProfile so the downstream
POST /api/students endpoint can consume the merged extraction directly.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agents.base import BaseAgent
from prompts.templates import IEP_EXTRACTOR_SYSTEM, IEP_EXTRACTOR_USER
from schemas.tools import EXTRACT_IEP_CONTENT

logger = logging.getLogger(__name__)

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
_PDF_EXTS = {".pdf"}


class IEPExtractor(BaseAgent):
    """Reads an IEP PDF or image and returns structured IEP content."""

    # Empty shell used as the base for merging and as the graceful-degrade
    # return value when the pipeline can't run at all.
    _EMPTY: Dict[str, Any] = {
        "student_name": "",
        "grade": None,
        "asd_level": None,
        "communication_level": "",
        "interests": [],
        "iep_goals": [],
        "accommodations": [],
        "notes": "",
    }

    def extract(
        self,
        document_path: str,
        source_filename: Optional[str] = None,
        max_pages: int = 2,
    ) -> Dict[str, Any]:
        """
        Extract IEP content from a document file.

        Args:
            document_path: Absolute path to the PDF or image on disk.
            source_filename: Original client-supplied filename for the prompt
                context. Defaults to the basename of document_path.
            max_pages: Maximum number of PDF pages to process. Defaults to 2
                to keep the demo fast.

        Returns:
            A dict with keys: student_name, grade, asd_level,
            communication_level, interests, iep_goals, accommodations, notes.
            Always returns the shape — empty fields if extraction fails.
        """
        path = Path(document_path)
        if not path.exists():
            logger.error("IEPExtractor: document not found at %s", document_path)
            return {**self._EMPTY, "notes": f"Document not found: {document_path}"}

        source = source_filename or path.name
        ext = path.suffix.lower()

        if ext in _IMAGE_EXTS:
            return self._extract_from_image(str(path), source, page_number=1)

        if ext in _PDF_EXTS:
            return self._extract_from_pdf(path, source, max_pages=max_pages)

        return {
            **self._EMPTY,
            "notes": f"Unsupported document type: {ext}",
        }

    # ------------------------------------------------------------------
    # PDF handling
    # ------------------------------------------------------------------

    def _extract_from_pdf(
        self,
        pdf_path: Path,
        source: str,
        max_pages: int,
    ) -> Dict[str, Any]:
        """Render up to max_pages of the PDF to PNGs and extract per page."""
        try:
            import fitz  # pymupdf
        except ModuleNotFoundError:
            logger.warning(
                "pymupdf not installed — cannot render PDF %s. "
                "Returning empty extraction.",
                pdf_path,
            )
            return {
                **self._EMPTY,
                "notes": (
                    "pymupdf (fitz) is not installed on this backend, so the "
                    "IEP PDF could not be rendered for extraction. Install "
                    "pymupdf to enable IEP auto-extraction."
                ),
            }

        temp_paths: List[str] = []
        per_page_results: List[Dict[str, Any]] = []
        try:
            doc = fitz.open(str(pdf_path))
            try:
                page_count = min(len(doc), max_pages)
                if page_count == 0:
                    return {**self._EMPTY, "notes": "PDF has no pages."}

                zoom = fitz.Matrix(2.0, 2.0)  # ~144 DPI — readable for OCR
                for i in range(page_count):
                    page = doc.load_page(i)
                    pix = page.get_pixmap(matrix=zoom, alpha=False)
                    png_bytes = pix.tobytes("png")

                    tmp = tempfile.NamedTemporaryFile(
                        suffix=".png", delete=False
                    )
                    tmp.write(png_bytes)
                    tmp.flush()
                    tmp.close()
                    temp_paths.append(tmp.name)

                    page_result = self._extract_from_image(
                        tmp.name, source, page_number=i + 1
                    )
                    per_page_results.append(page_result)
            finally:
                doc.close()
        except Exception as exc:  # noqa: BLE001 — degrade gracefully
            logger.exception("IEPExtractor: failed to render PDF: %s", exc)
            return {
                **self._EMPTY,
                "notes": f"Failed to render PDF: {exc}",
            }
        finally:
            for p in temp_paths:
                try:
                    os.unlink(p)
                except OSError:
                    pass

        return self._merge_pages(per_page_results)

    # ------------------------------------------------------------------
    # Image handling (single page)
    # ------------------------------------------------------------------

    def _extract_from_image(
        self,
        image_path: str,
        source: str,
        page_number: int,
    ) -> Dict[str, Any]:
        """Call Gemma with one image and coerce the result into our schema."""
        prompt = IEP_EXTRACTOR_USER.format(
            source_filename=source,
            page_number=page_number,
        )

        try:
            result = self.client.generate_with_tools(
                prompt=prompt,
                tools=[EXTRACT_IEP_CONTENT],
                system=IEP_EXTRACTOR_SYSTEM,
                image_path=image_path,
            )
        except Exception as exc:  # noqa: BLE001 — never crash the endpoint
            logger.exception("IEPExtractor: model call failed: %s", exc)
            return {
                **self._EMPTY,
                "notes": f"Model call failed: {exc}",
            }

        # Function calling succeeded — the args should already match our schema
        if isinstance(result, dict) and result.get("function") == "extract_iep_content":
            return self._coerce(result.get("args") or {})

        # Function calling was unused; try to parse JSON out of text
        if isinstance(result, dict) and "text" in result:
            parsed = self._parse_fallback(result["text"])
            return self._coerce(parsed)

        # Unknown shape — best-effort
        if isinstance(result, dict):
            return self._coerce(result)

        return {**self._EMPTY, "notes": "Unrecognized model response."}

    # ------------------------------------------------------------------
    # Merging + coercion
    # ------------------------------------------------------------------

    def _coerce(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Force whatever the model returned into our stable shape."""
        if not isinstance(raw, dict):
            return dict(self._EMPTY)

        def _as_str(val: Any) -> str:
            return val.strip() if isinstance(val, str) else ""

        def _as_int(val: Any) -> Optional[int]:
            if isinstance(val, bool):
                return None
            if isinstance(val, int):
                return val
            if isinstance(val, str):
                try:
                    return int(val.strip())
                except ValueError:
                    return None
            return None

        def _as_str_list(val: Any) -> List[str]:
            if not isinstance(val, list):
                return []
            out: List[str] = []
            for item in val:
                s = _as_str(item)
                if s:
                    out.append(s)
            return out

        goals_raw = raw.get("iep_goals") if isinstance(raw.get("iep_goals"), list) else []
        goals: List[Dict[str, Any]] = []
        for g in goals_raw:
            if not isinstance(g, dict):
                continue
            desc = _as_str(g.get("description"))
            if not desc:
                continue  # description is the load-bearing field
            goals.append(
                {
                    "goal_id": _as_str(g.get("goal_id")) or f"GOAL_{len(goals) + 1:02d}",
                    "domain": _as_str(g.get("domain")) or "academic",
                    "description": desc,
                    "baseline": _as_str(g.get("baseline")),
                    "target": _as_str(g.get("target")),
                    "measurement_method": _as_str(g.get("measurement_method")) or "percentage",
                }
            )

        return {
            "student_name": _as_str(raw.get("student_name")),
            "grade": _as_int(raw.get("grade")),
            "asd_level": _as_int(raw.get("asd_level")),
            "communication_level": _as_str(raw.get("communication_level")),
            "interests": _as_str_list(raw.get("interests")),
            "iep_goals": goals,
            "accommodations": _as_str_list(raw.get("accommodations")),
            "notes": _as_str(raw.get("notes")),
        }

    def _merge_pages(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge per-page extraction results into one dict.

        - Demographic scalars: first non-empty page wins.
        - Lists (interests, accommodations): union, preserving order, deduped.
        - iep_goals: concatenated, deduped by (goal_id, description).
        """
        merged: Dict[str, Any] = dict(self._EMPTY)
        seen_goals: set[Tuple[str, str]] = set()
        seen_interests: set[str] = set()
        seen_accom: set[str] = set()
        notes: List[str] = []

        for page in pages:
            if not page:
                continue

            for field in ("student_name", "communication_level"):
                if not merged.get(field) and page.get(field):
                    merged[field] = page[field]

            for field in ("grade", "asd_level"):
                if merged.get(field) is None and page.get(field) is not None:
                    merged[field] = page[field]

            for interest in page.get("interests", []) or []:
                if interest and interest not in seen_interests:
                    seen_interests.add(interest)
                    merged["interests"].append(interest)

            for acc in page.get("accommodations", []) or []:
                if acc and acc not in seen_accom:
                    seen_accom.add(acc)
                    merged["accommodations"].append(acc)

            for goal in page.get("iep_goals", []) or []:
                key = (goal.get("goal_id", ""), goal.get("description", ""))
                if key in seen_goals:
                    continue
                seen_goals.add(key)
                merged["iep_goals"].append(goal)

            page_note = page.get("notes")
            if page_note:
                notes.append(page_note)

        merged["notes"] = " ".join(notes)
        return merged
