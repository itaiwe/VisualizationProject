import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dash import Dash,dcc,html,ctx
from dash.dependencies import Input,Output,State

df = pd.read_csv("data/run_df_23_6.csv")

button_flag = ""
min_date = df[df["date"] == min(df["date"])][["year", "month", "day"]][:1]
max_date = df[df["date"] == max(df["date"])][["year", "month", "day"]][:1]

min_date_date = date(int(min_date["year"]), int(min_date["month"]), int(min_date["day"]))
max_date_date = date(int(max_date["year"]), int(max_date["month"]), int(max_date["day"]))

app = Dash(__name__)
app.layout = html.Div([
                html.Div(id="text_and_pics", children=[
                    html.Div(id="text", children=[html.H1("Police shootings on civilians in the USA"),
                    html.P(["You can change start date and end date from the date picker right below, or just change years with the slider.",\
                        html.Br(), "Here's a tip, enter year in YY format in end range to set the picker to that year."])
                        ], style={"width":"50%", "float":"left", "anchor":"top",'display': 'inline-block', "font-size": 16}),
                    html.Div(id="pics", children=[
                            html.Img(src=app.get_asset_url('blm-protest.jpg'), style={'float':'right', 'anchor':'top', 'display': 'inline-block', "width": "40%", "height": "40%"}),
                            html.Img(src=app.get_asset_url('police.jpg'), style={'display': 'inline-block', "width": "60%","object-fit":"scale-down", "anchor":"top"})
                        ],
                        style={"width":"50%", "float":"right", "anchor":"top",'display': 'inline-block',"position":"relative"})
                ]),
                html.Div(id="else", children=[
                    dcc.DatePickerRange(
                         id="Picker-Range",
                         min_date_allowed=min_date_date,
                         max_date_allowed=max_date_date,
                         initial_visible_month=max_date_date,
                         start_date=min_date_date,
                         end_date=max_date_date,
                         display_format='MMM Do, YY'
                    ),
                    dcc.RangeSlider(
                        min=int(min_date["year"]),
                        max=int(max_date["year"]),
                        id='range-slider',
                        value=[int(min_date["year"]), int(max_date["year"])],
                        marks={str(i): f"{i}" for i in df["year"].unique()},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": False},
                        allowCross=False
                    ),
                    html.Button('reset', id='reset_to_default', n_clicks=0),
                    html.P(["The year button gives us the amount of deaths according to each year selected earlier in the range slider \
                        the date picker.",
                        html.Br(),
                        "If you change the date difference between the start and end dates to less or equal to 36 months, you can also \
                             see the amounts per month.",
                             html.Br(),
                             "If you change the date difference to less or equal to 12 months, you can also see the amounts per day."], style={"font-size": 16}),
                    html.Div(id="bar_buttons", children=[
                        html.Button('year', id='show_year', n_clicks=0),
                        html.Button('month', id='show_month', n_clicks=0, disabled=True),
                        html.Button('day', id='show_day', n_clicks=0, disabled=True)
                    ]),
                    dcc.Checklist(
                        id="check_gender",
                        options=[
                            {"label": "Male", "value": "M"},
                            {"label": "Female", "value": "F"}],
                        value=list(df["gender"].unique()),
                        inline=True
                    ),
                    html.Div(dcc.Graph(id='amount-shoot-or-taser')),
                    html.P("You can click on a specific race on the pie chart to change all other graphs to show only that race.", style={"font-size": 16}),
                    html.Div(id="map_and_pie", children=[
                            dcc.Graph(id="map-shoot-or-taser", style={'display': 'inline-block', "width": "50%"}),
                            dcc.Graph(id="pie-race-by-date", style={'display': 'inline-block', "width": "50%"})
                        ]),
                    html.P("This slider affects the minimum number of incidents per state, so that only states with at least that \
                        amount will be shown in the map.", style={"font-size": 16}),
                    dcc.Slider(
                        min=0,
                        max=max(dict(df["state"].value_counts()).values()),
                        id='range_slider_kiling_amount',
                        value=0,
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Button('clear', id='clear_break_down', n_clicks=0),
                    html.Button('all', id='all_break_down', n_clicks=0),
                    html.P("Finally, this break down gives the option to choose what states you want to see shown on the map.", style={"font-size": 16}),
                    dcc.Dropdown(
                        id="break_down",
                        options=list(df["state"].unique()),
                        value=list(df["state"].unique()),
                        multi=True)
                ], style={"clear": "left", "anchor": "bottom"})
            ])

@app.callback(
    Output('amount-shoot-or-taser', 'figure'),
    Output('pie-race-by-date', 'figure'),
    Output('map-shoot-or-taser', 'figure'),
    Output('Picker-Range', 'initial_visible_month'),
    Output("range-slider", "value"),
    Output('range_slider_kiling_amount', 'max'),
    Output("show_month", "disabled"),
    Output("show_day", "disabled"),
    Input("pie-race-by-date", 'clickData'),
    Input("break_down", 'value'),
    Input("Picker-Range", 'start_date'),
    Input("Picker-Range", 'end_date'),
    Input("check_gender", "value"),
    Input('show_year', 'n_clicks'),
    Input('show_month', 'n_clicks'),
    Input('show_day', 'n_clicks'))
def main(click, break_value, start_date, end_date, gender, press_y, press_m, press_d):
    global button_flag
    data = df.query(f"date>='{str(start_date)}'").query(f"date<='{str(end_date)}'")
    data = data[data["state"].isin(break_value)]
    gender_data = data[data["gender"].isin(gender)]
    cases = dict(gender_data["race_full"].value_counts())

    if ctx.triggered_id == "pie-race-by-date":
        curr_label = click["points"][0]["label"]
        data = data.query(f"race_full=='{curr_label}'")
    gender_data = data[data["gender"].isin(gender)]

    dont_show_month = True
    dont_show_day = True
    fig_bar = go.Figure()
    fig_pie = go.Figure()
    fig_map = go.Figure()
    maximum = max(dict(df["state"].value_counts()).values())

    if gender_data.empty:
        return [fig_bar, fig_pie, fig_map, end_date, [int(start_date[:4]), int(end_date[:4])], maximum, dont_show_month, dont_show_day]

    maximum = max(dict(data["state"].value_counts()).values())
    curr_min_data = gender_data[gender_data["date"] == min(gender_data["date"])][["year", "month", "day"]][:1]
    curr_max_data = gender_data[gender_data["date"] == max(gender_data["date"])][["year", "month", "day"]][:1]
    curr_min_date = date(int(curr_min_data["year"]), int(curr_min_data["month"]), int(curr_min_data["day"]))
    curr_max_date = date(int(curr_max_data["year"]), int(curr_max_data["month"]), int(curr_max_data["day"]))
    diff_month = (curr_max_date.year - curr_min_date.year) * 12 + (curr_max_date.month - curr_min_date.month)

    if diff_month <= 36:
        dont_show_month = False
    if diff_month <= 12:
        dont_show_day = False


    if ctx.triggered_id in ["show_month", "show_day", "show_year"]:
        button_flag = ctx.triggered_id
    if button_flag == "show_month" and not dont_show_month:
        fig_bar.add_trace(go.Bar(
            x=[f"{y}-{m}" for y, m in sorted(gender_data[["year","month"]].drop_duplicates().to_numpy(), key=lambda x: x[0])],
            y=[i for _, i in sorted(dict(gender_data[["year","month"]].value_counts()).items(), key=lambda x: x[0])],
            name="temp",
            customdata=[date(y,m,1).strftime('%b, %Y') for y, m in sorted(gender_data[["year","month"]].drop_duplicates().to_numpy(), key=lambda x: x[0])],
            marker={"color": "lightgreen"}
          ))        
        fig_bar.update_layout(
            title='Amount of incidents per month',
            title_x=0.5,
            title_xanchor="center",
            xaxis={'title': "Month"},
            yaxis={'title': "Deaths"}
        )
        fig_bar.update_traces(hovertemplate="<br>".join([
            "Month: %{customdata}",
            "Amount of dead: %{y}"
        ]))
        # fig_bar.add_trace(go.Scatter(
        #     x=[f"{y}-{m}" for y, m in sorted(gender_data[["year", "month"]].drop_duplicates().to_numpy(), key=lambda x: x[0])],
        #     y=[i for _, i in sorted(dict(gender_data[["year", "month"]].value_counts()).items(), key=lambda x: x[0])],
        #     mode='lines+markers',
        #     showlegend=False,
        #     hoverinfo="skip"
        # ))

    elif button_flag == "show_day" and not dont_show_day:
        fig_bar.add_trace(go.Bar(
            x=[d for d, _, _, _ in sorted(gender_data[["date", "year", "month", "day"]].drop_duplicates().to_numpy(), key=lambda x: x[0])],
            y=[i for _, i in sorted(dict(gender_data[["year", "month","day"]].value_counts()).items(), key=lambda x: x[0])],
            name="temp",
            marker={"color": "lightgreen"}
          ))
        fig_bar.update_layout(
            title='Amount of incidents per day',
            title_x=0.5,
            title_xanchor="center",
            xaxis={'title': "Day"},
            yaxis={'title': "Deaths"}
        )
        fig_bar.update_traces(hovertemplate="<br>".join([
            "Date: %{x}",
            "Amount of dead: %{y}"
        ]))
        # fig_bar.add_trace(go.Scatter(
        #     x=[d for d, _, _, _ in sorted(gender_data[["date", "year", "month", "day"]].drop_duplicates().to_numpy(), key=lambda x: x[0])],
        #     y=[i for _, i in sorted(dict(gender_data[["year", "month","day"]].value_counts()).items(), key=lambda x: x[0])],
        #     mode='lines+markers',
        #     showlegend=False,
        #     hoverinfo="skip"
        # ))
    else:
        fig_bar.add_trace(go.Bar(
            x=[str(i) for i in sorted(list(gender_data["year"].unique()))],
            y=[i for _, i in sorted(dict(gender_data["year"].value_counts()).items(), key=lambda x: x[0])],
            name="temp",
            marker={"color": "lightgreen"}
          ))
        fig_bar.update_layout(
            title='Amount of incidents per year',
            title_x=0.5,
            title_xanchor="center",
            xaxis={'title': "Year"},
            yaxis={'title': "Deaths"}
        )
        fig_bar.update_traces(hovertemplate="<br>".join([
            "Year: %{x}",
            "Amount of dead: %{y}"
        ]))
        # fig_bar.add_trace(go.Scatter(
        #     x=[str(i) for i in sorted(list(gender_data["year"].unique()))],
        #     y=[i for _,i in sorted(dict(gender_data["year"].value_counts()).items(),key=lambda x: x[0])],
        #     mode='lines+markers',
        #     showlegend=False,
        #     hoverinfo="skip"
        # ))

    if {"M", "F"} != set(gender):
        if "M" in gender:
            fig_bar.update_traces(marker={"color": "blue"})
        elif "F" in gender:
            fig_bar.update_traces(marker={"color": "red"})

    fig_pie.add_trace(go.Pie(labels=list(cases.keys()), values=list(cases.values())))
    fig_pie.update_traces(textinfo='percent+label')
    fig_pie.update_layout(
        title='Percent of shooting incidents by race',
        title_x=0.5,
        title_xanchor="center",
        legend_itemdoubleclick="toggleothers"
    )
    
    if "M" in gender:
        fig_map.add_trace(go.Scattergeo(
            lon=data.query("gender=='M'")["longitude"],
            lat=data.query("gender=='M'")["latitude"],
            mode="markers",
            marker=dict(color="blue",opacity=0.7),
            name="Male",
            customdata=data.query("gender=='M'")[["is_geocoding_exact", "name", "date", "age", "race_full"]],
            showlegend=False
        ))
    if "F" in gender:
        fig_map.add_trace(go.Scattergeo(
            lon=data.query("gender=='F'")["longitude"],
            lat=data.query("gender=='F'")["latitude"],
            mode="markers",
            marker=dict(color="red",opacity=0.7),
            name="Female",
            customdata=data.query("gender=='F'")[["is_geocoding_exact", "name", "date", "age", "race_full"]],
            showlegend=False
        ))
    fig_map.update_traces(hovertemplate="<br>".join([
        "Location: (%{lat}&deg;,%{lon}&deg;)",
        "Exact Location: %{customdata[0]}",
        "Name: %{customdata[1]}",
        "Date: %{customdata[2]}",
        "Age: %{customdata[3]}",
        "Race: %{customdata[4]}"
    ]))
    fig_map.add_trace(go.Choropleth(
        locations=data['state'].unique(), # Spatial coordinates
        z=data["state"].value_counts(), # Data to be color-coded
        locationmode='USA-states', # set of locations match entries in `locations`
        colorscale='Reds',
        hoverinfo='skip',
        colorbar={"title": "Amount of deaths"}
    ))

    fig_map.update_layout(
        title='Police shooting incidents in USA',
        title_x=0.5,
        title_xanchor="center",
        geo_scope='usa',  # limit map scope to USA
        legend_itemdoubleclick="toggleothers"
    )
    
    fig_map.update_coloraxes(
        showscale=True
    )


    return [fig_bar, fig_pie, fig_map, end_date, [int(start_date[:4]), int(end_date[:4])], maximum, dont_show_month, dont_show_day]


@app.callback(
    Output("break_down", 'value'),
    Output("break_down", 'options'),
    Input('range_slider_kiling_amount', 'value'),
    Input('clear_break_down', 'n_clicks'),
    Input('all_break_down', 'n_clicks'),
    Input("reset_to_default", "n_clicks"),
    Input("pie-race-by-date", 'clickData'),
    State("break_down", 'value'),
    State("break_down", 'options'))
def change_country(value, clear, choose_all, reset, click_race, curr_value, all_countries):
    curr_id = ctx.triggered_id
    if curr_id is None:
        return [list(df["state"].unique()), all_countries]
    elif curr_id == 'clear_break_down':
        return [[], all_countries]
    elif curr_id == 'all_break_down':
        return [list(df["state"].unique()), all_countries]
    elif curr_id == 'range_slider_kiling_amount':
        option = [i for i, j in dict(df["state"].value_counts()).items() if j >= value]
        return [curr_value, option]
    elif curr_id == 'reset_to_default':
        return [list(df["state"].unique()), list(df["state"].unique())]
    elif curr_id == 'pie-race-by-date':
        curr_label = click_race["points"][0]["label"]
        data = df.query(f"race_full=='{curr_label}'")
        return [list(data["state"].unique()), all_countries]

@app.callback(
    Output("Picker-Range", "start_date"),
    Output("Picker-Range", "end_date"),
    Input("range-slider", 'value'),
    Input("reset_to_default", "n_clicks"),
    State("Picker-Range", "start_date"),
    State("Picker-Range", "end_date"))
def change_date(values, reset, start_date, end_date):
    if ctx.triggered_id == "reset_to_default":
        return [min_date_date, max_date_date]
    curr_min = str(values[0]) + start_date[4:]
    curr_max = str(values[1]) + end_date[4:]
    if str(min_date_date) >= curr_min:
        curr_min = min_date_date
    if str(max_date_date) <= curr_max:
        curr_max = max_date_date
    return curr_min, curr_max

@app.callback(
    Output("check_gender", "value"),
    Output('range_slider_kiling_amount', 'value'),
    Input("reset_to_default", "n_clicks"))
def reset_(reset):
    return [["M", "F"], 0]

if __name__ == '__main__':
  app.run(debug=False)