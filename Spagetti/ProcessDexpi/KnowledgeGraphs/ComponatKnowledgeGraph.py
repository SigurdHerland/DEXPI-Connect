import networkx as nx
from pyvis.network import Network

class ComponatKnowledgeGraphs:
    def __init__(self, vertices, piping_components, classChoice, classID):
        #initialize
        self.nx_graph = nx.DiGraph()
        self.add_root_nodes(classID,piping_components,classChoice)
        self.add_child_nodes(vertices,piping_components,classID)
    
    def add_root_nodes(self,classID,piping_components,classChoice):
        for ID in classID:
            self.nx_graph.add_node(ID,
                                   size = len(piping_components[ID].attributs)*2,
                                   label = ID,
                                   group = ID,
                                   title = f"Attributs = {len(piping_components[ID].attributs)}"
                                   )
    def add_child_nodes(self,vertices,piping_components,classID):
        for ID in classID:
            children = piping_components[ID].childs
            for child in children:
                node = vertices[child]
                nodeName = ID + node.elemTAG
                size = len(node.attributs) + 1
                label = node.elemTAG
                group = ID
                title = f"Attributs = {len(node.attributs)}"
                self.nx_graph.add_node(nodeName,
                                       size = size,
                                       label = label,
                                       group = group,
                                       title = title)
                self.nx_graph.add_edge(ID,nodeName)
            group_nodes = [n for n, attr in self.nx_graph.nodes(data=True) if attr.get('group') == ID]
            #print(group_nodes)
    
    # Function to print nodes in a specific group
    def print_group(self, graph, group_name):
        group_nodes = [n for n, attr in graph.nodes(data=True) if attr.get('group') == group_name]
        print(f"Nodes in group '{group_name}': {group_nodes}")
    
    def saveGraph(self,classChoice):
        filepath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/Spagetti/KnowledgeGraphs/ComponatKnowledgeGraph"
        nt = Network(
        height="1000px", width="100%", 
        notebook=False, directed=True, 
        cdn_resources='remote', bgcolor="#222222", 
        font_color="white", select_menu=True)
        
        nt.from_nx(self.nx_graph)
        print(f"Filed saved 😊")
        nt.show(filepath+"/"+classChoice+".html", notebook=False)
    
    
    