# Project Architecture Map - OpenClaw Factory: Hosteva

This document outlines the architectural structure and key components of the Hosteva project.

## Directory Structure Overview

-   **`agents/`**: Contains various AI agents, each designed for specific tasks.
    -   **`agents/iron-man/`**: Iron Man-themed agents.
        -   `snap_algorithm.py`: Implements a "snap" algorithm, possibly for data cleanup or simulating resource reduction, by randomly deleting half of the files in a target directory. It includes error handling and a test execution block.
-   **`app/`**: Houses the core application logic, configuration, scripts, and static assets.
    -   **`app/core/`**: Contains core application configurations.
        -   `config.py`: Defines application settings using Pydantic's `BaseSettings`.
    -   **`app/scripts/`**: Utility scripts for the application.
        -   `seed_florida_ordinances.py`: A script responsible for seeding a test ordinance for Florida State into a production database via an external API endpoint (`https://hosteva.onrender.com/api/ordinances/ingest`). It uses `requests` for HTTP POST and includes error handling.
    -   **`app/static/`**: Directory for static web assets.
        -   `.gitkeep`: Placeholder file to ensure the directory is tracked by Git.
-   **`backend/`**: No files from this directory were provided for analysis.
-   **`frontend/`**: No files from this directory were provided for analysis.
-   **`scrum_master.py`**: A placeholder file, possibly for a main orchestrator script or a general scrum-related utility, with a `TODO` for "Shuri's review of V3 architecture".
-   **`scrum_pipelines/`**: Contains definitions and configurations for automated scrum processes or AI-driven workflows.
    -   `gb_config.py`: Configuration for Graphbit workflows. It loads environment variables, initializes Graphbit, defines an LLM configuration for `ollama('llama3.1-orchestrator')`, and includes a `run_single_agent` function. This function constructs and executes a Graphbit workflow for a single agent, loading skills from `skills/` directory, crafting prompts, and integrating tools like `run_shell_command`, `read_file`, and `write_file`. It emphasizes absolute paths for file operations within the project root `/home/rdogen/OpenClaw_Factory/projects/Hosteva`.

## Key Components and Their Interactions:

1.  **AI Agents (`agents/`)**:
    *   **`snap_algorithm.py`**: A utility agent, potentially for system maintenance or controlled data reduction scenarios. It interacts with the file system (`os` module) to delete files.
2.  **Application Scripts (`app/scripts/`)**:
    *   **`seed_florida_ordinances.py`**: An external API client that interacts with `https://hosteva.onrender.com/api/ordinances/ingest` to populate the database with test data. It depends on the `requests` library.
3.  **Scrum Orchestration (`scrum_pipelines/gb_config.py`)**:
    *   **Graphbit Integration**: Uses the `graphbit` library to define and execute AI agent workflows.
    *   **LLM Configuration**: Configured to use `ollama` with `llama3.1-orchestrator` as the language model.
    *   **Agent Execution**: The `run_single_agent` function is central to executing individual AI agents. It dynamically loads agent skills, crafts system prompts, and enables agents to use a set of predefined `swarm_tools` (e.g., `run_shell_command`, `read_file`, `write_file`).
    *   **Environment Variables**: Relies on `.env` files for configuration, loaded from the project root.
    *   **Tool Usage**: Emphasizes the critical use of `write_file` for physical code changes and strict adherence to absolute file paths rooted at `/home/rdogen/OpenClaw_Factory/projects/Hosteva`.

## Dependencies:

*   `os` (Python standard library)
*   `random` (Python standard library)
*   `requests` (external library)
*   `dotenv` (external library)
*   `graphbit` (external library)
*   `swarm_tools` (internal/local library, specifically `run_shell_command`, `read_file`, `write_file`)

## Future Considerations (from TODOs):

*   **`scrum_master.py`**: Awaiting "Shuri's review of V3 architecture", indicating ongoing development or design phases for a larger system.

This map provides a high-level overview. For detailed understanding, refer to the individual source files.
