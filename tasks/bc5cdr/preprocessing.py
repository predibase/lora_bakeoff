from datasets import load_dataset
import pandas as pd

TAG_TO_ID_MAP = {
    # 0: "O",
    1: "B-Chemical",
    2: "B-Disease",
    3: "I-Disease",
    4: "I-Chemical",
}


def add_preprocessed_columns(df, split):
    df["split"] = split
    return df


def add_collected_tags(row):
    tag_dict = {
        "B-Chemical": [],
        "B-Disease": [],
        "I-Disease": [],
        "I-Chemical": [],
    }
    for i, tag in enumerate(row["tags"]):
        if tag == 0:
            continue
        tag_value = TAG_TO_ID_MAP[tag]
        corresponding_token = row["tokens"][i]
        tag_dict[tag_value].append(corresponding_token)
    return str(tag_dict)


def get_bc6cdr():
    train_dataset = load_dataset("tner/bc5cdr", split="train")
    dev_dataset = load_dataset("tner/bc5cdr", split="validation")

    train_df = add_preprocessed_columns(train_dataset.to_pandas(), 0)
    dev_df = add_preprocessed_columns(dev_dataset.to_pandas(), 1)

    train_df["collected_tags"] = train_df.apply(add_collected_tags, axis=1)
    train_df["tokens_concatenated"] = train_df["tokens"].apply(lambda x: " ".join(x))
    train_df = train_df.drop("tags", axis=1)
    train_df = train_df.drop("tokens", axis=1)

    dev_df["collected_tags"] = dev_df.apply(add_collected_tags, axis=1)
    dev_df["tokens_concatenated"] = dev_df["tokens"].apply(lambda x: " ".join(x))
    dev_df = dev_df.drop("tags", axis=1)
    dev_df = dev_df.drop("tokens", axis=1)

    return pd.concat([train_df, dev_df])
