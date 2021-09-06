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
pil_img_doctor = Image.open(
    requests.get('https://raw.githubusercontent.com/navarral/QuessWho-Patient/master/DrData.png', stream=True).raw)


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
                    
                    You will have **5** attempts to help Dr. Data in each round      
                    ''',
                                 className="card-text",
                                 ),
                    dbc.Button("Let's start!", color='primary', id='startButton'),
                    # Store random patient selection on every page refresh
                    dcc.Store(id='rndPatients'),
                    # Store total number of participants
                    dcc.Store(id='appInfo', storage_type='local'),
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
            dcc.Markdown('''
            This research was conducted with the financial support of [HELICAL](https://helical-itn.eu/) as part of the European Union’s 
            Horizon 2020 research and innovation programme under the Marie Sklodowska-Curie Grant Agreement 
            No. 813545 at the [ADAPT Centre for Digital Content Technology](https://www.adaptcentre.ie/) (grant number 13/RC/2106 P2) at 
            Trinity College Dublin, collaborating with the [European Institute for Innovation through Health Data (i~HD)](https://www.i-hd.eu/). | 
            Contact: albert.navarro@adaptcentre.ie
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
    ),
    dbc.Row(
        [
            dbc.Col(width=1),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        dcc.Markdown(id='appInfoText', style={'font-size': '14px'},
                                     className='card-text'),
                        html.Div(style={'margin-bottom': '-1em'})
                    ])
                ]), width=10),
            dbc.Col(width=1),
        ]
    ),

])

nodes = [
    {
        'data': {'id': short},
        'position': {'x': nx, 'y': ny}
    }
    for short, nx, ny in (
        # First row
        ('a11', 60, 80),
        ('a12', 60 + 118 * 1, 80),
        ('a13', 60 + 118 * 2, 80),
        ('a14', 60 + 118 * 3, 80),
        ('a15', 60 + 118 * 4, 80),
        # Second row
        ('a21', 60, 80 + 128 * 1),
        ('a22', 60 + 118 * 1, 80 + 128 * 1),
        ('a23', 60 + 118 * 2, 80 + 128 * 1),
        ('a24', 60 + 118 * 3, 80 + 128 * 1),
        ('a25', 60 + 118 * 4, 80 + 128 * 1),
        # Third row
        ('a31', 60, 80 + 130 * 2),
        ('a32', 60 + 118 * 1, 80 + 130 * 2),
        ('a33', 60 + 118 * 2, 80 + 130 * 2),
        ('a34', 60 + 118 * 3, 80 + 130 * 2),
        ('a35', 60 + 118 * 4, 80 + 130 * 2),
        # Forth row
        ('a41', 60, 80 + 132 * 3),
        ('a42', 60 + 119 * 1, 80 + 132 * 3),
        ('a43', 60 + 119 * 2, 80 + 132 * 3),
        ('a44', 60 + 119 * 3, 80 + 132 * 3),
        ('a45', 60 + 119 * 4, 80 + 132 * 3),
    )
]

# Country possibilities (rows)
countryColour = ['Blue', 'Yellow', 'Green', 'Pink']

# Select only teenagers or adults
nodesIDsMatrix = {'Blue': ['a12', 'a13', 'a14', 'a15'],
                  'Yellow': ['a22', 'a23', 'a24', 'a25'],
                  'Green': ['a32', 'a33', 'a34', 'a35'],
                  'Pink': ['a42', 'a43', 'a44', 'a45']}

# Select only teenagers or adults by sex
nodesIDsMatrix2 = {'Blue': {'male': ['a12', 'a13', 'a14', 'a15']},
                   'Yellow': {'male': ['a22', 'a23', 'a24', 'a25']},
                   'Green': {'female': ['a32', 'a33', 'a34', 'a35']},
                   'Pink': {'female': ['a42', 'a43', 'a44', 'a45']}}

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
    'doubleClick': False,
    'editable': False,
    'scrollZoom': False,
}

frCard_Grid = dbc.Card(
    dbc.CardBody(
        [html.Div([
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
            'background-size': '80% 90%', #'37em 34em',  # '600px 550px'
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
            html.Div([
                dbc.Alert([
                    html.H4("Oh that's not the patient!", className='alert-heading'),
                    html.P('Please try again.'),
                    html.P(id='greyAttempsLeft'),
                ],
                    id='wrongChoiceGrey',
                    dismissable=True,
                    is_open=False,
                    color='danger',
                    duration=2000,
                ),
                dbc.Alert([
                    html.H4('Well done!', className='alert-heading'),
                    html.P("Yes, that's the patient! Thanks for your help."),
                ],
                    id='rightChoiceGrey',
                    dismissable=False,
                    is_open=False,
                    color='success'
                ),
                dbc.Alert([
                    html.H4('No more attempts left!', className='alert-heading'),
                    html.P("Sorry but your help was not enough to find the patient. Please go to the next round."),
                ],
                    id='noAttChoiceGrey',
                    dismissable=False,
                    is_open=False,
                    color='warning'
                ),
            ]),
            dbc.CardImg(id='grey_doctor', className='image',
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '50%', 'width': '60%'},
                        bottom=True),
            dbc.Button('Next Round', color='primary', disabled=True,
                       id='greyButton'),
            # Number of attempts left for the first round
            dcc.Store(id='greyAttempts'),
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
                    id='cyto_grey2',
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
                'background-size': '80% 90%', #'37em 34em',  # '600px 550px'
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
            dcc.Markdown(id='hintGrey2',
                         className="card-text",
                         ),
            html.Div([
                dbc.Alert([
                    html.H4("Oh that's not the patient!", className='alert-heading'),
                    html.P('Please try again.'),
                    html.P(id='grey2AttempsLeft'),

                ],

                    id='wrongChoiceGrey2',
                    dismissable=True,
                    is_open=False,
                    color='danger',
                    duration=2000,
                ),
                dbc.Alert(
                    [
                        html.H4('Well done!', className='alert-heading'),
                        html.P("Yes, that's the patient! Thanks for your help."),
                    ],
                    id='rightChoiceGrey2',
                    dismissable=False,
                    is_open=False,
                    color='success'
                ),
                dbc.Alert([
                    html.H4('No more attempts left!', className='alert-heading'),
                    html.P("Sorry but your help was not enough to find the patient. Please go to the next round."),
                ],
                    id='noAttChoiceGrey2',
                    dismissable=False,
                    is_open=False,
                    color='warning'
                ),
            ]),
            dbc.CardImg(id='grey2_doctor', className='image',
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '50%', 'width': '60%'},
                        bottom=True),
            dbc.Button('Next Round', color='primary', disabled=True,
                       id='grey2Button'),
            # Number of attempts left for the second round
            dcc.Store(id='grey2Attempts'),
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

trCard_Grid = dbc.Card(
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
                'background-size': '80% 90%', # '37em 34em',  # '600px 550px'
                'background-repeat': 'no-repeat',
                # 'marginBottom': '-5em'
            }, ),
        ]
    ),
    className='mt-3',
)

trCard_Doctor = dbc.Card(
    dbc.CardBody(
        [
            html.H4('Can you help Dr. Data find the patient?', className='card-title'),
            dcc.Markdown(id='hintColour',
                         className="card-text",
                         ),
            html.Div([
                dbc.Alert([
                    html.H4("Oh that's not the patient!", className='alert-heading'),
                    html.P('Please try again.'),
                    html.P(id='colourAttempsLeft'),
                ],

                    id='wrongChoiceColour',
                    dismissable=True,
                    is_open=False,
                    color='danger',
                    duration=2000,
                ),
                dbc.Alert(
                    [
                        html.H4('Well done!', className='alert-heading'),
                        html.P("Yes, that's the patient! Thanks for your help."),
                    ],
                    id='rightChoiceColour',
                    dismissable=False,
                    is_open=False,
                    color='success'
                ),
                dbc.Alert([
                    html.H4('No more attempts left!', className='alert-heading'),
                    html.P("Sorry but your help was not enough to find the patient. Please go to the next round."),
                ],
                    id='noAttChoiceColour',
                    dismissable=False,
                    is_open=False,
                    color='warning'
                ),
            ]),
            dbc.CardImg(id='colour_doctor', className='image',
                        src='data:image/png;base64, ' + pil_to_b64(pil_img_doctor),
                        style={'height': '50%', 'width': '60%'},
                        bottom=True),
            dbc.Button('Conclusion', color='primary', disabled=True,
                       id='concButton'),
            # Number of attempts left for the third round
            dcc.Store(id='colourAttempts'),
        ]
    ),

    className='mt-3',
)

thirdRoundTab = dbc.Row(
    [
        dbc.Col(width=1),
        dbc.Col(trCard_Grid, width=7),
        dbc.Col(trCard_Doctor, width=3),
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
                    the patient's identity (Round 3). 
                    
                    However, if the adequate data protection regulations are applied
                    researchers can conduct their research safely (Rounds 1 and 2).         
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
        dbc.Tab(thirdRoundTab, label='Round 3', disabled=True),
        dbc.Tab(conclusionTab, label='Conclusion', disabled=True),
    ], id='tabsID', active_tab='tab-0',
)

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)

app.title = 'Guess the patient'
app.layout = html.Div([tabs])


@app.callback([Output('rndPatients', 'data'),
               Output('hintGrey', 'children'),
               Output('hintGrey2', 'children'),
               Output('hintColour', 'children')],
              [Input('startButton', 'n_clicks')],
              )
def chooseRndCountryPatient(n_clicks_start):
    if not n_clicks_start:
        raise PreventUpdate
    else:
        # Randomly select country and patient for Grey view
        rndCountry_Grey = random.choice(countryColour)
        rightPatient_Grey = random.choice(nodesIDsMatrix[rndCountry_Grey])

        # Randomly select country and patient for Grey 2 view
        rndCountry_Grey2 = random.choice(countryColour)
        rightPatient_Grey2 = random.choice(
            nodesIDsMatrix2[rndCountry_Grey2][str(list(nodesIDsMatrix2[rndCountry_Grey2].keys())[0])])

        # Randomly select country and patient for Colour view
        rndCountry_Colour = random.choice(countryColour)
        rightPatient_Colour = random.choice(nodesIDsMatrix[rndCountry_Colour])

        print('grey:', rightPatient_Grey)
        print('grey2:', rightPatient_Grey2)
        print('colour:', rightPatient_Colour)

        # Store country and patient choice in a dict that will refresh as the page is refreshed
        rndDict = {
            'greyC': rndCountry_Grey,
            'greyP': rightPatient_Grey,
            'grey2C': rndCountry_Grey2,
            'grey2S': str(list(nodesIDsMatrix2[rndCountry_Grey2].keys())[0]),
            'grey2P': rightPatient_Grey2,
            'colourC': rndCountry_Colour,
            'colourP': rightPatient_Colour}

        hintGrey = '''
        Hi! All I know is that the patient is a **teenager or adult** that lives in the **''' + rndDict['greyC'] + ''' country** ...

        Please click on the faces on the left to help me find the patient!'''

        hintGrey2 = '''
        Hi! All I know is that the patient is a **''' + rndDict[
            'grey2S'] + '''** **teenager or adult** that lives in the **''' + \
                    rndDict['grey2C'] + ''' country** ...

        Please click on the faces on the left to help me find the patient!'''

        hintColour = '''
        Hi! All I know is that the patient is a **teenager or adult** that lives in the **''' + rndDict['colourC'] + ''' country** ...

        Please click on the faces on the left to help me find the patient!'''

        return [rndDict, hintGrey, hintGrey2, hintColour]


@app.callback(Output('tabsID', 'active_tab'),
              [Input('startButton', 'n_clicks'),
               Input('greyButton', 'n_clicks'),
               Input('grey2Button', 'n_clicks'),
               Input('concButton', 'n_clicks')])
def goToRound1Tab(n_clicks_start, n_clicks_round1, n_clicks_round2, n_clicks_round3):
    if not n_clicks_start:
        raise PreventUpdate
    if n_clicks_start and not n_clicks_round1 and not n_clicks_round2 and not n_clicks_round3:
        return 'tab-1'
    if n_clicks_start and n_clicks_round1 and not n_clicks_round2 and not n_clicks_round3:
        return 'tab-2'
    if n_clicks_start and n_clicks_round1 and n_clicks_round2 and not n_clicks_round3:
        return 'tab-3'
    if n_clicks_start and n_clicks_round1 and n_clicks_round2 and n_clicks_round3:
        return 'tab-4'


@app.callback([Output('wrongChoiceGrey', 'is_open'),
               Output('rightChoiceGrey', 'is_open'),
               Output('noAttChoiceGrey', 'is_open'),
               Output('greyAttempts', 'data'),
               Output('greyAttempsLeft', 'children')],
              [Input('cyto_grey', 'tapNodeData'),
               Input('rndPatients', 'data')],
              [State('greyAttempts', 'data')])
def guessGreyPatient(nodeID_label, rndChoice, greyAttempts):
    if not rndChoice:
        raise PreventUpdate
    else:
        if not nodeID_label:
            raise PreventUpdate
        if nodeID_label['id'] != rndChoice['greyP']:
            # Update number of attempts
            # Give a default data dict with 0 clicks if there's no data.
            nRound1 = greyAttempts or {'round1_attempts': 5}
            nRound1['round1_attempts'] = nRound1['round1_attempts'] - 1
            attLeftMsg = 'You have ' + str(nRound1['round1_attempts']) + ' attempts left'
            if nRound1['round1_attempts'] > 0:
                return [True, False, False, nRound1, attLeftMsg]
            else:
                return [False, False, True, nRound1, attLeftMsg]

        if nodeID_label['id'] == rndChoice['greyP']:
            # Update number of attempts
            # Give a default data dict with 0 clicks if there's no data.
            nRound1 = greyAttempts or {'round1_attempts': 5}
            attLeftMsg = 'You have ' + str(nRound1['round1_attempts']) + ' attempts left'
            return [False, True, False, nRound1, attLeftMsg]


@app.callback([Output('greyButton', 'disabled')],
              [Input('rightChoiceGrey', 'is_open'),
               Input('noAttChoiceGrey', 'is_open')])
def nextRound1ButtonClick(rightAnswer_Ok, noAttempts_Ok):
    if rightAnswer_Ok or noAttempts_Ok:
        return [False]
    else:
        return [True]


@app.callback([Output('wrongChoiceGrey2', 'is_open'),
               Output('rightChoiceGrey2', 'is_open'),
               Output('noAttChoiceGrey2', 'is_open'),
               Output('grey2Attempts', 'data'),
               Output('grey2AttempsLeft', 'children')
               ],
              [Input('cyto_grey2', 'tapNodeData'),
               Input('rndPatients', 'data')],
              [State('grey2Attempts', 'data')])
def guessGrey2Patient(nodeID_label, rndChoice, greyAttempts):
    if not rndChoice:
        raise PreventUpdate
    else:
        if not nodeID_label:
            raise PreventUpdate
        if nodeID_label['id'] != rndChoice['grey2P']:
            # Update number of attempts
            # Give a default data dict with 0 clicks if there's no data.
            nRound1 = greyAttempts or {'round1_attempts': 5}
            nRound1['round1_attempts'] = nRound1['round1_attempts'] - 1
            attLeftMsg = 'You have ' + str(nRound1['round1_attempts']) + ' attempts left'
            if nRound1['round1_attempts'] > 0:
                return [True, False, False, nRound1, attLeftMsg]
            else:
                return [False, False, True, nRound1, attLeftMsg]

        if nodeID_label['id'] == rndChoice['grey2P']:
            # Update number of attempts
            # Give a default data dict with 0 clicks if there's no data.
            nRound1 = greyAttempts or {'round1_attempts': 5}
            attLeftMsg = 'You have ' + str(nRound1['round1_attempts']) + ' attempts left'
            return [False, True, False, nRound1, attLeftMsg]


@app.callback([Output('grey2Button', 'disabled')],
              [Input('rightChoiceGrey2', 'is_open'),
               Input('noAttChoiceGrey2', 'is_open')])
def nextRound2ButtonClick(rightAnswer_Ok, noAttempts_Ok):
    if rightAnswer_Ok or noAttempts_Ok:
        return [False]
    else:
        return [True]


@app.callback([Output('wrongChoiceColour', 'is_open'),
               Output('rightChoiceColour', 'is_open'),
               Output('noAttChoiceColour', 'is_open'),
               Output('colourAttempts', 'data'),
               Output('colourAttempsLeft', 'children')
               ],
              [Input('cyto_colour', 'tapNodeData'),
               Input('rndPatients', 'data')],
              [State('colourAttempts', 'data')])
def guessColourPatient(nodeID_label, rndChoice, colourAttempts):
    if not rndChoice:
        raise PreventUpdate
    else:
        if not nodeID_label:
            raise PreventUpdate
        if nodeID_label['id'] != rndChoice['colourP']:
            # Update number of attempts
            # Give a default data dict with 0 clicks if there's no data.
            nRound1 = colourAttempts or {'round1_attempts': 5}
            nRound1['round1_attempts'] = nRound1['round1_attempts'] - 1
            attLeftMsg = 'You have ' + str(nRound1['round1_attempts']) + ' attempts left'
            if nRound1['round1_attempts'] > 0:
                return [True, False, False, nRound1, attLeftMsg]
            else:
                return [False, False, True, nRound1, attLeftMsg]

        if nodeID_label['id'] == rndChoice['colourP']:
            # Update number of attempts
            # Give a default data dict with 0 clicks if there's no data.
            nRound1 = colourAttempts or {'round1_attempts': 5}
            attLeftMsg = 'You have ' + str(nRound1['round1_attempts']) + ' attempts left'
            return [False, True, False, nRound1, attLeftMsg]


@app.callback([Output('concButton', 'disabled')],
              [Input('rightChoiceColour', 'is_open'),
               Input('noAttChoiceColour', 'is_open')])
def nextRound3ButtonClick(rightAnswer_Ok, noAttempts_Ok):
    if rightAnswer_Ok or noAttempts_Ok:
        return [False]
    else:
        return [True]


# Statistics storage about the app
@app.callback([Output('appInfo', 'data'),
               Output('appInfoText', 'children')],
              [Input('startButton', 'n_clicks'),
               Input('greyButton', 'n_clicks'),
               Input('grey2Button', 'n_clicks'),
               Input('concButton', 'n_clicks')],
              [State('rightChoiceGrey', 'is_open'),
               State('noAttChoiceGrey', 'is_open'),
               State('rightChoiceGrey2', 'is_open'),
               State('noAttChoiceGrey2', 'is_open'),
               State('rightChoiceColour', 'is_open'),
               State('noAttChoiceColour', 'is_open')],
              [State('appInfo', 'data')]
              )
def chooseRndCountryPatient(n_clicks_start,
                            n_clicks_round1, n_clicks_round2, n_clicks_round3,
                            rightGrey, wrongGrey,
                            rightGrey2, wrongGrey2,
                            rightColour, wrongColour,
                            nPlayersInfo):
    # if not n_clicks_start:
    #    raise PreventUpdate
    # else:
    # Update number of participants that play and which rounds get right
    # Give a default data dict with 0 clicks if there's no data.
    nPlayersInfo = nPlayersInfo or {'total_players': 0,
                                    'round1_pass': 0,
                                    'round1_fail': 0,
                                    'round2_pass': 0,
                                    'round2_fail': 0,
                                    'round3_pass': 0,
                                    'round3_fail': 0, }
    print(n_clicks_round1, n_clicks_round2, n_clicks_round3)
    if n_clicks_start and not n_clicks_round1 and not n_clicks_round2 and not n_clicks_round3:
        nPlayersInfo['total_players'] = nPlayersInfo['total_players'] + 1

    if n_clicks_round1 and not n_clicks_round2 and not n_clicks_round3:
        if rightGrey:
            nPlayersInfo['round1_pass'] = nPlayersInfo['round1_pass'] + 1
        if wrongGrey:
            nPlayersInfo['round1_fail'] = nPlayersInfo['round1_fail'] + 1

    if n_clicks_round2 and not n_clicks_round3:
        if rightGrey2:
            nPlayersInfo['round2_pass'] = nPlayersInfo['round2_pass'] + 1
        if wrongGrey2:
            nPlayersInfo['round2_fail'] = nPlayersInfo['round2_fail'] + 1

    if n_clicks_round3:
        if rightColour:
            nPlayersInfo['round3_pass'] = nPlayersInfo['round3_pass'] + 1
        if wrongColour:
            nPlayersInfo['round3_fail'] = nPlayersInfo['round3_fail'] + 1

    print(nPlayersInfo)
    nPlayersInfoText = '**Total players**: ' + str(nPlayersInfo['total_players']) + \
                       ' | **Round 1**: ' + str(nPlayersInfo['round1_pass']) + '/' + str(nPlayersInfo['round1_fail']) + \
                       ' | **Round 2**: ' + str(nPlayersInfo['round2_pass']) + '/' + str(nPlayersInfo['round2_fail']) + \
                       ' | **Round 3**: ' + str(nPlayersInfo['round3_pass']) + '/' + str(nPlayersInfo['round3_fail'])

    return [nPlayersInfo, nPlayersInfoText]


if __name__ == '__main__':
    app.run_server(debug=False)
