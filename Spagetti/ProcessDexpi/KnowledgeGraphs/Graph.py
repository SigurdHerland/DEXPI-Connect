import networkx as nx
from pyvis.network import Network

class Graph:
    def __init__(self, directed=False):
        """
        Initializes the graph.
        :param directed: Boolean indicating if the graph is directed.
        """
        self.graph = nx.DiGraph() if directed else nx.Graph()
        self.directed = directed

    def add_node(self, node, **attrs):
        """
        Adds a node to the graph.
        :param node: Node identifier.
        :param attrs: Additional node attributes.
        """
        self.graph.add_node(node, **attrs)

    def add_edge(self, source, target, **attrs):
        """
        Adds an edge between two nodes.
        :param source: Source node.
        :param target: Target node.
        :param attrs: Additional edge attributes.
        """
        self.graph.add_edge(source, target, **attrs)

    def visualize(self, output_file):
        """
        Visualizes the graph using pyvis. Ensures root node IDs (starting with 'XMP' or 'XMC') are preserved,
        while all other nodes are converted to string-safe IDs.
        """
        from pyvis.network import Network
        import networkx as nx

        def get_safe_id(node):
            # If it's already a string starting with XMP or XMC, keep as-is (root node)
            if isinstance(node, str) and (node.startswith("XMP") or node.startswith("XMC")):
                return node
            if hasattr(node, 'elemTAG'):
                tag = str(node.elemTAG)
                if tag.startswith("XMP") or tag.startswith("XMC"):
                    return tag
                return tag
            elif hasattr(node, 'name'):
                return str(node.name)
            elif hasattr(node, 'id'):
                return str(node.id)
            return str(node)

        # Build unique ID mapping
        mapping = {}
        seen_ids = set()

        for node in self.graph.nodes:
            clean_id = get_safe_id(node)

            # Ensure uniqueness
            base_id = clean_id
            counter = 1
            while clean_id in seen_ids:
                clean_id = f"{base_id}_{counter}"
                counter += 1

            mapping[node] = clean_id
            seen_ids.add(clean_id)

        # Relabel nodes
        relabeled_graph = nx.relabel_nodes(self.graph, mapping, copy=True)

        # Add labels to nodes
        for node in relabeled_graph.nodes:
            relabeled_graph.nodes[node]['label'] = node
            # Optional: visually highlight root nodes
            if str(node).startswith("XMP") or str(node).startswith("XMC"):
                relabeled_graph.nodes[node]['color'] = "#ff9933"
                relabeled_graph.nodes[node]['size'] = 40

        # Pyvis network
        nt = Network(
            height="1000px", width="100%",
            notebook=False, directed=True,
            cdn_resources='remote', bgcolor="#222222",
            font_color="white", select_menu=True
        )
        
        nt.from_nx(relabeled_graph)
        nt.write_html(output_file, notebook=False)



    
    def combine_graphs(self, other_graph):
        """
        Combines another graph into this graph using a disjoint union.
        
        This ensures that node identifiers from both graphs remain unique,
        even if they have overlapping names. The result is stored in `self.graph`.

        :param other_graph: A NetworkX graph (nx.Graph or nx.DiGraph) to merge into `self.graph`.
        
        Note:
        - Node names may be changed internally to avoid conflicts.
        - Useful when combining multiple hierarchy graphs where node IDs are not globally unique.
        """

        if not isinstance(other_graph, (nx.Graph, nx.DiGraph)):
            raise TypeError("other_graph must be a NetworkX Graph or DiGraph")

        self.graph = nx.compose(self.graph, other_graph)