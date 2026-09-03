import os
import csv
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# =========================
# 1. Environment
# =========================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# =========================
# 2. Settings
# =========================

JUDGE_MODEL = "dots-studio/dots-3-note-preview:free"

BASE_DIR = Path(__file__).parent

INPUT_FILE = (
    BASE_DIR
    / "results"
    / "prompt_evaluation_results_v2.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "results"
    / "prompt_evaluation_judged.csv"
)


# =========================
# 3. Judge Prompt
# =========================

def build_judge_prompt(response):

    return f"""
You are evaluating an AI model launch post written for developers.

Evaluate the candidate response ONLY using the reference information
and scoring rubric below.

REFERENCE INFORMATION

Model: Spark-X1
Context window: 128K
Input price: $0.20 / 1M tokens
Output price: $0.80 / 1M tokens

Supported features:
- Tool calling
- JSON structured output
- OpenAI-compatible API

Target audience:
AI application developers

Do not assume any capabilities, benchmarks, performance,
availability, or facts that are not listed above.

SCORING RUBRIC

Accuracy (1-5)
1: Contains major factual errors or unsupported claims.
3: Mostly accurate with minor ambiguity.
5: Fully consistent with the reference information and introduces no unsupported claims.

Developer Value (1-5)
1: Mostly repeats features without explaining practical value.
3: Explains some developer benefits, but they remain generic.
5: Clearly connects features to concrete developer workflows,
integration effort, migration, or application-building value.

Clarity (1-5)
1: Difficult to understand or poorly organized.
3: Generally understandable but could be clearer.
5: Clear, well-organized, and easy for developers to scan.

Conciseness (1-5)
1: Highly verbose, repetitive, or unfocused.
3: Mostly concise with some unnecessary content.
5: Efficient and focused with little unnecessary content.

Overall Quality (1-5)
1: Not suitable as a developer-facing model launch post.
3: Usable but requires noticeable improvement.
5: Strong developer-facing launch content that is accurate,
useful, clear, and focused.

CANDIDATE RESPONSE

{response}

Return ONLY valid JSON using exactly this structure:

{{
  "accuracy": 1,
  "developer_value": 1,
  "clarity": 1,
  "conciseness": 1,
  "overall_quality": 1,
  "reason": "brief explanation"
}}
"""


# =========================
# 4. JSON Parser
# =========================

def parse_judge_output(text):

    text = text.strip()

    # Remove markdown fences if model adds them.
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)


# =========================
# 5. Load Experiment Data
# =========================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8-sig"
) as infile:

    reader = csv.DictReader(infile)
    rows = list(reader)


if not rows:
    raise ValueError("No experiment rows found.")


# =========================
# 6. Judge Each Response
# =========================

output_rows = []


for index, row in enumerate(rows, start=1):

    print(
        f"\nJudging {index}/{len(rows)} | "
        f"{row['prompt_variant']} run={row['run']}"
    )

    # Ignore failed generator calls.
    if row.get("status") != "success":

        row["judge_model"] = JUDGE_MODEL
        row["judge_status"] = "skipped"
        row["judge_accuracy"] = ""
        row["judge_developer_value"] = ""
        row["judge_clarity"] = ""
        row["judge_conciseness"] = ""
        row["judge_overall_quality"] = ""
        row["judge_reason"] = ""
        row["judge_error"] = ""

        output_rows.append(row)

        continue


    response = row.get("response", "")

    judge_prompt = build_judge_prompt(response)


    try:

        completion = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": judge_prompt
                }
            ],
            temperature=0,
        )

        judge_text = (
            completion.choices[0].message.content
            or ""
        )

        result = parse_judge_output(judge_text)


        row["judge_model"] = JUDGE_MODEL
        row["judge_status"] = "success"

        row["judge_accuracy"] = result["accuracy"]
        row["judge_developer_value"] = (
            result["developer_value"]
        )
        row["judge_clarity"] = result["clarity"]
        row["judge_conciseness"] = (
            result["conciseness"]
        )
        row["judge_overall_quality"] = (
            result["overall_quality"]
        )
        row["judge_reason"] = result["reason"]

        row["judge_error"] = ""


        print(
            "Success | "
            f"accuracy={result['accuracy']} | "
            f"value={result['developer_value']} | "
            f"clarity={result['clarity']} | "
            f"conciseness={result['conciseness']} | "
            f"overall={result['overall_quality']}"
        )


    except Exception as e:

        row["judge_model"] = JUDGE_MODEL
        row["judge_status"] = "error"

        row["judge_accuracy"] = ""
        row["judge_developer_value"] = ""
        row["judge_clarity"] = ""
        row["judge_conciseness"] = ""
        row["judge_overall_quality"] = ""
        row["judge_reason"] = ""

        row["judge_error"] = str(e)

        print(f"ERROR: {e}")


    output_rows.append(row)

    # Reduce free-tier rate-limit risk.
    time.sleep(3)


# =========================
# 7. Save Results
# =========================

fieldnames = list(output_rows[0].keys())


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as outfile:

    writer = csv.DictWriter(
        outfile,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(output_rows)


print("\nLLM-as-a-Judge evaluation finished.")
print(f"Results saved to: {OUTPUT_FILE}")