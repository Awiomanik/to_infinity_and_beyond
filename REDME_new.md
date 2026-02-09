Information below is a note to devs for rebuilding the README.md in the future.

## Cloud pipeline (Google Drive)

This repository uses a **manual cloud synchronization pipeline** for large and generated files
(renders, binaries, datasets) that are not stored directly in Git.

Cloud-related code is located in:

Src/Cloud

### Usage

Cloud synchronization must be triggered manually:

```bash
poetry run python -m Src.Cloud.run_sync_upload
```
This command:
- compares local and remote cloud manifests
- uploads new or changed files
- archives removed files
- updates manifests
- appends an entry to Src/Cloud/manifests/cloud_sync.log

Important rules
- Git commit / push does NOT sync the cloud
- Always run ```run_sync_upload``` after generating renders or large files
- Never modify or delete cloud files outside this pipeline
- Manifests and the sync log are the source of truth

## Python environment (Poetry)
This repository is managed using Poetry.

Setup from repository root:
```bash
poetry install
```
All scripts should be run via Poetry, e.g.:
```bash
poetry run python -m Src.Cloud.run_sync
```
Direct execution using python script.py is discouraged.

## Data safety
This project prioritizes explicit, manual workflows to avoid data loss.
If something is missing, the most likely cause is skipping cloud synchronization.



# New README.md:

<div align="center">

  <pre style="
    margin-top: 1.5em;
    padding: 0.5em 3.2em;
    display: inline-block;
    text-align: center;

    background: radial-gradient(circle at center,
      rgba(0,255,180,0.12),
      rgba(0,140,255,0.10),
      rgba(0,0,0,0.0));

    border: 1px solid rgba(0,190,255,0.35);
    border-radius: 18px;

    box-shadow:
      0 0 18px rgba(0,255,200,0.35),
      0 0 42px rgba(0,120,255,0.25);
  ">

<span style="
  display:block;
  font-size: 2.5em;
  font-weight: 900;
  letter-spacing: 0.05em;
  line-height: 1.0;
  margin-bottom: 0.01em;
  color: #7dffdc;
">
Holomorphic Dynamics
</span>

<span style="
  display:block;
  margin-top: 0.01em;
  font-size: 1.6em;
  letter-spacing: 0.05em;
  line-height: 0.05;
  margin-top: 0.01;
  color: #7ddcff;
">
an Odyssey from Chaos to Art
</span>

  </pre>

</div>