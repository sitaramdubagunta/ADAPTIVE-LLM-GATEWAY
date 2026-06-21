def classify_prompt(prompt: str):
    score = 0
    prompt_lower = prompt.lower()

    if len(prompt.split()) > 30:
        score += 1

    coding_keywords = [
        "code",
        "python",
        "java",
        "c++",
        "algorithm",
        "leetcode",
        "bug",
        "debug",
    ]

    if any(word in prompt_lower for word in coding_keywords):
        score += 2

    reasoning_keywords = [
        "compare",
        "analyze",
        "design",
        "explain why",
        "tradeoff",
        "architecture",
    ]

    if any(word in prompt_lower for word in reasoning_keywords):
        score += 2

    if score >= 3:
        return "complex"

    return "simple"


def choose_provider(prompt: str):
    complexity = classify_prompt(prompt)

    print(f"Prompt classified as: {complexity}")

    if complexity == "simple":
        return "groq"

    return "gemini"