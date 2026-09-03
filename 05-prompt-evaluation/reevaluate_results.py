import csv
from pathlib import Path


# =========================
# 1. Paths
# =========================

BASE_DIR = Path(__file__).parent

INPUT_FILE = (
    BASE_DIR
    / "results"
    / "prompt_evaluation_results.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "results"
    / "prompt_evaluation_results_v2.csv"
)


# =========================
# 2. Helper
# =========================

def contains_any(text, terms):
    text_lower = text.lower()
    return any(
        term.lower() in text_lower
        for term in terms
    )


# =========================
# 3. Evaluator v2
# =========================

def evaluate_shared_quality(text):
    """
    Shared quality metrics applied to ALL prompt variants.

    Maximum score: 10
    """

    lower = text.lower()

    # ----- Basic factual coverage -----

    context_correct = (
        "128k" in lower
    )

    input_price_correct = (
        "$0.20" in text
        or "$0.2" in text
    )

    output_price_correct = (
        "$0.80" in text
        or "$0.8" in text
    )

    tool_calling_present = contains_any(
        text,
        [
            "tool calling",
            "tool-calling",
        ]
    )

    json_present = (
        "json" in lower
    )

    openai_compatible_present = (
        "openai" in lower
        and "compatib" in lower
    )

    # ----- Developer value -----

    developer_value_terms = [
        "existing code",
        "existing sdk",
        "existing tools",
        "existing integration",
        "reuse",
        "without rewriting",
        "minimal code changes",
        "reduce migration",
        "easier migration",
        "easy migration",
        "switch models",
        "integrate quickly",
        "faster integration",
    ]

    developer_value_present = contains_any(
        text,
        developer_value_terms
    )

    developer_value_strong = (
        developer_value_present
        and openai_compatible_present
    )

    # ----- Unsupported claims -----

    suspicious_claims = [
        "state-of-the-art",
        "sota",
        "best-in-class",
        "industry-leading",
        "fastest",
        "lowest latency",
        "highest performance",
        "beats",
        "outperforms",
        "benchmark",
        "99.9% uptime",
        "production-proven",
    ]

    hallucination_free = not contains_any(
        text,
        suspicious_claims
    )

    # ----- CTA -----

    cta_present = contains_any(
        text,
        [
            "try",
            "start building",
            "start testing",
            "build with",
            "explore",
            "test it",
            "get started",
        ]
    )

    checks = {
        "context_correct":
            context_correct,

        "input_price_correct":
            input_price_correct,

        "output_price_correct":
            output_price_correct,

        "tool_calling_present":
            tool_calling_present,

        "json_present":
            json_present,

        "openai_compatible_present":
            openai_compatible_present,

        "developer_value_present":
            developer_value_present,

        "developer_value_strong":
            developer_value_strong,

        "hallucination_free":
            hallucination_free,

        "cta_present":
            cta_present,
    }

    score = sum(
        int(value)
        for value in checks.values()
    )

    return score, checks


# =========================
# 4. Load old results
# =========================

rows = []

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8-sig"
) as infile:

    reader = csv.DictReader(infile)

    for row in reader:

        response_text = (
            row.get("response", "")
            or ""
        )

        if row.get("status") == "success":

            new_score, checks = (
                evaluate_shared_quality(
                    response_text
                )
            )

        else:

            new_score = ""

            checks = {
                "context_correct": "",
                "input_price_correct": "",
                "output_price_correct": "",
                "tool_calling_present": "",
                "json_present": "",
                "openai_compatible_present": "",
                "developer_value_present": "",
                "developer_value_strong": "",
                "hallucination_free": "",
                "cta_present": "",
            }

        # Keep old evaluator score
        row["shared_quality_score_v1"] = (
            row.get(
                "shared_quality_score",
                ""
            )
        )

        row["shared_quality_max_v1"] = (
            row.get(
                "shared_quality_max",
                ""
            )
        )

        # Add evaluator v2 score
        row["shared_quality_score_v2"] = (
            new_score
        )

        row["shared_quality_max_v2"] = 10

        # Add individual checks
        for key, value in checks.items():

            row[key] = (
                int(value)
                if isinstance(value, bool)
                else value
            )

        rows.append(row)


# =========================
# 5. Save v2 results
# =========================

if not rows:
    raise ValueError(
        "No rows found in input CSV."
    )


fieldnames = list(rows[0].keys())


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

    writer.writerows(rows)


# =========================
# 6. Print summary
# =========================

print("\nRe-evaluation finished.")
print(f"Input:  {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")

print("\nEvaluator v2 scores:")

for row in rows:

    print(
        f"{row['prompt_variant']} "
        f"run={row['run']} | "
        f"v1={row['shared_quality_score_v1']}/"
        f"{row['shared_quality_max_v1']} | "
        f"v2={row['shared_quality_score_v2']}/10"
    )