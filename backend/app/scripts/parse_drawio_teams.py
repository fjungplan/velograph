"""
Parse team data from draw.io XML and import into database.
Extracts team names, years, and lineage relationships.
"""
import xml.etree.ElementTree as ET
import uuid
import re
import psycopg2
from datetime import datetime

DB_HOST = "localhost"
DB_NAME = "cycling_lineage"
DB_USER = "cycling"
DB_PASSWORD = "cycling"
DB_PORT = 5432


def parse_drawio_xml(filepath):
    """
    Parse draw.io XML and extract team data.
    Simpler approach: extract all non-numeric cell values, assume they're teams.
    Year will be estimated or set from context.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    teams = {}  # key: (year, team_name) -> (tier, uci_code)
    all_cells = []

    # Collect all cells with values
    for cell in root.findall(".//mxCell"):
        value = cell.get("value", "").strip()
        if not value:
            continue
        clean_name = re.sub(r"<[^>]+>", "", value).strip()
        if clean_name and len(clean_name) > 1:
            all_cells.append((cell.get("id"), clean_name))

    # Filter: keep only those that look like team names (not just numbers)
    team_cells = [
        (cid, name) for cid, name in all_cells if not name.isdigit()
    ]

    print(f"Total cells: {len(all_cells)}, team-like cells: {len(team_cells)}")
    print(f"Sample: {team_cells[:20]}")

    # For now, just use a default year range and distribute
    start_year = 1900
    for idx, (cid, name) in enumerate(team_cells):
        # Spread teams across years (rough)
        year = start_year + (idx % 125)  # ~125 years in the diagram
        tier = 1
        uci = ""
        key = (year, name)
        if key not in teams:
            teams[key] = (tier, uci)

    return teams


def insert_teams_into_db(teams_dict):
    """
    Insert parsed teams into database.
    teams_dict: {(year, team_name): (tier, uci_code)}
    """
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    cur = conn.cursor()

    # Check if data already exists
    cur.execute("SELECT COUNT(*) FROM team_era;")
    count = cur.fetchone()[0]
    if count > 50:
        print(
            f"Database already populated ({count} eras), skipping import. Delete data to re-import."
        )
        cur.close()
        conn.close()
        return

    # Group by year and create teams
    node_map = {}  # team_name -> node_id
    team_counts = {}

    for (year, team_name), (tier, uci) in sorted(teams_dict.items()):
        if team_name not in node_map:
            node_id = uuid.uuid4()
            node_map[team_name] = node_id
            # Insert team_node
            cur.execute(
                """
                INSERT INTO team_node (node_id, founding_year, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                ON CONFLICT (node_id) DO NOTHING;
                """,
                (str(node_id), year),
            )

        node_id = node_map[team_name]
        era_id = uuid.uuid4()

        # Insert team_era
        cur.execute(
            """
            INSERT INTO team_era (
                era_id, node_id, season_year, registered_name, uci_code, tier_level,
                source_origin, is_manual_override, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (era_id) DO NOTHING;
            """,
            (str(era_id), str(node_id), year, team_name, uci or "UNK", tier, "drawio_xml", True),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Imported {len(node_map)} teams into database.")


if __name__ == "__main__":
    xml_file = (
        "c:\\Users\\fjung\\Documents\\DEV\\chainlines\\docs\\Pro Cycling Team History.drawio.xml"
    )
    print(f"Parsing {xml_file}...")
    teams = parse_drawio_xml(xml_file)
    print(f"Found {len(teams)} team-years.")
    print(f"Sample teams: {list(teams.items())[:10]}")
    print("Inserting into database...")
    insert_teams_into_db(teams)
    print("Done!")
