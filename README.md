This is the demo repo for the LoRA Bakeoff!

In the `tasks` directory, there is a subdirectory named `glue_sst2`, and inside of that subdirectory, there is a file named `metadata.yaml`. This is an example of the task-based organizational structure that the harness relies on. To add another task to the directory, it must follow the same convention: `tasks/{task_name}/metadata.yaml`.

The `metadata.yaml` file includes metadata like:
- `data_path`: the path to the relevant dataset
- `prompt_template`: the prompt template
- `target_col`: the target column
- `metric_name`: the metric function to use
- `split_column`: the name of the column that defines splits in the dataset (optional)
- `split_column_value`:which split to use (optional)

In the `eval/glue_sst2` directory, the `run.sh` script serves as an example script to follow for other evaluations. There are three components of the script:
- `prep_pbase_requests.py` -- Generates the JSON payloads to the REST API
- `pbase_request_parallel_processor.py` -- Calls the REST API to get the responses from an adapter
- `parse_responses.py` -- Calculates a metric score over the responses from the adapter (metrics listed in `metric_fns.py`)

In particular, the `task` flag refers to the name of the subdirectory containing the relevant `metadata.yaml` file.