from .dark_spellbook import dark_spell_allowed_ingredients


def validate_ingredients(ingredients: str) -> str:
    """Tell whether the ingredients contain an allowed dark ingredient.

    The top-level import above, combined with the one in the dark
    spellbook, creates a circular dependency: importing either module
    blows up the laboratory.
    """
    lowered = ingredients.lower()
    allowed = dark_spell_allowed_ingredients()
    if any(ingredient in lowered for ingredient in allowed):
        return f"{ingredients} - VALID"
    return f"{ingredients} - INVALID"
