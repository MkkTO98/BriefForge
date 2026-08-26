# Interactive browser report rendering

Use BriefForge’s supported interactive route when a complete structured interactive-report JSON configuration already exists:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/render_interactive_report.py \
  --config /absolute/path/to/report_config.json \
  --output /absolute/path/to/index.html
```

The command reads only the explicitly named configuration, creates the output parent directory when needed, and writes one deterministic, self-contained HTML file through `briefforge.interactive_report_foundation`.

This route does not obtain data, analyze evidence, infer configuration from neighbouring files, or repair generated HTML. The configuration must already contain the report’s content, data, navigation, controls and evidence labels.

For explicitly requested minimal/static Ready-Package output, continue to use the legacy `render_minimal_html` route documented in `docs/minimal-html-renderer.md`. Do not send legacy presentation packages through the interactive command, and do not use the minimal/static renderer for a structured interactive browser report.
