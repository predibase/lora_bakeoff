from datasets import load_dataset
import pandas as pd


def get_realized_prompt(row):
    choices_with_labels = []
    for label, choice in zip(row["choices"]["label"], row["choices"]["text"]):
        choices_with_labels.append(f"{label}: {choice}")
    # return "\n".join(choices_with_labels)
    formatted_choices_with_labels = "\n".join(choices_with_labels)
    realized_prompt = f"""Given the following question: 

{row["question"]}

{formatted_choices_with_labels}

Answer with one of the following labels: {row["choices"]["label"]}.
"""
    return realized_prompt


def add_realized_prompt(df) -> pd.DataFrame:
    df["realized_prompt"] = df.apply(get_realized_prompt, axis=1)
    return df


def get_processed_df(dataset) -> pd.DataFrame:
    dataset_df = dataset.to_pandas()
    dataset_df = add_realized_prompt(dataset_df)
    return dataset_df


def get_subset_dfs(subsets) -> dict:
    subset_dfs = {}
    for subset_name, subset_info in subsets.items():
        dataset_name, data_subset, split = subset_info
        dataset = load_dataset(dataset_name, data_subset, split=split)
        subset_dfs[subset_name] = get_processed_df(dataset)

        # Write to CSV.
        subset_dfs[subset_name].to_csv(f"datasets/arc_{data_subset}.{split}.csv")
    return subset_dfs


def get_arc():
    subsets = {
        "train_challenge": ("allenai/ai2_arc", "ARC-Challenge", "train"),
        "train_easy": ("allenai/ai2_arc", "ARC-Easy", "train"),
        "validation_challenge": ("allenai/ai2_arc", "ARC-Challenge", "validation"),
        "validation_easy": ("allenai/ai2_arc", "ARC-Easy", "validation"),
        "test_challenge": ("allenai/ai2_arc", "ARC-Challenge", "test"),
        "test_easy": ("allenai/ai2_arc", "ARC-Easy", "test"),
    }
    subset_dfs = get_subset_dfs(subsets)

    # Write out combined datasets.
    for split in ["train", "validation", "test"]:
        combined_dataset_df = pd.concat(
            [subset_dfs[f"{split}_easy"], subset_dfs[f"{split}_challenge"]]
        )
        combined_dataset_df.to_csv(f"datasets/arc_combined.{split}.csv")
