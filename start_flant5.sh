docker run --gpus '"device=3"' -p 8088:80 -v /raid/hpc/mingzhe/transformers_cache:/data ghcr.io/huggingface/text-generation-inference:1.4 --model-id Elfsong/mouadsfilter
