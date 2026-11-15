# Archived exploratory science-validation scripts

These scripts were moved from `science/validation/` on 2026-11-15 to keep the active `science/` package limited to maintained pipeline modules. Their contents are preserved unchanged. They document earlier catalogue audits and external-query attempts; they are not validated reusable pipeline components.

There are 22 scripts plus the former empty package initializer. Seven filenames begin with `test_`; these are exploratory scripts, not unit tests. Some make network requests or rely on old assumptions. The maintained automated suite lives in the repository `tests/` directory, and root pytest discovery is restricted to that directory.
