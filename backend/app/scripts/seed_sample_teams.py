import uuid
import psycopg2
import os
from datetime import datetime
from urllib.parse import urlparse

# --- SMART CONFIGURATION ---
# 1. Try to load settings from the Docker Environment (DATABASE_URL)
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Fix for SQLAlchemy format: replace 'postgresql+asyncpg' with just 'postgresql'
    # so the standard psycopg2 driver can read it.
    if "+asyncpg" in database_url:
        database_url = database_url.replace("+asyncpg", "")
    
    # Parse the URL to get the details
    url = urlparse(database_url)
    DB_HOST = url.hostname
    DB_NAME = url.path[1:] # Removes the leading slash '/'
    DB_USER = url.username
    DB_PASSWORD = url.password
    DB_PORT = url.port or 5432
else:
    # 2. Fallback: Localhost defaults (for running python manually on laptop)
    DB_HOST = "localhost"
    DB_NAME = "cycling_lineage"
    DB_USER = "cycling"
    DB_PASSWORD = "cycling"
    DB_PORT = 5432

# Pre-generate UUIDs for teams that will be referenced in lineage events
TEAM_IDS = {
    "alpha": uuid.uuid4(),
    "bravo": uuid.uuid4(),
    "charlie": uuid.uuid4(),
    "delta": uuid.uuid4(),
    "echo": uuid.uuid4(),
    "foxtrot": uuid.uuid4(),
    "golf": uuid.uuid4(),
    "hotel": uuid.uuid4(),
    "india": uuid.uuid4(),
    "juliet": uuid.uuid4(),
    # New teams
    "kilo": uuid.uuid4(),
    "lima": uuid.uuid4(),
    "mike": uuid.uuid4(),
    "november": uuid.uuid4(),
    "oscar": uuid.uuid4(),
    "papa": uuid.uuid4(),
    "quebec": uuid.uuid4(),
    "romeo": uuid.uuid4(),
    "sierra": uuid.uuid4(),
    "tango": uuid.uuid4(),
    "uniform": uuid.uuid4(),
    "victor": uuid.uuid4(),
    "whiskey": uuid.uuid4(),
    "xray": uuid.uuid4(),
    "yankee": uuid.uuid4(),
}

SAMPLE_TEAMS = [
    {
        "node_id": TEAM_IDS["alpha"],
        "founding_year": 2000,
        "dissolution_year": 2012,
        "eras": [
            {"year": 2000, "name": "Alpha Cycling", "tier": 2, "uci": "ALP"},
            {"year": 2001, "name": "Alpha Cycling", "tier": 2, "uci": "ALP"},
            {"year": 2002, "name": "Alpha Pro Team", "tier": 1, "uci": "APT"},
            {"year": 2003, "name": "Alpha Pro Team", "tier": 1, "uci": "APT"},
            {"year": 2004, "name": "Alpha Pro Team", "tier": 1, "uci": "APT"},
            {"year": 2005, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2006, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2007, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2008, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2009, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2010, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2011, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
            {"year": 2012, "name": "Alpha WorldTour", "tier": 1, "uci": "AWT"},
        ],
    },
    {
        "node_id": TEAM_IDS["bravo"],
        "founding_year": 2003,
        "dissolution_year": 2012,
        "eras": [
            {"year": 2003, "name": "Bravo Continental", "tier": 3, "uci": "BRC"},
            {"year": 2004, "name": "Bravo Continental", "tier": 3, "uci": "BRC"},
            {"year": 2005, "name": "Bravo Pro", "tier": 2, "uci": "BRP"},
            {"year": 2006, "name": "Bravo Pro", "tier": 2, "uci": "BRP"},
            {"year": 2007, "name": "Bravo Pro", "tier": 2, "uci": "BRP"},
            {"year": 2008, "name": "Bravo Pro Cycling", "tier": 2, "uci": "BPC"},
            {"year": 2009, "name": "Bravo Pro Cycling", "tier": 2, "uci": "BPC"},
            {"year": 2010, "name": "Bravo Pro Cycling", "tier": 2, "uci": "BPC"},
            {"year": 2011, "name": "Bravo Pro Cycling", "tier": 2, "uci": "BPC"},
            {"year": 2012, "name": "Bravo Pro Cycling", "tier": 2, "uci": "BPC"},
        ],
    },
    {
        "node_id": TEAM_IDS["charlie"],
        "founding_year": 2013,
        "eras": [
            {"year": 2013, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2014, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2015, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2016, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2017, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2018, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2019, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2020, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2021, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2022, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2023, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2024, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
            {"year": 2025, "name": "Charlie Racing", "tier": 1, "uci": "CHA"},
        ],
    },
    {
        "node_id": TEAM_IDS["delta"],
        "founding_year": 2008,
        "dissolution_year": 2015,
        "eras": [
            {"year": 2008, "name": "Delta Cycling", "tier": 3, "uci": "DLT"},
            {"year": 2009, "name": "Delta Cycling", "tier": 3, "uci": "DLT"},
            {"year": 2010, "name": "Delta Pro", "tier": 2, "uci": "DLP"},
            {"year": 2011, "name": "Delta Pro", "tier": 2, "uci": "DLP"},
            {"year": 2012, "name": "Delta Pro", "tier": 2, "uci": "DLP"},
            {"year": 2013, "name": "Delta Pro", "tier": 2, "uci": "DLP"},
            {"year": 2014, "name": "Delta Pro", "tier": 2, "uci": "DLP"},
            {"year": 2015, "name": "Delta Pro", "tier": 2, "uci": "DLP"},
        ],
    },
    {
        "node_id": TEAM_IDS["echo"],
        "founding_year": 2016,
        "eras": [
            {"year": 2016, "name": "Echo Racing", "tier": 2, "uci": "ECH"},
            {"year": 2017, "name": "Echo Racing", "tier": 2, "uci": "ECH"},
            {"year": 2018, "name": "Echo Pro Cycling", "tier": 2, "uci": "EPC"},
            {"year": 2019, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
            {"year": 2020, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
            {"year": 2021, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
            {"year": 2022, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
            {"year": 2023, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
            {"year": 2024, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
            {"year": 2025, "name": "Echo Pro Cycling", "tier": 1, "uci": "EPC"},
        ],
    },
    {
        "node_id": TEAM_IDS["foxtrot"],
        "founding_year": 2016,
        "eras": [
            {"year": 2016, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2017, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2018, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2019, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2020, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2021, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2022, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2023, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2024, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
            {"year": 2025, "name": "Foxtrot Continental", "tier": 3, "uci": "FOX"},
        ],
    },
    {
        "node_id": TEAM_IDS["golf"],
        "founding_year": 1995,
        "dissolution_year": 2010,
        "eras": [
            {"year": 1995, "name": "Golf Cycling Team", "tier": 2, "uci": "GLF"},
            {"year": 1996, "name": "Golf Cycling Team", "tier": 2, "uci": "GLF"},
            {"year": 1997, "name": "Golf Cycling Team", "tier": 2, "uci": "GLF"},
            {"year": 1998, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 1999, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2000, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2001, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2002, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2003, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2004, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2005, "name": "Golf Pro Cycling", "tier": 1, "uci": "GPC"},
            {"year": 2006, "name": "Golf WorldTour", "tier": 1, "uci": "GWT"},
            {"year": 2007, "name": "Golf WorldTour", "tier": 1, "uci": "GWT"},
            {"year": 2008, "name": "Golf WorldTour", "tier": 1, "uci": "GWT"},
            {"year": 2009, "name": "Golf WorldTour", "tier": 1, "uci": "GWT"},
            {"year": 2010, "name": "Golf WorldTour", "tier": 1, "uci": "GWT"},
        ],
    },
    {
        "node_id": TEAM_IDS["hotel"],
        "founding_year": 2011,
        "eras": [
            {"year": 2011, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2012, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2013, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2014, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2015, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2016, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2017, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2018, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2019, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2020, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2021, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2022, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2023, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2024, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
            {"year": 2025, "name": "Hotel Racing", "tier": 1, "uci": "HTL"},
        ],
    },
    {
        "node_id": TEAM_IDS["india"],
        "founding_year": 2018,
        "eras": [
            {"year": 2018, "name": "India Cycling", "tier": 2, "uci": "IND"},
            {"year": 2019, "name": "India Cycling", "tier": 2, "uci": "IND"},
            {"year": 2020, "name": "India Cycling", "tier": 2, "uci": "IND"},
            {"year": 2021, "name": "India Pro Team", "tier": 2, "uci": "IPT"},
            {"year": 2022, "name": "India Pro Team", "tier": 2, "uci": "IPT"},
            {"year": 2023, "name": "India Pro Team", "tier": 2, "uci": "IPT"},
            {"year": 2024, "name": "India Pro Team", "tier": 2, "uci": "IPT"},
            {"year": 2025, "name": "India Pro Team", "tier": 2, "uci": "IPT"},
        ],
    },
    {
        "node_id": TEAM_IDS["juliet"],
        "founding_year": 2018,
        "eras": [
            {"year": 2018, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2019, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2020, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2021, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2022, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2023, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2024, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
            {"year": 2025, "name": "Juliet Continental", "tier": 3, "uci": "JUL"},
        ],
    },
    # === NEW TEAMS ===
    {
        "node_id": TEAM_IDS["kilo"],
        "founding_year": 1998,
        "dissolution_year": 2008,
        "eras": [
            {"year": 1998, "name": "Kilo Cycling", "tier": 3, "uci": "KIL"},
            {"year": 1999, "name": "Kilo Cycling", "tier": 3, "uci": "KIL"},
            {"year": 2000, "name": "Kilo Cycling", "tier": 3, "uci": "KIL"},
            {"year": 2001, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2002, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2003, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2004, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2005, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2006, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2007, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
            {"year": 2008, "name": "Kilo Pro", "tier": 2, "uci": "KLP"},
        ],
    },
    {
        "node_id": TEAM_IDS["lima"],
        "founding_year": 2009,
        "dissolution_year": 2017,
        "eras": [
            {"year": 2009, "name": "Lima Continental", "tier": 3, "uci": "LIM"},
            {"year": 2010, "name": "Lima Continental", "tier": 3, "uci": "LIM"},
            {"year": 2011, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
            {"year": 2012, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
            {"year": 2013, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
            {"year": 2014, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
            {"year": 2015, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
            {"year": 2016, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
            {"year": 2017, "name": "Lima Pro", "tier": 2, "uci": "LMP"},
        ],
    },
    {
        "node_id": TEAM_IDS["mike"],
        "founding_year": 2009,
        "eras": [
            {"year": 2009, "name": "Mike Racing", "tier": 2, "uci": "MIK"},
            {"year": 2010, "name": "Mike Racing", "tier": 2, "uci": "MIK"},
            {"year": 2011, "name": "Mike Racing", "tier": 2, "uci": "MIK"},
            {"year": 2012, "name": "Mike Racing", "tier": 2, "uci": "MIK"},
            {"year": 2013, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2014, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2015, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2016, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2017, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2018, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2019, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2020, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2021, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2022, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2023, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2024, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
            {"year": 2025, "name": "Mike WorldTour", "tier": 1, "uci": "MWT"},
        ],
    },
    {
        "node_id": TEAM_IDS["november"],
        "founding_year": 2002,
        "dissolution_year": 2010,
        "eras": [
            {"year": 2002, "name": "November Cycling", "tier": 2, "uci": "NOV"},
            {"year": 2003, "name": "November Cycling", "tier": 2, "uci": "NOV"},
            {"year": 2004, "name": "November Cycling", "tier": 2, "uci": "NOV"},
            {"year": 2005, "name": "November WorldTour", "tier": 1, "uci": "NWT"},
            {"year": 2006, "name": "November WorldTour", "tier": 1, "uci": "NWT"},
            {"year": 2007, "name": "November WorldTour", "tier": 1, "uci": "NWT"},
            {"year": 2008, "name": "November WorldTour", "tier": 1, "uci": "NWT"},
            {"year": 2009, "name": "November WorldTour", "tier": 1, "uci": "NWT"},
            {"year": 2010, "name": "November WorldTour", "tier": 1, "uci": "NWT"},
        ],
    },
    {
        "node_id": TEAM_IDS["oscar"],
        "founding_year": 2011,
        "eras": [
            {"year": 2011, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2012, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2013, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2014, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2015, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2016, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2017, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2018, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2019, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2020, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2021, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2022, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2023, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2024, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
            {"year": 2025, "name": "Oscar Racing", "tier": 1, "uci": "OSC"},
        ],
    },
    {
        "node_id": TEAM_IDS["papa"],
        "founding_year": 2005,
        "dissolution_year": 2014,
        "eras": [
            {"year": 2005, "name": "Papa Continental", "tier": 3, "uci": "PAP"},
            {"year": 2006, "name": "Papa Continental", "tier": 3, "uci": "PAP"},
            {"year": 2007, "name": "Papa Continental", "tier": 3, "uci": "PAP"},
            {"year": 2008, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
            {"year": 2009, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
            {"year": 2010, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
            {"year": 2011, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
            {"year": 2012, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
            {"year": 2013, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
            {"year": 2014, "name": "Papa Pro", "tier": 2, "uci": "PPR"},
        ],
    },
    {
        "node_id": TEAM_IDS["quebec"],
        "founding_year": 2015,
        "eras": [
            {"year": 2015, "name": "Quebec Cycling", "tier": 2, "uci": "QUE"},
            {"year": 2016, "name": "Quebec Cycling", "tier": 2, "uci": "QUE"},
            {"year": 2017, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2018, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2019, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2020, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2021, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2022, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2023, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2024, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
            {"year": 2025, "name": "Quebec Pro", "tier": 2, "uci": "QPR"},
        ],
    },
    {
        "node_id": TEAM_IDS["romeo"],
        "founding_year": 2015,
        "eras": [
            {"year": 2015, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2016, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2017, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2018, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2019, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2020, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2021, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2022, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2023, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2024, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
            {"year": 2025, "name": "Romeo Racing", "tier": 3, "uci": "ROM"},
        ],
    },
    {
        "node_id": TEAM_IDS["sierra"],
        "founding_year": 2000,
        "dissolution_year": 2007,
        "eras": [
            {"year": 2000, "name": "Sierra Cycling", "tier": 3, "uci": "SIE"},
            {"year": 2001, "name": "Sierra Cycling", "tier": 3, "uci": "SIE"},
            {"year": 2002, "name": "Sierra Cycling", "tier": 3, "uci": "SIE"},
            {"year": 2003, "name": "Sierra Pro", "tier": 2, "uci": "SPR"},
            {"year": 2004, "name": "Sierra Pro", "tier": 2, "uci": "SPR"},
            {"year": 2005, "name": "Sierra Pro", "tier": 2, "uci": "SPR"},
            {"year": 2006, "name": "Sierra Pro", "tier": 2, "uci": "SPR"},
            {"year": 2007, "name": "Sierra Pro", "tier": 2, "uci": "SPR"},
        ],
    },
    {
        "node_id": TEAM_IDS["tango"],
        "founding_year": 2008,
        "eras": [
            {"year": 2008, "name": "Tango Continental", "tier": 3, "uci": "TAN"},
            {"year": 2009, "name": "Tango Continental", "tier": 3, "uci": "TAN"},
            {"year": 2010, "name": "Tango Continental", "tier": 3, "uci": "TAN"},
            {"year": 2011, "name": "Tango Continental", "tier": 3, "uci": "TAN"},
            {"year": 2012, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2013, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2014, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2015, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2016, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2017, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2018, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2019, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2020, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2021, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2022, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2023, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2024, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
            {"year": 2025, "name": "Tango Pro", "tier": 2, "uci": "TPR"},
        ],
    },
    {
        "node_id": TEAM_IDS["uniform"],
        "founding_year": 2010,
        "dissolution_year": 2019,
        "eras": [
            {"year": 2010, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2011, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2012, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2013, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2014, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2015, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2016, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2017, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2018, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
            {"year": 2019, "name": "Uniform Continental", "tier": 3, "uci": "UNI"},
        ],
    },
    {
        "node_id": TEAM_IDS["victor"],
        "founding_year": 2020,
        "eras": [
            {"year": 2020, "name": "Victor Racing", "tier": 2, "uci": "VIC"},
            {"year": 2021, "name": "Victor Racing", "tier": 2, "uci": "VIC"},
            {"year": 2022, "name": "Victor Racing", "tier": 2, "uci": "VIC"},
            {"year": 2023, "name": "Victor Racing", "tier": 2, "uci": "VIC"},
            {"year": 2024, "name": "Victor Racing", "tier": 2, "uci": "VIC"},
            {"year": 2025, "name": "Victor Racing", "tier": 2, "uci": "VIC"},
        ],
    },
    {
        "node_id": TEAM_IDS["whiskey"],
        "founding_year": 2012,
        "dissolution_year": 2020,
        "eras": [
            {"year": 2012, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2013, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2014, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2015, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2016, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2017, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2018, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2019, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
            {"year": 2020, "name": "Whiskey Cycling", "tier": 3, "uci": "WHI"},
        ],
    },
    {
        "node_id": TEAM_IDS["xray"],
        "founding_year": 2018,
        "dissolution_year": 2021,
        "eras": [
            {"year": 2018, "name": "Xray Continental", "tier": 3, "uci": "XRA"},
            {"year": 2019, "name": "Xray Continental", "tier": 3, "uci": "XRA"},
            {"year": 2020, "name": "Xray Continental", "tier": 3, "uci": "XRA"},
            {"year": 2021, "name": "Xray Continental", "tier": 3, "uci": "XRA"},
        ],
    },
    {
        "node_id": TEAM_IDS["yankee"],
        "founding_year": 2022,
        "eras": [
            {"year": 2022, "name": "Yankee Pro", "tier": 2, "uci": "YAN"},
            {"year": 2023, "name": "Yankee Pro", "tier": 2, "uci": "YAN"},
            {"year": 2024, "name": "Yankee Pro", "tier": 2, "uci": "YAN"},
            {"year": 2025, "name": "Yankee Pro", "tier": 2, "uci": "YAN"},
        ],
    },
]

# Lineage events (merges and splits)
LINEAGE_EVENTS = [
    # Simple succession events (1-to-1)
    # Alpha → Charlie (representing merge visually as succession)
    {
        "previous_node_id": TEAM_IDS["alpha"],
        "next_node_id": TEAM_IDS["charlie"],
        "event_year": 2013,
        "event_type": "LEGAL_TRANSFER",
        "notes": "Alpha WorldTour transitioned to Charlie Racing",
    },
    # Bravo → Charlie (second succession to Charlie to show merge-like pattern)
    {
        "previous_node_id": TEAM_IDS["bravo"],
        "next_node_id": TEAM_IDS["charlie"],
        "event_year": 2013,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Bravo Pro Cycling joined Charlie Racing",
    },
    # Delta → Echo (representing split visually as succession)
    {
        "previous_node_id": TEAM_IDS["delta"],
        "next_node_id": TEAM_IDS["echo"],
        "event_year": 2016,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Delta Pro split, Echo Racing formed",
    },
    # Delta → Foxtrot (second succession from Delta to show split-like pattern)
    {
        "previous_node_id": TEAM_IDS["delta"],
        "next_node_id": TEAM_IDS["foxtrot"],
        "event_year": 2016,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Delta Pro split, Foxtrot Continental formed",
    },
    # Golf → Hotel (simple succession)
    {
        "previous_node_id": TEAM_IDS["golf"],
        "next_node_id": TEAM_IDS["hotel"],
        "event_year": 2011,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Golf WorldTour dissolved, Hotel Racing formed with similar roster",
    },
    # === NEW LINEAGE EVENTS ===
    # Kilo → Lima + Mike (split into two teams)
    {
        "previous_node_id": TEAM_IDS["kilo"],
        "next_node_id": TEAM_IDS["lima"],
        "event_year": 2009,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Kilo Pro split, Lima Continental formed",
    },
    {
        "previous_node_id": TEAM_IDS["kilo"],
        "next_node_id": TEAM_IDS["mike"],
        "event_year": 2009,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Kilo Pro split, Mike Racing formed",
    },
    # November → Oscar (simple succession)
    {
        "previous_node_id": TEAM_IDS["november"],
        "next_node_id": TEAM_IDS["oscar"],
        "event_year": 2011,
        "event_type": "LEGAL_TRANSFER",
        "notes": "November WorldTour license transferred to Oscar Racing",
    },
    # Papa + Lima → Quebec (merge of two teams into one)
    {
        "previous_node_id": TEAM_IDS["papa"],
        "next_node_id": TEAM_IDS["quebec"],
        "event_year": 2015,
        "event_type": "LEGAL_TRANSFER",
        "notes": "Papa Pro merged with Lima Pro to form Quebec Cycling",
    },
    {
        "previous_node_id": TEAM_IDS["lima"],
        "next_node_id": TEAM_IDS["quebec"],
        "event_year": 2015,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Lima Pro merged with Papa Pro to form Quebec Cycling",
    },
    # Sierra → Tango (simple succession)
    {
        "previous_node_id": TEAM_IDS["sierra"],
        "next_node_id": TEAM_IDS["tango"],
        "event_year": 2008,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Sierra Pro dissolved, Tango Continental formed with similar roster",
    },
    # Uniform + Whiskey → Victor (merge)
    {
        "previous_node_id": TEAM_IDS["uniform"],
        "next_node_id": TEAM_IDS["victor"],
        "event_year": 2020,
        "event_type": "LEGAL_TRANSFER",
        "notes": "Uniform Continental merged with Whiskey to form Victor Racing",
    },
    {
        "previous_node_id": TEAM_IDS["whiskey"],
        "next_node_id": TEAM_IDS["victor"],
        "event_year": 2020,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Whiskey Cycling merged with Uniform to form Victor Racing",
    },
    # Xray → Yankee (simple succession)
    {
        "previous_node_id": TEAM_IDS["xray"],
        "next_node_id": TEAM_IDS["yankee"],
        "event_year": 2022,
        "event_type": "SPIRITUAL_SUCCESSION",
        "notes": "Xray Continental disbanded, Yankee Pro formed",
    },
]


def seed():
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM team_node;")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"Existing data detected (team_node count={count}).")
        response = input("Clear existing data and reseed? (y/n): ")
        if response.lower() != 'y':
            print("Skipping seed.")
            cur.close()
            conn.close()
            return
        
        # Clear existing data
        print("Clearing existing data...")
        cur.execute("DELETE FROM lineage_event;")
        cur.execute("DELETE FROM team_era;")
        cur.execute("DELETE FROM team_node;")
        cur.execute("DELETE FROM edits;")
        conn.commit()
        print("Existing data cleared.")

    print("Creating sample teams...")
    for team in SAMPLE_TEAMS:
        dissolution_year = team.get("dissolution_year")
        cur.execute(
            """
            INSERT INTO team_node (node_id, founding_year, dissolution_year, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (node_id) DO NOTHING;
            """,
            (str(team["node_id"]), team["founding_year"], dissolution_year),
        )
        for era in team["eras"]:
            era_id = uuid.uuid4()
            cur.execute(
                """
                INSERT INTO team_era (
                    era_id, node_id, season_year, registered_name, uci_code, tier_level,
                    source_origin, is_manual_override, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (era_id) DO NOTHING;
                """,
                (
                    str(era_id),
                    str(team["node_id"]),
                    era["year"],
                    era["name"],
                    era["uci"],
                    era["tier"],
                    "seed_script",
                    True,
                ),
            )
    print(f"Created {len(SAMPLE_TEAMS)} sample teams.")
    
    # Create lineage events
    print("Creating lineage events...")
    for event in LINEAGE_EVENTS:
        event_id = str(uuid.uuid4())
        previous_id = str(event["previous_node_id"]) if event.get("previous_node_id") else None
        next_id = str(event["next_node_id"]) if event.get("next_node_id") else None
        event_year = event["event_year"]
        event_type = event["event_type"]
        notes = event.get("notes", "")
        
        cur.execute(
            """
            INSERT INTO lineage_event (
                event_id, previous_node_id, next_node_id, event_year, event_type, notes, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (event_id) DO NOTHING;
            """,
            (event_id, previous_id, next_id, event_year, event_type, notes),
        )
    
    print(f"Created {len(LINEAGE_EVENTS)} lineage events.")
    
    conn.commit()
    cur.close()
    conn.close()
    print("Seeded sample teams and lineage data successfully!")


if __name__ == "__main__":
    seed()
