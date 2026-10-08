from .dark_validator import validate_ingredients


def dark_spell_allowed_ingredients() -> list[str]:
    """Ingredients a dark spell may use."""
    return ["bats", "frogs", "arsenic", "eyeball"]


def dark_spell_record(spell_name: str, ingredients: str) -> str:
    """Record the spell if its ingredients pass validation."""
    verdict = validate_ingredients(ingredients)
    if verdict.endswith(" - VALID"):
        return f"Spell recorded: {spell_name} ({verdict})"
    return f"Spell rejected: {spell_name} ({verdict})"
