"""Command line interface: python -m jobmatch.cli --resume r.txt --jd jd.txt [--llm]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import ConfigError
from .service import run_match


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jobmatch", description="Compare a resume with a job description.")
    parser.add_argument("--resume", required=True, type=Path, help="path to resume text file")
    parser.add_argument("--jd", required=True, type=Path, help="path to job description text file")
    parser.add_argument("--llm", action="store_true", help="use OpenAI for embeddings and analysis")
    parser.add_argument("--cover-letter", action="store_true", help="draft a cover letter (needs --llm)")
    parser.add_argument("--json", action="store_true", help="print raw JSON")
    return parser


def _print_list(title: str, items: list[str]) -> None:
    if items:
        print(f"\n{title}:")
        for item in items:
            print(f"  - {item}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        resume = args.resume.read_text(encoding="utf-8")
        jd = args.jd.read_text(encoding="utf-8")
        result = run_match(resume, jd, use_llm=args.llm, cover_letter=args.cover_letter)
    except (OSError, ValueError, ConfigError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    print(f"Mode: {result.mode}")
    print(f"Match score: {result.score}/100  (similarity {result.similarity:.2f})")
    _print_list("Matched skills", result.matched_skills)
    _print_list("Missing skills", result.missing_skills)
    _print_list("Strengths", result.strengths)
    _print_list("Gaps", result.gaps)
    _print_list("Suggested bullets", result.suggested_bullets)
    if result.cover_letter:
        print("\nCover letter draft:\n" + result.cover_letter)
    print("\nNote: this is a drafting aid, not a hiring decision. Review all text before using it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
