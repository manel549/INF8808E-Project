import plotly.graph_objects as go
import plotly.io as pio

COLOR_PALETTE = {
    'Materials damage': '#1f77b4',
    'Minors': '#ff7f0e',
    'Low damage': '#2ca02c',
    'Severe': '#d62728'
}

GRAVITY_TRANSLATION = {
    'Dommages matériels seulement': 'Materials damage',
    'Léger': 'Minors',
    'Dommages matériels inférieurs au seuil de rapportage': 'Low damage',
    'Mortel ou grave': 'Severe'
}