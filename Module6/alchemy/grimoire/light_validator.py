def validate_ingredients(ingredients: str) -> str:
    """Tell whether the ingredients contain an allowed light ingredient.

    The spellbook is imported inside the function, once both modules
    are fully loaded, which breaks the circular dependency between
    the spellbook and this validator.
    """
    from .light_spellbook import light_spell_allowed_ingredients

    lowered = ingredients.lower()
    allowed = light_spell_allowed_ingredients()
    if any(ingredient in lowered for ingredient in allowed):
        return f"{ingredients} - VALID"
    return f"{ingredients} - INVALID"
