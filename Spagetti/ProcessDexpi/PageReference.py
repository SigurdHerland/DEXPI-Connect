from collections import Counter

class PageReference:
    def __init__(self, vertices, pipingnetworksegment):
        # Store vertex data and target piping segments for later processing
        self.vertices = vertices
        self.label = {}                        # {offPageRefID: [x, y] coordinates}
        self.ConnectorRefrenceTargetlabel = {} # {offPageRefID: target reference text}
        self.ConnectorReference = {}           # {target text: [segmentID, ...]}
        self.Comfirmed_connections = {}        # {segmentID: offPageRefID}
        self.Offpage_to_graph = []             # List of off-page IDs to add to graph
        self.uniqeReference = set()            # Unique target texts
        self.nonUniqeReference = set()         # Repeated target texts

        # Build maps of labels and their assigned strings
        self.processClasses()
        # Associate labels with pipeline segments based on matching text
        self.findSegmentConections(pipingnetworksegment)
        # Confirm which label-segment pairs to include in the graph
        self.confirmation_of_conectivity()

    def processClasses(self):
        # Counters for total labels and text assignments
        count = 0
        countAssaigmentClass = 0
        allAssignmentStrings = []  # Collect all assignment strings for frequency analysis

        # Loop through all vertices to find labels of type OffPageReference
        for elem_id, vertex in self.vertices.items():
            if vertex.elemTAG == "Label" and vertex.attributs.get("ComponentName") == "OffPageReference":
                count += 1
                ID = vertex.attributs.get("ID")

                # Extract the label's screen position coordinates
                for child_id in vertex.childs:
                    v = self.vertices[child_id]
                    if v.elemTAG == "Position":
                        for pos_id in v.childs:
                            loc = self.vertices[pos_id]
                            if loc.elemTAG == "Location":
                                # Store [X, Y] as floats
                                self.label[ID] = [
                                    float(loc.attributs.get("X")),
                                    float(loc.attributs.get("Y"))
                                ]

                # Extract the label's text content (assignment class)
                for child_id in vertex.childs:
                    v = self.vertices[child_id]
                    if v.elemTAG == "Text":
                        s = v.attributs.get("String")
                        if s:
                            countAssaigmentClass += 1
                            self.ConnectorRefrenceTargetlabel[ID] = s
                            allAssignmentStrings.append(s)

        # Count frequencies of each assignment string
        counter = Counter(allAssignmentStrings)
        self.uniqeReference    = {t for t, c in counter.items() if c == 1}
        self.nonUniqeReference = {t for t, c in counter.items() if c > 1}

        # Print summary of label discovery
        print("Total number of OffPageReference =", count, "🔢")
        print("Total number of AssignmentClass =", countAssaigmentClass, "🔗")
        print("Total number of UNIQUE AssignmentClass =", len(self.uniqeReference), "🦄\n")

        # If there are repeated texts, list them with counts
        if self.nonUniqeReference:
            print("Repeated AssignmentClass values and counts:")
            for t in self.nonUniqeReference:
                print(f"  • {t!r} appears {counter[t]} times")
            extras = sum(counter[t] - 1 for t in self.nonUniqeReference)
            print(
                "Total number of repeated entries (beyond the first occurrences) =",
                extras,
                "\n"
            )

    def findSegmentConections(self, pipingnetworksegment):
        # Reset any previous connector mappings
        self.ConnectorReference.clear()
        matched_segments = set()

        # Check each segment in the piping network for matching text
        for seg_id, segment in pipingnetworksegment.segments.items():
            for target in self.uniqeReference | self.nonUniqeReference:
                # If target text appears in segment subtree, record the match
                if self.childsAttributs(segment.childs, target):
                    matched_segments.add(seg_id)
                    self.ConnectorReference.setdefault(target, []).append(seg_id)

        # Summarize match counts
        total_segments = len(matched_segments)
        unique_edge_count = sum(
            1
            for t in self.uniqeReference
            if len(self.ConnectorReference.get(t, [])) == 1
        )

        print(
            "Total number of segments that matched with offPageReference =",
            total_segments,
            "🔢"
        )
        print(
            "Total number of one single edge to segment =",
            unique_edge_count,
            "🦄\n"
        )

        # If any text repeats, list how many segments each repeats for
        if self.nonUniqeReference:
            print("Repeated AssignmentClass to segments:")
            nonuniq_counts = {
                t: len(self.ConnectorReference.get(t, []))
                for t in self.nonUniqeReference
            }
            for t, cnt in nonuniq_counts.items():
                print(f"  • {t!r} appears {cnt} times")
            extras = sum(cnt - 1 for cnt in nonuniq_counts.values())
            print(
                "Total number of repeated entries (beyond the first occurrences) =",
                extras,
                "\n"
            )

    def childsAttributs(self, childs, target, visited=None):
        # Recursively search child elements for any attribute containing target text
        if visited is None:
            visited = set()
        for ch_id in childs:
            if ch_id in visited:
                continue
            visited.add(ch_id)

            child = self.vertices[ch_id]
            # 1) Check direct attributes for the target substring
            for val in child.attributs.values():
                if isinstance(val, str) and target in val:
                    return True

            # 2) Recurse into grandchildren
            if self.childsAttributs(child.childs, target, visited):
                return True

        return False

    def confirmation_of_conectivity(self):
        missingPath = 0
        singlePath = []
        multiplePath = []

        # For each off-page label, evaluate how many segments it matched
        for label_id, target_label in self.ConnectorRefrenceTargetlabel.items():
            segs = self.ConnectorReference.get(target_label, [])
            count = len(segs)

            if count == 0:
                # No connection found for this label
                missingPath += 1
                print(target_label)
            elif count == 1:
                # Exactly one match: confirm this connection
                print(
                    f"offPage {label_id!r} --> {segs[0]!r} segment: targetlabel = {target_label!r}"
                )
                self.Comfirmed_connections[segs[0]] = label_id
                singlePath.append(label_id)
                self.Offpage_to_graph.append(label_id)
            else:
                # Multiple matches found
                multiplePath.append(label_id)
                print(
                    f"❌🎯 offPage {label_id!r} has multiple segments: {segs}"
                )
                self.Offpage_to_graph.append(label_id)

        # Print summary of how many labels fell into each category
        print(missingPath, "OffPageLabels not found in any segment ❌")
        print(len(singlePath), "OffPageLabels found in exactly one segment ✅")
        print(len(multiplePath), "OffPageLabels found in multiple segments 🎯🎯🎯")
