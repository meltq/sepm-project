import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
import os


DEP_DIR = "jsons\\cleaned\\"
SCORES_FILE = "vulnerability_scores.csv"


@st.cache_resource
def load_graph():
    G = nx.DiGraph()
    file_list = os.listdir(DEP_DIR)
    visited = set()

    def load_package_data(package_name):
        path = os.path.join(DEP_DIR, package_name)
        if os.path.exists(path):
            try:
                with open(path, "r") as file:
                    return json.load(file)
            except:
                return None
        return None

    def build_2_level_graph(package_name):
        from collections import deque
        queue = deque([(package_name, 0)])
        while queue:
            current, level = queue.popleft()
            if current in visited or level > 2:
                continue

            visited.add(current)
            data = load_package_data(current)
            if not data:
                continue

            G.add_node(current)
            for dep in data.get("deps", []):
                G.add_node(dep)
                G.add_edge(current, dep)
                if dep not in visited and level < 2:
                    queue.append((dep, level + 1))

    for filename in file_list[:1000]:
        try:
            with open(os.path.join(DEP_DIR, filename), "r") as f:
                data = json.load(f)
            package_name = data.get("name")
            if package_name:
                build_2_level_graph(package_name)
        except:
            continue

    return G

@st.cache_data
def load_scores():
    df = pd.read_csv(SCORES_FILE)
    return df.set_index("Package")["VulnerabilityScore"].to_dict()


def main():
    st.set_page_config(page_title="Rust Vulnerability Dashboard", layout="wide")
    st.title("🔍 Rust Package Vulnerability Dashboard")

    G = load_graph()
    scores = load_scores()

    st.subheader("Search for a Package")
    typed_input = st.text_input("Start typing a package name...")

    matching_packages = sorted([pkg for pkg in G.nodes if typed_input.lower() in pkg.lower()]) if typed_input else []

    selected_pkg = st.selectbox("Matching Packages", matching_packages) if matching_packages else None

    if selected_pkg:
        st.subheader(f"Vulnerability Score for `{selected_pkg}`")
        main_score = scores.get(selected_pkg, "N/A")
        st.metric("Main Package Score", main_score)

        connected_nodes = set(G.successors(selected_pkg)) | set(G.predecessors(selected_pkg))
        connected_scores = {pkg: scores.get(pkg, "N/A") for pkg in connected_nodes}

        if connected_scores:
            st.subheader("Connected Packages and Their Scores")
            st.dataframe(pd.DataFrame({
                "Package": list(connected_scores.keys()),
                "Score": list(connected_scores.values())
            }).sort_values("Score", ascending=False).reset_index(drop=True))

    
        st.subheader("Dependency Network")
        subG = G.subgraph([selected_pkg] + list(connected_nodes))

        fig, ax = plt.subplots(figsize=(12, 8))  # Bigger size for clarity
        pos = nx.spring_layout(subG, k=0.5, seed=42)  # Adjust k for spacing

        # Node coloring based on reversed colormap
        node_colors = [scores.get(n, 0) for n in subG.nodes]

        nx.draw_networkx_nodes(subG, pos, node_color=node_colors, cmap=plt.cm.viridis_r,
                       node_size=300, ax=ax)  # <--- Reversed colormap

        nx.draw_networkx_edges(subG, pos, alpha=0.3, edge_color="gray", ax=ax)
        nx.draw_networkx_labels(subG, pos, font_size=7, font_color="black", ax=ax)

        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis_r,  # <--- Reversed colorbar
                           norm=plt.Normalize(vmin=0, vmax=100))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Vulnerability Score')

        ax.set_title(f"Dependency Graph for `{selected_pkg}`", fontsize=12)
        ax.axis("off")
        st.pyplot(fig)


if __name__ == "__main__":
    main()
