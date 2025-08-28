# NO_TOOL_BACKUPS.md
Use Git for history — do not commit tool-created backups or zips into the repo.
- Keep local backups under `backups/` (ignored) or use OS/system backups.
- Never commit keys or `.env` files. Use `.env.example` with placeholders.
- If a tool generates a backup, move it to `backups/` or delete it.
