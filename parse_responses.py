import json
import os

import argparse
import pandas as pd
from utils.metric_fns import METRIC_FNS
from utils.dataset_loading import get_dataframe_from_local_file

def get_pbase_response(response_data):
    if "generated_text" in response_data[1]:
        return response_data[1]["generated_text"]

def main(main_args):
    df = get_dataframe_from_local_file(main_args)
    skipped = []
    metric_fn = METRIC_FNS[main_args.metric_fn]

    scores = []
    with open(main_args.jsonl_responses_path) as file:
        for line in file:
            response_data = json.loads(line)
            metadata = response_data[2]
            df_index = metadata["df_index"]
            generated_text = get_pbase_response(response_data)
            target_text = df.loc[df.index == df_index][
                main_args.target_text_column
            ].item()
            if generated_text is not None:
                score = metric_fn(generated_text, target_text)
                scores.append(score)
            else:
                skipped.append(df_index)

    overall_score = sum(scores) / len(scores)
    print(f"Overall {main_args.metric_fn}: {overall_score:.3f}")
    print(f"Skipped {len(skipped)} examples: {skipped}")

    with open(
        os.path.join(os.path.dirname(main_args.jsonl_responses_path), f"skipped.txt"),
        "w",
    ) as file:
        file.write(f"Skipped {len(skipped)} examples: {skipped}")
    with open(
        os.path.join(
            os.path.dirname(main_args.jsonl_responses_path),
            f"{main_args.metric_fn}.txt",
        ),
        "w",
    ) as file:
        file.write(f"Overall {main_args.metric_fn}: {overall_score:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Parse responses from Predibase.",
        description="Parse responses from Predibase.",
    )
    parser.add_argument("--jsonl_responses_path", required=True)

    parser.add_argument("--target_text_column", required=True)
    parser.add_argument("--metric_fn", required=True)

    parser.add_argument(
        "--dataset",
        help="Local filepath",
        required=True,
    )

    parser.add_argument(
        "--split_column", help="The name of the split column.", default=None
    )
    parser.add_argument(
        "--split_column_value", help="The value of the split column.", default=None
    )

    parser.add_argument("--num_examples", default=None)

    main_args = parser.parse_args()

    main(main_args)
