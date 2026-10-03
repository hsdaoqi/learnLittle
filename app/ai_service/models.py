"""Model roles share credentials but may select different model names."""

from app.config import Settings


def settings_for_role(settings: Settings, role: str) -> Settings:
    names = {
        "classifier": settings.classifier_model,
        "plan": settings.plan_model,
        "reflection": settings.reflection_model or settings.plan_model,
        "title": settings.title_model or settings.classifier_model,
    }
    return settings.model_copy(update={"llm_model": names.get(role) or settings.llm_model})
