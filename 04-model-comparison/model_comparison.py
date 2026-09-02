import os
import time
import csv
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# 1. Load API Key
# =========================================================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY not found. "
        "Please check your .env file."
    )


# =========================================================
# 2. Create OpenRouter Client
# =========================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# =========================================================
# 3. Model Settings
#
# IMPORTANT:
# Replace model IDs with exact OpenRouter model IDs.
# Do NOT use display names here.
# =========================================================

models = [
    {
        "model_id": "liquid/lfm-2.5-2.6b:free",
        "model_label": "LFM 2.5-2.6B"
    },
    {
        "model_id": "dots-studio/dots-3-note-preview:free",
        "model_label": "dots-3-note-preview:free"
    },
    {
        "model_id": "minimax/minimax-m3:free",
        "model_label": "minimax"
    }
]


# =========================================================
# 4. Controlled Prompt
#
# Every model receives exactly the same prompt.
# =========================================================

prompt = """
Explain the difference between API latency and throughput
to a junior developer in 100-150 words.
""".strip()


# =========================================================
# 5. Experiment Settings
#
# Smoke test:
# runs_per_model = 1
#
# Formal experiment:
# runs_per_model = 5
# =========================================================

runs_per_model = 3

max_output_tokens = 800

csv_file = "model_comparison_v2.csv"


# =========================================================
# 6. Prepare CSV
# =========================================================

file_exists = os.path.isfile(csv_file)

with open(
    csv_file,
    "a",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.writer(f)

    if not file_exists:

        writer.writerow([
            "timestamp",
            "run",
            "model_id",
            "model_label",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "duration_seconds",
            "observed_output_tokens_per_second",
            "word_count",
            "response_char_count",
            "length_compliance",
            "finish_reason",
            "status",
            "error",
            "response_text"
        ])


    # =====================================================
    # 7. Interleaved Testing
    #
    # Run 1:
    #   Model A
    #   Model B
    #   Model C
    #
    # Run 2:
    #   Model A
    #   Model B
    #   Model C
    #
    # etc.
    # =====================================================

    for run in range(1, runs_per_model + 1):

        print("\n" + "=" * 70)
        print(f"STARTING RUN {run}")
        print("=" * 70)

        for model in models:

            model_id = model["model_id"]
            model_label = model["model_label"]

            print("\n" + "-" * 70)

            print(
                f"Run: {run}\n"
                f"Model: {model_label}\n"
                f"Model ID: {model_id}"
            )

            start_time = time.perf_counter()


            # =================================================
            # 8. API Request
            # =================================================

            try:

                response = client.chat.completions.create(
                    model=model_id,

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    # This is only an output ceiling.
                    # It does NOT ask the model to generate 800 tokens.
                    max_tokens=max_output_tokens
                )


                # =============================================
                # 9. Measure End-to-End Request Duration
                # =============================================

                duration = (
                    time.perf_counter()
                    - start_time
                )


                # =============================================
                # 10. Get Response Choice
                # =============================================

                choice = response.choices[0]

                text = choice.message.content

                if text is None:
                    text = ""


                # =============================================
                # 11. Finish Reason
                #
                # Common examples may include:
                # stop
                # length
                #
                # If "length", output likely hit token ceiling.
                # =============================================

                finish_reason = choice.finish_reason

                if finish_reason is None:
                    finish_reason = ""


                # =============================================
                # 12. Token Usage
                # =============================================

                if response.usage:

                    input_tokens = (
                        response.usage.prompt_tokens
                        or 0
                    )

                    output_tokens = (
                        response.usage.completion_tokens
                        or 0
                    )

                    total_tokens = (
                        response.usage.total_tokens
                        or 0
                    )

                else:

                    input_tokens = 0
                    output_tokens = 0
                    total_tokens = 0


                # =============================================
                # 13. Response Length Metrics
                # =============================================

                word_count = len(
                    text.split()
                )

                response_char_count = len(
                    text
                )


                # =============================================
                # 14. Instruction Following
                #
                # Prompt requires 100-150 English words.
                # =============================================

                if 100 <= word_count <= 150:
                    length_compliance = "yes"
                else:
                    length_compliance = "no"


                # =============================================
                # 15. Observed Output Tokens / Second
                #
                # IMPORTANT:
                #
                # This is:
                #
                # output_tokens
                # ------------------
                # total request time
                #
                # It is NOT strict generation throughput,
                # because duration includes networking,
                # queueing, TTFT, generation, etc.
                # =============================================

                if (
                    duration > 0
                    and output_tokens > 0
                ):

                    observed_tps = (
                        output_tokens
                        / duration
                    )

                else:

                    observed_tps = 0


                status = "success"
                error_message = ""


                # =============================================
                # 16. Print Results
                # =============================================

                print("\n--- RESULT ---")

                print(
                    "Status:",
                    status
                )

                print(
                    "Input tokens:",
                    input_tokens
                )

                print(
                    "Output tokens:",
                    output_tokens
                )

                print(
                    "Total tokens:",
                    total_tokens
                )

                print(
                    "Duration:",
                    round(duration, 3),
                    "seconds"
                )

                print(
                    "Observed output tokens/s:",
                    round(observed_tps, 3)
                )

                print(
                    "Word count:",
                    word_count
                )

                print(
                    "Response char count:",
                    response_char_count
                )

                print(
                    "Length compliance:",
                    length_compliance
                )

                print(
                    "Finish reason:",
                    finish_reason
                )

                print("\n--- MODEL RESPONSE ---")

                print(text)


            # =================================================
            # 17. Error Handling
            # =================================================

            except Exception as e:

                duration = (
                    time.perf_counter()
                    - start_time
                )

                input_tokens = 0
                output_tokens = 0
                total_tokens = 0

                observed_tps = 0

                word_count = 0
                response_char_count = 0

                length_compliance = "no"

                finish_reason = ""

                text = ""

                status = "error"

                error_message = str(e)


                print("\n--- ERROR ---")

                print(
                    "Model:",
                    model_label
                )

                print(
                    "Duration:",
                    round(duration, 3),
                    "seconds"
                )

                print(
                    "Error:",
                    error_message
                )


            # =================================================
            # 18. Save Row to CSV
            # =================================================

            writer.writerow([
                datetime.now().isoformat(
                    timespec="seconds"
                ),

                run,

                model_id,

                model_label,

                input_tokens,

                output_tokens,

                total_tokens,

                round(
                    duration,
                    3
                ),

                round(
                    observed_tps,
                    3
                ),

                word_count,

                response_char_count,

                length_compliance,

                finish_reason,

                status,

                error_message,

                text
            ])


            # Immediately write buffered data to disk.
            f.flush()


            print(
                "\nData saved to:",
                csv_file
            )


# =========================================================
# 19. Experiment Finished
# =========================================================

print("\n" + "=" * 70)

print(
    "EXPERIMENT COMPLETE"
)

print("=" * 70)

print(
    "Runs per model:",
    runs_per_model
)

print(
    "Number of models:",
    len(models)
)

print(
    "Expected total requests:",
    runs_per_model * len(models)
)

print(
    "Results saved to:",
    csv_file
)