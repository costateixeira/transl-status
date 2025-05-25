import os
import subprocess
import argparse
import yaml

def run(cmd, cwd=None):
    print("🛠️", cmd)
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def fetch_repo(entry):
    url = entry['clone']
    sparse_path = entry['sparse']
    local_dir = entry['local']
    repo_dir = "tmp_repo"

    print(f"⬇️ Cloning {url} (sparse: {sparse_path})")
    run(f"git clone --depth 1 --filter=blob:none --sparse {url} {repo_dir}")
    run(f"git sparse-checkout set {sparse_path}", cwd=repo_dir)

    os.makedirs(local_dir, exist_ok=True)
    full_path = os.path.join(repo_dir, sparse_path)
    for file in os.listdir(full_path):
        if file.endswith(".po"):
            src = os.path.join(full_path, file)
            dst = os.path.join(local_dir, file)
            print(f"📄 Copying {src} → {dst}")
            os.system(f"cp {src} {dst}")

    run(f"rm -rf {repo_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    for source in config.get("sources", []):
        if "clone" in source and "sparse" in source:
            fetch_repo(source)
