import sys
import os

PROJECT_DIR = r"C:\GeoSense_Agent"

sys.path.insert(
    0,
    os.path.join(PROJECT_DIR, "src", "phase1_ml")
)

from site_scorer import score_location


def test_score_location_returns_dict():
    result = score_location(22.5535, 88.3520)

    assert isinstance(result, dict)


def test_score_location_required_keys():
    result = score_location(22.5535, 88.3520)

    required_keys = [
        "latitude",
        "longitude",
        "opportunity_score",
        "risk_score",
        "features",
        "shap_explanation",
        "verdict"
    ]

    for key in required_keys:
        assert key in result


def test_scores_are_valid():
    result = score_location(22.5535, 88.3520)

    assert 0 <= result["opportunity_score"] <= 10
    assert 0 <= result["risk_score"] <= 10


def test_verdict_is_valid():
    result = score_location(22.5535, 88.3520)

    assert result["verdict"] in [
        "GOOD SITE",
        "POOR SITE"
    ]