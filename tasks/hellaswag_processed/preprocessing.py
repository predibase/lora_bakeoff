from datasets import load_dataset


def get_hellaswag_preprocessed():
    splits = ["train", "validation", "test"]
    dataset = load_dataset("Rowan/hellaswag")

    dfs = []
    for i, split in enumerate(splits):
        if split in dataset:
            df = dataset[split].to_pandas()
            if "split" in df.columns:
                df = df.drop("split", axis=1)
            df.insert(0, "split", i)
            dfs.append(df)

    df = pd.concat(dfs)

    correct_endings = []
    print(len(df))
    idx = []
    for i, line in df.iterrows():
        line["endings"] = line["endings"].strip("'\", []").split("\n")
        line["endings"] = [x.strip("'\" ,") for x in line["endings"]]
        if len(line["endings"]) != 4:
            for ending in line["endings"]:
                if "' '" in ending:
                    fixed = ending.split("' '")
                    line["endings"].remove(ending)
                    line["endings"].append(fixed[0])
                    line["endings"].append(fixed[1])
        try:
            assert len(line["endings"]) == 4
        except AssertionError:
            print(i)
            print(line["endings"])
            print(len(line["endings"]))
            continue
        try:
            correct_endings.append(line["endings"][int(line["label"])])
            idx.append(i)
        except ValueError:
            pass

    test_df = df.loc[df["split"] == 2]
    print(len(df))
    print(len(test_df))
    print(len(correct_endings))
    df = df.iloc[idx]
    df["correct_ending"] = correct_endings
    return df
