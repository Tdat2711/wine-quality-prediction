"""Apply numeric type formatting without deleting valid statistical outliers."""

import pandas as pd


def format_and_handle_outliers(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Backward-compatible formatter retained for older imports.

    Statistical outliers are not removed here. Domain-aware outlier and noise
    handling is implemented in ``handle_outliers_and_noise.process_dataset``.
    """
    cleaned = df.copy(deep=True)
    report: dict[str, int] = {"outliers_removed": 0}

    for column in ("price", "points"):
        if column in cleaned.columns:
            before_missing = int(cleaned[column].isna().sum())
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
            after_missing = int(cleaned[column].isna().sum())
            report[f"{column}_values_coerced_to_missing"] = (
                after_missing - before_missing
            )

    return cleaned, report
