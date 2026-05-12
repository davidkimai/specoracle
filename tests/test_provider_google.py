import sys
import types

import pytest

from specoracle.config import ModelSettings, default_model_settings
from specoracle.generator import GoogleClient, build_llm_client


def test_google_default_uses_gemini_api_key_env() -> None:
    settings = default_model_settings("google", role="generator")

    assert settings.model == "gemini-2.5-pro"
    assert settings.api_key_env == "GEMINI_API_KEY"


def test_google_client_uses_generate_content(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class FakeConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeModels:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            return type("FakeResponse", (), {"text": "def answer():\n    return 42\n"})()

    class FakeClient:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.models = FakeModels()

    google_module = types.ModuleType("google")
    genai_module = types.ModuleType("google.genai")
    types_module = types.ModuleType("google.genai.types")
    genai_module.Client = FakeClient
    types_module.GenerateContentConfig = FakeConfig
    google_module.genai = genai_module
    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.genai", genai_module)
    monkeypatch.setitem(sys.modules, "google.genai.types", types_module)

    client = GoogleClient(api_key="fake")
    text = client.complete(
        system_prompt="system",
        user_prompt="user",
        settings=ModelSettings(provider="google", model="gemini-2.5-pro", temperature=0.8),
    )

    assert text == "def answer():\n    return 42"
    assert calls[0]["model"] == "gemini-2.5-pro"
    assert calls[0]["contents"] == "user"
    assert calls[0]["config"].kwargs["system_instruction"] == "system"
    assert calls[0]["config"].kwargs["temperature"] == 0.8
    assert client.last_effective_temperature == 0.8


def test_build_google_client_requires_gemini_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        build_llm_client(
            ModelSettings(
                provider="google",
                model="gemini-2.5-pro",
                api_key_env="GEMINI_API_KEY",
            )
        )
