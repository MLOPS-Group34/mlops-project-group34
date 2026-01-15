> Guidance for autonomous coding agents
> Read this before writing, editing, or executing anything in this repo.

# Relevant commands

* The project uses `uv` for management of virtual environments. This means:
  * To install packages, use `uv add <package-name>`.
  * To run Python scripts, use `uv run <script-name>.py`.
  * To run other commands related to Python, prefix them with `uv run `, e.g., `uv run <command>`.
* The project uses `pytest` for testing. To run tests, use `uv run pytest tests/`.
* The project uses `ruff` for linting and formatting:
    * To format code, use `uv run ruff format .`.
    * To lint code, use `uv run ruff check . --fix`.
* The project uses `invoke` for task management. To see available tasks, use `uv run invoke --list` or refer to the
    `tasks.py` file.
* The project uses `pre-commit` for managing pre-commit hooks. To run all hooks on all files, use
    `uv run pre-commit run --all-files`. For more information, refer to the `.pre-commit-config.yaml` file.
* The project uses **Weights & Biases (wandb)** for experiment tracking and logging:
    * Make sure to create a `.env` file with your `WANDB_API_KEY` (see `.env.example`).
    * Training and evaluation metrics are automatically logged to wandb.
    * View results at wandb.ai after running experiments.
    * See `docs/WANDB_INTEGRATION.md` for detailed setup and usage.
* Update this `AGENTS.md` file if any new tools or commands are added to the project.
