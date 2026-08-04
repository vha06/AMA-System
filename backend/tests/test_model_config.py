import pytest
from src.core.config import (
    get_valid_google_model,
    get_valid_gemini_model,
    get_google_model_chain,
    get_gemini_model_chain,
    DEFAULT_WATERFALL_MODELS,
    Settings,
)


def test_get_valid_google_model_gemini():
    models = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-3-flash",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
    ]
    for model in models:
        assert get_valid_google_model(model) == model


def test_get_valid_google_model_gemma():
    gemma_models = ["gemma-4-26b-it", "gemma-4-31b-it"]
    for model in gemma_models:
        assert get_valid_google_model(model) == model


def test_get_valid_google_model_invalid_fallback():
    assert get_valid_google_model("invalid-model-name") == "gemini-3.5-flash"
    assert get_valid_google_model("") == "gemini-3.5-flash"


def test_backwards_compatibility_aliases():
    assert get_valid_gemini_model("gemma-4-31b-it") == "gemma-4-31b-it"
    chain = get_gemini_model_chain("gemma-4-26b-it")
    assert chain[0] == "gemma-4-26b-it"
    assert "gemini-3.5-flash" in chain


def test_waterfall_chain_ordering():
    chain = get_google_model_chain("gemma-4-31b-it")
    assert chain[0] == "gemma-4-31b-it"
    for model in DEFAULT_WATERFALL_MODELS:
        assert model in chain


def test_settings_llm_model(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "gemma-4-26b-it")
    s = Settings()
    assert s.LLM_MODEL == "gemma-4-26b-it"
    assert s.GEMINI_MODEL == "gemma-4-26b-it"
