#!/usr/bin/env python3
"""Emit research/intel-iqt-roster.json from public IQT lists.

A roster edge is capital adjacency (IQT listed as investor), not operational
control. Wikipedia's investments section is under-cited; those names are
grade=moderate. Intercept 2016 table and IQT press / Reuters are stronger.
Washington Post (2016): IQT listed 325 investments, 100+ secret — this file
is the public remainder, not the classified set.
"""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (display_name, source_tag, notes)
# source_tag: wiki | intercept | dealroom | tipranks | reuters | iqt
WIKI = """
A4Vision | 3D facial imaging
Adapx | Microsoft Office and GIS
Agent_Logic | event detection
Algorithmic | AI/ML deploy infrastructure
Authentica | secure messaging
Boundless_Spatial | geospatial; later Planet Labs
Carnegie_Speech | speech recognition
Cassatt | desktop software
D2iQ | Mesosphere / Kubernetes consulting
Dreadnode | AI offensive security testing
FMS | IC visualization knowledgebase
Fetch_Technologies | internet data management
Fuel3D | 3D scanning
GeoIQ | map visualization
Geosemble | geospatial unstructured data
HEO | space imagery
Initiate_Systems | real-time multi-database
Intelliseek | search
Internet_Evidence_Finder | digital forensics (Magnet)
Interset | user behavior analytics
Looking_Glass_Factory | holography
NovoDynamics | Arabic OCR
Nozomi_Networks | OT/IoT security
Oculis_Labs | visual cyber security
PiXlogic | visual search
Quantum4D | visualization
ReversingLabs | malware analysis
Sayari | financial intel / corporate ownership
SRD | identity resolution
SafeWeb | browsing privacy (closed 2001)
Silver_Tail_Systems | website fraud
Stratify | mass-data organization
TRX_Systems | 3D indoor mapping
Visible_Technologies | social media monitoring
Zaplet | email
ArcSight | SIEM
Attensity | text analytics
Basis_Technology | multilingual NLP / cyber forensics
CallMiner | speech analytics
Connectify | wifi/VPN
Convera | search
Destineer | training simulation
Digital_Reasoning | Synthesys
Endeca | search
FireEye | malware protection
Forterra_Systems | virtual-world training
Huddle | content collaboration
Inktomi | network infrastructure
InnoCentive | crowdsourcing
Inxight | search
Keyhole | geospatial viz; Google Earth
Language_Weaver | machine translation
Lingotek | translation
MemSQL | in-memory SQL (SingleStore)
MetaCarta | geo search
Palantir | data integration
Platfora | big-data viz
Recorded_Future | web intel
Socrata | open data
Spotfire | viz analytics
Tacit_Knowledge_Systems | internal knowledge
Teradici | desktop virtualization
TerraGo | GeoPDF
Traction_Software | web 2.0
Visual_Sciences | real-time viz
Wickr | encrypted messaging
zSpace | holographic displays
Xarion_Laser_Acoustics | ultrasonic imaging
Xanadu | photonic quantum
Tyfone | mobile/cloud/IoT security
Stoke_Space | reusable rocket
Starcloud | data centers in space
Bay_Microsystems | packet processing
Network_Appliance | Decru storage encryption
JetCool | data-center liquid cooling
Colossal_Biosciences | de-extinction / bioscience
Phoenix_Tailings | rare earths from tailings
"""

INTERCEPT = """
Aquifi | 3D vision
Beartooth | decentralized mobile network
CliQr | hybrid cloud
CloudPassage | infrastructure security
Databricks | big-data analytics
Dataminr | social-media situational awareness
Docker | containers
Echodyne | ESA radar
Epiq_Solutions | software-defined radio
Geofeedia | location social monitoring
goTenna | off-grid comms
Headspin | mobile app performance
Interset | insider threat analytics
Keyssa | contactless data transfer
Kymeta | satellite antennas
Lookout | mobile cybersecurity
Mapbox | maps
Mesosphere | datacenter automation
Nervana | ML platform (Intel-acquired)
Orbital_Insight | satellite imagery analytics
Orion_Labs | wearable voice
Parallel_Wireless | LTE small cells
PATHAR | social analytics
Pneubotics | mobile material handling
PsiKick | ultra-low-power sensors
PubNub | realtime apps
Rocket_Lab | smallsat launch
Skincential_Sciences | sample collection
Soft_Robotics | soft actuators
Sonatype | software supply-chain security
Spaceflight_Industries | smallsat launch/imagery
ThreatStream | threat intel platform (Anomali)
TransVoyant | live predictive intel
Transient_Electronics | dissolvable semiconductors
TRX_Systems | indoor location
Voltaiq | battery analytics
Zoomdata | big-data viz
"""

DEALROOM = """
Anduril | defense autonomy (third-party holding list)
Cerebras | wafer-scale AI chips
Groq | LPU inference
ICEYE | SAR satellites
Lambda | GPU cloud
Cohesity | data security
DataRobot | AutoML
Sila_Nanotechnologies | battery materials
Infleqtion | quantum sensing / ColdQuanta
Rigetti | superconducting quantum
Tenable | vuln management
Cloudera | big data
Pure_Storage | flash storage
Intel | semiconductors (holding list; not a startup cheque)
Databricks | lakehouse
Palantir | Gotham/Foundry
"""

TIPRANKS = """
Nozomi_Networks | OT security Series E 2025
VulnCheck | exploit intel Series B 2026
Substrate | US X-ray lithography foundry 2025
Twenty | network security 2025
HavocAI | maritime autonomy 2025
GetReal_Security | 2025
Deepgram | speech AI 2026
Armadin | security 2026
Emerald_AI | 2026
Mariana_Minerals | mining 2026
RevEng_ai | reverse-engineering AI 2026
"""

GAEBLER = """
Anomali | threat intel
Apigee | API gateway
Advanced_Navigation | inertial nav
Aira_Technologies | industrial AI
Alfalight | photonics
Biomatrica | sample stabilization
BlueLine_Grid | first-responder comms
Bounce_Imaging | tactical cameras
Cambrios | nanomaterials
Cigent_Technology | endpoint data protection
3VR | video intelligence
"""

DAKOTA = """
D_Wave | quantum annealing; IQT 2012 reporting
"""


def slug(name: str) -> str:
    n = name.strip()
    n = n.replace(" ", "_").replace("-", "_").replace(".", "_")
    n = re.sub(r"_+", "_", n).strip("_")
    aliases = {
        "Palantir_Technologies": "Palantir",
        "Keyhole_Inc": "Keyhole",
        "Recorded_Future": "Recorded_Future",
        "Xanadu_Quantum_Technologies": "Xanadu",
        "D_Wave_Quantum": "D_Wave",
        "DWave": "D_Wave",
        "ThreatStream": "Anomali",
        "Mesosphere": "D2iQ",
        "Sila_Nanotechnologies": "Sila",
        "RevEng_ai": "RevEng_AI",
        "Internet_Evidence_Finder": "Magnet_Forensics",
        "Network_Appliance": "NetApp",
        "Google_Earth": "Keyhole",
    }
    return aliases.get(n, n)


def parse_block(text: str, tag: str):
    rows = []
    for line in text.strip().splitlines():
        if "|" not in line:
            continue
        name, note = [x.strip() for x in line.split("|", 1)]
        rows.append((slug(name), note, tag))
    return rows


def grade_for(tag: str) -> str:
    return {
        "wiki": "moderate",
        "intercept": "strong",
        "dealroom": "moderate",
        "tipranks": "moderate",
        "gaebler": "moderate",
        "dakota": "moderate",
        "reuters": "strong",
        "iqt": "fact",
    }[tag]


def source_for(tag: str) -> str:
    return {
        "wiki": "https://en.wikipedia.org/wiki/In-Q-Tel",
        "intercept": "https://theintercept.com/2016/04/14/in-undisclosed-cia-investments-social-media-mining-looms-large/",
        "dealroom": "https://dealroom.co/investors/in-q-tel/",
        "tipranks": "https://www.tipranks.com/private-companies/investor/in-q-tel",
        "gaebler": "https://www.gaebler.com/VC-Investors-E9E74B4B-3244-4B97-8A57-32F9C7CAFE0B-In-Q-Tel",
        "dakota": "https://www.dakota.com/resources/blog/top-10-iqt-portfolio-companies-2025",
        "reuters": "https://www.reuters.com/world/asia-pacific/us-startup-substrate-announces-chipmaking-tool-that-it-says-will-rival-asml-2025-10-28/",
        "iqt": "https://www.iqt.org/",
    }[tag]


def main():
    rows = []
    rows += parse_block(WIKI, "wiki")
    rows += parse_block(INTERCEPT, "intercept")
    rows += parse_block(DEALROOM, "dealroom")
    rows += parse_block(TIPRANKS, "tipranks")
    rows += parse_block(GAEBLER, "gaebler")
    rows += parse_block(DAKOTA, "dakota")
    # force fact-grade names already independently cited
    rows.append(("Palantir", "early seed", "iqt"))
    rows.append(("Keyhole", "Google Earth predecessor", "iqt"))
    rows.append(("Substrate", "disclosed 2025 backer", "reuters"))

    best = {}
    rank = {"fact": 4, "strong": 3, "moderate": 2, "weak": 1}
    for name, note, tag in rows:
        g = grade_for(tag)
        prev = best.get(name)
        rec = {
            "name": name,
            "note": note,
            "tag": tag,
            "grade": g,
            "source": source_for(tag),
        }
        if not prev or rank[g] > rank[prev["grade"]]:
            best[name] = rec
        elif prev and note and note not in prev["note"]:
            prev["note"] = (prev["note"] + "; " + note)[:220]

    skip = {"In_Q_Tel", "CIA", "NSA", "Official_website"}
    names = sorted(n for n in best if n not in skip)

    entities = []
    edges = []
    for n in names:
        rec = best[n]
        entities.append({
            "name": n,
            "type": "vendor",
            "bucket": "clear",
            "notes": f"Public IQT roster ({rec['tag']}): {rec['note']}. Capital adjacency, not operational control.",
            "source": [rec["source"]],
        })
        edges.append({
            "from": "In_Q_Tel",
            "to": n,
            "kind": "affiliates",
            "instrument": f"public IQT roster ({rec['tag']})",
            "confidence": "high" if rec["grade"] in ("fact", "strong") else "moderate",
            "status": "public-record",
            "grade": rec["grade"],
            "source": [rec["source"]],
        })

    entities.insert(0, {
        "name": "In_Q_Tel",
        "type": "affiliate",
        "notes": "CIA-chartered nonprofit VC. Washington Post 2016: 325 listed investments, 100+ secret. This roster is the public remainder compiled from Wikipedia, Intercept (2016), Dealroom, TipRanks, Gaebler — not the classified set.",
        "source": ["https://www.iqt.org/", "https://en.wikipedia.org/wiki/In-Q-Tel"],
    })

    doc = {
        "as_of": "2026-09-05",
        "metadata": {
            "title": "In-Q-Tel public roster (Wikipedia + Intercept + Dealroom + TipRanks)",
            "layer": "evidenced",
            "theme": "intel",
            "roster_count": len(names),
            "caveat": "WaPo 2016: 100+ IQT investments were secret. This is not the classified remainder.",
        },
        "entities": entities,
        "edges": edges,
    }
    out = os.path.join(ROOT, "research", "intel-iqt-roster.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    print(f"wrote {out}  companies={len(names)}  by_grade=", end="")
    from collections import Counter
    print(dict(Counter(best[n]["grade"] for n in names)))


if __name__ == "__main__":
    main()
