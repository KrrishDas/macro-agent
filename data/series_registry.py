"""
data/series_registry.py

Central registry of macroeconomic series used by the system.

Every FRED series the agent may use is declared here with:
  - its FRED series_id
  - a human-readable name
  - a short description
  - units label (for chart axis labels)
  - the data frequency
  - which macro topic(s) it belongs to

Tools and the agent loop use this registry to:
  - look up the correct series_id for a concept (e.g. "core inflation")
  - discover which series are relevant for a topic (e.g. "labor")
  - label charts and reports correctly

Adding a new series requires only a new entry in SERIES_REGISTRY —
no other file needs to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SeriesInfo:
    """
    Metadata for a single FRED series.

    Attributes:
        series_id : str
            Official FRED series identifier.
        name : str
            Short human-readable name for display.
        description : str
            One-sentence description of what the series measures.
        units : str
            Units label (used on chart axes and in reports).
        frequency : str
            Reporting frequency: "monthly", "quarterly", "weekly", "daily".
        topics : list[str]
            Macro topic tags. Used by the agent loop for routing.
            Standard topics: "inflation", "labor", "rates", "growth", "monetary_policy".
    """

    series_id: str
    name: str
    description: str
    units: str
    frequency: str
    topics: list[str] = field(default_factory=list)


SERIES_REGISTRY: dict[str, SeriesInfo] = {
    
    "CPIAUCSL": SeriesInfo(
        series_id="CPIAUCSL",
        name="CPI (Headline)",
        description="Consumer Price Index for All Urban Consumers: All Items. Seasonally adjusted.",
        units="Index (1982-84=100)",
        frequency="monthly",
        topics=["inflation"],
    ),
    "CPILFESL": SeriesInfo(
        series_id="CPILFESL",
        name="CPI (Core)",
        description="CPI for All Urban Consumers: All Items Less Food and Energy. Seasonally adjusted.",
        units="Index (1982-84=100)",
        frequency="monthly",
        topics=["inflation"],
    ),
    "PCEPI": SeriesInfo(
        series_id="PCEPI",
        name="PCE Price Index (Headline)",
        description="Personal Consumption Expenditures: Chain-type Price Index. The Fed's preferred inflation gauge.",
        units="Index (2012=100)",
        frequency="monthly",
        topics=["inflation", "monetary_policy"],
    ),
    "PCEPILFE": SeriesInfo(
        series_id="PCEPILFE",
        name="PCE Price Index (Core)",
        description="PCE excluding Food and Energy. Core PCE is the Fed's primary inflation target.",
        units="Index (2012=100)",
        frequency="monthly",
        topics=["inflation", "monetary_policy"],
    ),
    

    "UNRATE": SeriesInfo(
        series_id="UNRATE",
        name="Unemployment Rate",
        description="Civilian unemployment rate, seasonally adjusted.",
        units="Percent",
        frequency="monthly",
        topics=["labor"],
    ),
    "PAYEMS": SeriesInfo(
        series_id="PAYEMS",
        name="Nonfarm Payrolls",
        description="Total nonfarm employees on private and government payrolls. Seasonally adjusted.",
        units="Thousands of persons",
        frequency="monthly",
        topics=["labor"],
    ),
    "U6RATE": SeriesInfo(
        series_id="U6RATE",
        name="U-6 Unemployment Rate",
        description="Broadest measure of labor underutilization (includes discouraged + part-time for economic reasons).",
        units="Percent",
        frequency="monthly",
        topics=["labor"],
    ),
    "JTSJOL": SeriesInfo(
        series_id="JTSJOL",
        name="Job Openings",
        description="Job Openings: Total Nonfarm (JOLTS). Measures unfilled positions.",
        units="Thousands",
        frequency="monthly",
        topics=["labor"],
    ),
    

    "GS10": SeriesInfo(
        series_id="GS10",
        name="10-Year Treasury Yield",
        description="Market yield on US Treasury securities at 10-year constant maturity.",
        units="Percent",
        frequency="monthly",
        topics=["rates", "monetary_policy"],
    ),
    "GS2": SeriesInfo(
        series_id="GS2",
        name="2-Year Treasury Yield",
        description="Market yield on US Treasury securities at 2-year constant maturity.",
        units="Percent",
        frequency="monthly",
        topics=["rates", "monetary_policy"],
    ),
    "GS1": SeriesInfo(
        series_id="GS1",
        name="1-Year Treasury Yield",
        description="Market yield on US Treasury securities at 1-year constant maturity.",
        units="Percent",
        frequency="monthly",
        topics=["rates"],
    ),
    "FEDFUNDS": SeriesInfo(
        series_id="FEDFUNDS",
        name="Federal Funds Rate",
        description="Effective Federal Funds Rate. The Fed's primary short-term policy rate.",
        units="Percent",
        frequency="monthly",
        topics=["rates", "monetary_policy"],
    ),
    "T10Y2Y": SeriesInfo(
        series_id="T10Y2Y",
        name="10Y-2Y Treasury Spread",
        description="10-Year minus 2-Year Treasury yield spread. Key recession signal when negative.",
        units="Percent",
        frequency="daily",
        topics=["rates", "monetary_policy"],
    ),
    

    "GDP": SeriesInfo(
        series_id="GDP",
        name="GDP (Nominal)",
        description="Gross Domestic Product, seasonally adjusted annual rate.",
        units="Billions of dollars",
        frequency="quarterly",
        topics=["growth"],
    ),
    "GDPC1": SeriesInfo(
        series_id="GDPC1",
        name="GDP (Real)",
        description="Real Gross Domestic Product, chained 2017 dollars, seasonally adjusted annual rate.",
        units="Billions of chained 2017 dollars",
        frequency="quarterly",
        topics=["growth"],
    ),
    "INDPRO": SeriesInfo(
        series_id="INDPRO",
        name="Industrial Production Index",
        description="Index of real output in manufacturing, mining, and utilities. High-frequency growth proxy.",
        units="Index (2017=100)",
        frequency="monthly",
        topics=["growth"],
    ),
}



def get_series_info(series_id: str) -> Optional[SeriesInfo]:
    """
    Return metadata for a given series_id, or None if not registered.

    Parameters
    ----------
    series_id : str
        FRED series identifier, e.g. "CPIAUCSL".
    """
    return SERIES_REGISTRY.get(series_id)


def get_series_ids_for_topic(topic: str) -> list[str]:
    """
    Return all series_ids that belong to a given topic tag.

    Parameters
    ----------
    topic : str
        One of: "inflation", "labor", "rates", "growth", "monetary_policy".

    Returns
    -------
    list[str]
        Series IDs with that topic tag. Empty list if topic is unknown.

    Example
    -------
    >>> get_series_ids_for_topic("inflation")
    ['CPIAUCSL', 'CPILFESL', 'PCEPI', 'PCEPILFE']
    """
    return [
        info.series_id
        for info in SERIES_REGISTRY.values()
        if topic in info.topics
    ]


def list_topics() -> list[str]:
    """Return the sorted list of all unique topic tags in the registry."""
    topics: set[str] = set()
    for info in SERIES_REGISTRY.values():
        topics.update(info.topics)
    return sorted(topics)


def all_series_ids() -> list[str]:
    """Return all registered series IDs."""
    return list(SERIES_REGISTRY.keys())