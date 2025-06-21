# PipingComponent is the main class for physical parts like valves, elbows, reducers.
# It describes both the function and geometry of components in DEXPI.
import networkx as nx
from networkx.algorithms import isomorphism
from pyvis.network import Network
from ProcessDexpi.KnowledgeGraphs.Graph import Graph
from tabulate import tabulate
from collections import Counter
from rdflib import Graph as RDFGRAPH, URIRef, RDFS

class PipingComponent:
    def __init__(self, vertices, PID_document):
        # Store all vertices from DEXPI and the document identifier
        self.vertices = vertices
        self.PID_document = PID_document

        # Data structures to track components and metadata
        self.piping_components = {}         # {componentID: vertex}
        self.Unique_component_classes = set()  # Unique ComponentClass values
        self.component_classes = {}         # {ComponentClass: [componentIDs]}
        self.Unique_RDL = {}                # {ComponentClass: {RDL URIs}}
        self.RDL = {}                       # {componentID: RDL URI}
        self.ConnectionPoints = {}          # {componentID: [[X, Y], ...]}
        self.OrphanComponents = []          # [componentIDs with orphan parent]
        self.HierarchyGraph = {}            # {componentID: Graph object}

        # Build component lists, detect orphans, record connection points
        self.processClasses(vertices)
        self.findOrphanComponents()
        self.Set_connectionPoints()

    def check_component_class_with_RDL(self, RDL, ComponentClass):
        # If no RDL URI provided, nothing to match
        if RDL is None:
            return 0, ComponentClass
        # Only parse if RDL follows the posccaesar.org pattern
        if RDL.startswith("http://data.posccaesar.org/rdl/"):
            g = RDFGRAPH()
            g.parse(RDL)
            pump_uri = URIRef(RDL)
            # Search for rdfs:label triples
            for _, p, o in g.triples((pump_uri, None, None)):
                if p == URIRef(RDFS + "label"):
                    # Compare label to provided ComponentClass
                    if self.is_match(o, ComponentClass):
                        return 0, ComponentClass
                    else:
                        NewComponentClass = self.format_to_component_class(o)
                        print("RDL label =", o,
                              f"ComponentClass = {ComponentClass}",
                              ", New component class ->", NewComponentClass)
                        print("")
                        return 1, NewComponentClass
        # Default: no change
        return 0, ComponentClass

    def is_match(self, rdl_label, component_class):
        # Normalize and compare labels ignoring spaces and case
        return rdl_label.replace(" ", "").lower() == component_class.lower()

    def format_to_component_class(self, rdl_label):
        # Convert spaced label into CamelCase component class
        return ''.join(word.capitalize() for word in rdl_label.lower().split())

    def processClasses(self, vertices):
        # Counters for classes and mismatches
        count = 0
        XMPcount = 0
        XMCcount = 0
        ComponentNotMatchingRDL = 0

        # Iterate through vertices to find PipingComponent elements
        for elem, vertex in vertices.items():
            if vertex.elemTAG == "PipingComponent":
                ID = vertex.attributs.get("ID")
                self.piping_components[ID] = vertex
                ComponentClass = vertex.attributs.get("ComponentClass")
                RDL = vertex.attributs.get("ComponentClassURI")

                # Check RDL label vs. ComponentClass
                mismatch, ComponentClass = self.check_component_class_with_RDL(RDL, ComponentClass)
                ComponentNotMatchingRDL += mismatch

                # Track unique classes and component lists
                self.Unique_component_classes.add(ComponentClass)
                self.component_classes.setdefault(ComponentClass, []).append(ID)
                self.Unique_RDL.setdefault(ComponentClass, set()).add(RDL)
                self.RDL[ID] = RDL

                # Update counts and distinguish XMC/XMP by ID prefix
                count += 1
                if ID.startswith("XMC"):
                    XMCcount += 1
                else:
                    XMPcount += 1

        # Print summary metrics
        print(f"Number of pipingComponent classes = {count} 🔩")
        print(f"Number of RDLs not matching dexpi ComponentClass = {ComponentNotMatchingRDL} ✅")
        print(f"Number of XMC components 🎨: {XMCcount}")
        print(f"Number of XMP components 🧠: {XMPcount}")

    def findOrphanComponents(self):
        # Identify components whose parent is an orphan network segment
        OrphanCount = 0
        for ID, component in self.piping_components.items():
            parent = component.parent
            parentClass = self.vertices[parent].attributs.get("ComponentClass")
            if parentClass == "OrphanPipingNetworkSegment":
                OrphanCount += 1
                self.OrphanComponents.append(ID)
        print(f"Number of OrphanComponents 🧒🪦🕊️: {OrphanCount}")

    def print_table_data(self):
        # Compile table rows comparing isomorphism statistics per class
        ComponentData = []
        for compClass in self.Unique_component_classes:
            # Separate XMP and XMC IDs
            XMP_ids = [ID for ID in self.component_classes[compClass] if ID.startswith("XMP")]
            XMC_ids = [ID for ID in self.component_classes[compClass] if ID.startswith("XMC")]
            XMPiso = self._count_isomorphic(XMP_ids)
            XMCiso = self._count_isomorphic(XMC_ids)

            # Build descriptive strings and collect RDL URIs
            RDLs = {link for link in self.Unique_RDL.get(compClass, set()) if link}
            row = [
                compClass,
                len(self.component_classes[compClass]),
                f"NR of ID = {len(XMC_ids)}, Iso = {XMCiso}",
                f"NR of ID = {len(XMP_ids)}, Iso = {XMPiso}",
                RDLs
            ]
            ComponentData.append(row)

        # Display with tabulate
        headers = ["Component","Quantity","XMC 🎨","XMP 🧠","RDL links 🌐"]
        print(tabulate(ComponentData, headers=headers, tablefmt="grid"))

    def _count_isomorphic(self, id_list):
        # Helper to count any isomorphic pairs among given IDs
        count_iso = 0
        used = set()
        for i, ID1 in enumerate(id_list):
            G1 = self.HierarchyGraph[ID1].graph
            for j in range(i+1, len(id_list)):
                ID2 = id_list[j]
                G2 = self.HierarchyGraph[ID2].graph
                if isomorphism.GraphMatcher(G1, G2).is_isomorphic():
                    count_iso += 1
                    used.update([ID1, ID2])
                    break
        return count_iso

    def create_hierarchy_graph(self):
        # Build a subgraph for each component capturing its XML hierarchy
        for ID, comp in self.piping_components.items():
            G = Graph(directed=True)
            # Add root node for component
            G.add_node(ID,
                       size=len(comp.attributs)*2,
                       label=str(ID),
                       id=str(ID),
                       title=comp.elemTAG)
            self._traverse_hierarchy(G, comp, ID)
            self.HierarchyGraph[ID] = G

    def _traverse_hierarchy(self, G, node, rootID):
        # Recursive pre-order traversal to add XML hierarchy nodes/edges
        for child_id in node.childs:
            child = self.vertices[child_id]
            # Skip generic or simple geometry tags
            if child.elemTAG in ("GenericAttributes","Text","Line","Circle"):
                continue
            # Add child node and edge
            G.add_node(str(child.elemTAG), size=len(child.attributs)*2,
                       label=rootID+child.elemTAG)
            G.add_edge(node, child)
            self._traverse_hierarchy(G, child, rootID)

    def visualize_hierarchy_by_componantClass(self, ProjectPath):
        # Combine and render graphs per ComponentClass into HTML files
        for compClass, IDs in self.component_classes.items():
            combined = Graph(directed=True)
            save_path = f"{ProjectPath}/Graph_Isomorphism/{self.PID_document}_{compClass}.html"
            for ID in IDs:
                if ID in self.HierarchyGraph:
                    combined.combine_graphs(self.HierarchyGraph[ID].graph)
            combined.visualize(save_path)

    def Set_connectionPoints(self):
        # Extract [X,Y] coordinates for each component's ConnectionPoints subtree
        for ID, comp in self.piping_components.items():
            for child_id in comp.childs:
                if self.vertices[child_id].elemTAG == "ConnectionPoints":
                    for node_id in self.vertices[child_id].childs:
                        if self.vertices[node_id].elemTAG == "Node":
                            pos_id = self.vertices[node_id].childs[0]
                            loc_id = self.vertices[pos_id].childs[0]
                            X = float(self.vertices[loc_id].attributs.get("X"))
                            Y = float(self.vertices[loc_id].attributs.get("Y"))
                            self.ConnectionPoints.setdefault(ID, []).append([X, Y])
