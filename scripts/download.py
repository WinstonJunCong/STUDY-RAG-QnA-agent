from huggingface_hub import snapshot_download

model_id = "Octen/Octen-Embedding-8B"
local_dir = "D:\\huggingface_models\\Octen-8B"

print(f"Downloading {model_id} to {local_dir}...")

snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    ignore_patterns=["*.msgpack", "*.h5", "*.ot"], # Optional: skip non-safetensor weights
)

print("Download complete.")