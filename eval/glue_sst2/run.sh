

# Appending to existing run.sh

## Prepare requests.
python prep_pbase_requests.py \
	--adapter_source 'pbase' \
	--prompt_template_file 'eval/glue_sst2/results/prompt_template.txt' \
	--outdir 'eval/glue_sst2' \
	--dataset 'datasets/glue_sst2_full.csv' \
	--split_column 'split' \
	--split_column_value '1' \
	--num_examples '1000' \
	--max_new_tokens '256' \
	--adapter_id 'glue_sst2_3_06_0/1' \

## Process requests.
python pbase_request_parallel_processor.py \
	--requests_filepath 'eval/glue_sst2/results/requests.jsonl' \
	--save_filepath 'eval/glue_sst2/results/responses.jsonl' \
	--deployment_base_model 'mistral-7b-dedicated-base' \
	--tenant_id '6dcb0c' \
	--stage 'prod' \

## Parse responses.
python parse_responses.py \
	--jsonl_responses_path 'eval/glue_sst2/results/responses.jsonl' \
	--target_text_column 'label' \
	--metric_fn 'binary_accuracy_flex' \
	--dataset 'datasets/glue_sst2_full.csv' \
	--split_column 'split' \
	--split_column_value '1' \
	--num_examples '1000' \
