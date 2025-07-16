import networkx as nx
import pickle
import os
from typing import Optional

# Define the main categories as initial nodes
CATEGORIES = [
    "Knowledge",
    "Feelings",
    "Personalities",
    "ImportanceOfPeople",
    "Preferences",
    "Morals",
    "AutomaticQuestions"
]

# Define the default path for storing the knowledge graph in the analysis folder
DEFAULT_GRAPH_PATH = os.path.join(
    os.path.dirname(__file__), "knowledge_graph.pkl"
)

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        for category in CATEGORIES:
            self.graph.add_node(category, type="category")

    def add_entry(self, category: str, question: str, answer: str, extra: Optional[dict] = None):
        """
        Add a Q&A node under a category. Optionally, add extra attributes.
        """
        if category not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        node_id = f"{category}:{question[:30]}"
        self.graph.add_node(node_id, question=question, answer=answer, **(extra or {}), type="qa")
        self.graph.add_edge(category, node_id)

    def add_relationship(self, from_node: str, to_node: str, relation: str):
        self.graph.add_edge(from_node, to_node, relation=relation)

    def save(self, path: Optional[str] = None):
        if path is None:
            path = DEFAULT_GRAPH_PATH
        with open(path, "wb") as f:
            pickle.dump(self.graph, f)

    def load(self, path: Optional[str] = None):
        if path is None:
            path = DEFAULT_GRAPH_PATH
        with open(path, "rb") as f:
            self.graph = pickle.load(f)

if __name__ == "__main__":
    kg = KnowledgeGraph()
    # Example insertions
    kg.add_entry("Knowledge", "What is your expertise?", "AI, coding, philosophy")
    kg.add_entry("Feelings", "How do you feel today?", "Curious and motivated")
    kg.add_entry("Personalities", "Which of the Big Five fits you best?", "Openness to experience")
    kg.add_entry("ImportanceOfPeople", "Who is most important in your life?", "Family and close friends")
    kg.add_entry("Preferences", "What is your favorite hobby?", "Reading science fiction")
    kg.add_entry("Morals", "Is honesty always the best policy?", "Usually, but context matters")
    kg.add_entry("AutomaticQuestions", "What would you like to learn next?", "Graph databases")
    kg.save()
    print(f"Knowledge graph created and saved at {DEFAULT_GRAPH_PATH}.")
