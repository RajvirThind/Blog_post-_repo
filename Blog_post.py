import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import math
import dash_bootstrap_components as dbc



# -------------------------------------------------------------------------------------
# Import the data 
df = px.data.tips()



app = dash.Dash(__name__) 





app.layout = dbc.Container([
    html.H1("Tips Visualisation App", style={'font-size':'30px', 'font-family':'sans-serif',"background-color":"green", "padding":"20px", "color":"white"}),

        dbc.Row([

            dbc.Col(dcc.Graph(id='scatter-chart'),style={'box-shadow': '4px 4px 4px #888888'}, md=12), #scatter chart
            
        ]),

    html.Br(),

        dbc.Row([

            dbc.Col(
                html.Div([
                    dash_table.DataTable( #datatable
                    id='datatable',
                    
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": True, "hideable": True}
                        for i in df.columns
                    ],
                    
                    data=df.to_dict('records'),  # the contents of the table
                    editable=True,              # allow editing of data inside all cell
                    row_selectable="multi",     # allow users to select 'multi' or 'single' rows
                    style_header={
                        'backgroundColor': 'green',
                        'color': 'white'
                        },
                    style_as_list_view=True,
                    fixed_rows={'headers': True},
                    export_format="xlsx",
                    style_cell={                
                        'minWidth': 95, 'maxWidth': 95, 'width': 95,
                        'fontSize':10, 'font-family':'sans-serif','padding': '5px'
                    },
                    )
                    ]),  md=12)


                ])

 
])

# -------------------------------------------------------------------------------------
# Create scatter chart
@app.callback(
    Output(component_id="scatter-chart",component_property= 'figure'),
    [Input(component_id='datatable', component_property="derived_virtual_data"),
     Input(component_id='datatable', component_property='derived_virtual_selected_rows')]
)
def update_scatter_chart(all_rows_data, slctd_row_indices):
    dff = pd.DataFrame(all_rows_data)



    # used to highlight selected countries on bar chart, both size and color changes
    colors = ['#00FF00' if i in slctd_row_indices else '#5A5A5A'
              for i in range(len(dff))]

    def SetSymbol (i):
        if i == "Female":
            return "circle-dot"
        elif i == "Male":
            return "x"
        else:
            return "x"



    #--------------------------------------------------------
    #calculating regression line and RMSE metrics

    female_df = dff[dff['sex']=="Female"]
    male_df = dff[dff['sex']=="Male"]

    X = female_df.total_bill.values.reshape(-1,1)
    y = female_df.tip.values

    model= LinearRegression()

    model.fit(X, y)

    x_range = np.linspace(X.min(), X.max(), len(y))
    y_range = (model.predict(x_range.reshape(-1,1)))

    mse = np.square(np.subtract(y, y_range)).mean() 
    rmse = math.sqrt(mse)




    figure=px.scatter(data_frame=dff,
                          x="total_bill",
                          y='tip'
                          

                          
                          
                      )
    figure.update_traces(marker={"symbol":list(map(SetSymbol, dff['sex'])), "color":colors} )
    figure.add_traces(go.Scatter(x=x_range, y=y_range, name="y={0:.2f}x^{1:.4f}".format(model.intercept_, model.coef_[0]), line=dict(color='green')))
    figure.add_traces(go.Scatter(x=x_range, y=y_range-rmse, line=dict(color='green', dash='dash'), showlegend=False))
    figure.add_traces(go.Scatter(x=x_range, y=y_range+rmse, line=dict(color='green', dash='dash'), name="RMSE={0:.5f}".format(rmse)))
    figure.update_layout(plot_bgcolor='whitesmoke')
    figure.update_layout(legend=dict(x=0.60,y=.9,traceorder="normal",font=dict(family="sans-serif",size=12,color="black")))
    figure.update_xaxes(showgrid=True, gridwidth=1, gridcolor='whitesmoke', rangemode='tozero',showline=True )
    figure.update_yaxes(showgrid=True, gridwidth=1, gridcolor='whitesmoke', rangemode='tozero')

    return figure
                      

if __name__ == '__main__':
    app.run_server(debug=True)
    