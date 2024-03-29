import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
#import psycopg2 as pg

######  Define PostgreSQL connection
#conn = pg.connect(
#    database="postgres",
#    user="postgres",
#    password="pg_p@ss",
#    host="localhost",
#    port="5432")

###### Define DataFrame by reading in data from PostgreSQL
#df = pd.read_sql_query(
#    f"""
#    SELECT article_id, outlet_name, tag_name, provider, provider_value, zip_code
#    FROM airbus_bhqlite_excerpt
#    """,
#    con=conn)

###### Define DataFrame by reading in CSV created from PostgreSQL data
df = pd.read_csv('airbus_bhqlite_excerpt.csv')
df = df.drop('Unnamed: 0', axis=1)

###### Create parent_tag and child_tag columns from tag_name column
df['parent_tag'] = df['tag_name'].str.split(':').str.get(0)
df['child_tag'] = df['tag_name'].str.split(':').str.get(1)

###### Remove unnecessary rows
indexNames = df[(df['provider'] == 'Majestic') |
                (df['provider'] == 'GnipTwitter:Retro') |
                (df['provider'] == 'LinkedIn') |
                (df['provider'] == 'Facebook:comments')].index
df.drop(indexNames, inplace=True)

##### Define variables
parent_tag_list=['Airbus', 'Boeing']
child_tag_list = ['Aircraft Production', 'Corporate', 'Financial Perf.', 'Safety', 'Government Relations', 'Technology']
title='Aerospace Media Coverage: 2016'
tabtitle='PublicRelay'
githublink='https://github.com/aidanjdm/airbus'

##### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

##### Set up the layout
app.layout = html.Div(children=[
    html.H2(title),
    html.Div('Select Company:'),
    html.Div([
        html.Div([dcc.Dropdown(id='parent-dropdown',
                                options= [{'label':i, 'value':i} for i in parent_tag_list],
                                value=parent_tag_list[0])
        ], className='three columns')
    ], className='twelve columns'),
    html.Br(),
    html.Br(),
    html.Div('Select Topic:'),
    html.Div([
        html.Div([dcc.Dropdown(id='child-dropdown',
                                options= [{'label':i, 'value':i} for i in child_tag_list],
                                value=child_tag_list[0])
        ], className='three columns')
    ], className='twelve columns'),
    html.Br(),
    html.Br(),
    dcc.Graph(id='output-div'),
    html.A('Code on Github', href=githublink),
    ]
)

###### Define callback
@app.callback(dash.dependencies.Output('output-div', 'figure'),
                [dash.dependencies.Input('parent-dropdown', 'value'), dash.dependencies.Input('child-dropdown', 'value')])
def getChart(parent, child):
    ##### Define filtered DataFrame and create outlet volume, sharing, and reach DataFrame from filtered DataFrame
    df_filtered = df[df['tag_name'] == f'{parent}:{child}']
    df_outlet_volume = df_filtered.groupby('outlet_name')[['article_id']].nunique().reset_index()
    df_outlet_sharing = df_filtered.groupby(['outlet_name', 'article_id', 'provider'])[['provider_value']].min().reset_index()
    df_outlet_sharing_totals = df_outlet_sharing.groupby('outlet_name')[['provider_value']].sum().reset_index()
    df_outlet_merged = pd.merge(df_outlet_volume, df_outlet_sharing_totals, how='left', on='outlet_name')
    df_outlet_reach = df_filtered.groupby('outlet_name')[['reach_circulation']].min().reset_index()
    df_outlet_merged = pd.merge(df_outlet_merged, df_outlet_reach, how='left', on='outlet_name')
    df_outlet_merged = df_outlet_merged.fillna(0)

    ##### Create trace and define layout referencing df_outlet_merged
    trace = go.Scatter(
        x = df_outlet_merged['article_id'],
        y = df_outlet_merged['provider_value'],
        hovertext = df_outlet_merged['outlet_name'],
        hoverinfo = 'text+x+y',
        mode = 'markers',
        marker=dict(
            size=(df_outlet_merged['reach_circulation']/1000000),
            color = df_outlet_merged['reach_circulation'],
            colorscale="Blues",
            opacity=0.5,
            showscale=True
            )
        )

    data = [trace]
    layout = go.Layout(
        title = f'Outlets covering {parent} {child} by Article Volume, Social Sharing, and Reach',
        xaxis = dict(title = 'Article Volume'),
        yaxis = dict(title = 'Social Shares'),
        hovermode = 'closest'
        )
    fig = go.Figure(data=data, layout=layout)
    return fig

##### Deploy the app
if __name__ == '__main__':
    app.run_server()
