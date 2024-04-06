docker run --gpus '"device=3"' -p 9001:80 -d -v /raid/hpc/mingzhe/transformers_cache:/data ghcr.io/huggingface/text-generation-inference:1.4 --model-id Elfsong/mouadsfilter
