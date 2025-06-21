import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for rendering without a display (useful for servers)
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import datetime
from tabulate import tabulate  # Library to format text tables

class Draw_network:
    def __init__(self, network, segment, component, Equipment, OffPageReference, path):
        # Initialize drawing frame size
        self.frameX = 841
        self.frameY = 594
        # Store references to input data
        self.network = network
        self.segment = segment
        self.component = component
        self.equipment = Equipment
        self.PageReference = OffPageReference
        self.path = path
        # Extract drawing name from file path
        self.DrawingName = path.split('/')[-1]
        # Get selected network IDs
        self.IDrows = self.showNetworks()
        # Draw the diagram
        self.drawdiagram()

    def showNetworks(self):    
        # Prepare lists to collect network statistics
        NetworkLabels = []
        numberOfSegmets = []
        numberOfComponants = []
        numberOfcenterlines = []

        # Iterate through each network
        for ID in self.network.systems:
            countSegments = 0
            countComponents = 0
            countCenterLines = 0
            
            # Count segments, components, and centerlines in each network
            for segmentID in self.network.segments[ID]:
                countSegments += 1
                print(segmentID)

                if segmentID in self.segment.pipingComponats:
                    countComponents += len(self.segment.pipingComponats[segmentID])
                if segmentID in self.segment.CenterLinePoints:
                    countCenterLines += len(self.segment.CenterLinePoints[segmentID])

            NetworkLabels.append(ID)
            numberOfSegmets.append(countSegments)
            numberOfComponants.append(countComponents)
            numberOfcenterlines.append(countCenterLines)

        # Create row indices and print table
        row_numbers = list(range(1, len(NetworkLabels) + 1))
        headers = ["Row", "Network ID", "Nr of segments", "Nr of components", "Nr of lines"]
        table = list(zip(row_numbers, NetworkLabels, numberOfSegmets, numberOfComponants, numberOfcenterlines))
        print("\n=== Network Table ===")
        print(tabulate(table, headers=headers))

        # Prompt user to select rows
        user_input = input("\nEnter row numbers to select (comma separated) or 'all' to select all rows: ")
        
        if user_input.lower() == 'all':
            selected_rows = row_numbers
        else:
            try:
                selected_rows = [int(row.strip()) for row in user_input.split(',')]
            except ValueError:
                print("Invalid input! Please enter row numbers separated by commas.")
                return

        selected_ids = [NetworkLabels[i-1] for i in selected_rows if i <= len(NetworkLabels)]
        print(f"Selected IDs: {selected_ids}")
        return selected_ids

    def createFilename(self):
        # Generate a filename for saving the output diagram
        fileName = self.path + f"/Spagetti/VizulationOfFolder/{str(datetime.date.today())}.png"
        return fileName

    def colors_to_plot(self):
        # Define a long list of distinct colors for plotting
        colors = [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                '#ffbb78', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d0',
                '#f1c6b5', '#e7ba52', '#e74c3c', '#f39c12', '#2ecc71',
                '#3498db', '#9b59b6', '#16a085', '#1abc9c', '#f39c12',
                '#e74c3c', '#8e44ad', '#2c3e50', '#95a5a6', '#f1c40f',
                '#e67e22', '#2ecc71', '#3498db', '#9b59b6', '#16a085',
                '#1abc9c', '#f39c12', '#e74c3c', '#8e44ad', '#2c3e50',
                '#95a5a6', '#f1c40f', '#e67e22', '#2ecc71', '#3498db',
                '#9b59b6', '#16a085', '#1abc9c', '#f39c12', '#e74c3c',
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                '#ffbb78', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d0',
                '#f1c6b5', '#e7ba52', '#e74c3c', '#f39c12', '#2ecc71',
                '#3498db', '#9b59b6', '#16a085', '#1abc9c', '#f39c12',
                '#e74c3c', '#8e44ad', '#2c3e50', '#95a5a6', '#f1c40f',
                '#e67e22', '#2ecc71', '#3498db', '#9b59b6', '#16a085',
                '#1abc9c', '#f39c12', '#e74c3c', '#8e44ad', '#2c3e50',
                '#95a5a6', '#f1c40f', '#e67e22', '#2ecc71', '#3498db',
                '#9b59b6', '#16a085', '#1abc9c', '#f39c12', '#e74c3c'
            ]
        return colors

    def showPageReference(self):
        # Extract coordinates from OffPageReference data
        X = []
        Y = []
        for ID in self.PageReference.label:
            X.append(float(self.PageReference.label[ID][0]))
            Y.append(float(self.PageReference.label[ID][1]))
        return X, Y

    def drawdiagram(self):
        # Main function to draw the full network diagram
        fileName = self.createFilename()
        plt.figure(figsize=(84, 59))
        X, Y = self.showPageReference()
        # Plot off-page references
        plt.plot(X, Y, "^", markersize=20, color="black", label="OffPageReference with no segmentConections or electrical")

        # Draw equipment as rectangles
        NozzleIndex = 1
        for EquipmentID in self.equipment.EquipmentWithNozzle:
            Nozzels = self.equipment.EquipmentWithNozzle[EquipmentID]
            EquipmentLocationX = []
            EquipmentLocationY = []
            for nozzleID in Nozzels:
                IOLocation = self.equipment.NozzleLocation[nozzleID][1]
                EquipmentLocationX.append(IOLocation[0])
                EquipmentLocationY.append(IOLocation[1])
            label = self.equipment.equipment[EquipmentID].attributs.get("ComponentClass")
            if Nozzels:
                EqXmax = max(EquipmentLocationX)
                EqXmin = min(EquipmentLocationX)
                EqYmax = max(EquipmentLocationY)
                EqYmin = min(EquipmentLocationY)
                width = EqXmax - EqXmin
                height = EqYmax - EqYmin
                plt.gca().add_patch(Rectangle((EqXmin, EqYmin), width, height, facecolor='skyblue', edgecolor='black', alpha=0.2, label=label))
                plt.text(EqXmin + width / 2, EqYmin + height / 2, f'{label}', ha='center', va='center', fontsize=30, color='y')

        # Plot nozzles
        for EquipmentID in self.equipment.EquipmentWithNozzle:
            Nozzels = self.equipment.EquipmentWithNozzle[EquipmentID]
            for nozzleID in Nozzels:
                OriginLocation = self.equipment.NozzleLocation[nozzleID][0]
                IOLocation = self.equipment.NozzleLocation[nozzleID][1]
                plt.plot(IOLocation[0], IOLocation[1], "o", markersize=25, color="black", markerfacecolor='none')
                plt.plot([IOLocation[0], OriginLocation[0]], [IOLocation[1], OriginLocation[1]], "-", color="black")
                plt.text(OriginLocation[0], OriginLocation[1], f"Nozzle_{NozzleIndex}", color="black", fontsize=25, ha="center", va="center")
                NozzleIndex += 1

        # Plot orphan piping components
        Orphan_X_graph = []
        Orphan_Y_graph = []
        for OrphanID in self.component.OrphanComponents:
            for point in self.component.ConnectionPoints[OrphanID]:
                Orphan_X_graph.append(point[0])
                Orphan_Y_graph.append(point[1])
        plt.plot(Orphan_X_graph, Orphan_Y_graph, "o", color="brown", markersize=25, alpha=0.3, label="Orphan piping components")

        # Plot each selected network
        color = self.colors_to_plot()
        indexColor = 0
        for systemID in self.IDrows:
            systemColor = color[indexColor]
            segments = self.network.segments[systemID]
            for idx, segmentID in enumerate(segments):
                # Add off-page reference if available
                if segmentID in self.PageReference.Comfirmed_connections:
                    OffpageID = self.PageReference.Comfirmed_connections[segmentID]
                    Offpage_XY_Cordinate = self.PageReference.label[OffpageID]
                    plt.plot(float(Offpage_XY_Cordinate[0]), float(Offpage_XY_Cordinate[1]), "^", markersize=20, color=systemColor)

                CenterLine = self.segment.CenterLinePoints[segmentID]
                PipingComponats = self.segment.pipingComponats.get(segmentID, None)

                for n in range(len(CenterLine)-1):
                    x_coords = [CenterLine[n][0], CenterLine[n+1][0]]
                    y_coords = [CenterLine[n][1], CenterLine[n+1][1]]
                    plt.plot(x_coords, y_coords, color=systemColor, linewidth=5)
                    if idx == len(segments) - 1:
                        midpoint_x = (x_coords[0] + x_coords[1]) / 2
                        midpoint_y = (y_coords[0] + y_coords[1]) / 2
                        if CenterLine[n][0] == CenterLine[n+1][0]:
                            midpoint_x -= 5
                            rotation = 90
                        else:
                            midpoint_y += 5
                            rotation = 0

                if PipingComponats is not None:
                    for ComponatID in PipingComponats:
                        connectionPointComponent = self.component.ConnectionPoints.get(ComponatID, None)
                        if connectionPointComponent is not None:
                            for i in range(len(connectionPointComponent)):
                                componantX = float(connectionPointComponent[i][0])
                                componantY = float(connectionPointComponent[i][1])
                                plt.plot(componantX, componantY, "o", color=systemColor, markersize=20)

            labelsystemID = systemID[:3] + "    " + systemID[-4:]
            plt.text(midpoint_x, midpoint_y, labelsystemID, color=systemColor, fontsize=20, ha='center', va='center', rotation=rotation)
            indexColor += 1

        # Finalize and save plot
        plt.xlim(0, self.frameX)
        plt.ylim(0, self.frameY)
        print(self.frameX)
        print(self.frameY)
        plt.legend(fontsize=30)
        plt.title(self.DrawingName, fontsize=100)
        plt.savefig(self.path + ".png")
