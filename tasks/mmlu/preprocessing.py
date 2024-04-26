from datasets import load_dataset
import pandas as pd


def get_realized_prompt(row):
    choices_with_labels = []
    for i, choice in enumerate(row["choices"]):
        choices_with_labels.append(f"{i}: {choice}")
    formatted_choices_with_labels = "\n".join(choices_with_labels)
    realized_prompt = f"""Given the following question:

{row["question"]}

{formatted_choices_with_labels}

What is your answer? Please respond with 1, 2, 3, or 4.
"""
    return realized_prompt


def add_realized_prompt(df) -> pd.DataFrame:
    df["realized_prompt"] = df.apply(get_realized_prompt, axis=1)
    return df


def get_processed_df(dataset) -> pd.DataFrame:
    dataset_df = dataset.to_pandas()
    dataset_df = add_realized_prompt(dataset_df)
    return dataset_df


def write_processed_df() -> pd.DataFrame:
    subsets = [
        ("cais/mmlu", "all", "auxiliary_train"),
        ("cais/mmlu", "all", "validation"),
        ("cais/mmlu", "all", "dev"),
        ("cais/mmlu", "all", "test"),
    ]

    for subset in subsets.items():
        dataset_name, subset_name, split = subset
        dataset = load_dataset(dataset_name, subset_name, split=split)
        dataset_df = dataset.to_pandas()
        dataset_df = add_realized_prompt(dataset_df)
        dataset_df.to_csv(f"datasets/mmlu.{split}.csv")
