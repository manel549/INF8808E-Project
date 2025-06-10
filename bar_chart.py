import plotly.graph_objects as go
import plotly.io as pio

from modes import MODES, MODE_TO_COLUMN
import pandas as pd


GRAVITE_TRANSLATION = {
    'Mortel ou grave': 'Fatal or Serious',
    'Léger': 'Minor',
    'Dommages matériels seulement': 'Property Damage Only',
    'Dommages matériels inférieurs au seuil de rapportage': 'Below Reporting Threshold'
}

def get_counts_by_type_and_time(df, time_col='AN', type_col='GRAVITE'):
    '''
    Calcule le nombre d’accidents groupés par unité de temps et type d’accident.

    Args:
        df (pd.DataFrame): Données contenant au minimum les colonnes de temps et de type
        time_col (str): Nom de la colonne temporelle (ex: 'mois', 'jour', 'heure')
        type_col (str): Nom de la colonne représentant le type d’accident

    Returns:
        pd.DataFrame: Tableau avec colonnes [temps, type_accident, count]
    '''
    df = pd.read_csv('./assets/data/data_fusionnee.csv')

    # Traduire les types d'accidents
    df[type_col] = df[type_col].map(GRAVITE_TRANSLATION)

    grouped = df.groupby([time_col, type_col]).size().reset_index(name='count')
    grouped.columns = [time_col, type_col, 'count']
    return grouped

def init_figure(title='Accident Frequency in Quebec'):
    '''
        Initializes the Graph Object figure used to display the bar chart.
        Sets the template to be used to "simple_white" as a base with
        our custom template on top. Sets the title to 'Lines per act'

        Returns:
            fig: The figure which will display the bar chart
    '''
    fig = go.Figure()

    # TODO : Update the template to include our new theme and set the title

    fig.update_layout(
        template=pio.templates['simple_white'],
        dragmode=False,
        barmode='stack',  # important : pour affichage empilé
        title=title,
        xaxis_title='Year',
        yaxis_title='',
        legend_title='Accident Type'
    )

    return fig


def draw(fig, data, mode, time_col='AN', type_col='GRAVITE'):
    '''
    Dessine le graphique à barres empilées selon le mode choisi.

    Args:
        fig (go.Figure): Figure Plotly à compléter
        data (pd.DataFrame): Données contenant au moins 'temps' et 'type_accident'
        mode (str): 'count' ou 'percent'
    
    Returns:
        go.Figure: Figure avec les traces ajoutées
    '''

    # Palette de couleurs fixe
    COLOR_PALETTE = {
        'Fatal or Serious': "#ea5646",
        'Minor': "#a02c3b",
        'Property Damage Only': "#d65e27",
        'Below Reporting Threshold': "#b43d1f"
    }

    # Ordre souhaité pour les types d’accident
    ordered_types = ['Fatal or Serious', 'Minor', 'Property Damage Only', 'Below Reporting Threshold']

    # Réinitialiser la figure
    fig = go.Figure(fig)
    fig.data = []

    # Compter les accidents par temps et type
    grouped = get_counts_by_type_and_time(data, time_col=time_col, type_col=type_col)

    # Calcul du mode (valeurs absolues ou pourcentages)
    if mode == 'percent':
        total_per_time = grouped.groupby(time_col)['count'].transform('sum')
        grouped['value'] = 100 * grouped['count'] / total_per_time
    else:
        grouped['value'] = grouped['count']

    # Ajout des barres par type
    for t in ordered_types:
        subset = grouped[grouped[type_col] == t]
        if not subset.empty:
            fig.add_bar(
                x=subset[time_col],
                y=subset['value'],
                name=t,
                marker_color=COLOR_PALETTE.get(t, '#999999')  # gris par défaut
            )

    # Configuration finale
    fig.update_layout(
        barmode='stack',
        xaxis_title='Time',
        yaxis_title='Accident Frequency' if mode == 'count' else 'Accidents (%)',
        legend_title='Accident Type'
    )

    return fig
