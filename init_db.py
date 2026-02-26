import sqlite3

conn = sqlite3.connect("prompts.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    prompt TEXT NOT NULL
)
""")

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)", 
               ("Information", "Can artificial intelligence be truly creative?"))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Consciousness", "Is consciousness an emergent property of complex computation, or does it require a fundamentally different physical process? Analyze neuroscientific and computational perspectives."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Quantum Reality", "Does quantum mechanics imply that reality is probabilistic at a fundamental level, or is probability merely a limitation of human knowledge? Compare Copenhagen and Many Worlds interpretations."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("AI Alignment", "What are the core technical challenges in aligning advanced artificial intelligence systems with human values? Evaluate reward modeling, inverse reinforcement learning, and constitutional AI."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Free Will", "Is free will compatible with determinism? Examine compatibilism, libertarianism, and neuroscientific evidence on decision making."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Information Theory", "How does Shannon information theory define information, and how does it differ from semantic meaning? Provide mathematical intuition and practical examples."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Black Holes", "What happens to information that falls into a black hole? Discuss Hawking radiation and the black hole information paradox."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Evolution and Intelligence", "Is human intelligence an inevitable outcome of evolution, or a rare accident? Evaluate evolutionary pressures and comparative cognition across species."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Simulation Hypothesis", "Is the simulation hypothesis scientifically testable, or is it a philosophical speculation? Analyze falsifiability and epistemology."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Entropy and Time", "Why does entropy increase over time, and how does this relate to the arrow of time? Connect thermodynamics and cosmology."))

cursor.execute("INSERT INTO prompts (title, prompt) VALUES (?, ?)",
               ("Limits of Computation", "What are the theoretical limits of computation according to Turing machines and Gödel incompleteness? Can quantum computing overcome these limits?"))

conn.commit()
conn.close()

print("Database initialized successfully.")