// Cohesian k-graph schema 0.3.0

CREATE CONSTRAINT k_node_key IF NOT EXISTS
FOR (n:KNode)
REQUIRE n.key IS UNIQUE;

CREATE INDEX k_node_kind IF NOT EXISTS
FOR (n:KNode)
ON (n.kind);

CREATE CONSTRAINT contributor_id IF NOT EXISTS
FOR (c:Contributor)
REQUIRE c.id IS UNIQUE;
