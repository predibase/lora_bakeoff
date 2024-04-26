from datasets import load_dataset
import pandas as pd


def get_processed_df() -> pd.DataFrame:
    splits = ["train", "validation", "test"]
    dataset = load_dataset("dbpedia_14")

    dfs = []
    for i, split in enumerate(splits):
        if split in dataset:
            df = dataset[split].to_pandas()
            df.insert(0, "split", i)
            dfs.append(df)

    df = pd.concat(dfs)
    labels = [
        "Company",
        "EducationalInstitution",
        "Artist",
        "Athlete",
        "OfficeHolder",
        "MeanOfTransportation",
        "Building",
        "NaturalPlace",
        "Village",
        "Animal",
        "Plant",
        "Album",
        "Film",
        "WrittenWork",
    ]
    df["label"] = df["label"].apply(lambda x: labels[x - 1])
    return df
