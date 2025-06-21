import plotly.graph_objects as go
import plotly.io as pio

import pandas as pd
from template import COLOR_PALETTE,GRAVITY_TRANSLATION




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


    # Traduire les types d'accidents
    df[type_col] = df[type_col].map(GRAVITY_TRANSLATION)

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

    fig.update_layout(
        template=pio.templates['simple_white'],
        dragmode=False,
        barmode='stack',
        title=title,
        xaxis_title='Year',
        yaxis_title='',
        legend_title='Accident Type'
    )

    return fig



def get_aggregated_counts(df, granularity='year', type_col='GRAVITE'):
    df = df.copy()
    df[type_col] = df[type_col].map(GRAVITY_TRANSLATION)

    if granularity == 'year':
        df['time_unit'] = df['AN'].astype(str)
    elif granularity == 'month':
        df['time_unit'] = df['AN'].astype(str) + '-' + df['MS_ACCDN'].astype(str).str.zfill(2)
    elif granularity == 'daytype':
        df['time_unit'] = df['JR_SEMN_ACCDN']
    elif granularity == 'quarter_day':
        df['time_unit'] = df['HR_ACCDN']
    else:
        df['time_unit'] = df['AN'].astype(str)

    grouped = df.groupby(['time_unit', type_col]).size().reset_index(name='count')
    return grouped

def draw(fig, data, mode, type_col='GRAVITE', granularity='year'):


    ordered_types = ['Severe', 'Minors', 'Materials damage', 'Low damage']

    fig = go.Figure(fig)
    fig.data = []

    grouped = get_aggregated_counts(data, granularity=granularity, type_col=type_col)
    grouped[type_col] = grouped[type_col].replace(GRAVITY_TRANSLATION)

    if mode == 'percent':
        total_per_time = grouped.groupby('time_unit')['count'].transform('sum')
        grouped['value'] = 100 * grouped['count'] / total_per_time
    else:
        grouped['value'] = grouped['count']

    for t in ordered_types:
        subset = grouped[grouped[type_col] == t]
        if not subset.empty:
            fig.add_bar(
                x=subset['time_unit'],
                y=subset['value'],
                name=t,
                marker_color=COLOR_PALETTE.get(t, '#999999')
            )

    fig.update_layout(
        barmode='stack',
        xaxis_title='',
        yaxis_title='Accident Frequency' if mode == 'count' else 'Accidents (%)',
        legend_title='Accident Type'
    )

    return fig
