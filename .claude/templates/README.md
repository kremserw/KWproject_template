# Content Templates

Reusable, tokenized skeletons that agents and skills **copy from** when creating new files — so every
artifact follows the same proven shape. These are source-of-truth fragments, not working files.

| Template | Copied by | Becomes |
|---|---|---|
| `_summary.md` | `/session-wrap`, linter, `/new-unit` | a folder's `knowledge/**/_summary.md` |
| `_index.md` | `inbox-processor` | a `knowledge/sources/materials/<bundle>/_index.md` manifest |
| `source-digest.md` | `inbox-processor` | a per-source digest in `knowledge/sources/<type>/` |
| `provenance-tag.md` | every agent/skill that writes knowledge | the `Source/Verification/Confidence` block |
| `report-main.md` | Writing Agent / `project-initializer` | `outputs/reports/main/<slug>-current.md` |
| `report-unit.md` | `/new-unit`, Writing Agent | `outputs/reports/units/<slug>-current.md` |
| `unit-knowledge.md` | `/new-unit` | `knowledge/units/<slug>/knowledge.md` |
| `session-log.md` | `/session-wrap` | a `sessions/<prefix>-<date>.md` entry |
| `index-trajectory.md` | `project-initializer` | one trajectory block in `INDEX.md` |
| `lint-report.md` | `knowledge-linter` | `working/review/knowledge-lint-<date>.md` |
| `review-report.md` | `report-reviewer` | `working/review/<slug>-review-<date>.md` |

Tokens (`{{...}}`) are filled when the template is instantiated. Keep these files generic; specialise
their *copies*, never the source.
