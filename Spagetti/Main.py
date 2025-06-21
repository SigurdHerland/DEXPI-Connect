#import neceserry liberies
from DrawDexpi.Plot_Line_circle import VisualiseXML
from DrawDexpi.ParseLinesAndCircles import ParseLinesAndCircles
from vertex import Vertex
from DrawPipingNetworks import Draw_network
from ProcessDexpi.elementSearch import elementSearch
from ProcessDexpi.PipingComponent import PipingComponent
from ProcessDexpi.Equipment import Equipment
from ProcessDexpi.PipingNetworkSystem import PipingNetworkSystem
from ProcessDexpi.PipingNetworkSegment import PipingNetworkSegment
from ProcessDexpi.PageReference import PageReference
from ProcessDexpi.Conectivity import BuildConectivityGraph

import lxml
from lxml import etree
from rdflib import Graph, URIRef, RDF, RDFS, OWL
from collections import Counter
import os
import re

filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1630_ D 20.FPQ-AKSO-P-XB-20005-01_FGD PRODUCTION MANIFOLDS.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1657_ D 20.FPQ-AKSO-P-XB-20010-01_MAIN PRODUCTION MANIFOLD.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1701_ D 20.FPQ-AKSO-P-XB-20015-01_FGD TEST MANIFOLDS.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1706_ D 20.FPQ-AKSO-P-XB-20020-01_TEST MANIFOLD.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1716_ D 20.FPQ-AKSO-P-XB-20030-01_TEST SEPARATOR INLET HEATER.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1730_ D 20.FPQ-AKSO-P-XB-20031-01_TEST SEPARATOR INLET MANIFOLD.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1731_ D 20.FPQ-AKSO-P-XB-20040-01_UPP INLET HEATER.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1746_ D 20.FPQ-AKSO-P-XB-20045-01_MUNIN FLOWLINE PRESSURE  TROL.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1755_ D 20.FPQ-AKSO-P-XB-20050-01_TEST SEPARATOR.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1811_ D 20.FPQ-AKSO-P-XB-20051-01_TEST SEPARATOR PSVS.XML"
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/C01V04-VER.EX01.xml"

#projectPath
#filePath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster/DEXPI_HuginA/20241031_1755_ D 20.FPQ-AKSO-P-XB-20050-01_TEST SEPARATOR.XML"
ProjectPath = "/Users/sigurdherland/Library/CloudStorage/OneDrive-NTNU/5yearMaster"
# 1) Using os.path + split
filename = os.path.basename(filePath)            # →  example "20241031_1716_ D 20...HEATER.XML"
stem, ext = os.path.splitext(filename)           #  example stem="20241031_1716_ D 20...HEATER", ext=".XML"
last_piece = stem.split('_')[-1]                 # → example "TEST SEPARATOR INLET HEATER"

print(last_piece)
pathtosaveGraph = ProjectPath + "/Knowleadge graph/" + last_piece
pathtosaveFigure = ProjectPath + "/P&ID/" + last_piece
# Main menu interface for processing DEXPI files
# Main menu interface for processing DEXPI files
def main_menu():
    tree = etree.parse(filePath)  # Parse the XML tree from file path
    vertices = load_DEXPI_File(tree)  # Load and structure the DEXPI XML elements
    a = [0,0,0,0,0]  # Track whether each processing step has been completed

    while True:
        # Displaying menu options
        print("\n=== DEXPI Processing Menu ===")
        print("0. Search for element or attribute")
        print("1. Process PipingComponent") 
        print("2. Process Equipment")
        print("3. Process PipingNetworkSystem")
        print("4. Process PipingNetworkSegment")
        print("5. Process OffPageReference")
        print("")
        print("6. Draw a Network")
        print("7. Build conectivityGraph")
        print("")
        print("e. To Exit")

        choice = input("Enter your choice : ")  # User input for menu selection

        if choice == '1':
            print("\n=== PROCESS PIPINGCOMPONENT 🔍 ===")
            # Instantiate and process piping components
            pipingcomponent = PipingComponent(vertices,last_piece)
            pipingcomponent.create_hierarchy_graph()
            pipingcomponent.visualize_hierarchy_by_componantClass(ProjectPath)
            pipingcomponent.print_table_data()
            a[0] = 1  # Mark as processed

        elif choice == '2':
            print("\n=== PROCESS EQIPMENT 🔍 ===")
            # Instantiate and process equipment
            equipment = Equipment(vertices)
            a[1] = 1

        elif choice == "0":
            print("\n=== SEARCH FOR ELEMENT OR ATTRIBUTES 🔍 ===")
            # Search for elements or attributes
            search = elementSearch(vertices)
            search.search_for_element()

        elif choice == "3":
            print("\n=== PROCESS PIPING NETWORK SYSTEM 🔍 ===")
            # Process piping network system
            pipingnetworksystem = PipingNetworkSystem(vertices)
            a[2] = 1

        elif choice == "4":
            # Process piping network segment
            pipingnetworksegment = PipingNetworkSegment(vertices)
            a[3] = 1

        elif choice == "5":
            # Ensure piping segment is processed before OffPageReference
            if a[3] != 1:
                pipingnetworksegment = PipingNetworkSegment(vertices)
                a[3] = 1
            OffPageReference = PageReference(vertices, pipingnetworksegment)
            a[4] = 1

        elif choice == "6":
            # Ensure all components are processed before drawing network
            if a != [1,1,1,1,1]:
                pipingcomponent = PipingComponent(vertices,last_piece)
                equipment = Equipment(vertices)
                pipingnetworksegment = PipingNetworkSegment(vertices)
                OffPageReference = PageReference(vertices,pipingnetworksegment)
                pipingnetworksystem = PipingNetworkSystem(vertices)
            # Draw the complete process network
            draw_the_network = Draw_network(pipingnetworksystem,
                                            pipingnetworksegment,
                                            pipingcomponent,
                                            equipment,
                                            OffPageReference,
                                            pathtosaveFigure)

        elif choice == "7":
            # Ensure all components are processed before building graph
            if a != [1,1,1,1,1]:
                pipingcomponent = PipingComponent(vertices,last_piece)
                equipment = Equipment(vertices)
                pipingnetworksegment = PipingNetworkSegment(vertices)
                OffPageReference = PageReference(vertices,pipingnetworksegment)
                pipingnetworksystem = PipingNetworkSystem(vertices)
            # Build connectivity graph
            Create_conectivityGraph = BuildConectivityGraph(pipingnetworksystem,
                                                            pipingnetworksegment,
                                                            pipingcomponent,
                                                            OffPageReference,
                                                            equipment,
                                                            pathtosaveGraph)

        elif choice == 'e':
            # Exit the menu loop
            print("Exiting... Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")

# Function to load DEXPI XML structure into Vertex objects
def load_DEXPI_File(tree):
    vertices = {}  # Dictionary to hold all Vertex objects
    total = sum(1 for _ in tree.iter())  # Count total number of XML elements
    current = 0

    for elem in tree.iter():
        current += 1
        print(f"🔄 Loading element {current}/{total}: {elem.tag}", end='\r')

        # Create Vertex and assign properties from XML structure
        vertices[elem] = Vertex(elem, elem.tag)
        vertices[elem].add_parent(elem.getparent())  # Set parent

        # Loop through children and record child relationships
        for child in elem:
            vertices[elem].add_child(child)
            vertices[elem].add_childName(child.tag)

        # Add attributes and optional metadata
        vertices[elem].add_attributs(elem.attrib)
        vertices[elem].add_layer(elem.attrib.get("Layer"))  # Optional: Layer filtering
        vertices[elem].add_RDL(elem.attrib.get("ComponentClassURI"))  # Optional: Link to RDL

    print("\n✅ Loading complete.")
    return vertices  # Return dictionary of structured vertices

# Start the menu if this script is run directly
if __name__ == "__main__":
    main_menu()
