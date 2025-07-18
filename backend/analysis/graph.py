import networkx as nx
import pickle
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

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

# Map training categories to knowledge graph categories
TRAINING_CATEGORY_MAP = {
    "Questions about my knowledge": "Knowledge",
    "Questions about my feelings and 5 personalities": "Personalities",
    "Question about the importance of people in my life": "ImportanceOfPeople",
    "Iteratively add to a knowledge graph": "Knowledge",
    "Preferences": "Preferences",
    "Moral questions": "Morals",
    "Automatic questions to extend known knowledge": "AutomaticQuestions"
}

# Define the default path for storing the knowledge graph in the analysis folder
DEFAULT_GRAPH_PATH = os.path.join(
    os.path.dirname(__file__), "knowledge_graph.pkl"
)

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        for category in CATEGORIES:
            self.graph.add_node(category, type="category")
        
        # Add main Training node
        self.graph.add_node("Training", type="training_main")

        # Main Documents node (for extracted knowledge) - keep same blue color in frontend
        self.graph.add_node("Documents", type="document_main")
        
        # Add training category subnodes
        for training_category, kg_category in TRAINING_CATEGORY_MAP.items():
            training_subnode = f"Training_{kg_category}"
            self.graph.add_node(training_subnode, type="training_category", training_category=training_category)
            self.graph.add_edge("Training", training_subnode)

    def add_entry(self, category: str, question: str, answer: str, extra: Optional[dict] = None):
        """
        Add a Q&A node under a category. Optionally, add extra attributes.
        """
        if category not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        node_id = f"{category}:{question[:30]}"
        self.graph.add_node(node_id, question=question, answer=answer, **(extra or {}), type="qa")
        self.graph.add_edge(category, node_id)
        return node_id  # Return the node identifier so callers can link elsewhere
    
    def add_training_entry(self, training_category: str, question_id: str, question: str, answer: Any, answer_type: str, timestamp: str):
        """
        Add a training Q&A entry to the knowledge graph.
        Maps training categories to knowledge graph categories and connects to training subnodes.
        """
        # Map training category to knowledge graph category
        kg_category = TRAINING_CATEGORY_MAP.get(training_category)
        if not kg_category:
            print(f"Warning: Unknown training category: {training_category}")
            return
        
        # Create a unique node ID based on question ID and timestamp
        node_id = f"training_{question_id}_{timestamp.replace(':', '_').replace('.', '_')}"
        
        # Format answer based on type
        if answer_type == "multiple_choice" and isinstance(answer, list):
            formatted_answer = ", ".join(answer)
        else:
            formatted_answer = str(answer)
        
        # Add the training node
        self.graph.add_node(
            node_id,
            question=question,
            answer=formatted_answer,
            question_id=question_id,
            training_category=training_category,
            answer_type=answer_type,
            timestamp=timestamp,
            type="training_qa"
        )
        
        # Connect to the appropriate training category subnode
        training_subnode = f"Training_{kg_category}"
        self.graph.add_edge(training_subnode, node_id)
    
    def sync_with_training_data(self, training_data_path: str = "training_data.json"):
        """
        Synchronize the knowledge graph with training data from JSON file.
        """
        if not os.path.exists(training_data_path):
            print(f"Training data file not found: {training_data_path}")
            return
        
        try:
            with open(training_data_path, 'r') as f:
                training_data = json.load(f)
            
            # Remove existing training nodes to avoid duplicates
            nodes_to_remove = [node for node, data in self.graph.nodes(data=True) 
                             if data.get('type') == 'training_qa']
            self.graph.remove_nodes_from(nodes_to_remove)
            
            # Add training entries
            for entry in training_data:
                self.add_training_entry(
                    training_category=entry.get('category', ''),
                    question_id=entry.get('question_id', ''),
                    question=entry.get('question', ''),
                    answer=entry.get('answer', ''),
                    answer_type=entry.get('answer_type', ''),
                    timestamp=entry.get('timestamp', '')
                )
            
            print(f"Successfully synchronized {len(training_data)} training entries")
            
        except Exception as e:
            print(f"Error syncing training data: {e}")
    
    def get_training_summary(self) -> Dict[str, Any]:
        """
        Get a summary of training data in the knowledge graph.
        """
        training_nodes = [node for node, data in self.graph.nodes(data=True) 
                         if data.get('type') == 'training_qa']
        
        # Group by category
        category_summary = {}
        for node in training_nodes:
            node_data = self.graph.nodes[node]
            category = node_data.get('training_category', 'Unknown')
            
            if category not in category_summary:
                category_summary[category] = {
                    'count': 0,
                    'questions': []
                }
            
            category_summary[category]['count'] += 1
            category_summary[category]['questions'].append({
                'question_id': node_data.get('question_id', ''),
                'question': node_data.get('question', ''),
                'answer': node_data.get('answer', ''),
                'timestamp': node_data.get('timestamp', '')
            })
        
        return {
            'total_training_entries': len(training_nodes),
            'categories': category_summary
        }

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
