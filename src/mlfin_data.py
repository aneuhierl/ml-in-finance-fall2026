"""Data loading for FIN 43800 / FIN 69000.

One file, no package, no install. A Colab notebook gets this by downloading
it from the course's public GitHub repo (see the setup cell in any week's
notebook) and then:

    import mlfin_data

Why this exists: course data is not committed to the public repo, and some
of it is copyrighted, so it cannot sit behind a public link either. Since
2026-09-23 the data files are posted on Brightspace: a student downloads a
file and uploads it into the Colab session (the Files pane, folder icon),
or puts it in a data/ folder on their own laptop. Clumsy, but the files are
small. Free public sources (yfinance, Ken French, Goyal-Welch) can still be
fetched from a plain URL through DATA_URLS, which ships empty.

Resolution order (see DESIGN.md section 4):

    1. a local copy      -- a file uploaded into Colab, or a data/ folder
    2. the download cache -- anything a previous call already fetched
    3. a direct download  -- DATA_URLS first, then DATA_URL_BASE

**Google Drive is deliberately NOT in this list.** `drive.mount()` was the
original design and was dropped 2026-09-04: it requires every student to
authenticate to Drive *and* requires the folder to be shared with each of
them individually. That per-student gate was the likeliest way for week 1
to fail in front of the room. Reading the data involves no sign-in; only
Colab itself needs a Google account.
"""
from __future__ import annotations

import shutil
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Where a file can be downloaded from. Two mechanisms, because the two kinds
# of link have different shapes:
#
#   DATA_URLS     -- a whole URL per file. This is what a Dropbox or Google
#                    Drive share link looks like: the file name does not
#                    appear in it, so it cannot be built from a base path.
#                    Paste the link exactly as the provider gives it, but
#                    make it a DIRECT download (Dropbox: end it "?dl=1";
#                    Drive: "https://drive.google.com/uc?export=download&id=<id>").
#
#   DATA_URL_BASE -- a folder whose files are addressed as base + "/" + name.
#                    Use this only when the files really do sit under one
#                    prefix, e.g. a GitHub raw path or a plain web server.
#
# DATA_URLS wins when a file appears in both. Either may be left empty.
# ---------------------------------------------------------------------------
DATA_URLS: dict[str, str] = {
    # "returns.csv": "https://www.dropbox.com/scl/fi/.../returns.csv?rlkey=...&dl=1",
}

DATA_URL_BASE = ""

# Where a downloaded file is kept so the next call (and the next runtime
# restart, in Colab) does not download it again. Also searched as a root.
DOWNLOAD_CACHE: Path = Path.home() / ".fin43800-data"

# Searched in order. The first existing file wins.
DEFAULT_SEARCH_ROOTS: list[Path] = [
    # Colab, file uploaded by hand into the session.
    Path("/content/data"),
    # Colab, file dragged into the Files pane (folder icon) -- it lands in
    # /content, the session's working folder. This is the Brightspace route.
    Path("/content"),
    # A local clone of the public repo.
    Path("data"),
    Path(__file__).resolve().parent.parent / "data",
    # Anything a previous call already downloaded.
    DOWNLOAD_CACHE,
]


class DataNotFoundError(FileNotFoundError):
    """Raised when a data file is in none of the search roots."""


def _download(filename: str, url: str, cache_dir: Path) -> Path:
    """Fetch `url` into `cache_dir` as `filename`; return its path.

    Downloads to a temporary name and renames on success, so an interrupted
    download can never leave a half-written file that the next call would
    happily read as data.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    destination = cache_dir / filename
    partial = cache_dir / (filename + ".partial")
    with urllib.request.urlopen(url, timeout=60) as response:
        with partial.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    partial.replace(destination)
    return destination


def _download_url_for(
    filename: str, urls: dict[str, str], url_base: str
) -> str | None:
    """Return the URL to fetch `filename` from, or None if none is configured.

    A per-file entry in `urls` wins over `url_base`, because a share link
    carries its own opaque path and cannot be derived from a prefix.
    """
    if filename in urls:
        return urls[filename]
    if url_base:
        return url_base.rstrip("/") + "/" + filename
    return None


def resolve_data_path(
    filename: str,
    search_roots: list[Path] | None = None,
    download_url_base: str | None = None,
    download_urls: dict[str, str] | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Return the path to `filename`, searching each root in order.

    If no root has it and a download URL is configured for it, download it
    into the cache directory and return that. `filename` must be a bare file
    name, not a path.
    """
    if "/" in filename or "\\" in filename or filename.startswith(".."):
        raise ValueError(
            f"filename must be a bare file name, not a path; got {filename!r}"
        )

    roots = search_roots if search_roots is not None else DEFAULT_SEARCH_ROOTS
    url_base = DATA_URL_BASE if download_url_base is None else download_url_base
    urls = DATA_URLS if download_urls is None else download_urls
    cache = DOWNLOAD_CACHE if cache_dir is None else cache_dir

    for root in roots:
        candidate = Path(root) / filename
        if candidate.is_file():
            return candidate

    url = _download_url_for(filename, urls, url_base)
    if url is None:
        download_note = (
            "\nNo download is configured for this file (neither DATA_URLS nor\n"
            "DATA_URL_BASE in src/mlfin_data.py names a source for it), so it\n"
            "has to come from Brightspace.\n"
        )
    else:
        try:
            return _download(filename, url, Path(cache))
        except (urllib.error.URLError, OSError, ValueError) as error:
            download_note = (
                f"\nThe download ({url}) also failed:\n"
                f"  {type(error).__name__}: {error}\n"
            )

    searched = "\n".join(f"  - {Path(r) / filename}" for r in roots)
    raise DataNotFoundError(
        f"Could not find {filename!r}. Looked in:\n{searched}\n"
        f"{download_note}\n"
        f"What to do: download {filename!r} from Brightspace, then\n"
        "  - in Colab: click the folder icon on the left and drag the file\n"
        "    into that pane. Colab deletes uploaded files when the session\n"
        "    ends, so you repeat this each time you come back.\n"
        "  - on your own laptop: put the file in a folder named data next to\n"
        "    the notebook.\n"
        "Then re-run this cell. Keep the file name exactly as it is."
    )


def load_returns(filename: str = "returns.csv") -> pd.DataFrame:
    """Load a returns panel, indexed by date.

    Returns are SIMPLE monthly returns in decimal form (0.01 = 1 percent),
    already in EXCESS of the risk-free rate. To annualize a mean of monthly
    simple returns, multiply by 12; to annualize a standard deviation of
    monthly returns, multiply by sqrt(12).
    """
    path = resolve_data_path(filename)
    frame = pd.read_csv(path, parse_dates=["date"])
    return frame.set_index("date").sort_index()
