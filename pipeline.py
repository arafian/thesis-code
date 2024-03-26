import sys
import sqlite3
import pandas as pd
from bson.binary import Binary
import base64

sys.path.append('../bioreactor-technical-analysis')
import biota.steadyfluxes as steady

kwargs = {
    'workingVolume': 20000,
    'tankDiameter':  2.34,
    'rpm': 42.3,
    'backPressure': 1.3,
    'superficialVel': 0.004,
    'moleFracO2': 0.21,
    'moleFracCO2':  0.03,
    'initCells': 4e6,
    'temp': 310,
    'powerNumber': 5,
    'mediumDensity': 1000,
    'mediumViscosity': 9e-4,
    'vesselVolDay': 0.0,
    'perfLactateRate': 5.0,
    'perfAmmrate': 5.0,
    'growthRate': 0.029,
    'glutamineUptakeRate': 0,
    'glucoseUptakeRate': 0,
    'oxygenUptakeRate': 0.49, 
    'carbonDioxideProdRate': 0.593,
    'ammoniaProductionRate': 0.013571,
    'lactateProductionRate': 0.135707, 
    'massDensity': 1030,
    'cellRadius': 18e-6,
    'wetmass': 3000,
    'dryMassFraction': 0.3,
    'ammoniaLimit': 5,
    'lactateLimit': 50, 
    'CO2Limit': 100,
    'turbLengthLimit': 20e-6,
    'count': 50,
    'doublings': 7,
    'rpmlims': (1,75),
    'supervellims': (0.0001,0.005),
    'celldenslims': (5.9e5,6.1e5)
}

from pymongo import MongoClient

uri = "mongodb://localhost:27017/"
client = MongoClient(uri)

db = client['sims']
collection = db['table1']

def runSim( showGraphs=True, **kwargs):
    
    impellerDiameter=kwargs['tankDiameter']/3
    initVol = 0.76 * kwargs['workingVolume']
    STR_Humbird_20kl = steady.Bioreactor(wv=kwargs['workingVolume'],t=kwargs['tankDiameter'],d=impellerDiameter,
                                         n=kwargs['rpm'],p_back=kwargs['backPressure'],u_s=kwargs['superficialVel'],
                                         mf_O2_gas=kwargs['moleFracO2'],mf_CO2_gas=kwargs['moleFracCO2'],v0=initVol,
                                         ns=kwargs['initCells'],Temp=kwargs['temp'],Np=kwargs['powerNumber'],
                                         rho=kwargs['mediumDensity'],mu=kwargs['mediumViscosity'],vvd=kwargs['vesselVolDay'],
                                         perfAMM=kwargs['perfAmmrate'],perfLAC=kwargs['perfLactateRate'])

    uptakeList = [kwargs['glutamineUptakeRate'], kwargs['glucoseUptakeRate'], kwargs['oxygenUptakeRate']]
    prodList = [kwargs['carbonDioxideProdRate'], kwargs['ammoniaProductionRate'], kwargs['lactateProductionRate']]
    limitsList = [kwargs['ammoniaLimit'], kwargs['lactateLimit'], kwargs['CO2Limit'], kwargs['turbLengthLimit']]
    cell_Humbird = steady.Cell(mu=kwargs['growthRate'],uptakes=uptakeList,prod=prodList,rho=kwargs['massDensity'],
                               rad=kwargs['cellRadius'],wetmass=kwargs['wetmass'],dmf=kwargs['dryMassFraction'],limits=limitsList)
    
    bioreactor = STR_Humbird_20kl
    cell = cell_Humbird
    return steady.brute(count=kwargs['count'],b=bioreactor,c=cell,dbls=kwargs['doublings'],rpmlims=kwargs['rpmlims'],
                        uslims=kwargs['supervellims'],nslims=kwargs['celldenslims'],graphs=showGraphs)

def insertDf(kwargs, df):
    df_dict_list = df.to_dict(orient='records')
    df_dict = {}
    for item in df_dict_list:
        df_dict[item['Constraint']] = item['Maximum Yield [g/L wet]']
        
    with open('static/ConstraintYieldGraphs.png', 'rb') as f:
        png_binary = f.read()
        
    document = {
        "inputs": {},
        "outputs": {},
        "graph": Binary(png_binary)
    }
    
    for key, value in kwargs.items():
        document['inputs'][key] = value
    
    for key, value in df_dict.items():
        document['outputs'][key] = value
    
    existing_document = collection.find_one(document)
    if existing_document:
        print("A similar document already exists.")
    else:
        result = collection.insert_one(document)
        print(f"Document inserted with ID: {result.inserted_id}")
           
simulation_complete = False
table_html = None
graph_data = None

def get_table_html():
    global table_html
    return table_html

def get_graph_data():
    global graph_data
    return graph_data

def runSimAndInsert(inputs):
    global simulation_complete, table_html, graph_data
    
    df = runSim(**inputs)
    insertDf(inputs, df)
    
    # Update the table HTML and graph data
    df_dict_list = df.to_dict(orient='records')
    df_dict = {}
    for item in df_dict_list:
        df_dict[item['Constraint']] = item['Maximum Yield [g/L wet]']
    table_html = pd.DataFrame(df_dict.items(), columns=['Constraint', 'Maximum Yield [g/L wet]']).to_html(classes='table table-striped', index=False)
    
    with open('static/ConstraintYieldGraphs.png', 'rb') as f:
        image_binary = f.read()
        graph_data = 'data:image/png;base64,' + base64.b64encode(image_binary).decode('utf-8')
    
    simulation_complete = True

## Drop the selected database
#db.client.drop_database('sims')
#if not db.list_collection_names():
#    print("The database is empty")
#else:
#    print("The database is not empty")
#
## Close the connection
#client.close()
