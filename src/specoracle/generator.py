from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from specoracle.config import (
    GENERATION_USER_TEMPLATE,
    GenerationMode,
    ModelSettings,
    NEUTRAL_STYLE_SPEC,
    Task,
    oracle_spec_for_task,
    oracle_spec_label_for_task,
    system_prompt_for_mode,
    variant_name,
)


class LLMClient(Protocol):
    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        settings: ModelSettings,
    ) -> str:
        """Return a single text completion for a system/user prompt pair."""


@dataclass(frozen=True)
class GenerationResult:
    task_id: str
    mode: GenerationMode
    variant: str
    provider: str
    model: str
    sample_index: int
    requested_temperature: float
    effective_temperature: float | None
    entry_point: str
    task: dict[str, Any]
    oracle_spec: str
    oracle_spec_label: str
    code: str
    raw_response: str
    system_prompt: str
    user_prompt: str
    hybrid: dict[str, Any] | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)


class OpenAIClient:
    def __init__(self, api_key: str | None = None) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self.last_effective_temperature: float | None = None

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        settings: ModelSettings,
    ) -> str:
        request = {
            "model": settings.model,
            "instructions": system_prompt,
            "input": user_prompt,
            "temperature": settings.temperature,
            "max_output_tokens": settings.max_tokens,
            "timeout": settings.timeout_seconds,
        }
        self.last_effective_temperature = settings.temperature
        try:
            response = self._client.responses.create(**request)
        except Exception as exc:
            if not _is_unsupported_temperature_error(exc):
                raise
            if settings.require_temperature:
                raise RuntimeError(
                    f"{settings.model} rejected temperature={settings.temperature}; "
                    "cannot claim independent samples with --require-temperature"
                ) from exc
            request.pop("temperature", None)
            self.last_effective_temperature = None
            response = self._client.responses.create(**request)
        return _extract_openai_text(response)


class AnthropicClient:
    def __init__(self, api_key: str | None = None) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Anthropic support requires the optional dependency: "
                "python -m pip install 'specoracle[anthropic]'"
            ) from exc

        self._client = Anthropic(api_key=api_key)
        self.last_effective_temperature: float | None = None

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        settings: ModelSettings,
    ) -> str:
        self.last_effective_temperature = settings.temperature
        response = self._client.messages.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            timeout=settings.timeout_seconds,
        )
        parts: list[str] = []
        for block in getattr(response, "content", []):
            text = getattr(block, "text", None)
            if text:
                parts.append(str(text))
        return "\n".join(parts).strip()


class GoogleClient:
    def __init__(self, api_key: str | None = None) -> None:
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "Google/Gemini support requires the optional dependency: "
                "python -m pip install 'specoracle[google]'"
            ) from exc

        self._client = genai.Client(api_key=api_key)
        self.last_effective_temperature: float | None = None

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        settings: ModelSettings,
    ) -> str:
        try:
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError(
                "Google/Gemini support requires the optional dependency: "
                "python -m pip install 'specoracle[google]'"
            ) from exc

        self.last_effective_temperature = settings.temperature
        response = self._client.models.generate_content(
            model=settings.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=settings.temperature,
                max_output_tokens=settings.max_tokens,
            ),
        )
        return _extract_google_text(response)


class MockLLMClient:
    """Offline client for smoke tests; not a research model."""

    last_effective_temperature: float | None = None

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        settings: ModelSettings,
    ) -> str:
        self.last_effective_temperature = settings.temperature
        if "strict JSON" in system_prompt or '"score"' in user_prompt:
            return (
                '{"score": 8, "rationale": "Readable, explicit, and locally auditable.", '
                '"strengths": ["simple control flow"], "weaknesses": ["mock judgment"]}'
            )
        return "def solution(*args, **kwargs):\n    raise NotImplementedError('mock task fixture missing')\n"


def build_llm_client(settings: ModelSettings) -> LLMClient:
    if settings.provider == "mock":
        return MockLLMClient()

    api_key = os.getenv(settings.api_key_env)
    if not api_key:
        raise RuntimeError(
            f"{settings.provider} provider requires ${settings.api_key_env}; "
            "set it in your shell or use --provider mock for an offline smoke run"
        )

    if settings.provider == "openai":
        return OpenAIClient(api_key=api_key)
    if settings.provider == "anthropic":
        return AnthropicClient(api_key=api_key)
    if settings.provider == "google":
        return GoogleClient(api_key=api_key)
    raise ValueError(f"unknown provider: {settings.provider}")


class SpecOracleGenerator:
    def __init__(self, client: LLMClient, settings: ModelSettings) -> None:
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> ModelSettings:
        return self._settings

    @property
    def client(self) -> LLMClient:
        return self._client

    def baseline_generation(self, task: Task) -> GenerationResult:
        return self.generate(task, mode="baseline")

    def oracle_generation(self, task: Task) -> GenerationResult:
        return self.generate(task, mode="oracle")

    def neutral_style_generation(self, task: Task) -> GenerationResult:
        return self.generate(task, mode="neutral_style")

    def generate(
        self,
        task: Task,
        *,
        mode: GenerationMode,
        sample_index: int = 0,
    ) -> GenerationResult:
        system_prompt = system_prompt_for_mode(mode, task=task)
        user_prompt = GENERATION_USER_TEMPLATE.format(
            task_id=task.id,
            entry_point=task.entry_point,
            prompt=task.prompt.strip(),
        )

        if self._settings.provider == "mock" and task.mock_solution:
            raw_response = task.mock_solution
        else:
            raw_response = self._client.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                settings=self._settings,
            )

        code = extract_python_code(raw_response)
        effective_temperature = getattr(
            self._client,
            "last_effective_temperature",
            self._settings.temperature,
        )
        active_spec = NEUTRAL_STYLE_SPEC if mode == "neutral_style" else oracle_spec_for_task(task)
        active_spec_label = "neutral_style" if mode == "neutral_style" else oracle_spec_label_for_task(task)
        return GenerationResult(
            task_id=task.id,
            mode=mode,
            variant=variant_name(mode),
            provider=self._settings.provider,
            model=self._settings.model,
            sample_index=sample_index,
            requested_temperature=self._settings.temperature,
            effective_temperature=effective_temperature,
            entry_point=task.entry_point,
            task=task.to_mapping(),
            oracle_spec=active_spec,
            oracle_spec_label=active_spec_label,
            code=code,
            raw_response=raw_response,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )


_PYTHON_FENCE = re.compile(r"```(?:python|py)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def extract_python_code(text: str) -> str:
    matches = _PYTHON_FENCE.findall(text)
    if matches:
        return max((match.strip() for match in matches), key=len)
    return text.strip()


def generation_result_from_mapping(
    payload: dict[str, Any],
    *,
    code: str | None = None,
) -> GenerationResult:
    return GenerationResult(
        task_id=str(payload["task_id"]),
        mode=_as_generation_mode(payload["mode"]),
        variant=str(payload["variant"]),
        provider=str(payload["provider"]),
        model=str(payload["model"]),
        sample_index=int(payload.get("sample_index", 0)),
        requested_temperature=float(payload["requested_temperature"]),
        effective_temperature=_optional_float(payload.get("effective_temperature")),
        entry_point=str(payload["entry_point"]),
        task=dict(payload.get("task") or {}),
        oracle_spec=str(payload.get("oracle_spec") or ""),
        oracle_spec_label=str(payload.get("oracle_spec_label") or ""),
        code=code if code is not None else str(payload.get("code") or ""),
        raw_response=str(payload.get("raw_response") or ""),
        system_prompt=str(payload.get("system_prompt") or ""),
        user_prompt=str(payload.get("user_prompt") or ""),
        hybrid=dict(payload["hybrid"]) if isinstance(payload.get("hybrid"), dict) else None,
    )


def _extract_openai_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text).strip()

    parts: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(str(text))
    return "\n".join(parts).strip()


def _extract_google_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return str(text).strip()

    parts: list[str] = []
    for candidate in getattr(response, "candidates", []) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            part_text = getattr(part, "text", None)
            if part_text:
                parts.append(str(part_text))
    return "\n".join(parts).strip()


def _is_unsupported_temperature_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "unsupported parameter" in message and "temperature" in message


def _as_generation_mode(value: Any) -> GenerationMode:
    if value in {"baseline", "oracle", "neutral_style", "hybrid"}:
        return value
    raise ValueError(f"unknown generation mode in artifact: {value}")


def _optional_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    return float(value)
