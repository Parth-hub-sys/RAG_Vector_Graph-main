import pytest
from ingestion.graph_store import clean_relationship


def test_uppercase():
    assert clean_relationship("authored") == "AUTHORED"

def test_spaces_replaced():
    assert clean_relationship("has skill") == "HAS_SKILL"

def test_special_chars_replaced():
    assert clean_relationship("works-at!") == "WORKS_AT_"

def test_already_clean():
    assert clean_relationship("WORKS_AT") == "WORKS_AT"

def test_numbers_preserved():
    assert clean_relationship("has_2_skills") == "HAS_2_SKILLS"

def test_arrow_relation():
    result = clean_relationship("→")
    assert isinstance(result, str)
