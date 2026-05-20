"""Database module with connection management and CRUD operations."""

import os
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Use data/ subdirectory so it works in Docker with volume mounts
DATABASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "prompts.db"
)


def _ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)


@contextmanager
def get_db_connection():
    """Context manager for safe database connections."""
    conn = None
    try:
        _ensure_data_dir()
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Initialize database schema and seed data if empty."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                prompt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute("SELECT COUNT(*) FROM prompts")
        if cursor.fetchone()[0] == 0:
            seed_data = [
                (
                    "AI Creativity",
                    "AI & Technology",
                    "Can artificial intelligence be truly creative? Analyze current examples and theoretical limits.",
                ),
                (
                    "Consciousness",
                    "Philosophy",
                    "Is consciousness an emergent property of complex computation, or does it require a fundamentally different physical process?",
                ),
                (
                    "Quantum Reality",
                    "Physics",
                    "Does quantum mechanics imply that reality is probabilistic at a fundamental level? Compare Copenhagen and Many Worlds interpretations.",
                ),
                (
                    "AI Alignment",
                    "AI & Technology",
                    "What are the core technical challenges in aligning advanced AI systems with human values? Evaluate reward modeling and constitutional AI.",
                ),
                (
                    "Free Will",
                    "Philosophy",
                    "Is free will compatible with determinism? Examine compatibilism, libertarianism, and neuroscientific evidence.",
                ),
                (
                    "Information Theory",
                    "Mathematics",
                    "How does Shannon information theory define information, and how does it differ from semantic meaning?",
                ),
                (
                    "Black Holes",
                    "Physics",
                    "What happens to information that falls into a black hole? Discuss Hawking radiation and the information paradox.",
                ),
                (
                    "Evolution & Intelligence",
                    "Biology",
                    "Is human intelligence an inevitable outcome of evolution, or a rare accident?",
                ),
                (
                    "Simulation Hypothesis",
                    "Philosophy",
                    "Is the simulation hypothesis scientifically testable, or purely philosophical speculation?",
                ),
                (
                    "Entropy & Time",
                    "Physics",
                    "Why does entropy increase over time, and how does this relate to the arrow of time?",
                ),
                (
                    "Limits of Computation",
                    "Mathematics",
                    "What are the theoretical limits of computation according to Turing machines and Godel's incompleteness theorems?",
                ),
            ]
            cursor.executemany(
                "INSERT INTO prompts (title, category, prompt) VALUES (?, ?, ?)",
                seed_data,
            )
            logger.info(f"Seeded {len(seed_data)} prompts into database.")

        conn.commit()
        logger.info(f"Database initialized successfully at {DATABASE_PATH}")


def get_all_prompts():
    """Retrieve all prompts ordered by category and title."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, category, prompt, created_at FROM prompts ORDER BY category, title"
        )
        return [dict(row) for row in cursor.fetchall()]


def get_prompt_by_id(prompt_id):
    """Retrieve a single prompt by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT prompt FROM prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        return dict(row)["prompt"] if row else None


def get_prompts_by_category(category):
    """Retrieve all prompts in a specific category."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, category, prompt FROM prompts WHERE category = ?",
            (category,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_categories():
    """Retrieve all unique categories."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM prompts ORDER BY category")
        return [row["category"] for row in cursor.fetchall()]
