import networkx as nx
import matplotlib.pyplot as plt
import pickle
import os

CATEGORY_COLORS = {
    "Knowledge": "skyblue",
    "Feelings": "lightgreen",
    "Personalities": "orange",
    "ImportanceOfPeople": "violet",
    "Preferences": "gold",
    "Morals": "salmon",
    "AutomaticQuestions": "lightgrey"
}

# Always use the knowledge graph at Model_Myself/backend/analysis/knowledge_graph.pkl
GRAPH_PATH = os.path.join(os.path.dirname(__file__), "knowledge_graph.pkl")

def load_graph(path=GRAPH_PATH):
    with open(path, "rb") as f:
        return pickle.load(f)

def visualize_graph(G):
    pos = nx.spring_layout(G, seed=42)
    node_colors = []
    labels = {}
    for node, data in G.nodes(data=True):
        if data.get("type") == "category":
            node_colors.append(CATEGORY_COLORS.get(node, "grey"))
            labels[node] = node
        else:
            # Q&A node: color by parent category
            parents = list(G.predecessors(node))
            parent = parents[0] if parents else None
            node_colors.append(CATEGORY_COLORS.get(parent, "grey"))
            labels[node] = data.get("question", node)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=1200, edge_color="#888", font_size=10)
    nx.draw_networkx_labels(G, pos, labels, font_size=9)
    plt.title("Knowledge Graph Visualization")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    G = load_graph()
    visualize_graph(G)