# -*- coding: utf-8 -*-
"""Built-in theme definitions for the ProwlrBot console."""

from __future__ import annotations

from typing import Any, Dict, List

THEMES: List[Dict[str, Any]] = [
    {
        "id": "ocean-depths",
        "name": "Ocean Depths",
        "description": "Professional and calming maritime theme",
        "best_for": "Corporate, financial, consulting",
        "colors": {
            "primary": "#1a2332",
            "secondary": "#2d8b8b",
            "accent": "#a8dadc",
            "background": "#f1faee",
        },
        "fonts": {
            "header": "DejaVu Sans Bold",
            "body": "DejaVu Sans",
        },
    },
    {
        "id": "sunset-boulevard",
        "name": "Sunset Boulevard",
        "description": "Warm and vibrant sunset colors",
        "best_for": "Creative, marketing, events",
        "colors": {
            "primary": "#264653",
            "secondary": "#e76f51",
            "accent": "#f4a261",
            "background": "#e9c46a",
        },
        "fonts": {
            "header": "DejaVu Serif Bold",
            "body": "DejaVu Sans",
        },
    },
    {
        "id": "forest-canopy",
        "name": "Forest Canopy",
        "description": "Natural and grounded earth tones",
        "best_for": "Environmental, sustainability, wellness",
        "colors": {
            "primary": "#2d4a2b",
            "secondary": "#7d8471",
            "accent": "#a4ac86",
            "background": "#faf9f6",
        },
        "fonts": {
            "header": "FreeSerif Bold",
            "body": "FreeSans",
        },
    },
    {
        "id": "modern-minimalist",
        "name": "Modern Minimalist",
        "description": "Clean and contemporary grayscale",
        "best_for": "Tech, architecture, design",
        "colors": {
            "primary": "#36454f",
            "secondary": "#708090",
            "accent": "#d3d3d3",
            "background": "#ffffff",
        },
        "fonts": {
            "header": "DejaVu Sans Bold",
            "body": "DejaVu Sans",
        },
    },
    {
        "id": "golden-hour",
        "name": "Golden Hour",
        "description": "Rich and warm autumnal palette",
        "best_for": "Hospitality, artisan, lifestyle",
        "colors": {
            "primary": "#4a403a",
            "secondary": "#c1666b",
            "accent": "#f4a900",
            "background": "#d4b896",
        },
        "fonts": {
            "header": "FreeSans Bold",
            "body": "FreeSans",
        },
    },
    {
        "id": "arctic-frost",
        "name": "Arctic Frost",
        "description": "Cool and crisp winter-inspired theme",
        "best_for": "Healthcare, clean tech, pharma",
        "colors": {
            "primary": "#4a6fa5",
            "secondary": "#d4e4f7",
            "accent": "#c0c0c0",
            "background": "#fafafa",
        },
        "fonts": {
            "header": "DejaVu Sans Bold",
            "body": "DejaVu Sans",
        },
    },
    {
        "id": "desert-rose",
        "name": "Desert Rose",
        "description": "Soft and sophisticated dusty tones",
        "best_for": "Fashion, beauty, interior design",
        "colors": {
            "primary": "#5d2e46",
            "secondary": "#b87d6d",
            "accent": "#d4a5a5",
            "background": "#e8d5c4",
        },
        "fonts": {
            "header": "FreeSans Bold",
            "body": "FreeSans",
        },
    },
    {
        "id": "tech-innovation",
        "name": "Tech Innovation",
        "description": "Bold and modern tech aesthetic",
        "best_for": "Startups, software, AI/ML",
        "colors": {
            "primary": "#1e1e1e",
            "secondary": "#0066ff",
            "accent": "#00ffff",
            "background": "#ffffff",
        },
        "fonts": {
            "header": "DejaVu Sans Bold",
            "body": "DejaVu Sans",
        },
    },
    {
        "id": "botanical-garden",
        "name": "Botanical Garden",
        "description": "Fresh and organic garden colors",
        "best_for": "Food, farm-to-table, natural products",
        "colors": {
            "primary": "#4a7c59",
            "secondary": "#b7472a",
            "accent": "#f9a620",
            "background": "#f5f3ed",
        },
        "fonts": {
            "header": "DejaVu Serif Bold",
            "body": "DejaVu Sans",
        },
    },
    {
        "id": "midnight-galaxy",
        "name": "Midnight Galaxy",
        "description": "Dramatic and cosmic deep tones",
        "best_for": "Entertainment, gaming, luxury",
        "colors": {
            "primary": "#2b1e3e",
            "secondary": "#4a4e8f",
            "accent": "#a490c2",
            "background": "#e6e6fa",
        },
        "fonts": {
            "header": "FreeSans Bold",
            "body": "FreeSans",
        },
    },
]

THEME_IDS = {t["id"] for t in THEMES}
