class elementSearch:
    def __init__(self, vertices):
        # Store the mapping of element IDs to vertex objects
        self.vertices = vertices
    
    def search_for_element(self):
        # Prompt user for search criteria via console input
        specific_elemTag = input("Write element TAG: ")
        specific_attribute_key = input("Write a specific attribute Key: ")
        specific_attribute_value = input("Write a specific attribute Value: ")

        # Use default criteria if none provided
        if specific_elemTag == "":
            specific_elemTag = "PlantInformation"
            specific_attribute_key = "Application"
            specific_attribute_value = "Dexpi"

        correct_elem = None
        # Find the element matching both tag and attribute/value pair
        for elem, vertex in self.vertices.items():
            if vertex.elemTAG == specific_elemTag:
                for key_attribute, value_attribute in vertex.attributs.items():
                    if (key_attribute == specific_attribute_key \
                            and value_attribute == specific_attribute_value):
                        correct_elem = elem
                        break
                if correct_elem is not None:
                    break

        # Display separators and heading
        print("\n___________________________________")
        print(" SHOWING ANCESTORS AND CHILDRENS  ")
        print()

        # ANSI color codes for console output
        red = "\033[31m"
        reset = "\033[0m"

        # Navigate through the hierarchy until user exits
        while True:
            # Compute ancestor chain and direct children of current element
            ancestors = self.ancestors(self.vertices[correct_elem], [correct_elem])
            children = self.vertices[correct_elem].childs
            elementLine = list(reversed(ancestors)) + children

            # Print the formatted tree of ancestors and children
            self.showAncestors(ancestors, children)
            print(red + "Select an index of branch to analyse: " + reset)

            # Get user choice and update current element or exit
            try:
                choiceElement = int(input())
                if 1 <= choiceElement <= len(elementLine):
                    correct_elem = elementLine[choiceElement - 1]
                else:
                    print("Exiting elementSearch Goodbye! 👋")
                    break
            except ValueError:
                print("Invalid input: please enter a number.")
                break

    def ancestors(self, vertex, list_of_ancestors=None):
        # Recursively collect all ancestor IDs up to the root
        if list_of_ancestors is None:
            list_of_ancestors = []

        # If the vertex has a parent, add it and recurse upward
        if vertex.parent is not None:
            parentKey = vertex.parent
            list_of_ancestors.append(parentKey)
            return self.ancestors(self.vertices[parentKey], list_of_ancestors)
        else:
            # Return full ancestor list when root reached
            return list_of_ancestors
        
    def showAncestors(self, ancestors, children):
        # Number of ancestor levels
        total_ancestors = len(ancestors)
        line_number = 1  # Counter for menu indexing

        # ANSI color codes for visual tree formatting
        red = "\033[31m"
        cyan = "\033[36m"
        yellow = "\033[33m"
        green = "\033[32m"
        reset = "\033[0m"

        # Print each ancestor with tree branches
        for idx, key in enumerate(reversed(ancestors)):
            vertex = self.vertices[key]

            # Build prefix for nested levels
            prefix = ""
            for i in range(idx):
                prefix += red + "│   " + reset

            # Choose branch character based on position
            branch = red + ("└── " if idx == total_ancestors - 1 else "├── ") + reset

            # Construct and print ancestor line with attributes
            linePrint = red + f"{line_number:>3}. " + reset
            linePrint += prefix + branch + cyan + f"{vertex.elemTAG}" + reset + " "
            for k, v in vertex.attributs.items():
                linePrint += yellow + k + reset + ":" + green + v + reset + " "
            print(linePrint)
            line_number += 1

            # If this is the deepest ancestor, also list its children
            if idx == total_ancestors - 1:
                child_prefix = prefix + red + "    " + reset
                for c_idx, child_key in enumerate(children):
                    child = self.vertices[child_key]
                    child_branch = red + ("└── " if c_idx == len(children) - 1 else "├── ") + reset
                    child_line = red + f"{line_number:>3}. " + reset
                    child_line += child_prefix + child_branch + cyan + f"{child.elemTAG}" + reset + " "
                    for k, v in child.attributs.items():
                        child_line += yellow + k + reset + ":" + green + v + reset + " "
                    print(child_line)
                    line_number += 1
