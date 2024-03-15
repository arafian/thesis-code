#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import sqlite3
import pandas as pd

sys.path.append('../bioreactor-technical-analysis')
#sys.path.append('/Users/armanrafian/Programs/thesis/bioreactor-technical-analysis/')


# In[2]:


import biota.steadyfluxes as steady


# ## Run 2nd experiment

# In[3]:


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
    cell_Humbird = steady.Cell(mu=kwargs['growthRate'],uptakes=uptakeList,prod=prodList,rho=kwargs['massDensity'],rad=kwargs['cellRadius'],wetmass=kwargs['wetmass'],dmf=kwargs['dryMassFraction'],limits=limitsList)
    
    bioreactor = STR_Humbird_20kl
    cell = cell_Humbird
    return steady.brute(count=kwargs['count'],b=bioreactor,c=cell,dbls=kwargs['doublings'],rpmlims=kwargs['rpmlims'],uslims=kwargs['supervellims'],nslims=kwargs['celldenslims'],graphs=showGraphs)


# In[4]:


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


# In[5]:


df = runSim(**kwargs)


# In[6]:


df


# In[8]:


from pymongo import MongoClient

uri = "mongodb://localhost:27017/"
client = MongoClient(uri)

db = client['sims']
collection = db['table1']


# In[9]:


def insertDf(kwargs, df):
    df_dict_list = df.to_dict(orient='records')
    df_dict = {}
    for item in df_dict_list:
        df_dict[item['Constraint']] = item['Maximum Yield [g/L wet]']
        
    document = {
        "inputs": {},
        "outputs": {}
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


# In[10]:


#insertDf(kwargs, df)


# In[12]:


#for i in range(100, 501, 25):
#    kwargs['temp'] = i
#    df = runSim(**kwargs)
#    insertDf(kwargs, df)


# In[13]:


#from pprint import pprint
#
#cursor = db.table1.find()
#
## Iterate over the cursor and print each document
#for document in cursor:
#    pprint(document)


# In[1]:


def runSimAndInsert(inputs):
    df = runSim(**inputs)
    insertDf(inputs, df)

