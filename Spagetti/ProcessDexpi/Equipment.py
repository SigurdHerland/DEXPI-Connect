# PipingComponent is Main class for all physical parts like valves, elbows, reducers. 📌
# Superclass for all individual physical parts used to construct a pipeline.
# In DEXPI, it's a class used to describe both the function and geometry of that component.

class Equipment:

    def __init__(self, vertices):
        # Store all DEXPI vertices for later processing
        self.vertices = vertices

        # Dictionaries to hold equipment data and RDL links
        self.equipment = {}              # {equipmentID: vertex}
        self.RDL = {}                    # {equipmentID: ComponentClassURI}
        self.ConnectionPoints = {}       # {equipmentID: [[nodeID, attrs, nodeElemID], ...]}
        self.EquipmentWithNozzle = {}    # {equipmentID: [nozzleID, ...]}
        self.NozzleLocation = {}         # {nozzleID: [[originX, originY], [ioX, ioY]]}

        # Build equipment lookup and related data
        self.processClasses(vertices)
        # Extract connection point coordinates for each equipment
        self.connection_points()
        # Identify and record nozzle elements per equipment
        self.find_nozzle()

    def processClasses(self, vertices):
        # Counters for equipment and tag types
        count = 0   # total Equipment elements
        XMPcount = 0  # eXtensible Model Properties
        XMCcount = 0  # eXtensible Model Components
        RDLcount = 0  # count of RDL links found

        # Iterate through all vertices to identify Equipment elements
        for elem, vertex in vertices.items():
            if vertex.elemTAG == "Equipment":
                ID = vertex.attributs.get("ID")
                # Store this equipment vertex
                self.equipment[ID] = vertex
                # Record its RDL link (if any)
                self.RDL[ID] = vertex.attributs.get("ComponentClassURI")
                if self.RDL[ID] is not None:
                    RDLcount += 1
                count += 1
                # Classify as XMC or XMP based on ID prefix
                if ID.startswith("XMC"):
                    XMCcount += 1
                else:
                    XMPcount += 1

        # Print summary of discovered equipment
        print(f"Number of Equipment classes = {count} ⚙️")
        print(f"Number of eXtensible Model Component (XMC) 🎨: {XMCcount}")
        print(f"Number of eXtensible Model Properties (XMP) 🧠: {XMPcount}")
        print(f"Number of RDL links to equipment objects 🌐: {RDLcount}")

    def connection_points(self):
        # For each equipment, locate its ConnectionPoints subtree and extract node positions
        for equipment_id, equipment in self.equipment.items():
            # Initialize list for this equipment's connection point data
            self.ConnectionPoints[equipment_id] = []

            # Find the 'ConnectionPoints' child element, if present
            connection_points_id = next(
                (child_id for child_id in equipment.childs
                 if self.vertices[child_id].elemTAG == "ConnectionPoints"),
                None
            )
            if connection_points_id is None:
                # No connection points defined for this equipment
                continue

            # Iterate each child under the ConnectionPoints element
            connection_children = self.vertices[connection_points_id].childs
            for node_id in connection_children:
                node = self.vertices[node_id]
                # Only process Node elements
                if node.elemTAG != "Node":
                    continue
                # Extract Node ID
                node_id_value = node.attributs.get("ID")
                # Assume first child of Node holds position info
                position_id = node.childs[0]
                position = self.vertices[position_id]

                # Look for a Location tag under position to get coordinates
                for pos_child_id in position.childs:
                    pos_child = self.vertices[pos_child_id]
                    if pos_child.elemTAG == "Location":
                        # Store node ID, attributes dict, and element reference
                        location_attribs = pos_child.attributs
                        self.ConnectionPoints[equipment_id].append(
                            [node_id_value, location_attribs, node_id]
                        )

    def find_nozzle(self):
        # Identify nozzle elements attached to each equipment and record their origin/IO positions
        print("Finding nozzzles")
        for ID in self.equipment:
            EquipmentNozzles = []
            equip = self.equipment[ID]
            # Examine each child of the equipment vertex
            for childID in equip.childs:
                child = self.vertices[childID]
                # Only consider Nozzle tags, excluding XMC prefixed IDs
                if child.elemTAG == "Nozzle" and not child.attributs.get("ID").startswith("XMC"):
                    NozzleID = child.attributs.get("ID")
                    EquipmentNozzles.append(NozzleID)

                    # Last child under Nozzle holds its connection points element
                    ConnectionPointsKEY = child.childs[-1]
                    ConnectionPoints = self.vertices[ConnectionPointsKEY]
                    # 2nd and 3rd children are origin and I/O nodes
                    OriginNode = self.vertices[ConnectionPoints.childs[1]]
                    IONode   = self.vertices[ConnectionPoints.childs[2]]

                    # First child under each node holds the Location element reference
                    OriginPosition = self.vertices[OriginNode.childs[0]]
                    IOPosition     = self.vertices[IONode.childs[0]]

                    # Extract origin coordinates
                    OriginX = float(self.vertices[OriginPosition.childs[0]].attributs.get("X"))
                    OriginY = float(self.vertices[OriginPosition.childs[0]].attributs.get("Y"))
                    # Extract I/O coordinates if present, else default to origin
                    if IOPosition.childs:
                        IOX = float(self.vertices[IOPosition.childs[0]].attributs.get("X"))
                        IOY = float(self.vertices[IOPosition.childs[0]].attributs.get("Y"))
                    else:
                        IOX, IOY = OriginX, OriginY

                    # Store both origin and I/O locations for the nozzle
                    self.NozzleLocation[NozzleID] = [[OriginX, OriginY], [IOX, IOY]]

            # Map equipment ID to its nozzle list
            if EquipmentNozzles:
                self.EquipmentWithNozzle[ID] = EquipmentNozzles
