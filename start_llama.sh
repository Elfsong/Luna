
token="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"

docker run \
  --gpus '"device=3"' \
  --ipc=host \
  -d \
  -p 8080:80 \
  -v /raid/hpc/mingzhe/transformers_cache:/data \
  -e HF_API_TOKEN=${token} \
  -e DISABLE_EXLLAMA=True \
  ghcr.io/huggingface/text-generation-inference:1.3 \
  --hostname 0.0.0.0 \
  --model-id meta-llama/Llama-2-70b-chat-hf \
  --quantize bitsandbytes \
  --num-shard 1 \
  --max-total-tokens 4096 \
  --max-input-length 4000