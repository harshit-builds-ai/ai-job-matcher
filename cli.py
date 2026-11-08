"""Command line interface: python -m jobmatch.cli --resume r.txt --jd jd.txt [--llm] [--cover-letter]"""
import argparse
import json
import sys

from . import matcher


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Compare a resume with a job description.")
    p.add_argument("--resume", required=True)
    p.add_argument("--jd", required=True)
    p.add_argument("--llm", action="store_true", help="use OpenAI for analysis + embeddings")
    p.add_argument("--cover-letter", action="store_true", help="also draft a cover letter (needs --llm)")
    args = p.parse_args(argv)

    resume, jd = open(args.resume, encoding="utf-8").read(), open(args.jd, encoding="utf-8").read()
    llm = embedder = None
    if args.llm or args.cover_letter:
        from .llm import OpenAIEmbedder, OpenAILLM
        llm, embedder = OpenAILLM(), OpenAIEmbedder()

    print(json.dumps(matcher.analyze(resume, jd, llm, embedder), indent=2, ensure_ascii=False))
    if args.cover_letter:
        print("\n--- COVER LETTER ---\n" + matcher.cover_letter(resume, jd, llm))
    return 0


if __name__ == "__main__":
    sys.exit(main())
