// Cohesian k-graph schema 0.5.0

DROP CONSTRAINT k_node_path IF EXISTS;

CREATE CONSTRAINT k_node_id IF NOT EXISTS
FOR (n:KNode)
REQUIRE n.id IS UNIQUE;

CREATE INDEX k_node_kind IF NOT EXISTS
FOR (n:KNode)
ON (n.kind);

CREATE CONSTRAINT contributor_id IF NOT EXISTS
FOR (c:Contributor)
REQUIRE c.id IS UNIQUE;
