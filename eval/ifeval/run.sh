## Prepare requests.
python prep_pbase_requests.py \
	--outdir 'eval/ifeval/results' \
	--task 'ifeval' \
	--num_examples '1000' \
	--max_new_tokens '1024' \

## Process requests.
python pbase_request_parallel_processor.py \
	--requests_filepath 'eval/ifeval/results/requests.jsonl' \
	--save_filepath 'eval/ifeval/results/responses.jsonl' \
	--deployment_base_model "NAME_OF_DEPLOYMENT" \
	--tenant_id 'TENANT_ID_FROM_SETTINGS_PAGE' \

## Parse responses.
python parse_if_eval.py \
	--jsonl_responses_path 'eval/ifeval/results/responses.jsonl' \
	--task 'ifeval' \
	--num_examples '1000' \
