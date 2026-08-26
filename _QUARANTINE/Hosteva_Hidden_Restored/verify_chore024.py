import os

def verify():
    path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/"
    assert os.path.exists(os.path.join(path, "pyproject.toml")), "pyproject.toml missing"
    assert os.path.exists(os.path.join(path, "uv.lock")), "uv.lock missing"
    assert not os.path.exists(os.path.join(path, "requirements.txt")), "requirements.txt still exists"
    print("CHORE-024 Acceptance Criteria verified locally: pyproject.toml and uv.lock present, requirements.txt removed.")

if __name__ == "__main__":
    verify()
