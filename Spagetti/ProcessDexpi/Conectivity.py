import networkx as nx
from networkx.algorithms import isomorphism
from pyvis.network import Network
from ProcessDexpi.KnowledgeGraphs.Graph import Graph
from tabulate import tabulate
from collections import Counter
import numpy as np

class BuildConectivityGraph:
    def __init__(self,pipingnetworksystem,pipingnetworksegment,pipingcomponent,OffPageReference, equipment,path):
        self.Conectivitygraph = Graph(directed=False) #Creating a none direct graph
        self.PipingNetworkSystem = pipingnetworksystem
        self.PipingNetworkSegment = pipingnetworksegment
        self.PipingComponent = pipingcomponent
        self.OffPageReference = OffPageReference
        self.Equipment = equipment
        self.vertex_in_network = {} #Key=netowrkID ---> Value = [segmentID]
        self.TotalOrphanComponants = 0
        self.OrphanFoundSegment = 0
        
        EdgesEvolving = []
        DisconectionEvolving = []
        self.totalSegmentConectionpoints = 0
        self.totalSegmentedgesinGraph = 0
        
        
        graphindex = 1
        self.add_offPageReference_to_graph()
        self.add_pipingNetwork_to_Graph()
        self.add_Orphaned_Component_to_graph()
        self.add_equipment_to_graph()
        NumberOfNodes = len(self.Conectivitygraph.graph.nodes)
        print("")
        print("Number of nodes: ", NumberOfNodes)
        new_edges_after_first = len(list(self.Conectivitygraph.graph.edges()))
        print("Number of egdes after first function:", len(list(self.Conectivitygraph.graph.edges())))
        print("Number of disconected nodes:", len(self.Disconected_Nodes()))
        self.saveGraph(f"{path}Conectivity_ITTERATION{graphindex}.html")
        print("")
        graphindex += 1
        EdgesEvolving.append(len(list(self.Conectivitygraph.graph.edges())))
        DisconectionEvolving.append(len(self.Disconected_Nodes()))

        new_edges_after_second = len(list(self.Conectivitygraph.graph.edges())) - new_edges_after_first
        self.edge_for_orphan_components()
        self.saveGraph(f"{path}Conectivity_ITTERATION{graphindex}.html")
        print("Number of edges after fourth function",len(list(self.Conectivitygraph.graph.edges())))
        print("Number of disconected nodes:", len(self.Disconected_Nodes()))
        print("")
        graphindex += 1
        EdgesEvolving.append(len(list(self.Conectivitygraph.graph.edges())))
        DisconectionEvolving.append(len(self.Disconected_Nodes()))

        
        self.edge_for_segments()
        self.saveGraph(f"{path}Conectivity_ITTERATION{graphindex}.html")
        print("Number of edges after second function",len(list(self.Conectivitygraph.graph.edges())))
        print("Number of disconected nodes:", len(self.Disconected_Nodes()))
        print("")
        graphindex += 1
        EdgesEvolving.append(len(list(self.Conectivitygraph.graph.edges())))
        DisconectionEvolving.append(len(self.Disconected_Nodes()))


        self.edge_for_pipingNetwork()
        self.saveGraph(f"{path}Conectivity_ITTERATION{graphindex}.html")
        print("Number of edges after third function",len(list(self.Conectivitygraph.graph.edges())))
        print("Number of disconected nodes:", len(self.Disconected_Nodes()))
        print("")
        graphindex += 1
        EdgesEvolving.append(len(list(self.Conectivitygraph.graph.edges())))
        DisconectionEvolving.append(len(self.Disconected_Nodes()))

        self.edge_for_equipments()
        self.saveGraph(f"{path}Conectivity_ITTERATION{graphindex}.html")
        print("Number of edges after fifth function",len(list(self.Conectivitygraph.graph.edges())))
        print("Number of disconected nodes:", len(self.Disconected_Nodes()))
        print("")
        graphindex += 1
        EdgesEvolving.append(len(list(self.Conectivitygraph.graph.edges())))
        DisconectionEvolving.append(len(self.Disconected_Nodes()))


        self.edge_for_missing_offPageReference(1) #Intitilize start with 1 in sensitivity
        self.saveGraph(f"{path}_ConectivityFinalGraph.html")
        print("Number of edges after fifth function",len(list(self.Conectivitygraph.graph.edges())))
        print("Number of disconected nodes:", len(self.Disconected_Nodes()))
        EdgesEvolving.append(len(list(self.Conectivitygraph.graph.edges())))
        DisconectionEvolving.append(len(self.Disconected_Nodes()))
        print("")

        last_piece = path.split('/')[-1]
        DisconectionEvolving = np.array(DisconectionEvolving)
        EdgesEvolving = np.array(EdgesEvolving)
        print(f"label = " , str(last_piece))
        print("Total_of_Nodes = ", NumberOfNodes)
        print("EdgesEvolving = ",list(EdgesEvolving))
        print("DisconectionEvolving = ",list(1-DisconectionEvolving/NumberOfNodes))
        print("")
        print("totalSegmentedgesinGraph = ",self.totalSegmentedgesinGraph)
        print("totalSegmentConectionpoints = ", self.totalSegmentConectionpoints)
        print("Connections_found = ", self.totalSegmentedgesinGraph/self.totalSegmentConectionpoints)
        print("")
        total_continuous, total_systems = self.notFullConnectedNetwork()
        print("Total_pipingNeworkSystems = ", total_systems)
        print("total_continuous_Systems = ", total_continuous)
        print("Percent_of_full_connected_systems = ", total_continuous/total_systems)
        
        print("")
        print("OrphanComponentsMatchSegment_percent = ", self.OrphanFoundSegment/self.TotalOrphanComponants )






    def Disconected_Nodes(self):
        # Access the graph from the connectivity graph wrapper
        graph = self.Conectivitygraph.graph
        
        # Identify all nodes that have no connections (degree 0)
        disconected_nodes = [n for n in graph.nodes if graph.degree(n) == 0]
        
        # Return the list of disconnected nodes
        return disconected_nodes
    
    def add_equipment_to_graph(self):
        # Initialize counters for nozzle numbering and color selection
        NozzleIndex = 1
        ColorIndex = 0

        # Iterate over each equipment that has associated nozzles
        for equipmentID in self.Equipment.EquipmentWithNozzle:
            # Assign a distinct color for this equipment node
            EquipmentColor = self.givegraphColor(ColorIndex)
            # Retrieve the list of nozzle IDs for this equipment
            nozzels = self.Equipment.EquipmentWithNozzle[equipmentID]
            # Prepare descriptive labels for the equipment node
            title = f"Equipment with ID {equipmentID}"
            label = self.Equipment.equipment[equipmentID].attributs.get("ComponentClass")

            # Add the equipment node to the connectivity graph
            self.Conectivitygraph.add_node(
                equipmentID,
                label=label,
                title=title,
                size=50,
                color=EquipmentColor
            )

            # For each nozzle belonging to this equipment
            for nozzle in nozzels:
                # Determine its position from stored coordinates
                Position = self.Equipment.NozzleLocation[nozzle]
                # Generate a label and title for the nozzle node
                label = f"Nozzle{NozzleIndex}"
                title = f"Nozzle with ID={nozzle}"

                # Add the nozzle node to the graph with same color as its equipment
                self.Conectivitygraph.add_node(
                    nozzle,
                    label=label,
                    title=title,
                    size=30,
                    color=EquipmentColor,
                    Position=Position
                )
                # Connect nozzle node to its parent equipment node
                self.Conectivitygraph.add_edge(nozzle, equipmentID)

                # Increment nozzle counter for labeling
                NozzleIndex += 1

            # Move to next color for the next equipment
            ColorIndex += 1




    def edge_for_equipments(self):
        # Iterate through each equipment that has associated nozzles
        for EquipmentID in self.Equipment.EquipmentWithNozzle:
            # Retrieve list of nozzle IDs for this equipment
            nozzels = self.Equipment.EquipmentWithNozzle[EquipmentID]

            # For each nozzle under the current equipment
            for nozzelID in nozzels:
                # Get the spatial coordinates of the nozzle
                nozzelCordinates = self.Equipment.NozzleLocation[nozzelID]

                # Find the nearest segment in the network to this nozzle (within tolerance level 1)
                foundSegment = self.nearest_segment_neighbour(1, nozzelCordinates)

                # If a segment was found, create an edge from the nozzle to that segment
                if foundSegment is not False:
                    self.Conectivitygraph.add_edge(nozzelID, foundSegment)
                    # Track the count of segment edges added to the graph
                    self.totalSegmentedgesinGraph += 1
                else:
                    # No valid segment found; skip to next nozzle
                    continue




    
    def add_offPageReference_to_graph(self):
        # Iterate through each off-page reference label in the graph data
        for offpageLabelID in self.OffPageReference.Offpage_to_graph:
            # Retrieve the descriptive title for this off-page connector
            title = self.OffPageReference.ConnectorRefrenceTargetlabel[offpageLabelID]
            # Use a generic label for all off-page reference nodes
            label = "OffPageReference"
            # Get the spatial position for the label node
            position = self.OffPageReference.label[offpageLabelID]

            # Add the off-page reference node with custom styling to the connectivity graph
            self.Conectivitygraph.add_node(
                offpageLabelID,
                label=label,
                shape="^",  # Use a triangle shape for off-page references
                font={
                    "color": "black",
                    "strokeWidth": 0
                },  # Configure font styling explicitly
                size=20,
                title=title,
                color="#aa6e28",  # Brown color for off-page references
                position=position
        )




    def add_pipingNetwork_to_Graph(self):
        # Initialize counters for segment numbering and color selection
        pipeindex = 1
        colorindex = 0

        # Loop through each piping network system by its ID
        for systemID in self.PipingNetworkSystem.segments:
            # Prepare title and color for this piping system
            title = f"Part of Piping Network System {systemID}"
            systemColor = self.givegraphColor(colorindex)
            colorindex += 1

            # Get all segment IDs belonging to the current system
            systemsegments = self.PipingNetworkSystem.segments[systemID]

            # Iterate over each segment in the system
            for segmentID in systemsegments:
                # Label this segment uniquely within the graph
                pipeLabel = f"NetworkSegment_{pipeindex}"

                # Retrieve segment geometry and initial connection count
                CurrentSegment = self.PipingNetworkSegment.segments[segmentID]
                segmentCordinates = self.PipingNetworkSegment.CenterLinePoints[segmentID]
                NrofConnections = 2  # Base connection points for each segment

                # If this segment has piping components attached
                if segmentID in self.PipingNetworkSegment.pipingComponats:
                    # Iterate through each component attached to the segment
                    for idx in range(len(self.PipingNetworkSegment.pipingComponats[segmentID])):
                        ComponentID = self.PipingNetworkSegment.pipingComponats[segmentID][idx]
                        currentComponent = self.PipingComponent.piping_components[ComponentID]
                        # Create a descriptive label for the component node
                        label = currentComponent.attributs.get("ComponentClass") + "_" + ComponentID

                        # Get the component's connection point coordinates
                        ComponentPosition = self.PipingComponent.ConnectionPoints[ComponentID]
                        # Include component positions in the segment coordinate list for layout
                        segmentCordinates = segmentCordinates + ComponentPosition
                        # Adjust total expected connections based on actual points
                        NrofConnections += len(ComponentPosition) - 3

                        # Add the component node to the connectivity graph
                        self.Conectivitygraph.add_node(
                            ComponentID,
                            label=label,
                            color=systemColor,
                            size=20,
                            shape="diamond",
                            title=title,
                            type="component",
                            segmentCordinates=segmentCordinates,
                            isPartofSegment=segmentID,
                            position=ComponentPosition
                        )

                    # After adding components, add the segment node itself
                    self.Conectivitygraph.add_node(
                        segmentID,
                        label=pipeLabel,
                        color=systemColor,
                        size=10,
                        title=title,
                        type="segment",
                        segmentCordinates=segmentCordinates,
                        NrofConnections=NrofConnections
                    )
                    # Update network-wide counts and vertex tracking
                    self.totalSegmentConectionpoints += NrofConnections
                    pipeindex += 1
                    self.vertex_in_network.setdefault(systemID, []).append(segmentID)

                    # Connect each component node to the segment node in the graph
                    for ComponentID in self.PipingNetworkSegment.pipingComponats[segmentID]:
                        self.Conectivitygraph.add_edge(ComponentID, segmentID)

                else:
                    # No components: simply add the segment node
                    self.Conectivitygraph.add_node(
                        segmentID,
                        label=pipeLabel,
                        color=systemColor,
                        size=10,
                        title=title,
                        type="segment",
                        segmentCordinates=segmentCordinates,
                        NrofConnections=NrofConnections
                    )
                    # Track this segment in the system vertex list
                    self.vertex_in_network.setdefault(systemID, []).append(segmentID)
                    self.totalSegmentConectionpoints += NrofConnections
                    pipeindex += 1

                # If this segment links to an off-page reference, add that edge
                if segmentID in self.OffPageReference.Comfirmed_connections:
                    OffpageID = self.OffPageReference.Comfirmed_connections[segmentID]
                    self.Conectivitygraph.add_edge(segmentID, OffpageID)
                    self.totalSegmentedgesinGraph += 1


    
    def add_Orphaned_Component_to_graph(self):
        # Title for all orphaned component nodes
        title = "Orphan PipingComponent"

        # Iterate through each component that has no segment associations
        for OrhanComponentID in self.PipingComponent.OrphanComponents:
            # Retrieve the component object and build a descriptive label
            OrpanComponent = self.PipingComponent.piping_components[OrhanComponentID]
            label = OrpanComponent.attributs.get("ComponentClass") + "_" + OrhanComponentID

            # Get the spatial coordinates of the orphan component
            segmentsCordinates = self.PipingComponent.ConnectionPoints[OrhanComponentID]

            # Add the orphan component node to the connectivity graph
            self.Conectivitygraph.add_node(
                OrhanComponentID,
                label=label,
                color="white",        # Use white color to distinguish orphans
                size=20,
                shape="diamond",      # Diamond shape for components
                title=title,            # Title describing the node type
                component=True,         # Flag indicating node is a piping component
                segmentCordinates=segmentsCordinates,
                isPartofSegment=None    # No segment association for orphan
            )

            

                    
    def edge_for_segments(self):
        # Iterate over each system in the network vertex map
        for systemID in self.vertex_in_network:
            segments = self.vertex_in_network[systemID]

            # Compare each segment to every other segment in the same system
            for i in range(len(segments)):
                segment_1_ID = segments[i]
                vertex_1 = self.Conectivitygraph.graph.nodes[segment_1_ID]
                hidden_vertices_1 = vertex_1.get("segmentCordinates")  # Retrieve hidden vertex coordinates for segment 1

                for j in range(len(segments)):
                    segment_2_ID = segments[j]
                    # Skip comparing a segment with itself
                    if segment_1_ID == segment_2_ID:
                        continue

                    vertex_2 = self.Conectivitygraph.graph.nodes[segment_2_ID]
                    hidden_vertices_2 = vertex_2.get("segmentCordinates")  # Coordinates for segment 2

                    # If any coordinate is shared between the two segments, connect them
                    if any(coord in hidden_vertices_1 for coord in hidden_vertices_2):
                        self.Conectivitygraph.add_edge(segment_1_ID, segment_2_ID)
                        # Increment the count of edges between segments
                        self.totalSegmentedgesinGraph += 1

    

    def edge_for_pipingNetwork(self):
        # Iterate over each piping system in the network
        for system_1_ID in self.vertex_in_network:
            segments_1 = self.vertex_in_network[system_1_ID]

            # Loop through each segment in the first system
            for i in range(len(segments_1)):
                segment_1 = segments_1[i]
                hidden_vertices_1 = self.Conectivitygraph.graph.nodes[segment_1].get("segmentCordinates")

                # Compare against all other systems to find inter-system connections
                for system_2_ID in self.vertex_in_network:
                    # Skip the same system
                    if system_1_ID == system_2_ID:
                        continue

                    segments_2 = self.vertex_in_network[system_2_ID]
                    # Loop through each segment in the second system
                    for j in range(len(segments_2)):
                        segment_2 = segments_2[j]
                        hidden_vertices_2 = self.Conectivitygraph.graph.nodes[segment_2].get("segmentCordinates")

                        # If the two segments share any hidden vertex coordinate, connect them
                        if any(coord in hidden_vertices_1 for coord in hidden_vertices_2):
                            self.Conectivitygraph.add_edge(segment_1, segment_2)
                            # Track the addition of an inter-system segment edge
                            self.totalSegmentedgesinGraph += 1

    
    def edge_for_orphan_components(self):
        # Iterate through each orphaned component ID
        for OrphanID in self.PipingComponent.OrphanComponents:
            # Increment total count of orphan components processed
            self.TotalOrphanComponants += 1

            # Retrieve the coordinates of the orphan component node
            OrphanCordinates = self.Conectivitygraph.graph.nodes[OrphanID].get("segmentCordinates")

            # Find the nearest network segment to this orphan (tolerance=3)
            foundSegment = self.nearest_segment_neighbour(3, OrphanCordinates)

            # If a valid segment is found, create an edge and update metrics
            if foundSegment is not False:
                # Add edge between orphan component and its found segment
                self.Conectivitygraph.add_edge(OrphanID, foundSegment)
                # Track successful orphan-to-segment connections
                self.OrphanFoundSegment += 1

                # Merge orphan coordinates into the segment's hidden coordinates list
                self.Conectivitygraph.graph.nodes[foundSegment] \
                    .setdefault("segmentCordinates", []) \
                    .extend(OrphanCordinates)

                # Ensure the segment has an integer connection count and update it
                node_attrs = self.Conectivitygraph.graph.nodes[foundSegment]
                node_attrs.setdefault("NrofConnections", 0)
                node_attrs["NrofConnections"] += len(OrphanCordinates) - 3

                # Update global count of segment connection points
                self.totalSegmentConectionpoints += len(OrphanCordinates) - 3
            else:
                # No segment found within tolerance; skip to next orphan
                continue

    
    def edge_for_missing_offPageReference(self, sensitivity):
        # Get list of nodes currently disconnected in the graph
        disconented_nodes = self.Disconected_Nodes()

        # Iterate through each off-page reference ID that should be in the graph
        for OffPageID in self.OffPageReference.Offpage_to_graph:
            # Skip any off-page nodes that are not marked as disconnected
            if OffPageID not in disconented_nodes:
                continue
            else:
                # Prepare to gather coordinates of potential target segments
                target_cordinates = []

                # Source coordinate of the off-page node
                Source_cordinate = self.Conectivitygraph.graph.nodes[OffPageID].get("position")

                # Determine which segments this off-page reference should connect to
                TargetTag = self.OffPageReference.ConnectorRefrenceTargetlabel[OffPageID]
                target_ids = self.OffPageReference.ConnectorReference[TargetTag]

                # Collect each target segment's hidden coordinates
                for segmentID in target_ids:
                    segmentCordinates = self.Conectivitygraph.graph.nodes[segmentID].get("segmentCordinates")
                    target_cordinates.append(segmentCordinates)

                # Re-fetch the off-page node's position (source)
                Source_cordinate = self.Conectivitygraph.graph.nodes[OffPageID].get("position")

                # Find the best matching segment within the given sensitivity
                segmentConenction = self.nearest_neigbour(
                    sensitivity,
                    Source_cordinate,
                    target_cordinates,
                    target_ids
                )

                # Add an edge from the found segment to the off-page node
                self.Conectivitygraph.add_edge(segmentConenction, OffPageID)
                # Update the count of segment edges in the graph
                self.totalSegmentedgesinGraph += 1

        # Return the sensitivity parameter unchanged
        return sensitivity





    def nearest_segment_neighbour(self, sensitivity, cordinates):
        # Lists to track computed distances and corresponding segment IDs
        distanceList = []
        segmentIndexList = []

        # Iterate through each piping system in the network
        for systemID in self.vertex_in_network:
            segments = self.vertex_in_network[systemID]

            # Loop through each segment in the system
            for segment_ID in segments:
                # Retrieve hidden coordinates (vertices) for this segment
                segmentCordinates = self.Conectivitygraph.graph.nodes[segment_ID].get("segmentCordinates")

                # Compare each input coordinate against each segment coordinate
                for cordinate in cordinates:
                    X1, Y1 = cordinate  # Coordinates of the query point
                    for segmentCordinate in segmentCordinates:
                        X2, Y2 = segmentCordinate  # Coordinates of the segment vertex

                        # Compute Euclidean distance between the two points
                        d = np.sqrt((X1 - X2) ** 2 + (Y1 - Y2) ** 2)

                        # Record the distance and the segment they relate to
                        distanceList.append(d)
                        segmentIndexList.append(segment_ID)

        # Determine the smallest distance and its index
        minimum_distance = min(distanceList)
        index = distanceList.index(minimum_distance)
        segmentID = segmentIndexList[index]

        # If the nearest segment is within the allowed sensitivity, return its ID
        if minimum_distance > sensitivity:
            return False
        else:
            return segmentID


    def nearest_neigbour(self, sensitivity, Source_cordinate, target_cordinates, target_ids):
        # List to track the minimum distance to each potential target
        distanceList = []

        # Extract the x, y coordinates of the source point
        X1, Y1 = Source_cordinate

        # Iterate through each set of target coordinates
        for target_cordinate in target_cordinates:
            # Convert to numpy array for vectorized operations
            arr = np.array(target_cordinate)
            X2 = arr[:, 0]  # All x-values of the target segment's points
            Y2 = arr[:, 1]  # All y-values of the target segment's points

            # Compute the minimum Euclidean distance from the source to any point in this target
            d = min(np.sqrt((X1 - X2) ** 2 + (Y1 - Y2) ** 2))
            distanceList.append(d)

        # Find the global minimum distance and corresponding target index
        minimum_distance = min(distanceList)
        index = distanceList.index(minimum_distance)
        segmentID = target_ids[index]

        # If the nearest target is beyond the sensitivity threshold,
        # increase sensitivity and retry recursively
        if minimum_distance > sensitivity:
            sensitivity += 1
            return self.nearest_neigbour(
                sensitivity,
                Source_cordinate,
                target_cordinates,
                target_ids
            )
        else:
            # Otherwise, return the ID of the closest segment
            return segmentID



                


            
                


    def saveGraph(self, fileName):
        # 1) Relabel every node to str(node)
        G_str = nx.relabel_nodes(
            self.Conectivitygraph.graph,
            lambda n: str(n),
            copy=True
        )

        # 2) Build your pyvis.Network
        nt = Network(
            height="1000px", width="100%",
            notebook=False, directed=True,
            cdn_resources='remote', bgcolor="#222222",
            font_color="white", select_menu=True
        )

        # 3) Import from the string-ified graph
        nt.from_nx(G_str)

        # 4) Write out
        nt.write_html(fileName, notebook=False)



    def givegraphColor(self,index):
        colors = [
            "#e6194b",  # Red
            "#3cb44b",  # Green
            "#ffe119",  # Yellow
            "#0082c8",  # Blue
            "#f58231",  # Orange
            "#911eb4",  # Purple
            "#46f0f0",  # Cyan
            "#f032e6",  # Magenta
            "#d2f53c",  # Lime
            "#fabebe",  # Pink
            "#008080",  # Teal
            "#e6beff",  # Lavender
            "#fffac8",  # Beige
            "#800000",  # Maroon
            "#aaffc3",  # Mint
            "#808000",  # Olive
            "#ffd8b1",  # Apricot
            "#000080",  # Navy
            "#808080",  # Grey
            "#000000",  # Black
            "#bcf60c",  # Lime green
            "#fabed4",  # Light pink
            "#dcbeff"]  # Pale purple
        
        return colors[index% len(colors)]

    def notFullConnectedNetwork(self):
        # Convert all directed edges into undirected frozensets for easy membership testing
        undirected_edges = {frozenset((u, v))
                            for u, v in self.Conectivitygraph.graph.edges()}

        # Total number of piping systems tracked in the network
        total_systems = len(self.vertex_in_network)
        # Counter for systems that are not fully connected internally
        not_full_count = 0

        # Iterate through the list of segments for each system
        for segments in self.vertex_in_network.values():
            # Check if any segment inside this system has no connection to any other segment
            any_is_isolated = any(
                not any(
                    # Test if an edge exists between seg1 and any other seg2
                    frozenset((seg1, seg2)) in undirected_edges
                    for seg2 in segments
                    if seg2 != seg1
                )
                for seg1 in segments
            )

            # If at least one isolated segment is found, mark this system as not fully connected
            if any_is_isolated:
                not_full_count += 1

        # Return the count of incomplete systems and the total number of systems
        return not_full_count, total_systems



                        
                    