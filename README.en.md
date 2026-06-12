# Codex Chinese Automation Kit

An open-source Codex plugin that turns Chinese-language automation requests
into validated configurations, source-backed daily briefs, and XLSX reports.

## Features

- `automation-builder-zh` creates a fixed automation JSON contract.
- `source-backed-daily-brief` preserves sources, timestamps, and access issues.
- `report-to-xlsx` exports validated reports using only the Python standard
  library.

The project does not ship scrapers, credentials, or fabricated data. Codex
collects sources with available tools; the bundled scripts provide deterministic
validation and export.

## Requirements

- A Codex environment with plugin support
- Python 3.9+
- No third-party Python runtime dependencies

## Quick Start

```bash
python3 scripts/validate_config.py examples/automation.json
python3 scripts/validate_report.py examples/daily-brief.json
python3 scripts/report_to_xlsx.py examples/daily-brief.json outputs/demo.xlsx
python3 -m zipfile -t outputs/demo.xlsx
python3 -m unittest discover -s tests -v
```

Load the repository as a local Codex plugin source and invoke:

```text
$automation-builder-zh
$source-backed-daily-brief
$report-to-xlsx
```

## License

[MIT](LICENSE)

