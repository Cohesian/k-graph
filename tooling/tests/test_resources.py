from __future__ import annotations

import unittest
from pathlib import Path

from to_neo4j import emit_cypher, load_directory_graph


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMPOSITE_PATH = "T-computer-science/L-composite/E-01-carbon-binder"


class ResourceProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph = load_directory_graph(REPOSITORY_ROOT)

    def test_current_graph_is_valid(self) -> None:
        self.assertEqual(self.graph.errors, [])

    def test_resources_have_v2_addresses_and_integrity(self) -> None:
        node = self.graph.nodes[COMPOSITE_PATH]
        resources = {
            (item.contributor, item.hierarchy, item.key): item.protocol
            for item in node.contributions
        }
        self.assertEqual(
            resources[("research", ("documents",), "md")],
            "markdown-file@1",
        )
        self.assertEqual(
            resources[("research", ("media",), "loci-project")],
            "loci-project@1",
        )
        self.assertEqual(
            resources[("research", ("media",), "mp4")],
            "mp4-file@1",
        )
        self.assertTrue(all(len(item.sha256) == 64 for item in node.contributions))

    def test_current_graph_has_71_accepted_resources(self) -> None:
        resources = sum(len(node.contributions) for node in self.graph.nodes.values())
        self.assertEqual(resources, 71)

    def test_neo4j_projection_preserves_v2_acceptance_records(self) -> None:
        cypher = emit_cypher(self.graph)
        self.assertIn(
            'MERGE (c)-[r:PROVIDES {hierarchy: ["documents"], key: "md"}]->(n)',
            cypher,
        )
        self.assertIn('r.protocol = "markdown-file@1"', cypher)
        self.assertIn("r.sha256 = ", cypher)
        self.assertNotIn("MERGE (c)-[r:CONTRIBUTED]->(n)", cypher)


if __name__ == "__main__":
    unittest.main()
