#!/usr/bin/env python3
"""Canonical navbar for every Weak.Intel page."""

NAV_ITEMS = [
    ("index.html", "Home"),
    ("bubblemap.html", "Bubble Map"),
    ("dashboard.html", "Dashboard"),
    ("globe.html", "Globe"),
    ("atlas.html", "Atlas"),
    ("research.html", "Research"),
    ("methodology.html", "Methodology"),
    ("https://github.com/pq-cybarg/weak-intel", "Source ↗"),
]

DISCLAIMER = (
    "Independent research and opinion. Public-record citations, graded claims. "
    "Nothing here is an accusation of crime, a statement of classified fact, "
    "or a finding of guilt. Intent is not inferred from association. "
    '<a href="methodology.html">Methodology</a>.'
)


def navbar(active="", disclaimer=True):
    def a(h, t):
        cur = t == active
        color = "#e0c07a" if cur else "#c9c2b3"
        wt = 700 if cur else 400
        return (
            f'<a href="{h}" style="color:{color};text-decoration:none;'
            f'white-space:nowrap;font-weight:{wt}">{t}</a>'
        )
    strip = (
        '<nav style="background:#0b0e14;border-bottom:1px solid #2a241c;padding:10px 16px;'
        'display:flex;flex-wrap:wrap;gap:6px 18px;justify-content:center;'
        'font:13.5px/1.5 IBM Plex Sans,Segoe UI,sans-serif">'
        + "".join(a(h, t) for h, t in NAV_ITEMS)
        + "</nav>"
    )
    disc = ""
    if disclaimer:
        disc = (
            '<div style="background:#12161f;color:#8a8378;font:11px/1.5 IBM Plex Sans,'
            'sans-serif;text-align:center;padding:6px 16px;border-bottom:1px solid #2a241c">'
            + DISCLAIMER + "</div>"
        )
    return (
        '<header style="position:sticky;top:0;z-index:200;background:#0b0e14;'
        'isolation:isolate">'
        + strip + disc + "</header>"
    )
