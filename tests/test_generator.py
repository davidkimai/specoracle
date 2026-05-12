import pytest

from specoracle.config import KARPATHY_ORACLE_SPEC, ModelSettings, Task
from specoracle.generator import (
    MockLLMClient,
    OpenAIClient,
    SpecOracleGenerator,
    ToolCall,
    ToolCompletion,
    extract_python_code,
)


def test_extract_python_code_prefers_fenced_python_block() -> None:
    text = "Here:\n```python\ndef answer():\n    return 42\n```\nDone"

    assert extract_python_code(text) == "def answer():\n    return 42"


def test_extract_python_code_handles_unclosed_leading_fence() -> None:
    text = "```python\ndef answer():\n    return 42\n"

    assert extract_python_code(text) == "def answer():\n    return 42"


def test_task_schema_requires_human_reference() -> None:
    with pytest.raises(ValueError, match="human_reference"):
        Task.from_mapping(
            {
                "id": "missing_reference",
                "prompt": "Implement answer().",
                "test_code": "def test_placeholder():\n    assert True\n",
                "day2_prompt": "Add answer_text().",
                "day2_test_code": "def test_placeholder():\n    assert True\n",
            }
        )


def test_oracle_generation_routes_through_oracle_prompt() -> None:
    task = Task(
        id="demo",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code=(
            "from solution import answer_text\n\n"
            "def test_answer_text():\n    assert answer_text() == '42'\n"
        ),
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        entry_point="answer",
        mock_solution="def answer():\n    return 42\n",
        mock_day2_solution="def answer_text():\n    return '42'\n",
    )
    settings = ModelSettings(provider="mock", model="mock-local")
    generator = SpecOracleGenerator(MockLLMClient(), settings)

    baseline = generator.baseline_generation(task)
    oracle = generator.oracle_generation(task)

    assert baseline.variant == "baseline_generation"
    assert oracle.variant == "oracle_generation"
    assert "Zen of Python primitives" not in baseline.system_prompt
    assert "Zen of Python primitives" in oracle.system_prompt
    assert oracle.code == "def answer():\n    return 42"
    assert oracle.task["day2_prompt"] == "Add answer_text() -> str returning '42'."
    assert oracle.task["day2_stressors"] == ["interface_generalization"]
    assert oracle.task["human_reference"] == "def answer():\n    return 42\n"
    assert oracle.oracle_spec_label == "zen_of_python"


def test_custom_spec_override_replaces_zen_oracle_prompt() -> None:
    task = Task(
        id="legacy",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code=(
            "from solution import answer_text\n\n"
            "def test_answer_text():\n    assert answer_text() == '42'\n"
        ),
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        custom_spec_override="All helpers must have alliterative names and return tuples.",
        entry_point="answer",
        mock_solution="def answer():\n    return 42\n",
    )
    settings = ModelSettings(provider="mock", model="mock-local")
    generator = SpecOracleGenerator(MockLLMClient(), settings)

    oracle = generator.oracle_generation(task)

    assert oracle.oracle_spec_label == "custom_spec_override"
    assert oracle.oracle_spec == "All helpers must have alliterative names and return tuples."
    assert "Zen of Python primitives" not in oracle.system_prompt
    assert "All helpers must have alliterative names" in oracle.system_prompt


def test_karpathy_oracle_generation_uses_karpathy_prompt() -> None:
    task = Task(
        id="karpathy",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code="def test_placeholder():\n    assert True\n",
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        entry_point="answer",
        mock_solution="def answer():\n    return 42\n",
    )
    generator = SpecOracleGenerator(MockLLMClient(), ModelSettings(provider="mock", model="mock-local"))

    result = generator.karpathy_oracle_generation(task)

    assert result.mode == "oracle_karpathy"
    assert result.variant == "oracle_karpathy_generation"
    assert result.oracle_spec_label == "karpathy_oracle"
    assert result.oracle_spec == KARPATHY_ORACLE_SPEC
    assert "Karpathy Guidelines" in result.system_prompt
    assert "Zen of Python primitives" not in result.system_prompt


def test_neutral_style_generation_uses_neutral_prompt() -> None:
    task = Task(
        id="neutral",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code="def test_placeholder():\n    assert True\n",
        day2_stressors=("interface_generalization",),
        human_reference="def answer():\n    return 42\n",
        entry_point="answer",
        mock_solution="def answer():\n    return 42\n",
    )
    generator = SpecOracleGenerator(MockLLMClient(), ModelSettings(provider="mock", model="mock-local"))

    result = generator.neutral_style_generation(task)

    assert result.variant == "neutral_style_generation"
    assert "maintainable Python" in result.system_prompt
    assert "Zen of Python primitives" not in result.system_prompt


def test_modular_discovery_loads_skill_and_records_metadata() -> None:
    class ToolAwareClient:
        last_effective_temperature: float | None = None

        def __init__(self) -> None:
            self.final_prompt = ""

        def complete_with_tools(self, *, system_prompt, user_prompt, tools, settings):
            self.last_effective_temperature = settings.temperature
            assert tools[0]["name"] == "get_skill"
            assert "dafny" in user_prompt
            return ToolCompletion(
                text="",
                tool_calls=(ToolCall(name="get_skill", input={"skill_id": "dafny"}, id="t0"),),
                raw_response="tool call",
            )

        def complete(self, *, system_prompt, user_prompt, settings):
            self.final_prompt = user_prompt
            return "def answer():\n    return 42\n"

    task = Task(
        id="modular",
        prompt="Implement answer() -> int returning 42.",
        test_code="from solution import answer\n\ndef test_answer():\n    assert answer() == 42\n",
        day2_prompt="Add answer_text() -> str returning '42'.",
        day2_test_code="def test_placeholder():\n    assert True\n",
        day2_stressors=("formal_correctness",),
        human_reference="def answer():\n    return 42\n",
        entry_point="answer",
    )
    client = ToolAwareClient()
    generator = SpecOracleGenerator(client, ModelSettings(provider="mock", model="mock-local"))

    result = generator.modular_discovery_generation(task)

    assert result.mode == "modular_discovery"
    assert result.variant == "modular_discovery_generation"
    assert result.code == "def answer():\n    return 42"
    assert result.metadata is not None
    assert result.metadata["modular_discovery"]["selected_skill_ids"] == ["dafny"]
    assert "Dafny Formal Verification" in client.final_prompt


def test_openai_client_retries_without_temperature_when_model_rejects_it() -> None:
    class FakeResponse:
        output_text = "def answer():\n    return 42"

    class FakeResponses:
        def __init__(self) -> None:
            self.calls: list[dict] = []

        def create(self, **kwargs):
            self.calls.append(kwargs)
            if "temperature" in kwargs:
                raise RuntimeError("Unsupported parameter: 'temperature' is not supported")
            return FakeResponse()

    client = OpenAIClient.__new__(OpenAIClient)
    fake_responses = FakeResponses()
    client._client = type("FakeOpenAI", (), {"responses": fake_responses})()

    text = client.complete(
        system_prompt="system",
        user_prompt="user",
        settings=ModelSettings(provider="openai", model="gpt-5.5"),
    )

    assert text == "def answer():\n    return 42"
    assert "temperature" in fake_responses.calls[0]
    assert "temperature" not in fake_responses.calls[1]
    assert client.last_effective_temperature is None
