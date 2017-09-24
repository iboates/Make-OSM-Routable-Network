Make OSM Routable Network

This is a Python-based QGIS plugin that offers a visual interface for the osm2pgrouting tool.  It can read local OSMnfiles, or download regions from Geofabrik.  A bounding box may also be applied, which is created by osmosis.  The result is a series of tables in a specified database that is compatible with pgRouting, the PostGIS extension for PostgreSQL.

Dependencies:

    osm2pgrouting: A command line tool that creates routing networks from OpenStreetMap .osm files. (http://pgrouting.org/docs/tools/osm2pgrouting.html)
    Java: Required to run osmosis, the bounding-box tool.
    PostgreSQL: Relational Database management software.
    PostGIS & pgRouting: Extensions for PostgreSQL that enable geometry and routing for PostgreSQL, respectively.
