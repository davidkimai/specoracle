from pathlib import Path

import pytest

from specoracle.skills import load_skill_oracle


def test_load_skill_oracle_parses_frontmatter_and_body(tmp_path: Path) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        """---
name: demo-skill
description: Use for demo oracle loading.
---

# Demo

Prefer simple code.
""",
        encoding="utf-8",
    )

    name, body = load_skill_oracle(skill)

    assert name == "demo-skill"
    assert "Prefer simple code." in body


def test_load_skill_oracle_requires_description(tmp_path: Path) -> None:
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        """---
name: demo-skill
---

Body.
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="description"):
        load_skill_oracle(skill)


def test_packaged_skill_oracles_parse() -> None:
    for path in [
        Path("data/skills/zen-of-python-oracle/SKILL.md"),
        Path("data/skills/karpathy-guidelines-oracle/SKILL.md"),
    ]:
        name, body = load_skill_oracle(path)
        assert name
        assert len(body) > 100
