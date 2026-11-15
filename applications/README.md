# Teammate application source snapshots

This folder contains tracked source files copied into the main SPHEREx repository from the user's public GitHub repositories. Copying preserves the existing root `backend/` and `frontend/` directories, avoids nested Git repositories, and does not change either upstream repository. The source files and their original README/setup instructions are retained.

| Application | Upstream repository | Snapshot commit |
|---|---|---|
| Backend | <https://github.com/YashCBtech2024/Backend> | `dd39b966a9ad5b5e5cf7338776396e5cf9636bd0` |
| Frontend | <https://github.com/YashCBtech2024/Frontend> | `ef544a10b3a731351590a4100e889adf1f83d695` |

The two snapshots are under `applications/backend/` and `applications/frontend/`. Their source repository Git metadata is intentionally not included. To update a snapshot later, review the upstream changes first and copy them into a fresh comparison area; do not blindly overwrite local changes.

## Integration status

These are the teammates' existing application implementations, included as source snapshots. They are separate from the scientific backend/frontend adaptation under `spherex-temporary-integration/`; that temporary integration build consumes the actual processed SPHEREx products and has its own test report. Do not treat code or synthetic/demo fixtures in the upstream applications as scientific SPHEREx measurements. Preserve the null/provisional conventions documented in the scientific integration handoff.
