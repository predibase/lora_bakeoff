import os
import json
import argparse
import dotenv
from utils.dataset_loading import get_dataframe_from_local_file, get_metadata_for_task

def append_to_jsonl(data, filename: str) -> None:
    """Append a json payload to the end of a jsonl file."""
    json_string = json.dumps(data)
    with open(filename, "a") as f:
        f.write(json_string + "\n")

def main(main_args):
    # Environment variables.
    dotenv.load_dotenv()

    # Clear the output file path if it already exists.
    output_file_path = os.path.join(main_args.outdir, "requests.jsonl")
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    task_metadata = get_metadata_for_task(main_args.task)

    # Get the dataset from or local.
    df = get_dataframe_from_local_file(task_metadata, main_args.num_examples)

    os.makedirs(main_args.outdir, exist_ok=True)

    prompt_template = task_metadata["prompt_template"]

    for df_index, example in df.iterrows():
        realized_prompt = prompt_template.format(**example)

        # Truncate the realized prompt to a token cap.
        realized_prompt = realized_prompt[: int(main_args.max_prompt_length_chars)]

        if main_args.adapter_id is not None and main_args.adapter_id != "None":
            # Adapter querying.
            data = {
                "inputs": realized_prompt,
                "parameters": {
                    "api_token": os.getenv("PREDIBASE_API_TOKEN"),
                    "adapter_source": main_args.adapter_source,
                    "adapter_id": main_args.adapter_id,
                    "max_new_tokens": int(main_args.max_new_tokens),
                },
                # This is needed for matching responses back to examples during post-processing.
                "metadata": {"df_index": df_index},
            }
        else:
            # Base model querying.
            data = {
                "inputs": realized_prompt,
                "parameters": {
                    "api_token": os.getenv("PREDIBASE_API_TOKEN"),
                    "max_new_tokens": int(main_args.max_new_tokens),
                },
                # This is needed for matching responses back to examples during post-processing.
                "metadata": {"df_index": df_index},
            }

        append_to_jsonl(data, output_file_path)


if __name__ == "__main__":
    # Environment variables.
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(
        prog="Generate LLM requests to Predibase.",
        description="Generate LLM requests to Predibase.",
    )
    parser.add_argument("--task", required=True)

    parser.add_argument("--num_examples", default=None)

    # Predibase adapter arguments.
    parser.add_argument("--adapter_source", default="pbase", required=False)
    parser.add_argument("--adapter_id", default=None, required=False)

    parser.add_argument("--max_new_tokens", default=256, required=False)
    parser.add_argument("--max_prompt_length_chars", default=1500, required=False)

    # Other arguments.
    parser.add_argument("--outdir", required=True)

    main_args = parser.parse_args()
    main(main_args)
