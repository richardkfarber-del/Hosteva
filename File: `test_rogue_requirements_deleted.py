import os

def test_rogue_requirements_deleted():
    file_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/requirements.txt"
    assert not os.path.exists(file_path), f"The rogue requirements.txt file still exists at {file_path}"

if __name__ == "__main__":
    test_rogue_requirements_deleted()
