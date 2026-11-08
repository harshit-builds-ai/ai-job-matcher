"""Prompt templates. They are plain strings so they are easy to review and iterate on."""

ANALYSIS_SYSTEM = (
    "You are a careful career assistant. Use ONLY facts that appear in the resume text. "
    "Never invent skills, employers, dates, tools or numbers. Do not infer or mention age, "
    "gender, religion, caste, nationality or any other protected attribute, and do not let "
    "such attributes influence the assessment. Answer with valid JSON only."
)

ANALYSIS_USER = """Compare the resume with the job description.

Return JSON with exactly these keys:
- "match_score": integer 0-100 based on skills and experience evidence
- "strengths": list of up to 5 short strings, each backed by something in the resume
- "gaps": list of up to 5 short strings for requirements with no evidence in the resume
- "suggested_bullets": list of up to 4 resume bullets that REWORD existing resume content to
  mirror the job description's language. Do not add anything that is not in the resume.

JOB DESCRIPTION:
{jd}

RESUME:
{resume}
"""

COVER_LETTER_SYSTEM = (
    "You write concise, honest cover letters. Use ONLY facts present in the resume. "
    "If the job asks for something the resume does not show, do not claim it."
)

COVER_LETTER_USER = """Write a cover letter of 150-200 words for the job below.
Plain, direct tone. No clichés. No placeholders left in brackets except [Hiring Manager].

JOB DESCRIPTION:
{jd}

RESUME:
{resume}
"""
