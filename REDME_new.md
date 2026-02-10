Information below is a note to devs for rebuilding the README.md in the future.

## Cloud pipeline (Google Drive)

This repository uses a **manual cloud synchronization pipeline** for large and generated files
(renders, binaries, datasets) that are not stored directly in Git.

Cloud-related code is located in:

Src/Cloud

## Cloud assets (after clone)

This repository is **not a Python package**.
Poetry is used only for **dependency management and virtual environment setup**.

This repository stores large binary files (renders, PDFs, datasets) in Google Drive.

After cloning the repo, **binary assets are NOT present locally by default**.

To restore all files from the cloud:

```bash
poetry install
poetry run python -m Src.Cloud.scripts.public_pull
```

What this does:

- reads Src/Cloud/manifests/public_index.json
- downloads missing files from Google Drive (no credentials required)
- skips files that already exist locally and match hashes
- interactively asks what to do on conflicts or corrupted files

Typical use cases:
- fresh clone on a new machine
- restoring files after accidental deletion
- safely removing the repo locally and rebuilding it later

If the script reports hash mismatches or permission errors, do not ignore them – they indicate an inconsistent local state or incorrect Drive sharing.

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


- `Rendering_tool` jest modułem projektu i **nie powinien być uruchamiany jako standalone script**.
- Narzędzie zakłada uruchamianie przez środowisko Poetry:
  
  `poetry run python -m Src.Rendering_tool.Rendering_tool`

- Kod nie może polegać na aktualnym katalogu roboczym (CWD).
  Wszystkie ścieżki do zasobów i rendererów powinny być rozwiązywane
  względem lokalizacji modułu (`__file__`), nie `os.getcwd()`.

- Renderery i pliki wyjściowe (PNG/GIF/DAT) są traktowane jako assety binarne
  i **nie powinny trafiać do gita**. Obowiązują reguły `.gitignore` i pipeline chmurowy.

- Struktura projektu jest w trakcie porządkowania.
  README opisowe i interfejs użytkownika zostaną ustabilizowane później.

Rendering tool uruchamiany jest przez entry point Poetry:
`poetry run render`












  


# New README.md:
<!---
<div align="center">

  <div style="
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

<div style="
  display:block;
  font-size: 2.5em;
  font-weight: 800;
  letter-spacing: 0.01em;
  line-height: 1.5;
  margin-bottom: 0.1em;
  color: #7dffdc;
">
Holomorphic Dynamics
</div>

<div style="
  display:block;
  margin-top: 0.1em;
  font-size: 1.9em;
  font-weight: 750;
  letter-spacing: 0.01em;
  line-height: 1.0;
  margin-top: 0.01;
  margin-bottom: 0.5em;
  color: #7ddcff;
">
an Odyssey from Chaos to Art
</div>
-->

<div align="center">
  <h1 style="margin: 0;">Holomorphic Dynamics:</h1>
  <h2 style="margin: 0;">an Odyssey from Chaos to Art</h2>
  <br>
</div>

This repository contains a collection of algorithms and visualization tools aimed at exploring the fascinating world of fractals, developed as a learning endeavour to deepen our understanding of both programming and complex mathematical concepts.

Explore various fractals with Python shell scripts, Jupyter notebooks and LaTex documents. This project is aimed at learning coding and exploring math.