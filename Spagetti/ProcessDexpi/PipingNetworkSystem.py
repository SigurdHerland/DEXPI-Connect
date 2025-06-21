import itertools
from ProcessDexpi.elementSearch import elementSearch
import time


class PipingNetworkSystem:
    def __init__(self, vertices):
        # Store all DEXPI vertices and initialize search helper
        self.vertices = vertices
        self.elementSearch = elementSearch(vertices)

        # Dictionaries to hold system definitions and their segments
        self.systems = {}           # {systemID: vertex}
        self.segments = {}          # {systemID: [segmentIDs]}
        self.segmetnsElem = {}      # {systemID: [segment element references]}

        # Build system and segment maps from the input data
        self.processClasses()
        # Optional: display system-segment hierarchy
        # self.showSystemSegmets()

    def processClasses(self):
        # Counters and collectors for attribute analysis
        count = 0
        common_attributes = []  # Collect attribute sets for each system
        common_childs = []      # Collect child-name lists for intersection

        # Iterate through all vertices to find valid PipingNetworkSystem elements
        for elem, vertex in self.vertices.items():
            # Identify system classes excluding 'OrphanPipingNetworkSystem'
            if (vertex.elemTAG == "PipingNetworkSystem") and \
               (vertex.attributs.get("ComponentClass") != "OrphanPipingNetworkSystem"):
                ID = vertex.attributs.get("ID")
                self.systems[ID] = vertex

                # Track this system’s attribute keys and child names
                common_attribute = []
                common_child = []
                for key in vertex.attributs:
                    common_attribute.append(key)
                # Initialize a placeholder for later property breakdowns

                # Iterate child elements of this system vertex
                for i, childName in enumerate(vertex.childName):
                    common_child.append(childName)
                    # If child is a network segment, record its ID and element ref
                    if childName == "PipingNetworkSegment":
                        childElem = vertex.childs[i]
                        childID = self.vertices[childElem].attributs.get("ID")
                        self.segments.setdefault(ID, []).append(childID)
                        self.segmetnsElem.setdefault(ID, []).append(childElem)

                # Accumulate for intersection/union analysis
                common_childs.append(common_child)
                common_attributes.append(common_attribute)

                count += 1

        # Compute common vs. unique attributes and child names across systems
        common_values = set.intersection(*map(set, common_attributes))
        unique_values = set(itertools.chain(*common_attributes))

        # Print summary statistics to console
        print(f"Number of Piping Network Systems classes = {count} 🕸️")
        print("Common attributes for each Piping Network System: 🤝 ", common_values)
        print("Unique attributes for each Piping Network System: 🦄 ", unique_values)
        print("Common childs for each Piping Network System: 🤝👶 ",
              set.intersection(*map(set, common_childs)))
        print("Unique childs for each Piping Network System: 👶🦄 ",
              set(itertools.chain(*common_childs)))

    def showSystemSegmets(self):
        # Display ancestry and children for each system and its segments
        for systemID, system in self.systems.items():
            # Find and print ancestors for the system element
            systemAncestor = self.elementSearch.ancestors(system, [system.elem])
            systemchildren = system.childs
            print(systemID)
            self.elementSearch.showAncestors(systemAncestor, systemchildren)

            # Repeat for each segment element within this system
            for segmentelem in self.segmetnsElem[systemID]:
                segmentAncestor = self.elementSearch.ancestors(
                    self.vertices[segmentelem], [segmentelem]
                )
                segmentChildren = self.vertices[segmentelem].childs
                self.elementSearch.showAncestors(segmentAncestor, segmentChildren)
     