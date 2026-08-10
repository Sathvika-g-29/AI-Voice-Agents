LEARNING_PATHS = {
    "python": {
        "ai engineer": [
            "Python fundamentals",
            "NumPy and Pandas",
            "Machine Learning fundamentals",
            "scikit-learn",
            "Deep Learning with PyTorch",
            "LLMs and RAG",
            "LangChain and LangGraph",
        ],
        "software engineer": [
            "Python fundamentals",
            "Object Oriented Programming",
            "Data Structures and Algorithms",
            "SQL and databases",
            "REST APIs",
            "Git and GitHub",
        ],
    },
    "html": {
        "frontend developer": [
            "HTML fundamentals",
            "CSS",
            "JavaScript",
            "React",
            "Next.js",
        ],
    },
    "javascript": {
        "frontend developer": [
            "JavaScript fundamentals",
            "DOM and browser APIs",
            "React",
            "TypeScript",
            "Next.js",
        ],
    },
}


def get_learning_path(current_skill: str, goal: str) -> list[str] | None:
    skill = current_skill.strip().lower()
    target = goal.strip().lower()

    skill_data = LEARNING_PATHS.get(skill)

    if not skill_data:
        return None

    return skill_data.get(target)