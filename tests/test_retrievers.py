"""Tests for the fuzzy side of the router (no API key or embedding model needed)."""
from common.llm import clean_translation
from locrag.retrievers import FuzzyRetriever, band_of, cat_fuzzy

TM = [
    {"id": "tm0", "src": "Keep this medicine out of the sight and reach of children.", "tgt": "Mantener fuera de la vista y del alcance de los niños."},
    {"id": "tm1", "src": "Do not store above 25 °C.", "tgt": "No conservar a temperatura superior a 25 °C."},
    {"id": "tm2", "src": "Swallow the tablets whole with a glass of water.", "tgt": "Trague los comprimidos enteros con un vaso de agua."},
]


def test_cat_fuzzy_is_word_level_percentage():
    assert cat_fuzzy("Do not store above 25 °C.", "Do not store above 25 °C.") == 100
    assert 75 <= cat_fuzzy("Do not store above 30 °C.", "Do not store above 25 °C.") < 100


def test_bands_match_cat_conventions():
    assert band_of(100) == "100" and band_of(96) == "95-99" and band_of(74.9) == "50-74" and band_of(10) == "<50"


def test_fuzzy_retriever_finds_near_match_first():
    hits = FuzzyRetriever(TM).search("Swallow the tablet whole with a glass of water.", k=2)
    assert hits[0].idx == 2 and hits[0].score >= 75


def test_reworded_segment_falls_below_cat_threshold():
    # same meaning, different words: invisible to fuzzy matching (this is the case LocRAG handles)
    hits = FuzzyRetriever(TM).search("Store this product where children cannot see or reach it.", k=1)
    assert hits[0].score < 75


def test_clean_translation_joins_multiline_output():
    assert clean_translation("ES: Frecuentes: prurito\nPoco frecuentes: eritema") == "Frecuentes: prurito Poco frecuentes: eritema"
