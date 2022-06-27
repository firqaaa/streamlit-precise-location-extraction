import pandas as pd
from collections import defaultdict
import streamlit as st

@st.cache
def getCitiesList():
    countries_cities = pd.read_json('countries+cities.json')
    citiesList = []
    for i in range(len(countries_cities)):
        for j in range(len(countries_cities['cities'][i])):
            citiesList.append(countries_cities['cities'][i][j].get('name'))
    return citiesList

@st.cache
def getCountriesList():
    countries_only = pd.read_json('countries.json')
    countriesList = []
    for i in range(len(countries_only)):
        countriesList.append(countries_only['name'][i])
    return countriesList

@st.cache
def getStatesList():
    countries_states = pd.read_json('countries+states.json')
    statesList= []
    for i in range(len(countries_states)):
        for j in range(len(countries_states['states'][i])):
            statesList.append(countries_states['states'][i][j].get('name'))
    return statesList

@st.cache
def getStatesNameToStateCode():
    countries_states = pd.read_json('countries+states.json')
    statesNameToStateCode = defaultdict(list)
    for i in range(len(countries_states)):
        for j in range(len(countries_states['states'][i])):
            statesNameToStateCode[countries_states['states'][i][j].get('name')].append(countries_states['states'][i][j].get('state_code'))
    return statesNameToStateCode

@st.cache
def getStatesCodesToStatesName():
    countries_states = pd.read_json('countries+states.json')
    statesCodeToStatesName = defaultdict(list)
    for i in range(len(countries_states)):
        for j in range(len(countries_states['states'][i])):
            statesCodeToStatesName[countries_states['states'][i][j].get('state_code')].append(countries_states['states'][i][j].get('name'))
    return statesCodeToStatesName