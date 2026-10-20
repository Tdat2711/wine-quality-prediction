"""Remove exported row IDs and exact duplicates; flag ambiguous matches."""

import pandas as pd


LOGICAL_DUPLICATE_KEY = ["description", "taster_name"]


def find_possible_logical_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Return exact-deduplicated rows that still share the logical key."""
    if not all(column in df.columns for column in LOGICAL_DUPLICATE_KEY):
        return df.iloc[0:0].copy()
    candidate_mask = df.duplicated(subset=LOGICAL_DUPLICATE_KEY, keep=False)
    return df.loc[candidate_mask].sort_values(LOGICAL_DUPLICATE_KEY).reset_index(drop=True)


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy(deep=True)
    report: dict[str, int] = {}

    if "Unnamed: 0" in cleaned.columns:
        cleaned = cleaned.drop(columns=["Unnamed: 0"])
        report["system_index_columns_removed"] = 1
    else:
        report["system_index_columns_removed"] = 0

    initial_rows = len(cleaned)
    cleaned = cleaned.drop_duplicates(keep="first").reset_index(drop=True)
    report["exact_duplicates_removed"] = initial_rows - len(cleaned)

    candidates = find_possible_logical_duplicates(cleaned)
    report["possible_logical_duplicate_rows"] = len(candidates)
    report["possible_logical_duplicate_groups"] = int(
        candidates[LOGICAL_DUPLICATE_KEY].drop_duplicates().shape[0]
    ) if len(candidates) else 0

    return cleaned, report
