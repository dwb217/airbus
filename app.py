import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import psycopg2 as pg

###########  Define PostgreSQL connection
conn = pg.connect(
    database="airbus",
    user="tableau",
    password="d3f@ulT_9G_p@ss",
    host="dbgw.publicrelay.com",
    port="5432")

########### Define article volume function
def volume(tag):
    return pd.read_sql_query(
    f"""
    SELECT COUNT (DISTINCT article_id)
    FROM bhqlite
    WHERE intake_date >= '12/31/2015'
    AND intake_date <= '1/1/2017'
    AND is_primary = True
    AND tag_name = '{tag}'
    """,
    con=conn)['count'][0]

########### Define variables
tags=['Airbus', 'Boeing', 'Bombardier', 'Embraer']
volumes=[volume(tag) for tag in tags]
color='#303f9f'
title='Article Volume by Company'
tabtitle='PublicRelay'
myheading= 'Airbus Competitors'
label='Volume'

########### Set up the chart
article_volume = go.Bar(
    x=tags,
    y=volumes,
    name=label,
    marker={'color':color}
)

data = article_volume
layout = go.Layout(
    barmode='group',
    title = title
)

fig = go.Figure(data=data, layout=layout)


########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),
    dcc.Graph(
        id='Airbus',
        figure=fig
    ),
    ]
)

if __name__ == '__main__':
    app.run_server()
