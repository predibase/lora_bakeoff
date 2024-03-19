import pandas as pd
from utils.metadata import get_metadata_for_task, TASKS_DIRECTORY

def filter_on_split(df, task_metadata):
    if "split_column" not in task_metadata or task_metadata["split_column"] in [
        None,
        "None",
    ]:
        print("No split column specified. Not filtering on split.")
        return df

    # Filter out examples that don't match the split column value.
    if task_metadata["split_column_value"] is None:
        raise ValueError(
            f"For reading local data files with --split_column {task_metadata['split_column']}, --split_column_value must be specified."
        )

    return df[
        df[task_metadata["split_column"]].astype(str) == str(task_metadata["split_column_value"])
    ]

def get_dataframe_from_local_file(task_metadata, num_examples):
    eval_df = None

    # Parse into pandas based on the file extension.
    file_extension = task_metadata["data_path"].split(".")[-1]
    if file_extension not in ["csv", "json", "jsonl"]:
        raise ValueError(
            f"File extension {file_extension} not supported. Must be one of: csv, json."
        )
    if file_extension == "csv":
        eval_df = pd.read_csv(task_metadata["data_path"])
    elif file_extension == "json":
        eval_df = pd.read_json(task_metadata["data_path"])
    elif file_extension == "jsonl":
        eval_df = pd.read_json(task_metadata["data_path"], lines=True)

    eval_df = filter_on_split(eval_df, task_metadata)

    example_cap = num_examples
    if example_cap is not None:
        eval_df = eval_df[: int(example_cap)]

    return eval_df
    
def load_training_data_for_task(task_name: str) -> pd.DataFrame:
    df = None
    task = f"{TASKS_DIRECTORY}/{task_name}"
    metadata = get_metadata_for_task(task)
    dataset_path = f"datasets/{metadata['training_data']}"

    # Parse into pandas based on the file extension.
    file_extension = dataset_path.split(".")[-1]
    if file_extension not in ["csv", "json", "jsonl"]:
        raise ValueError(
            f"File extension {file_extension} not supported. Must be one of: csv, json, jsonl."
        )
    if file_extension == "csv":
        df = pd.read_csv(dataset_path)
    elif file_extension == "json":
        df = pd.read_json(dataset_path)
    elif file_extension == "jsonl":
        df = pd.read_json(dataset_path, lines=True)
    return df