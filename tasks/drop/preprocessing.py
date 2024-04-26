from datasets import load_dataset
import pandas as pd


def get_processsed_df() -> pd.DataFrame:
    dataset = load_dataset(input("Dataset name: "), input("Dataset config: "))
    splits = ["train", "validation", "test"]
    dfs = []
    for i, split in enumerate(splits):
        if split in dataset:
            df = dataset[split].to_pandas()
            if "split" in df.columns:
                df = df.drop("split", axis=1)
            df.insert(0, "split", i)
            dfs.append(df)

    df = pd.concat(dfs)
    idx = []
    answers = []
    lead_string = "{'spans': array(["
    close_string = "']"
    for i, row in df.iterrows():
        assert row["answers_spans"].startswith(lead_string)
        try:
            close_idx = row["answers_spans"].index(close_string)
        except ValueError:
            breakpoint()
        answer = row["answers_spans"][len(lead_string) : close_idx]
        if "', '" in answer:
            answer = answer.split("', '")
            answer = answer[0]
        answer = answer.strip("'")
        if "dtype" not in answer and "\n" not in answer:
            print(answer)
            answers.append(answer)
            idx.append(i)
    df = df.iloc[idx]
    df["answer"] = answers
    return df
