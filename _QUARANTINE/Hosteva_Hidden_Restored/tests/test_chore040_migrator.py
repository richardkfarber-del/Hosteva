import pytest
import os
import sys

sys.path.append("/home/rdogen/OpenClaw_Factory/projects/Hosteva")
from memory_migrator import chunk_markdown

def test_chunk_markdown_headers_and_bullets():
    md = """# Main Header
Some intro text.
* Bullet 1
* Bullet 2

## Sub Header
Details here.
"""
    chunks = chunk_markdown(md)
    # verify headers
    assert chunks[0]["metadata"]["parent_header"] == "Main Header"
    assert "Main Header" in chunks[0]["text"]
    assert "Some intro text." in chunks[0]["text"]
    
    # verify bullets
    assert chunks[1]["metadata"]["parent_header"] == "Main Header"
    assert "* Bullet 1" in chunks[1]["text"]
    
    assert chunks[2]["metadata"]["parent_header"] == "Main Header"
    assert "* Bullet 2" in chunks[2]["text"]

    # verify subheader
    assert chunks[3]["metadata"]["parent_header"] == "Sub Header"
    assert "## Sub Header" in chunks[3]["text"]
    assert "Details here." in chunks[3]["text"]

