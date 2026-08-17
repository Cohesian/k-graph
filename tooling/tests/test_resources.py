from __future__ import annotations

import unittest
from pathlib import Path

from to_neo4j import emit_cypher, load_directory_graph


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMPOSITE_PATH = "T-computer-science/L-composite/F-01-carbon-binder"


class ResourceProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = load_directory_graph(REPOSITORY_ROOT)

    def test_current_graph_is_valid(self) -> None:
        self.assertEqual(self.graph.errors, [])

    def test_resources_are_domain_aware(self) -> None:
        node = self.graph.nodes[COMPOSITE_PATH]
        self.assertEqual(node.contributors["research"], {"documents": ["md"]})
        self.assertEqual(node.contributors["studio"]["scenes"], ["py"])
        self.assertEqual(node.contributors["studio"]["videos"], ["mp4"])

    def test_current_graph_has_33_logical_resources(self) -> None:
        resources = sum(
            len(formats)
            for node in self.graph.nodes.values()
            for domains in node.contributors.values()
            for formats in domains.values()
        )
        self.assertEqual(resources, 33)

    def test_neo4j_projection_preserves_domains(self) -> None:
        cypher = emit_cypher(self.graph)
        self.assertIn('MERGE (c)-[r:PROVIDES {domain: "documents"}]->(n)', cypher)
        self.assertIn('MERGE (c)-[r:PROVIDES {domain: "scenes"}]->(n)', cypher)
        self.assertIn('MERGE (c)-[r:PROVIDES {domain: "videos"}]->(n)', cypher)
        self.assertNotIn("MERGE (c)-[r:CONTRIBUTED]->(n)", cypher)


if __name__ == "__main__":
    unittest.main()
