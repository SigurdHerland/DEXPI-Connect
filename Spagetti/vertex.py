from rdflib import Graph, URIRef, RDF, RDFS, OWL

# Multi-Way Linked List Node representing a vertex in the P&ID hierarchy
class Vertex:
    def __init__(self, elem, elemTAG):
        self.elem = elem              # Unique identifier (e.g., XML element ID or class name)
        self.elemTAG = elemTAG        # Human-readable tag name (e.g., 'Pump01', 'Valve05')
        
        self.parent = None            # Parent node in the hierarchy (used to trace structure)
        self.childs = []              # List of child nodes (e.g., connected sub-elements)
        self.childName = []           # Corresponding names for each child (same index as self.childs)
        
        self.attributs = {}           # Dictionary of element-specific attributes (e.g., position, type)
        self.RDL = None               # Optional: URI link to the POSC Caesar Reference Data Library
        self.layer = None             # Optional: Layer or level for structural organization

    # --- Optional Methods for Graph Relationships (can be extended further if used) ---
    

    def add_parent(self, parent):
        """Sets the parent node in the XML hierarchy."""
        self.parent = parent

    def add_child(self, child):
        """Appends a child node to the current vertex."""
        self.childs.append(child)

    def add_childName(self, childName):
        """Appends the name of a child (corresponds by index to child list)."""
        self.childName.append(childName)

    def add_attributs(self, attributs):
        """Sets metadata attributes for the element (e.g., TagName, ComponentClass)."""
        self.attributs = attributs

    def add_RDL(self, link):
        """Links the element to a Reference Data Library URI (semantic type)."""
        self.RDL = link

    def add_layer(self, layer):
        """Sets the structural or visual layer (useful in graph visualization)."""
        self.layer = layer
