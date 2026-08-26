# Folder Summary Policy

Folder summaries remain in the project as context-map inputs. They are not separate truth sources.

Rules:
- Canonical maintainer: `tools/update_context_summaries.py`.
- Summaries refresh when folders change, tasks complete, or context is built with `--refresh-summaries`.
- Agents may refine Purpose/Active Work/Needs Attention, but must not contradict state or decision artifacts.
- No separate legacy summary updater should be used.
