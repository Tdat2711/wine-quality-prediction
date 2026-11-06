"""Enforce text consistency without changing domain-specific identifiers."""

import pandas as pd


COUNTRY_ALIASES = {
    "Us": "US",
    "Usa": "US",
    "United States": "US",
}


def enforce_consistency(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    cleaned = df.copy(deep=True)
    report: dict[str, int] = {}

    string_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        cleaned[col] = cleaned[col].astype("string").str.strip()
        cleaned[col] = cleaned[col].str.replace(r"\s+", " ", regex=True)

    report["formatted_text_columns"] = len(string_cols)

    if "country" in cleaned.columns:
        before = cleaned["country"].copy()
        cleaned["country"] = cleaned["country"].replace(COUNTRY_ALIASES)
        report["country_values_standardized"] = int(
            before.fillna("<NA>").ne(cleaned["country"].fillna("<NA>")).sum()
        )

    if "taster_twitter_handle" in cleaned.columns:
        handle = cleaned["taster_twitter_handle"]
        mask = (
            handle.notna()
            & ~handle.isin(["Not provided", "Unknown"])
            & ~handle.str.startswith("@", na=False)
        )
        cleaned.loc[mask, "taster_twitter_handle"] = "@" + handle.loc[mask]
        report["twitter_handles_fixed"] = int(mask.sum())

    return cleaned, report
