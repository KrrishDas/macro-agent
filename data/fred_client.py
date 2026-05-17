"""
data/fred_client.py
 
Thin wrapper around the FRED API.
 
Responsibilities:
  - Read the API key from the environment.
  - Fetch a time series by series_id.
  - Cache raw observations as JSON so repeated runs are fast and offline-safe.
  - Return a clean pandas DataFrame with typed columns.
 
Nothing about macro interpretation lives here — this is pure data access.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

logger = logging.getLogger(__name__)


DEFAULT_CACHE_DIR = Path(os.getenv("CACHE_DIR", "data/cache"))
DEFULT_LOOKBACK_YEARS = 10

class FredClient:
    """
    Fetches macroeconomic series from the St. Louis FRED API.
 
    Parameters
    ----------
    api_key : str | None
        FRED API key. Falls back to the FRED_API_KEY environment variable.
    cache_dir : Path | str | None
        Directory to store cached JSON responses. Pass None to disable caching.
 
    Usage
    -----
    >>> client = FredClient()
    >>> df = client.fetch("CPIAUCSL")
    >>> print(df.tail())
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path | str] = DEFAULT_CACHE_DIR,
    ) -> None:
        resolved_key = api_key or os.getenv("FRED_API_KEY")
        if not resolved_key:
            raise EnvironmentError(
                "FRED_API_KEY not set. Add it to your .env file or pass it explicitly."
            )
 
        self._fred = Fred(api_key=resolved_key)
 
        if cache_dir is not None:
            self._cache_dir = Path(cache_dir)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._cache_dir = None

    def fetch(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch a FRED series and return it as a DataFrame.
 
        Parameters
        ----------
        series_id : str
            FRED series identifier, e.g. "CPIAUCSL".
        start_date : str | None
            ISO date string "YYYY-MM-DD". Defaults to 10 years ago.
        end_date : str | None
            ISO date string "YYYY-MM-DD". Defaults to today.
 
        Returns
        -------
        pd.DataFrame
            Columns: ["date", "value"]
            - date  : datetime64[ns], sorted ascending, no timezone
            - value : float64, NaN rows dropped
        """
        start_date = start_date or self._default_start()
        end_date = end_date or datetime.today().strftime("%Y-%m-%d")
 
        cache_key = f"{series_id}_{start_date}_{end_date}"
 
        # Try cache first
        cached = self._load_cache(cache_key)
        if cached is not None:
            logger.debug("Cache hit: %s", cache_key)
            return cached
 
        # Fetch from FRED
        logger.info("Fetching from FRED: %s [%s → %s]", series_id, start_date, end_date)
        try:
            raw: pd.Series = self._fred.get_series(
                series_id,
                observation_start=start_date,
                observation_end=end_date,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to fetch FRED series '{series_id}': {exc}"
            ) from exc
 
        df = self._to_dataframe(raw)
        self._save_cache(cache_key, df)
        return df
    
    def fetch_many(
        self,
        series_ids: list[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch multiple series. Returns a dict keyed by series_id.
 
        Failed fetches are logged and excluded from the result rather than
        raising, so a single bad series_id does not abort the whole batch.
        """
        results: dict[str, pd.DataFrame] = {}
        for sid in series_ids:
            try:
                results[sid] = self.fetch(sid, start_date, end_date)
            except RuntimeError as exc:
                logger.warning("Skipping %s: %s", sid, exc)
        return results
    


    @staticmethod
    def _default_start() -> str:
        ten_years_ago = datetime.today() - timedelta(days=365 * DEFULT_LOOKBACK_YEARS)
        return ten_years_ago.strftime("%Y-%m-%d")
    
    @staticmethod
    def _to_dataframe(series: pd.Series) -> pd.DataFrame:
        df = series.reset_index()
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
        return df
    

    def _cache_path(self, cache_key: str) -> Optional[Path]:
        if self._cache_dir is None:
            return None
        safe_key = cache_key.replace("/", "_").replace(" ", "_")
        return self._cache_dir / f"{safe_key}.json"
    
    def _load_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        path = self._cache_path(cache_key)
        if path is None or not path.exists():
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"])
            return df
        except Exception as exc:
            logger.warning("Failed to load cache for %s: %s", cache_key, exc)
            return None
        
    def _save_cache(self, cache_key: str, df: pd.DataFrame) -> None:
        path = self._cache_path(cache_key)
        if path is None:
            return
        try:
            records = df.copy()
            records["date"] = records["date"].dt.strftime("%Y-%m-%d")
            path.write_text(json.dumps(records.to_dict(orient="records"), indent=2))
            logger.debug("Cached: %s", path)
        except Exception as exc:
            logger.warning("Failed to save cache for %s: %s", cache_key, exc)