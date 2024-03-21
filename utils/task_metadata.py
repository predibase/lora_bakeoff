import os
import yaml

TASKS_DIRECTORY = "tasks"

def get_metadata_for_task(task_name: str) -> dict:
    """Return metadata for a single task."""
    metadata = {}
    task_dir = os.path.join(TASKS_DIRECTORY, task_name)
    with open(os.path.join(task_dir, "metadata.yaml")) as f:
        metadata = yaml.safe_load(f.read())
        # Add task name based on the directory name.
        metadata["task_name"] = os.path.basename(task_dir)
    return metadata

def get_metadata_for_task(task_name: str) -> dict:
    """Return metadata for a single task."""
    metadata = {}
    task_dir = os.path.join(TASKS_DIRECTORY, task_name)
    with open(os.path.join(task_dir, "metadata.yaml")) as f:
        metadata = yaml.safe_load(f.read())
        # Add task name based on the directory name.
        metadata["task_name"] = os.path.basename(task_dir)
    return metadata


def get_all_metadata() -> list:
    """Return metadata for all tasks, sorted alphabetically."""
    # Get all task directories.
    task_dirs = []
    for dir in os.listdir(TASKS_DIRECTORY):
        if os.path.isdir(os.path.join(TASKS_DIRECTORY, dir)):
            task_dirs.append(os.path.join(TASKS_DIRECTORY, dir))

    metadata_list = []
    for task_dir in task_dirs:
        task_name = os.path.basename(task_dir)
        metadata_list.append(get_metadata_for_task(task_name))

    return sorted(metadata_list, key=lambda x: x["task_name"])


def get_all_metadata_as_dict() -> dict:
    """Return metadata for all tasks as a dictionary."""
    metadata = get_all_metadata()
    metadata_dict = {}
    for task in metadata:
        metadata_dict[task["task_name"]] = task
    return metadata_dict