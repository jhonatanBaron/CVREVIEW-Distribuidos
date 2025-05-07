def is_valid_cv(text: str) -> bool:
    keywords = ["currículum", "cv", "experiencia", "formación", "educación", "perfil"]
    text_lower = text.lower()
    return any(k in text_lower for k in keywords)
