from torchmetrics.text.rouge import ROUGEScore
import json
import re
import inflect
from utils.instruction_following_eval.evaluation_main import InputExample, test_instruction_following_loose, test_instruction_following_strict

def get_accuracy(generated_text, target_text):
    if str(generated_text).strip(".").lower() == str(target_text).strip(".").lower():
        return 1
    try:
        if (
            str(float(generated_text)) == str(target_text).strip()
        ):  # For example, "1.0" == "1"
            return 1
        return 0
    except:
        return 0


def get_bool_value_from_text(text):
    """Returns None if there was no meaningful boolean value that could be found."""
    # Convert to string if necessary.
    text = str(text)
    if "1" in text:
        return True
    if "0" in text:
        return False
    if "yes" in text.lower():
        return True
    if "no" in text.lower():
        return False
    if "true" in text.lower():
        return True
    if "false" in text.lower():
        return False
    if "positive" in text.lower():
        return True
    if "negative" in text.lower():
        return False
    return None


def get_binary_accuracy_flex(generated_text, target_text):
    """Returns 1 if the generated text and target text are equal in boolean space.

    This is a flexible matching function that can handle a variety of boolean representations.
    - yes/no
    - true/false
    - 1/0
    - positive/negative
    """
    generated_prediction = get_bool_value_from_text(generated_text)
    if generated_prediction is None:
        print("Could not extract a boolean prediction from the generated text.")
        return 0

    target_prediction = get_bool_value_from_text(target_text)
    if target_prediction is None:
        print("Could not extract a boolean prediction from the target text.")
        return 0

    return int(generated_prediction == target_prediction)


def get_mrpc_accuracy(generated_text, target_text):
    """Tries to match based on vanilla accuracy. If not, then check for the consistent presence of (1 | 2)."""
    vanilla_accuracy = get_accuracy(generated_text, target_text)
    if vanilla_accuracy == 1:
        return 1

    # If the vanilla accuracy is 0, then we need to check other heuristics.
    if "1" in generated_text and "1" in str(target_text):
        return 1

    if "2" in generated_text and "2" in str(target_text):
        return 1

    return 0


def get_mnli_accuracy(generated_text, target_text):
    """Tries to match based on vanilla accuracy. If not, then check for the consistent presence of (0 | 1 | 2)."""
    vanilla_accuracy = get_accuracy(generated_text, target_text)
    if vanilla_accuracy == 1:
        return 1

    # If the vanilla accuracy is 0, then we need to check other heuristics.
    if "0" in generated_text and "0" in str(target_text):
        return 1

    if "1" in generated_text and "1" in str(target_text):
        return 1

    if "2" in generated_text and "2" in str(target_text):
        return 1

    return 0


def get_hellaswag_accuracy(generated_text, target_text):
    """Tries to match based on vanilla accuracy. If not, then check for the consistent presence of (0 | 1 | 2 | 3)."""
    vanilla_accuracy = get_accuracy(generated_text, target_text)
    if vanilla_accuracy == 1:
        return 1

    # If the vanilla accuracy is 0, then we need to check other heuristics.
    if "0" in generated_text and "0" in str(target_text):
        return 1

    if "1" in generated_text and "1" in str(target_text):
        return 1

    if "2" in generated_text and "2" in str(target_text):
        return 1

    if "3" in generated_text and "3" in str(target_text):
        return 1

    return 0


def get_rouge(generated_text, target_text):
    rouge = ROUGEScore()
    return rouge([generated_text], [target_text])["rougeL_fmeasure"]


def get_first_number(text):
    # Pattern explanation:
    # \d{1,3}(?:,\d{3})* - Matches numbers with commas for thousands
    # (?:\.\d+)? - Optional decimal part
    pattern = r"\d{1,3}(?:,\d{3})*(?:\.\d+)?"

    # Find all matches in the string
    matches = re.findall(pattern, text)

    # Return the first match or None if no match is found
    return matches[0] if matches else None


def get_stsb_number(text):
    """Returns a number from 0 to 5.

    If the text is not just the number, then we try to find the first number in the text.

    If there is no number in the text, then we return None.
    If the number is greater than 5, then we return None.
    If the number is less than 0, then we return None.
    """
    try:
        return float(text)
    except:
        first_number = get_first_number(str(text))
        if first_number is None:
            return None

        number = float(first_number)
        if number > 5:
            return None
        if number < 0:
            return None

        return float(first_number)


def get_stsb(generated_text, target_text):
    # Return 1 - percentage error.
    generated_text_number = get_stsb_number(generated_text)
    target_text_number = get_stsb_number(target_text)

    if generated_text_number is None:
        return 0

    # Normalize by dividing by 5, which is maximum.
    mean_absolute_error = abs(generated_text_number - target_text_number) / 5
    return 1 - mean_absolute_error


def get_dbpedia(generated_text, target_text):
    classes = [
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
    try:
        generated_text = int(generated_text)
        generated_text = classes[generated_text]
    finally:
        return get_rouge(generated_text, target_text)


def get_drop(generated_text, target_text):
    engine = inflect.engine()
    start = target_text.index("[") + 2
    end = target_text.index("]") - 1
    target_text = target_text[start:end].lower()
    generated_text = generated_text.lower()

    # Example: "{'spans': array(['86598'], dtype=object), 'types': array(['number'], dtype=object)}" --> "86598"
    if generated_text.startswith("{'spans': array(['"):
        start = generated_text.index("[") + 2
        end = generated_text.index("]") - 1
        generated_text = generated_text[start:end]

    # Example: "1" vs. "one"
    try:
        target_text = int(target_text)
        target_text = engine.number_to_words(target_text)
    except:
        pass
    try:
        generated_text = int(generated_text)
        generated_text = engine.number_to_words(generated_text)
    finally:
        return get_rouge(generated_text, target_text)


def get_label_and_explanation(generated_text, target_text):
    """For use with datasets created with join_explanations.py."""
    try:
        generated_json = json.loads(generated_text)
        target_json = json.loads(target_text)

        # Check assertions.
        assert len(generated_json) == len(target_json) == 2
        assert "explanation" in generated_json
        assert "explanation" in target_json

        generated_label = list(generated_json.keys() - {"explanation"})[0]
        target_label = list(target_json.keys() - {"explanation"})[0]
    except Exception as e:
        print(f"Encountered exception during label_and_explanation metric: {e}")
        return 0

    if generated_json[generated_label] == target_json[target_label]:
        # The labels are correct. Now check the explanation ROUGE score.
        return get_rouge(generated_json["explanation"], target_json["explanation"])

    # If the label is inaccurate, then the explanation is irrelevant.
    return 0


def find_last_number(s):
    # Pattern explanation:
    # [\$€£]? - Optional currency symbols ($, €, £)
    # [+-]? - Optional sign (plus or minus)
    # \d{1,3}(?:,\d{3})* - Matches numbers with commas for thousands
    # (?:\.\d+)? - Optional decimal part
    pattern = r"[\$€£]?[+-]?\d{1,3}(?:,\d{3})*(?:\.\d+)?"

    # Find all matches in the string
    matches = re.findall(pattern, s)

    # Return the last match or None if no match is found
    return matches[-1] if matches else None


def get_gsm8k_regex(generated_text, target_text):
    pattern = "(-?[$0-9.,]{2,})|(-?[0-9]+)"

    try:
        generated_match = "".join(re.findall(pattern, generated_text)[-1])
        target_match = "".join(re.findall(pattern, target_text)[-1])
    except IndexError:
        print(f"IndexError: {generated_text} vs. {target_text}")
        return 0

    # generated_match = find_last_number(generated_text)
    # target_match = find_last_number(target_text)
    if generated_match == None or target_match == None:
        return 0
    try:
        if float(generated_match.strip("$.").replace(",", "")) == float(
            target_match.strip("$.").replace(",", "")
        ):
            return 1
    except ValueError:
        pass
    print(f"Incorrect: {generated_match} vs. {target_match}")
    print(f"Generated: {generated_text}")
    print(f"Target: {target_text}")
    print("--------")
    return 0


def get_customer_support_accuracy(generated_text, target_text):
    vanilla_accuracy = get_accuracy(generated_text, target_text)
    if vanilla_accuracy == 1:
        return 1
    if target_text.lower() in generated_text.lower():
        return 1
    return 0

def get_ifeval_instruction_following_loose(target, prompt_to_response):
    target = target.reset_index(drop=True).iloc[0].to_dict()
    try:
        inp = InputExample(key=target["key"],
                        instruction_id_list=target["instruction_id_list"],
                        prompt=target["prompt"],
                        kwargs=target["kwargs"])
        out = test_instruction_following_loose(inp, prompt_to_response)
        return out.follow_all_instructions
    except Exception as e:
        print(f"Encountered exception during ifeval_instruction_following_loose metric: {e}")
        return 0

def get_ifeval_instruction_following_strict(target, prompt_to_response):
    target = target.reset_index(drop=True).iloc[0].to_dict()
    try:
        inp = InputExample(key=target["key"],
                        instruction_id_list=target["instruction_id_list"],
                        prompt=target["prompt"],
                        kwargs=target["kwargs"])
        out = test_instruction_following_strict(inp, prompt_to_response)
        return out.follow_all_instructions
    except Exception as e:
        print(f"Encountered exception during ifeval_instruction_following_strict metric: {e}")
        return 0

METRIC_FNS = {
    "accuracy": get_accuracy,
    "rouge": get_rouge,
    "stsb": get_stsb,
    "dbpedia": get_dbpedia,
    "drop": get_drop,
    "label_and_explanation": get_label_and_explanation,
    "binary_accuracy_flex": get_binary_accuracy_flex,
    "gsm8k_regex": get_gsm8k_regex,
    "mrpc_accuracy": get_mrpc_accuracy,
    "mnli_accuracy": get_mnli_accuracy,
    "hellaswag_accuracy": get_hellaswag_accuracy,
    "customer_support_accuracy": get_customer_support_accuracy,
    "amazon_review_mpe": get_stsb,  # 1-5 ratings.
    "ifeval_loose": get_ifeval_instruction_following_loose,
    "ifeval_strict": get_ifeval_instruction_following_strict,
}
