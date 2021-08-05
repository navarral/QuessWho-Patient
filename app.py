
from PIL import Image
import base64
from io import BytesIO as _BytesIO
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import random
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from flask import Flask
import requests

# Import images for the app
pil_img_colour = Image.open('GuessWho_Grid.jpg')
pil_img_grey = Image.open('GuessWho_Grid_Grey.jpg')
pil_img_doctor = Image.open(requests.get('https://raw.githubusercontent.com/navarral/QuessWho-Patient/master/DrData.png', stream=True).raw)



def pil_to_b64(im, enc_format='png', **kwargs):
    """
    Converts a PIL Image into base64 string for HTML displaying
    :param im: PIL Image object
    :param enc_format: The image format for displaying. If saved the image will have that extension.
    :return: base64 encoding
    """

    buff = _BytesIO()
    im.save(buff, format=enc_format, **kwargs)
    encoded = base64.b64encode(buff.getvalue()).decode("utf-8")

    return encoded


introCard = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5('How to play the game?', className="card-title"),
                    dcc.Markdown('''
                    Dr. Data is a researcher in scientific data who needs help finding a patient with a rare 
                    disease. The doctor has a group of 20 patients but she can only have access to certain information 
                    because the patients identity needs to remain secret.           
                    ''',
                                 className="card-text",
                                 ),
                    dbc.Button("Let's start!", color='primary', id='startButton'),
                    # Store random patient selection
                    dcc.Store(id='rndPatients')
                ]
            )
        ),
        dbc.Card(
            dbc.CardImg(id='intro_doctor', className='align-self-center',  # align-self-center
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '90%', 'width': '90%'},
                        ),
            # className="bg-primary",
            style={'maxWidth': '50%',
                   'maxHeight': '90%'},
        ),
    ],
    className='mt-3',
)

ackCard = dbc.Card([
    dbc.CardBody(
        [
            # html.H4('Collaborators', className='card-title'),
            dcc.Markdown('''
            This research was conducted with the financial support of [HELICAL](https://helical-itn.eu/) as part of the European Union’s 
            Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie Grant Agreement 
            No. 813545 at the [ADAPT Centre for Digital Content Technology](https://www.adaptcentre.ie/) (grant number 13/RC/2106 P2) at 
            Trinity College Dublin, collaborating with the [European Institute for Innovation through Health Data (i~HD)](https://www.i-hd.eu/). | 
            Contact: albert.navarro@adaptcentre.ie'
            ''', style={'font-size': '14px'},
                         className='card-text',
                         ),
            html.Div(style={'margin-bottom': '-1em'})
        ]
    ),
],
    className='mt-3')

introTab = html.Div([
    dbc.Row(
        [
            dbc.Col(width=3),
            dbc.Col(introCard, width=6),
            dbc.Col(width=3),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(width=1),
            dbc.Col(ackCard, width=10),
            dbc.Col(width=1),
        ]
    )

])

nodes = [
    {
        'data': {'id': short},
        'position': {'x': nx, 'y': ny}
    }
    for short, nx, ny in (
        # First row
        ('a11', 63, 80),
        ('a12', 63 + 119 * 1, 80),
        ('a13', 63 + 119 * 2, 80),
        ('a14', 63 + 119 * 3, 80),
        ('a15', 63 + 119 * 4, 80),
        # Second row
        ('a21', 63, 80 + 134 * 1),
        ('a22', 63 + 119 * 1, 80 + 134 * 1),
        ('a23', 63 + 119 * 2, 80 + 134 * 1),
        ('a24', 63 + 119 * 3, 80 + 134 * 1),
        ('a25', 63 + 119 * 4, 80 + 134 * 1),
        # Third row
        ('a31', 63, 80 + 134 * 2),
        ('a32', 63 + 119 * 1, 80 + 134 * 2),
        ('a33', 63 + 119 * 2, 80 + 134 * 2),
        ('a34', 63 + 119 * 3, 80 + 134 * 2),
        ('a35', 63 + 119 * 4, 80 + 134 * 2),
        # Forth row
        ('a41', 63, 80 + 134 * 3),
        ('a42', 63 + 119 * 1, 80 + 134 * 3),
        ('a43', 63 + 119 * 2, 80 + 134 * 3),
        ('a44', 63 + 119 * 3, 80 + 134 * 3),
        ('a45', 63 + 119 * 4, 80 + 134 * 3),
    )
]

# Country possibilities
countryColour = ['Blue', 'Yellow', 'Green', 'Pink']
# Select only adults
nodesIDsMatrix = {'Blue': ['a12', 'a13', 'a14', 'a15'],
                  'Yellow': ['a22', 'a23', 'a24', 'a25'],
                  'Green': ['a32', 'a33', 'a34', 'a35'],
                  'Pink': ['a42', 'a43', 'a44', 'a45']}
'''
# Randomly select country and patient for Grey view
rndCountry_Grey = random.choice(countryColour)
rightPatient_Grey = random.choice(nodesIDsMatrix[rndCountry_Grey])

# Randomly select country and patient for Colour view
rndCountry_Colour = random.choice(countryColour)
rightPatient_Colour = random.choice(nodesIDsMatrix[rndCountry_Colour])

print('grey:', rightPatient_Grey)
print('colour:', rightPatient_Colour)
'''
node_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)',
            'width': '115%',
            'height': '115%',
            'opacity': '0.01',
        }
    }
]

graphConfigDict = {
    # 'displayModeBar': False,
    'doubleClick': False,
    'editable': False,
    'scrollZoom': False,
    # 'staticPlot': True,
}

frCard_Grid = dbc.Card(
    dbc.CardBody(
        [
            html.Div([
                cyto.Cytoscape(
                    id='cyto_grey',
                    elements=nodes,
                    autoungrabify=False,
                    autolock=True,
                    zoom=1,
                    minZoom=1,
                    maxZoom=1,
                    panningEnabled=False,
                    stylesheet=node_stylesheet,
                ),
            ], style={
                'background-image': 'url(https://raw.githubusercontent.com/navarral/QuessWho-Patient/master/GuessWho_Grid_Grey.jpg)',
                'background-size': '600px 550px',
                'background-repeat': 'no-repeat',
                # 'marginBottom': '-5em'
            }, ),
        ]
    ),
    className='mt-3',
)

frCard_Doctor = dbc.Card(
    dbc.CardBody(
        [
            html.H4('Can you help Dr. Data find the patient?', className='card-title'),
            dcc.Markdown(id='hintGrey',
                         className="card-text",
                         ),
            dbc.CardImg(id='grey_doctor', className='image',
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '50%', 'width': '60%'},
                        bottom=True),
            dcc.ConfirmDialog(
                id='wrongChoiceGrey',
                message='Please try again!',
            ),
            dcc.ConfirmDialog(
                id='rightChoiceGrey',
                message="Yes, that's the patient! Thanks for your help!",
            ),
            dbc.Button('Next Round', color='primary', disabled=True,
                       id='nextRound'),
        ]
    ),

    className='mt-3',
)

firstRoundTab = dbc.Row(
    [
        dbc.Col(width=1),
        dbc.Col(frCard_Grid, width=7),
        dbc.Col(frCard_Doctor, width=3),
        dbc.Col(width=1),
    ]
)

srCard_Grid = dbc.Card(
    dbc.CardBody(
        [
            html.Div([
                cyto.Cytoscape(
                    id='cyto_colour',
                    elements=nodes,
                    autoungrabify=False,
                    autolock=True,
                    zoom=1,
                    minZoom=1,
                    maxZoom=1,
                    panningEnabled=False,
                    stylesheet=node_stylesheet,
                ),
            ], style={
                'background-image': 'url(https://raw.githubusercontent.com/navarral/QuessWho-Patient/master/GuessWho_Grid.jpg)',
                'background-size': '600px 550px',
                'background-repeat': 'no-repeat',
                # 'marginBottom': '-5em'
            }, ),
        ]
    ),
    className='mt-3',
)

srCard_Doctor = dbc.Card(
    dbc.CardBody(
        [
            html.H4('Can you help Dr. Data find the patient?', className='card-title'),
            dcc.Markdown(id='hintColour',
                         className="card-text",
                         ),
            dbc.CardImg(id='colour_doctor', className='image',
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '50%', 'width': '60%'},
                        bottom=True),
            dcc.ConfirmDialog(
                id='wrongChoiceColour',
                message='Please try again!',
            ),
            dcc.ConfirmDialog(
                id='rightChoiceColour',
                message="Yes, that's the patient! Thanks for your help!",
            ),
            dbc.Button('Conclusion', color='primary', disabled=True,
                       id='concButton'),
        ]
    ),

    className='mt-3',
)

secondRoundTab = dbc.Row(
    [
        dbc.Col(width=1),
        dbc.Col(srCard_Grid, width=7),
        dbc.Col(srCard_Doctor, width=3),
        dbc.Col(width=1),
    ]
)

concCard = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5('What have we learnt by helping Dr. Data?', className="card-title"),
                    dcc.Markdown('''
                    Today we learnt that people diagnosed with a rare disease are at an increased
                    risk of identification from research data because linking of a couple of factors may expose
                    the patient's identity. However, if the adequate data protection regulations are applied
                    researchers can conduct their research safely.         
                    ''',
                                 className="card-text",
                                 ),
                    html.A(dbc.Button('Play again!', color='primary'), href='/'),
                ]
            )
        ),
        dbc.Card(
            dbc.CardImg(id='conclusion_doctor', className='align-self-center',  # align-self-center
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '90%', 'width': '90%'},
                        ),
            # className="bg-primary",
            style={'maxWidth': '50%',
                   'maxHeight': '90%'},
        ),
    ],
    className='mt-3',
)

conclusionTab = html.Div([
    dbc.Row(
        [
            dbc.Col(width=3),
            dbc.Col(concCard, width=6),
            dbc.Col(width=3),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(width=1),
            dbc.Col(ackCard, width=10),
            dbc.Col(width=1),
        ]
    )

])

tabs = dbc.Tabs(
    [
        dbc.Tab(introTab, label='Introduction'),
        dbc.Tab(firstRoundTab, label='Round 1', disabled=True),
        dbc.Tab(secondRoundTab, label='Round 2', disabled=True),
        dbc.Tab(conclusionTab, label='Conclusion', disabled=True),
    ], id='tabsID', active_tab='tab-0',
)

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
#server = Flask(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = 'Guess the patient'
app.layout = html.Div([tabs])



@app.callback([Output('rndPatients', 'data'),
               Output('hintGrey','children'),
               Output('hintColour','children')],
              [Input('startButton', 'n_clicks')],
              )
def chooseRndCountryPatient(n_clicks_start):
    if n_clicks_start != 1:
        raise PreventUpdate
    else:
        # Randomly select country and patient for Grey view
        rndCountry_Grey = random.choice(countryColour)
        rightPatient_Grey = random.choice(nodesIDsMatrix[rndCountry_Grey])

        # Randomly select country and patient for Colour view
        rndCountry_Colour = random.choice(countryColour)
        rightPatient_Colour = random.choice(nodesIDsMatrix[rndCountry_Colour])

        print('grey:', rightPatient_Grey)
        print('colour:', rightPatient_Colour)
        # Store country and patient choice in a dict that will refresh as the page is refreshed
        rndDict = {
            'greyC': rndCountry_Grey,
            'greyP': rightPatient_Grey,
            'colourC': rndCountry_Colour,
            'colourP': rightPatient_Colour}

        hintGrey = '''
        Hi! All I know is that the patient is an **adult** that lives in the **''' + rndDict['greyC'] + ''' country** ...

        Please click on the faces on the left and let's how long it takes to find it together!'''

        hintColour = '''
        Hi! All I know is that the patient is an **adult** that lives in the **''' + rndDict['colourC'] + ''' country** ...

        Please click on the faces on the left and let's how long it takes to find it together!'''

        return [rndDict, hintGrey, hintColour]


@app.callback(Output('tabsID', 'active_tab'),
              [Input('startButton', 'n_clicks'),
               Input('nextRound', 'n_clicks'),
               Input('concButton', 'n_clicks')],
              )
def goToRound1Tab(n_clicks_start, n_clicks_round1, n_clicks_round2):
    if not n_clicks_start:
        raise PreventUpdate
    if n_clicks_start and not n_clicks_round1 and not n_clicks_round2:
        return 'tab-1'
    if n_clicks_start and n_clicks_round1 and not n_clicks_round2:
        return 'tab-2'
    if n_clicks_start and n_clicks_round1 and n_clicks_round2:
        return 'tab-3'


@app.callback([Output('wrongChoiceGrey', 'displayed'),
               Output('rightChoiceGrey', 'displayed')],
              [Input('cyto_grey', 'tapNodeData'),
               Input('rndPatients', 'data')])
def guessGreyPatient(nodeID_label, rndChoice):
    if not rndChoice:
        raise PreventUpdate
    else:
        if not nodeID_label:
            raise PreventUpdate
        if nodeID_label['id'] != rndChoice['greyP']:
            return [True, False]
        if nodeID_label['id'] == rndChoice['greyP']:
            return [False, True]


@app.callback([Output('nextRound', 'disabled')],
              [Input('rightChoiceGrey', 'submit_n_clicks'),
               Input('rightChoiceGrey', 'cancel_n_clicks')])
def nextRoundButtonClick(rightAnswer_Ok, rightAnswer_Cancel):
    if not rightAnswer_Ok and not rightAnswer_Cancel:
        return [True]
    else:
        return [False]


@app.callback([Output('wrongChoiceColour', 'displayed'),
               Output('rightChoiceColour', 'displayed')],
              [Input('cyto_colour', 'tapNodeData'),
               Input('rndPatients', 'data')])
def guessGreyPatient(nodeID_label, rndChoice):
    if not rndChoice:
        raise PreventUpdate
    else:
        if not nodeID_label:
            raise PreventUpdate
        if nodeID_label['id'] != rndChoice['colourP']:
            return [True, False]
        if nodeID_label['id'] == rndChoice['colourP']:
            return [False, True]


@app.callback([Output('concButton', 'disabled')],
              [Input('rightChoiceColour', 'submit_n_clicks'),
               Input('rightChoiceColour', 'cancel_n_clicks')])
def nextRoundButtonClick(rightAnswer_Ok, rightAnswer_Cancel):
    if not rightAnswer_Ok and not rightAnswer_Cancel:
        return [True]
    else:
        return [False]


if __name__ == '__main__':
    app.run_server(debug=False)
