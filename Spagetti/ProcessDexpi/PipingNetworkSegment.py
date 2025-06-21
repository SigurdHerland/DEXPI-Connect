import itertools

class PipingNetworkSegment:
    def __init__(self, vertices):
        # Store all DEXPI vertices for lookup
        self.vertices = vertices

        # Dictionaries to hold segment elements, centerline coordinates, and attached components
        self.segments = {}           # {segmentID: vertex}
        self.CenterLinePoints = {}   # {segmentID: [[x1,y1],[x2,y2],... ]}
        self.pipingComponats = {}    # {segmentID: [componentID, ...]}

        # Placeholder for <Connection> elements (if used)
        self.Connection = None
        # Placeholder for future property breakouts per segment
        self.PropertyBreak = {}

        # Build segment lookup and child linkage
        self.processClasses()
        self.set_linkChildrens()
    
    def processClasses(self):
        # Counters and collectors for attribute/child analysis
        count = 0
        common_attributes = []  # attribute keys across all non-orphan segments
        common_childs = []      # child tag names across segments
        unique_URL = []         # collect all ComponentClassURI values

        # Iterate through all vertices to find PipingNetworkSegment elements
        for elem, vertex in self.vertices.items():
            # Exclude orphan segments by ComponentClass attribute
            if (vertex.elemTAG == "PipingNetworkSegment" and \
                vertex.attributs.get("ComponentClass") != "OrphanPipingNetworkSegment"):
                ID = vertex.attributs.get("ID")
                URL = vertex.attributs.get("ComponentClassURI")
                unique_URL.append(URL)
                # Store segment vertex for later
                self.segments[ID] = vertex

                # Collect attribute keys and child tag names for analysis
                common_attribute = list(vertex.attributs.keys())
                common_child = list(vertex.childName)

                common_childs.append(common_child)
                common_attributes.append(common_attribute)
                count += 1

        # Determine common vs unique attributes and child tags
        common_values  = set.intersection(*map(set, common_attributes))
        unique_values = set(itertools.chain(*common_attributes))

        # Print summary information about segments
        print("Unique RDLS =", set(unique_URL))
        print(f"Number of Piping Network Segment classes = {count} 🕸️")
        print("Common attributes for each Piping Network Segment: 🤝", common_values)
        print("Unique attributes for each Piping Network Segment: 🦄", unique_values)
        print("Common childs for each Piping Network Segment: 🤝👶", set.intersection(*map(set, common_childs)))
        print("Unique childs for each Piping Network Segment: 👶🦄", set(itertools.chain(*common_childs)))

    def set_linkChildrens(self):
        # For each stored segment, extract centerline coordinates and attached component IDs
        for ID, segment in self.segments.items():
            # Track attached component classes (for potential diagnostics)
            componatclassespiping = []

            # Prepare lists of child element IDs and their tag names
            segmentChilds = segment.childs
            segmentChildNames = segment.childName

            NRofCenterlines = 0
            # Iterate through each child under the segment
            for i, childName in enumerate(segmentChildNames):
                childElemID = segmentChilds[i]
                # Process all <CenterLine> children
                if childName == "CenterLine":
                    NRofCenterlines += 1
                    cl_childs = self.vertices[childElemID].childs
                    cl_childNames = self.vertices[childElemID].childName
                    # Find each <Coordinate> index and extract points
                    indices = [idx for idx, tag in enumerate(cl_childNames) if tag == "Coordinate"]
                    for idx in indices:
                        coordElem = cl_childs[idx]
                        X = float(self.vertices[coordElem].attributs.get("X"))
                        Y = float(self.vertices[coordElem].attributs.get("Y"))
                        self.CenterLinePoints.setdefault(ID, []).append([X, Y])
                # Process attached piping components
                if childName == "PipingComponent":
                    comp = self.vertices[childElemID]
                    compID = comp.attributs.get("ID")
                    componatclassespiping.append(comp.attributs.get("ComponentClass"))
                    self.pipingComponats.setdefault(ID, []).append(compID)

            # If multiple centerlines found, warn the user
            if NRofCenterlines > 1:
                print(f"Pipingnetwork segment {ID} has {NRofCenterlines} centerlines")
          

            
                

                    

