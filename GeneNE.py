#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 16:58:36 2021

@author: laurenkirsch

"""

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.io as pio
pio.templates.default = "plotly_dark"

try:
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
        server = app.server
    
    
        app.layout = html.Div([
        html.H2('Gene-NE'),
        html.H6('Created by Lauren Kirsch and Dr. Chiquito Crasto'),
            html.Label('Search Box'),
        dcc.Input(id="search_gene", 
                  type="text",
                  value = '',
                  placeholder="Type a human gene name",
                  debounce = True,
                  minLength = 0, maxLength = 50,
                  autoComplete='on',
                  size='40'),
        html.Div([
            dcc.Graph(id='mygraph')]), 
        dcc.RadioItems(
                id="vertical_display_toggle",
                options=[
                        {'label': 'Show vertical date bars', 'value': 'show'},
                        {'label': 'Remove vertical bars', 'value': 'hide'},
                        ],
                value='hide', #first loading value selected
                labelStyle={'display': 'inline-block'}
                        ),
        dcc.RadioItems(
                id="synonym_display_toggle",
                options=[
                        {'label': 'Show synonyms', 'value': 'show'},
                        {'label': 'Remove synonyms', 'value': 'hide'},
                        ],
                value='hide', #first loading value selected
                labelStyle={'display': 'inline-block'}
                        ),
        html.Br(),
        html.Div([
            html.A('Click for PubMedIDs', id="outlink", href='/')
                ]),
        html.Br(),
        html.H6('Texas Tech University Center for Biotechnology and Genomics')
        ])           
                              
        @app.callback(
                Output('mygraph', 'figure'),
                [Input('search_gene', 'value'),
                Input('vertical_display_toggle', 'value'),
                Input('synonym_display_toggle', 'value')])
        def update_output(search_gene, vertical_display_user_slct, synonym_display_user_slct):
            df = pd.read_csv('list_out.txt', sep = '\t', dtype=str)
            df = df.transpose().reset_index().rename(columns={'index':'Date'})
            new_header = df.iloc[0] 
            df = df[1:] 
            df.columns = new_header
            df = df.iloc[0:600]
            df = df.set_index('Date')
            df = df.iloc[:, ~df.columns.duplicated()]

            
            lookup_df = pd.read_csv('Gene_Lookup.csv', dtype = str)
            link = lookup_df.set_index('Approved_Symbol').Linked_Genes.str.split('|').to_dict()
            link_date = lookup_df.set_index('Approved_Symbol').Date_Name_Changed.to_dict()
            
            if search_gene:
                search_gene = (search_gene).upper()
                syns = link[search_gene]
                
                trace1 = go.Scatter(x=df.index, 
                                    y = df[search_gene], 
                                    line_shape='linear', 
                                    line = dict(color='white'), 
                                    name = search_gene)
                fig = go.Figure()
                fig.add_trace(trace1)
                
                if synonym_display_user_slct == "show":
                    for i in syns:
                        try:
                            fig.add_trace(go.Scatter(x=df.index, 
                            y = df[i], 
                            line_shape='linear', 
                            name = i))
                        except:
                            pass
                
                fig.update_layout(xaxis_title="Date", yaxis_title="Count")
                genes = link[search_gene]
                genes.append(search_gene)
                df_date= df[syns]
                date = link_date[search_gene]
                d_max = df_date.applymap(int).values.max()
                graph_max = d_max + 10
                
                if vertical_display_user_slct == "show":
                    fig.add_shape(type="line", name = 'Date Human Genome Sequenced',
                              x0='2003-4', y0= 0, x1='2003-4', y1=graph_max,
                              line=dict(color="lightblue",width=3))
                    fig.add_trace(go.Scatter(
                            x=['2003-4'],y=[d_max], name = 'Genome Publication',
                            mode="markers+text",
                            text=["Date Human Genome Published"], textposition = 'top left', line = dict(color='lightblue')))
                    fig.add_shape(type="line", name = 'Date Name Changed',
                              x0=date, y0=0, x1=date, y1=graph_max,
                              line=dict(color="blue",width=3))
                    fig.add_trace(go.Scatter(
                            x=[date],y=[d_max], name = 'Symbol Standardiztion',
                            mode="markers+text",
                            text=["Date Gene Name Changed"], textposition = 'top left', line = dict(color='blue')))
                    
            elif search_gene is None or len(search_gene) == 0:
                default_gene = df['BRCA2']
                default_syns = link[default_gene]
                df1 = default_gene + default_syns
                fig = px.line(df1, x=df1.index, y=df1.columns)
                fig.update_layout(title="Human Gene Name Occurances Per Month", xaxis_title="Date", yaxis_title="Count", height = 600)
                if vertical_display_user_slct == "show":
                    fig.add_shape(type="line", name = 'Date Name Standardized',
                              x0='2016-5', y0= '-10', x1='2016-5', y1=100,
                              line=dict(color="darkblue",width=3))
                    fig.add_shape(type="line", name = 'Date Human Genome Sequenced',
                              x0='2003-4', y0= '-10', x1='2003-4', y1=100,
                              line=dict(color="lightblue",width=3))
                
            return fig
        
        @app.callback(Output('outlink', 'children'),
                  Input('search_gene', 'value'))
        def link_up(search_gene):
            if len(search_gene) != 0:
                return (html.A('PubMed IDs', href='/assets/'+search_gene+'.html', target="_blank"))
                
                
        if __name__ == '__main__':
            app.run_server(debug=True)

except:
    pass
