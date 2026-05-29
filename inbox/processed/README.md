# inbox/processed/

This directory holds original source files after they have been digested into `knowledge/`.

## How it works

1. New materials are dropped into `inbox/`
2. The `inbox-processor` agent reads them, extracts relevant information, and files it into `knowledge/`
3. Originals are moved here (never deleted)
4. The hook `protect-inbox.sh` enforces this: you cannot edit files in `inbox/` directly

## Why this directory appears (almost) empty in git

Processed files are excluded from version control (`.gitignore`) because they are often
large binaries (PDFs, PPTX, DOCX, audio) that can reach tens of megabytes each. The
intellectual content is already extracted into the markdown files under `knowledge/`.

## If you need an original source file

Ask the project lead — the originals are preserved locally and can be shared on demand.
