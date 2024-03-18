import pandas as pd

def filter_on_split(df, main_args):
    if "split_column" not in main_args.__dict__ or main_args.split_column in [
        None,
        "None",
    ]:
        print("No split column specified. Not filtering on split.")
        return df

    # Filter out examples that don't match the split column value.
    if main_args.split_column_value is None:
        raise ValueError(
            f"For reading local data files with --split_column {main_args.split_column}, --split_column_value must be specified."
        )

    return df[
        df[main_args.split_column].astype(str) == str(main_args.split_column_value)
    ]

def get_dataframe_from_local_file(main_args):
    eval_df = None

    # Parse into pandas based on the file extension.
    file_extension = main_args.dataset.split(".")[-1]
    if file_extension not in ["csv", "json", "jsonl"]:
        raise ValueError(
            f"File extension {file_extension} not supported. Must be one of: csv, json."
        )
    if file_extension == "csv":
        eval_df = pd.read_csv(main_args.dataset)
    elif file_extension == "json":
        eval_df = pd.read_json(main_args.dataset)
    elif file_extension == "jsonl":
        eval_df = pd.read_json(main_args.dataset, lines=True)

    eval_df = filter_on_split(eval_df, main_args)

    example_cap = main_args.num_examples
    if example_cap is not None:
        eval_df = eval_df[: int(example_cap)]

    return eval_df
    