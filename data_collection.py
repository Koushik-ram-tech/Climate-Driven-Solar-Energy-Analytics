"""
data_collection.py
==================
NASA POWER Climate Data Downloader
-----------------------------------
Downloads daily meteorological data for 15 Indian cities from the
NASA POWER (Prediction Of Worldwide Energy Resources) API.

Features:
- Retry with exponential backoff
- Configurable via CLI arguments (argparse)
- File validation (empty, corrupted, missing data)
- Dataset statistics and metadata JSON export
- Structured logging to file + console
- Download summary CSV
- tqdm progress bar
- Custom User-Agent header

Usage:
    python data_collection.py
    python data_collection.py --start 20190101 --end 20241231
    python data_collection.py --start 20220101 --end 20231231 --output data/custom

Author : Koushik Ram
Project: Indian Urban Climate Data Pipeline
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# ── custom exceptions ─────────────────────────────────────────────────────────

class ValidationError(Exception):
    """
    Raised when user-supplied arguments (dates, paths) fail validation.

    Caught in main() to print a clean, user-friendly message and exit
    without a Python traceback — keeps CLI output professional.
    """

class DownloadError(Exception):
    """
    Raised when a city download fails all retry attempts.

    Separates network/API failures from programming bugs (which surface
    as standard exceptions), making log triage faster.
    """

class ConfigurationError(Exception):
    """
    Raised when static configuration is invalid before any download starts.

    Examples: empty PARAMETERS list, bad coordinate values, unwritable
    output directory.  Failing fast here prevents partial downloads that
    waste API quota and leave an inconsistent dataset on disk.
    """


# ── result dataclass ──────────────────────────────────────────────────────────

@dataclass
class DownloadResult:
    """
    Typed record for a single city's download outcome.

    Using a dataclass instead of a plain dict gives:
    - Compile-time field names (IDE autocomplete, no typo bugs)
    - Self-documenting structure (fields visible at a glance)
    - Free __repr__ for clean log output
    - Easy conversion to dict via dataclasses.asdict() for DataFrame/JSON

    Fields:
        city            : City name (matches CITIES key).
        status          : 'success' | 'skipped' | 'failed'.
        size_bytes      : File size on disk in bytes (0 on failure).
        rows            : Count of valid data rows (0 on failure).
        api_url         : Full URL used for this city's request.
        downloaded_at   : ISO-8601 UTC timestamp of the download attempt.
        duration_seconds: Wall-clock seconds spent on this city's download.
        validation_reason: 'ok' on success, or the failure reason string.
    """
    city:              str
    status:            str
    size_bytes:        int
    rows:              int
    api_url:           str
    downloaded_at:     str
    duration_seconds:  float
    validation_reason: str

# ── constants ─────────────────────────────────────────────────────────────────

CITIES: dict[str, tuple[float, float]] = {
    "Bengaluru":   (12.9716, 77.5946),
    "Chennai":     (13.0827, 80.2707),
    "Hyderabad":   (17.3850, 78.4867),
    "Kochi":       ( 9.9312, 76.2673),
    "Mangalore":   (12.9141, 74.8560),
    "Mumbai":      (19.0760, 72.8777),
    "Pune":        (18.5204, 73.8567),
    "Ahmedabad":   (23.0225, 72.5714),
    "Delhi":       (28.6139, 77.2090),
    "Chandigarh":  (30.7333, 76.7794),
    "Jaipur":      (26.9124, 75.7873),
    "Kolkata":     (22.5726, 88.3639),
    "Bhubaneswar": (20.2961, 85.8245),
    "Bhopal":      (23.2599, 77.4126),
    "Guwahati":    (26.1445, 91.7362),
}

# Added ALLSKY_SFC_SW_DNI (Direct Normal Irradiance) alongside existing parameters.
PARAMETERS: list[str] = [
    "T2M",              # Temperature at 2m (°C)
    "T2M_MAX",          # Daily max temperature (°C)
    "T2M_MIN",          # Daily min temperature (°C)
    "RH2M",             # Relative Humidity at 2m (%)
    "PS",               # Surface Pressure (kPa)
    "WS10M",            # Wind Speed at 10m (m/s)
    "CLOUD_AMT",        # Cloud Amount (%)
    "PRECTOTCORR",      # Precipitation (mm/day)
    "ALLSKY_SFC_SW_DWN", # Global Horizontal Irradiance (kWh/m²/day)
    "ALLSKY_SFC_SW_DNI", # Direct Normal Irradiance (kWh/m²/day)  ← NEW
]

# Default config — overridden by CLI if provided.
DEFAULT_START     = "20190101"
DEFAULT_END       = "20241231"
DEFAULT_OUTPUT    = Path("data/raw")

MAX_RETRIES       = 3
RETRY_DELAY       = 5    # seconds; doubles each retry (exponential backoff)
REQUEST_DELAY     = 1    # seconds between cities (API courtesy delay)
TIMEOUT           = 60   # seconds per request

# A valid NASA POWER CSV for a 6-year daily range is typically ~80 KB.
# Files below this threshold are almost certainly error responses or truncated.
# Tune downward if you use a shorter date range (e.g. 1 year ≈ 15 KB).
MIN_EXPECTED_BYTES = 10_000  # 10 KB

USER_AGENT        = (
    "IndianUrbanClimateResearch/1.0 "
    "(MCA Research Project, BMSCE Bengaluru; "
    "github.com/koushikram; koushikram@example.com)"
)

API_BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

# ── logging setup ─────────────────────────────────────────────────────────────

def setup_logging(log_dir: Path) -> logging.Logger:
    """
    Configure and return a logger that writes to both console and a log file.

    Args:
        log_dir: Directory where 'download.log' will be created.

    Returns:
        Configured Logger instance.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir.parent / "download.log"),
        ],
    )
    return logging.getLogger(__name__)


# ── CLI argument parsing ──────────────────────────────────────────────────────

def _parse_date(value: str) -> str:
    """
    Validate a date string is in strict YYYYMMDD format.

    Used as the `type=` converter in argparse so invalid dates are caught
    immediately, before any files are created or network calls are made.

    Args:
        value: Raw string from the command line.

    Returns:
        The original string unchanged if valid.

    Raises:
        argparse.ArgumentTypeError: With a human-friendly message if invalid.
    """
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Expected format: YYYYMMDD  (e.g. 20190101)"
        )
    return value


def parse_args() -> argparse.Namespace:
    """
    Parse and validate command-line arguments for the downloader.

    Supports:
        --start   Start date in YYYYMMDD format (default: 20190101)
        --end     End date in YYYYMMDD format   (default: 20241231)
        --output  Output directory              (default: data/raw)

    Returns:
        Parsed argparse.Namespace object.

    Raises:
        ValidationError: If start date is later than end date.
    """
    parser = argparse.ArgumentParser(
        description="NASA POWER Climate Data Downloader for Indian Cities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python data_collection.py\n"
            "  python data_collection.py --start 20200101 --end 20231231\n"
            "  python data_collection.py --start 20190101 --end 20241231 --output data/custom\n"
        ),
    )
    parser.add_argument(
        "--start",
        type=_parse_date,           # validates format immediately
        default=DEFAULT_START,
        metavar="YYYYMMDD",
        help=f"Start date for data download (default: {DEFAULT_START})",
    )
    parser.add_argument(
        "--end",
        type=_parse_date,           # validates format immediately
        default=DEFAULT_END,
        metavar="YYYYMMDD",
        help=f"End date for data download (default: {DEFAULT_END})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="DIR",
        help=f"Output directory for CSV files (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    # Cross-field validation: start must be before (or equal to) end.
    start_dt = datetime.strptime(args.start, "%Y%m%d")
    end_dt   = datetime.strptime(args.end,   "%Y%m%d")
    if start_dt > end_dt:
        raise ValidationError(
            f"--start ({args.start}) must not be later than --end ({args.end}).\n"
            f"  Hint: start={args.start}, end={args.end} — did you swap them?"
        )

    return args


# ── API helpers ───────────────────────────────────────────────────────────────

def build_url(lat: float, lon: float, start: str, end: str) -> str:
    """
    Construct the NASA POWER API request URL for a given location and date range.

    Args:
        lat:   Latitude of the city.
        lon:   Longitude of the city.
        start: Start date string in YYYYMMDD format.
        end:   End date string in YYYYMMDD format.

    Returns:
        Fully-formed API URL string.
    """
    params_str = ",".join(PARAMETERS)
    return (
        f"{API_BASE_URL}"
        f"?parameters={params_str}"
        f"&community=RE"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={start}"
        f"&end={end}"
        f"&format=CSV"
    )


def build_headers() -> dict[str, str]:
    """
    Build HTTP request headers including the custom User-Agent.

    A descriptive User-Agent helps the NASA POWER team identify legitimate
    research traffic and is considered good API citizenship.

    Returns:
        Dictionary of HTTP headers.
    """
    return {
        "User-Agent": USER_AGENT,
        "Accept":     "text/csv,text/plain,*/*",
    }


def create_session() -> requests.Session:
    """
    Create and return a configured requests.Session for all API calls.

    Why use a Session instead of requests.get()?
    ─────────────────────────────────────────────
    1. Connection reuse (HTTP keep-alive): the TCP connection to
       power.larc.nasa.gov stays open between requests, eliminating
       the TCP + TLS handshake overhead for every city. With 15 cities
       this saves ~15 × ~200ms = ~3 seconds of latency.
    2. Headers set once: User-Agent and Accept are attached to the session
       once and sent on every request automatically — no risk of forgetting
       them on a future request.
    3. Centralised configuration: timeout, auth, and retry adapters can all
       be attached here in one place if needed later.

    Returns:
        A requests.Session with default headers pre-configured.
    """
    session = requests.Session()
    session.headers.update(build_headers())
    return session


# ── configuration validation ──────────────────────────────────────────────────

def validate_configuration(output_dir: Path) -> None:
    """
    Validate static configuration before any download begins.

    Checks performed:
    1. PARAMETERS list is not empty.
    2. Every city has coordinates within valid geographic bounds.
    3. The output directory can be created and is writable.

    Failing here is intentional — it is far better to abort immediately
    with a clear message than to discover a misconfiguration after 10
    minutes of downloads have already partially completed.

    Args:
        output_dir: The directory where CSV files will be written.

    Raises:
        ConfigurationError: With a descriptive message for any failure.
    """
    # 1. Parameters must not be empty
    if not PARAMETERS:
        raise ConfigurationError(
            "PARAMETERS list is empty. Add at least one NASA POWER parameter "
            "(e.g. 'T2M') before running."
        )

    # 2. Validate each city's latitude/longitude
    for city, (lat, lon) in CITIES.items():
        if not (-90.0 <= lat <= 90.0):
            raise ConfigurationError(
                f"City '{city}' has invalid latitude {lat}. "
                f"Latitude must be between -90 and 90."
            )
        if not (-180.0 <= lon <= 180.0):
            raise ConfigurationError(
                f"City '{city}' has invalid longitude {lon}. "
                f"Longitude must be between -180 and 180."
            )

    # 3. Output directory must be writable
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        # Write a temporary probe file and immediately remove it
        probe = output_dir / ".write_check"
        probe.touch()
        probe.unlink()
    except OSError as exc:
        raise ConfigurationError(
            f"Output directory '{output_dir}' is not writable: {exc}\n"
            f"  Hint: Check permissions or choose a different --output path."
        )


# ── file validation ───────────────────────────────────────────────────────────

def count_data_rows(path: Path) -> int:
    """
    Count actual meteorological data rows in a NASA POWER CSV file.

    NASA POWER CSVs have a multi-line metadata header block before the
    data starts. This function skips all header/comment lines and counts
    only rows where the first four characters form a valid year (e.g. 2019).

    Robust against:
    - Blank lines
    - Metadata comment lines (starting with '-', letters, or spaces)
    - Column header lines (e.g. 'YEAR  MO  DY ...')

    Args:
        path: Path to the downloaded CSV file.

    Returns:
        Number of data rows, or -1 if the file cannot be read.
    """
    try:
        count = 0
        with path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                token = line.strip()[:4]
                # A valid data row starts with a 4-digit year (e.g. 2019-2024)
                if len(token) == 4 and token.isdigit() and 1900 <= int(token) <= 2100:
                    count += 1
        return count
    except OSError:
        return -1


def validate_file(path: Path, log: logging.Logger) -> tuple[bool, str]:
    """
    Validate a downloaded NASA POWER CSV for correctness and completeness.

    Checks performed (in order — fastest/cheapest first):
    1. File exists and size exceeds the minimum expected threshold.
    2. File does not contain an HTML response (server error pages).
    3. File does not contain a JSON error payload from the NASA POWER API.
    4. File contains at least one valid data row.

    Args:
        path: Path to the file to validate.
        log:  Logger instance for warning output.

    Returns:
        A tuple (is_valid: bool, reason: str).
        reason is 'ok' on success, or a short failure description.
    """
    # Check 1 — existence and minimum size
    if not path.exists():
        return False, "file does not exist"
    size = path.stat().st_size
    if size == 0:
        return False, "file is empty (0 bytes)"
    if size < MIN_EXPECTED_BYTES:
        return False, (
            f"file is suspiciously small ({size:,} bytes < {MIN_EXPECTED_BYTES:,} minimum). "
            f"Likely a truncated transfer or error response."
        )

    # Read a small prefix for header-level checks (avoid loading full multi-MB file)
    try:
        # 2 KB is enough to detect HTML/JSON response bodies
        with path.open(encoding="utf-8", errors="replace") as f:
            preview = f.read(2048)
    except OSError as exc:
        return False, f"cannot read file: {exc}"

    # Check 2 — HTML error page (e.g. 502 Bad Gateway returned as HTML)
    if preview.lstrip().startswith("<!") or "<html" in preview.lower():
        return False, "file contains an HTML response — server likely returned an error page"

    # Check 3 — JSON error payload (NASA POWER API error format)
    if preview.lstrip().startswith("{") and ('"errors"' in preview or '"message"' in preview):
        return False, "file contains a JSON error payload from the NASA POWER API"

    # Check 4 — at least one valid data row
    rows = count_data_rows(path)
    if rows <= 0:
        return False, f"no valid data rows found (count={rows}) — file may be corrupted"

    return True, "ok"


# ── core download ─────────────────────────────────────────────────────────────

def download_city(
    city: str,
    lat: float,
    lon: float,
    start: str,
    end: str,
    output_dir: Path,
    session: requests.Session,
    log: logging.Logger,
) -> DownloadResult:
    """
    Download NASA POWER climate data for a single city with retry logic.

    Behavior:
    - Skips download if a valid file already exists on disk.
    - Retries up to MAX_RETRIES times on HTTP or network errors.
    - Uses exponential backoff between retries.
    - Validates the downloaded file immediately after writing.
    - Removes corrupted/invalid files so they are re-downloaded next run.
    - Records per-city URL, timestamp, and wall-clock duration.

    Args:
        city:       Human-readable city name (also used as filename stem).
        lat:        Latitude of the city.
        lon:        Longitude of the city.
        start:      Start date string (YYYYMMDD).
        end:        End date string (YYYYMMDD).
        output_dir: Directory to write the CSV file into.
        session:    Shared requests.Session (connection reuse, pre-set headers).
        log:        Logger instance.

    Returns:
        DownloadResult dataclass with status, size, row count, URL,
        timestamp, duration, and validation reason.
    """
    file_path    = output_dir / f"{city}.csv"
    url          = build_url(lat, lon, start, end)
    city_start_t = time.monotonic()

    def _make_result(status: str, size: int, rows: int, reason: str) -> DownloadResult:
        """Helper to build a DownloadResult with auto-filled timing fields."""
        return DownloadResult(
            city=city,
            status=status,
            size_bytes=size,
            rows=rows,
            api_url=url,
            downloaded_at=datetime.now(timezone.utc).isoformat(),
            duration_seconds=round(time.monotonic() - city_start_t, 2),
            validation_reason=reason,
        )

    # ── skip if already valid ────────────────────────────────────────────────
    if file_path.exists():
        is_valid, reason = validate_file(file_path, log)
        if is_valid:
            size = file_path.stat().st_size
            rows = count_data_rows(file_path)
            log.info(f"{city}: already valid ({size:,} bytes, {rows} rows) — skipping")
            return _make_result("skipped", size, rows, reason)
        else:
            log.warning(f"{city}: existing file is invalid ({reason}) — re-downloading")
            file_path.unlink(missing_ok=True)

    wait = RETRY_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info(f"{city}: attempt {attempt}/{MAX_RETRIES} …")
            # Session reuses the TCP connection and sends pre-configured headers
            resp = session.get(url, timeout=TIMEOUT)
            resp.raise_for_status()

            file_path.write_bytes(resp.content)

            # ── validate immediately after writing ───────────────────────────
            is_valid, reason = validate_file(file_path, log)
            if not is_valid:
                log.warning(f"{city}: download failed validation ({reason}) — removing file")
                file_path.unlink(missing_ok=True)
                raise DownloadError(f"Validation failed: {reason}")

            size = file_path.stat().st_size
            rows = count_data_rows(file_path)
            log.info(f"{city}: ✓ saved  {size:,} bytes  {rows} data rows")
            return _make_result("success", size, rows, reason)

        except requests.exceptions.HTTPError as exc:
            code = exc.response.status_code if exc.response is not None else "?"
            log.warning(
                f"{city}: HTTP {code} — "
                f"{'retrying' if attempt < MAX_RETRIES else 'giving up'}"
            )
        except requests.exceptions.Timeout:
            log.warning(
                f"{city}: request timed out after {TIMEOUT}s — "
                f"{'retrying' if attempt < MAX_RETRIES else 'giving up'}"
            )
        except requests.exceptions.RequestException as exc:
            log.warning(
                f"{city}: {exc} — "
                f"{'retrying' if attempt < MAX_RETRIES else 'giving up'}"
            )
        except DownloadError as exc:
            log.warning(
                f"{city}: {exc} — "
                f"{'retrying' if attempt < MAX_RETRIES else 'giving up'}"
            )

        if attempt < MAX_RETRIES:
            log.info(f"{city}: waiting {wait}s before retry …")
            time.sleep(wait)
            wait *= 2   # exponential backoff: 5s → 10s → 20s

    log.error(f"{city}: all {MAX_RETRIES} attempts failed")
    return _make_result("failed", 0, 0, f"all {MAX_RETRIES} attempts exhausted")


# ── statistics & metadata ─────────────────────────────────────────────────────

def compute_statistics(results: list[DownloadResult]) -> dict:
    """
    Compute dataset-level statistics from a list of DownloadResult records.

    Args:
        results: List of DownloadResult dataclasses from the download loop.

    Returns:
        Dictionary of aggregated statistics.
    """
    total      = len(results)
    successful = sum(1 for r in results if r.status == "success")
    skipped    = sum(1 for r in results if r.status == "skipped")
    failed     = sum(1 for r in results if r.status == "failed")

    # Include skipped files in totals — they are valid on-disk datasets
    available       = [r for r in results if r.status in ("success", "skipped")]
    total_rows      = sum(r.rows       for r in available)
    total_size      = sum(r.size_bytes for r in available)
    avg_rows        = round(total_rows / len(available), 1) if available else 0.0

    # Timing stats (excludes skipped — no network call was made)
    timed = [r for r in results if r.status in ("success", "failed")]
    avg_duration = round(sum(r.duration_seconds for r in timed) / len(timed), 2) if timed else 0.0

    return {
        "total_cities":           total,
        "successful_downloads":   successful,
        "skipped_downloads":      skipped,
        "failed_downloads":       failed,
        "total_rows_downloaded":  total_rows,
        "total_size_bytes":       total_size,
        "total_size_mb":          round(total_size / (1024 * 1024), 2),
        "avg_rows_per_city":      avg_rows,
        "avg_download_seconds":   avg_duration,
    }


def write_metadata(
    output_dir: Path,
    start: str,
    end: str,
    results: list[DownloadResult],
    stats: dict,
    log: logging.Logger,
) -> None:
    """
    Write a dataset_metadata.json file summarising this download session.

    The JSON includes full provenance: when each city was downloaded, which
    exact API URL was used, and per-city validation outcomes.  This makes
    the dataset reproducible — anyone (including future-you) can re-run
    the exact same API calls that produced each CSV file.

    Args:
        output_dir: Directory to write 'dataset_metadata.json' into.
        start:      Start date used for this download.
        end:        End date used for this download.
        results:    List of DownloadResult records from the download loop.
        stats:      Pre-computed statistics dict.
        log:        Logger instance.
    """
    # Per-city detail block — includes API URL and timestamp for reproducibility
    city_details = [
        {
            "city":              r.city,
            "status":            r.status,
            "rows":              r.rows,
            "size_bytes":        r.size_bytes,
            "api_url":           r.api_url,
            "downloaded_at_utc": r.downloaded_at,
            "duration_seconds":  r.duration_seconds,
            "validation_reason": r.validation_reason,
        }
        for r in results
    ]

    metadata = {
        "dataset_name":    "Indian Urban Climate Data (NASA POWER)",
        "description":     (
            "Daily meteorological observations for 15 major Indian cities "
            "sourced from NASA POWER Prediction Of Worldwide Energy Resources API."
        ),
        "download_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "date_range": {
            "start": start,
            "end":   end,
        },
        "parameters": {p: _param_description(p) for p in PARAMETERS},
        "api_source":      API_BASE_URL,
        "community":       "RE (Renewable Energy)",
        "cities": {
            name: {"latitude": lat, "longitude": lon}
            for name, (lat, lon) in CITIES.items()
        },
        "statistics":   stats,
        "city_details": city_details,
    }

    meta_path = output_dir / "dataset_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    log.info(f"Metadata saved → {meta_path}")


def _param_description(param: str) -> str:
    """Return a human-readable description for a NASA POWER parameter code."""
    descriptions = {
        "T2M":              "Temperature at 2m height (°C)",
        "T2M_MAX":          "Daily maximum temperature at 2m (°C)",
        "T2M_MIN":          "Daily minimum temperature at 2m (°C)",
        "RH2M":             "Relative humidity at 2m (%)",
        "PS":               "Surface pressure (kPa)",
        "WS10M":            "Wind speed at 10m height (m/s)",
        "CLOUD_AMT":        "Cloud amount (%)",
        "PRECTOTCORR":      "Bias-corrected total precipitation (mm/day)",
        "ALLSKY_SFC_SW_DWN": "All-sky surface shortwave downward irradiance / GHI (kWh/m²/day)",
        "ALLSKY_SFC_SW_DNI": "All-sky surface shortwave direct normal irradiance / DNI (kWh/m²/day)",
    }
    return descriptions.get(param, param)


def write_quality_report(
    output_dir: Path,
    results: list[DownloadResult],
    log: logging.Logger,
) -> None:
    """
    Write a data_quality_report.json file for post-download inspection.

    Differs from dataset_metadata.json in purpose:
    - metadata.json answers "what is this dataset?"
    - quality_report.json answers "is this dataset trustworthy?"

    The report is structured for quick scanning: failures and warnings are
    promoted to the top, healthy cities are listed separately at the bottom.

    Args:
        output_dir: Directory to write 'data_quality_report.json' into.
        results:    List of DownloadResult records from the download loop.
        log:        Logger instance.
    """
    missing_files  = [
        r.city for r in results
        if r.status == "failed" or not (output_dir / f"{r.city}.csv").exists()
    ]
    failed_downloads = [r.city for r in results if r.status == "failed"]

    per_city = {}
    for r in results:
        file_path = output_dir / f"{r.city}.csv"
        per_city[r.city] = {
            "status":            r.status,
            "file_exists":       file_path.exists(),
            "file_size_bytes":   r.size_bytes,
            "row_count":         r.rows,
            "validation_status": "pass" if r.validation_reason == "ok" else "fail",
            "validation_detail": r.validation_reason,
            "downloaded_at_utc": r.downloaded_at,
            "duration_seconds":  r.duration_seconds,
        }

    report = {
        "report_generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_cities":    len(results),
            "missing_files":   missing_files,
            "failed_downloads": failed_downloads,
            "issues_detected": len(missing_files) > 0 or len(failed_downloads) > 0,
        },
        "per_city": per_city,
    }

    report_path = output_dir / "data_quality_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    log.info(f"Quality report saved → {report_path}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Entry point for the NASA POWER climate data downloader.

    Orchestrates:
    1. Argument parsing + date validation
    2. Configuration validation (coordinates, permissions, parameters)
    3. Logging setup
    4. Shared HTTP session creation
    5. Per-city downloads (with retry, skip, and file validation)
    6. Summary CSV export
    7. Dataset statistics computation (with timing)
    8. Metadata JSON export (with per-city URL + timestamps)
    9. Data quality report export
    10. Total execution time logging
    """
    # ── parse & validate CLI arguments ───────────────────────────────────────
    try:
        args = parse_args()
    except ValidationError as exc:
        # Print a clean, traceback-free message for user input errors
        print(f"\n  ERROR: {exc}\n")
        raise SystemExit(1)

    start_date = args.start
    end_date   = args.end
    output_dir = args.output

    # ── validate static config before touching the network ───────────────────
    try:
        validate_configuration(output_dir)
    except ConfigurationError as exc:
        print(f"\n  CONFIGURATION ERROR: {exc}\n")
        raise SystemExit(1)

    log = setup_logging(output_dir)

    # Wall-clock timer for total execution duration
    pipeline_start = time.monotonic()

    log.info("=" * 60)
    log.info("NASA POWER Climate Data Downloader")
    log.info(f"  Date range : {start_date} → {end_date}")
    log.info(f"  Output dir : {output_dir}")
    log.info(f"  Parameters : {', '.join(PARAMETERS)}")
    log.info(f"  Cities     : {len(CITIES)}")
    log.info("=" * 60)

    # ── progress bar (optional dependency) ───────────────────────────────────
    try:
        from tqdm import tqdm
        city_iter = tqdm(CITIES.items(), desc="Downloading", unit="city")
    except ImportError:
        log.warning("tqdm not installed — no progress bar  (pip install tqdm)")
        city_iter = CITIES.items()

    # ── shared HTTP session ───────────────────────────────────────────────────
    # One session for all 15 cities: reuses TCP connection, sends headers once.
    session = create_session()

    # ── download loop ─────────────────────────────────────────────────────────
    results: list[DownloadResult] = []
    with session:
        for city, (lat, lon) in city_iter:
            result = download_city(
                city, lat, lon, start_date, end_date, output_dir, session, log
            )
            results.append(result)
            if result.status != "skipped":
                time.sleep(REQUEST_DELAY)

    # ── summary CSV (convert dataclasses → DataFrame) ─────────────────────────
    summary  = pd.DataFrame([asdict(r) for r in results])
    log_path = output_dir / "download_log.csv"
    summary.to_csv(log_path, index=False)

    # ── dataset statistics ────────────────────────────────────────────────────
    stats = compute_statistics(results)

    total_elapsed = round(time.monotonic() - pipeline_start, 1)

    log.info("\n" + "─" * 60)
    log.info(summary[["city", "status", "rows", "size_bytes", "duration_seconds"]].to_string(index=False))
    log.info("─" * 60)
    log.info(f"  Total cities processed   : {stats['total_cities']}")
    log.info(f"  Successful downloads     : {stats['successful_downloads']}")
    log.info(f"  Skipped (existing valid) : {stats['skipped_downloads']}")
    log.info(f"  Failed downloads         : {stats['failed_downloads']}")
    log.info(f"  Total rows downloaded    : {stats['total_rows_downloaded']:,}")
    log.info(f"  Total data size          : {stats['total_size_mb']} MB")
    log.info(f"  Avg rows per city        : {stats['avg_rows_per_city']:,}")
    log.info(f"  Avg download time/city   : {stats['avg_download_seconds']}s")
    log.info(f"  Total pipeline runtime   : {total_elapsed}s")
    log.info("─" * 60)
    log.info(f"Download log saved → {log_path}")

    if stats["failed_downloads"] > 0:
        failed_cities = [r.city for r in results if r.status == "failed"]
        log.error(f"Failed cities: {failed_cities}")
        log.error("Re-run the script to retry failed cities automatically.")

    # ── metadata JSON ─────────────────────────────────────────────────────────
    write_metadata(output_dir, start_date, end_date, results, stats, log)

    # ── data quality report ───────────────────────────────────────────────────
    write_quality_report(output_dir, results, log)

    log.info("All done.")


if __name__ == "__main__":
    main()