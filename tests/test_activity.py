import pytest
from sentinel.activity.classifier import ActivityClassifier

def test_activity_classification_low():
    clf = ActivityClassifier()
    res = clf.classify(count=1, tracks=[], count_diff=0)
    assert res["activity"] == "Low Activity"
    assert res["confidence"] >= 0.70

def test_activity_classification_high():
    clf = ActivityClassifier()
    # High count and high movement
    res = clf.classify(count=15, tracks=[], count_diff=3, entry_rate=2.0)
    assert res["activity"] == "High Activity"
    assert "High" in res["probabilities"]
