import sys

sys.path.append("../")

from utils import *
from data import getCitiesList, getStatesList, getCountriesList, getStatesCodesToStatesName

citiesList = getCitiesList()
countriesList = getCountriesList()
statesList = getStatesList()
statesCodeToStatesName = getStatesCodesToStatesName()

cid_mapper = {country.name: country.alpha_2 for country in pycountry.countries}


def get_locations(locstr):
    states, cities, countries, country_id, continent_code, continent_name = None, None, None, None, None, None

    ############################################################################
    # ROAD REFORMATING (ex: 159, Sin Ming Road # 07-02 Lobby 2 Amtech Building
    # --> 159, Sin Ming Road)
    ############################################################################
    if "Road" in locstr:
        locstr = locstr[0:re.search(r"\bRoad\b", locstr).end()]
    if "ROAD" in locstr:
        locstr = locstr[0:re.search(r"\bROAD\b", locstr).end()]
    if "road" in locstr:
        locstr = locstr[0:re.search(r"\broad\b", locstr).end()]
    if "Street" in locstr:
        locstr = locstr[0:re.search(r"\bStreet\b", locstr).end()]
    if "street" in locstr:
        locstr = locstr[0:re.search(r"\bstreet\b", locstr).end()]

    ############################################################################
    ### PREPROCESSING
    ############################################################################
    locstr = detect_pipe(locstr)
    # locstr = detect_and1(locstr)
    locstr = detect_dash(locstr)
    locstr = detect_backslash(locstr)

    ############################################################################
    # ROAD
    ############################################################################
    print(locstr)
    if (re.findall('\d+', locstr)) \
            or (locstr.split(' ')[-1] == "Road") \
            or (locstr.split(' ')[-1] == "ROAD") \
            or ("Road" in locstr.split(' ')) \
            or ("ROAD" in locstr.split(' ')) \
            or ("Street" in locstr.split(' ')) \
            or ("street" in locstr.split(' ')):
        try:
            cities, states, countries = get_city_state_countries_from_road(locstr)
            cities = cities.strip()
            states = states.strip()
            countries = countries.strip()
        except:
            pass
            # # remove street number
            # locstr = rm_num(locstr)
            # if len(locstr.split(',')) > 3:
            #     # only pick state, country
            #     locstr = ",".join(locstr.split(',')[-2:])
    ###########################################################################

    ###########################################################################
    # COUNTRY ONLY
    ###########################################################################
    if locstr.title() in countriesList:
        countries = locstr
    ############################################################################

    ###########################################################################
    # CITY ONLY
    ###########################################################################

    if locstr in citiesList:
        states, countries = get_country_and_state_using_city_only(locstr)
    ############################################################################

    ############################################################################
    # CITY - STATES
    ############################################################################
    if (len(locstr.split(",")) == 2) and (len(locstr.split(",")[-1].strip()) > 2):
        if locstr.split(",")[0] in citiesList:
            cities = locstr.split(",")[0]
        if locstr.split(",")[-1].strip() in statesList:
            states = locstr.split(",")[-1].strip()
        try:
            locstr = cities + ", " + states
        except:
            pass

    ############################################################################

    ############################################################################
    ## THIS CODE TO SOLVE CITY - STATE CODE FORMAT (ex: Bonney Lake, WA) #######
    ############################################################################
    if len(locstr.split(',')) == 2:
        if len(locstr.split(',')[-1].strip()):
            if statesCodeToStatesName.get(locstr.split(',')[-1].strip()) and len(
                    statesCodeToStatesName.get(locstr.split(',')[-1].strip())) > 1:
                if locstr.split(',')[0] in citiesList:
                    cities = locstr.split(',')[0]
                    states, countries = get_state_country(locstr)
                    if type(states) == list:
                        states = states[0]
                    # cities = cities.translate(str.maketrans('', '', string.punctuation))
                    # states = states.translate(str.maketrans('', '', string.punctuation))
                    # countries = countries.translate(str.maketrans('', '', string.punctuation))
            elif statesCodeToStatesName.get(locstr.split(',')[-1].strip()) and len(
                    statesCodeToStatesName.get(locstr.split(',')[-1].strip())) == 1:
                cities = locstr.split(',')[0]
                states = statesCodeToStatesName.get(locstr.split(',')[-1].strip())
                if type(states) == list:
                    states = states[0]
                # cities = cities.translate(str.maketrans('', '', string.punctuation))
                # states = states.translate(str.maketrans('', '', string.punctuation))
    else:
        locstr = locstr.title()
    ############################################################################

    ############################################################################
    ## THIS CODE TO SOLVE CITY - STATE AREA OR STATE AREA FORMAT
    ## (ex: Greater Jakarta Area / Richland, Washington Area)
    ############################################################################
    if (locstr.split(" ")[0] == "Greater") and (locstr.split(" ")[-1] == "Area"):
        locstr = ' '.join(locstr.split(' ')[1:-1]).strip()
        geolocator = Nominatim(user_agent="geo11", timeout=3)
        location = geolocator.geocode(locstr)
        try:
            location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])),
                                          exactly_one=True)
            address = location.raw['address']
            cities = address.get('city', '').strip()
            countries = address.get('country', '').strip()
            states = address.get('state', '').strip()
        except:
            cities = ""
            countries = ""
    elif (locstr.split(',')[-1].split(" ")[-1] == "Area") and (len(locstr.split(',')) == 2):
        cities = locstr.split(',')[0]
        states = locstr.split(',')[-1].strip().split(" ")[0]
        geolocator = Nominatim(user_agent="geo12", timeout=3)
        location = geolocator.geocode("{}, {}".format(cities, states))
        try:
            location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])),
                                          exactly_one=True)
            address = location.raw['address']
            countries = address.get('country', '').strip()
        except:
            countries = ""
    ##############################################################################

    place_entity = locationtagger.find_locations(text=locstr)

    ###########################################################################
    # COUNTRIES
    ###########################################################################
    if countries is None:
        if len(place_entity.countries) > 0:
            countries = place_entity.countries[0]
        else:
            countries = ""
    ###########################################################################
    # STATES
    ###########################################################################
    if states is None:
        if len(place_entity.regions) > 0:
            if place_entity.cities:
                if (place_entity.regions[0] == place_entity.cities[0]) \
                        and (place_entity.regions[0] != "Central") \
                        and (place_entity.regions[0] != "Capital") \
                        and (place_entity.regions[0] != "Northern") \
                        and (place_entity.regions[0] != "Southern") \
                        and (place_entity.regions[0] != "Eastern") \
                        and (place_entity.regions[0] != "Western") \
                        and (place_entity.regions[0] != "North") \
                        and (place_entity.regions[0] != "South") \
                        and (place_entity.regions[0] != "East") \
                        and (place_entity.regions[0] != "West"):
                    if place_entity.other:
                        states = place_entity.other[0]
                elif place_entity.other:
                    if (place_entity.other[0] == "Region") \
                            or (place_entity.other[0] == "Province") \
                            or (place_entity.other[0] == "Division") \
                            or (place_entity.other[0] == "District") \
                            or (place_entity.other[0] == "Capital") \
                            or (place_entity.other[0] == "Governorate") \
                            or (place_entity.other[0] == "Coast"):
                        if place_entity.regions[0].find(place_entity.other[0]) == -1:
                            states = place_entity.regions[0] + ' ' + place_entity.other[0]
                        else:
                            states = place_entity.regions[0]
                else:
                    states = place_entity.regions[0]
            else:
                states = place_entity.regions[0]
        elif len(place_entity.other) > 0:
            states = place_entity.other[0]
            try:
                if states in place_entity.cities[0]:
                    states = place_entity.cities[0]
                else:
                    states = place_entity.regions[0]
            except:
                for i in place_entity.other:
                    if ('Region' in i) \
                            or ('Province' in i) \
                            or ('Division' in i) \
                            or ("District" in i) \
                            or ("Capital" in i) \
                            or ("Governorate" in i) \
                            or ("Coast" in i):
                        try:
                            states = place_entity.regions[0]
                        except:
                            states = i
                        break
        else:
            try:
                if ("District" in place_entity.regions[0]) \
                        or ("Province" in place_entity.regions[0]) \
                        or ("Coast" in place_entity.regions[0]):
                    states = place_entity.regions[0]
            except:
                states = ""

        if states is None:
            if place_entity.regions:
                states = place_entity.regions[0]
        if states == "Surrounding Area":
            states = ""
    #########################################################################
    # CITIES
    #########################################################################
    if cities is None:
        temp = []
        if len(place_entity.cities) > 0:
            cities = place_entity.cities[0]
            if (cities == "North") \
                    or (cities == "South") \
                    or (cities == "East") \
                    or (cities == "West") \
                    or (cities == "Central"):
                cities = ""
            if cities == countries:
                for i in place_entity.other:
                    if ('Region' not in i) \
                            or ('Province' not in i) \
                            or ('Division' not in i) \
                            or ('Capital' not in i) \
                            or ("District" not in i) \
                            or ("Governorate" not in i) \
                            or ("Coast" not in i):
                        temp.append(i)
                        # cities = i
                # cities = ""
            # print(temp)
            # temp2 = []
            for j in temp:
                if (j.find("Province") != -1) \
                        or (j.find("Region") != -1) \
                        or (j.find("Division") != -1) \
                        or (j.find("Capital") != -1) \
                        or (j.find("District") != -1) \
                        or (j.find("Coast") != -1):
                    # temp2.append(j)
                    continue
                else:
                    cities = j
            # print(temp2)
        else:
            try:
                for i in place_entity.other:
                    if (i.find(countries) != -1) \
                            or (i.find("Province") != -1) \
                            or (i.find("Region") != -1) \
                            or (i.find("Division") != -1) \
                            or (i.find("Capital") != -1) \
                            or (i.find("District") != -1) \
                            or (i.find("Coast") != -1):
                        continue
                    else:
                        cities = i
            except:
                cities = ""

        ##########################################################################
        #### SPECIAL CASE FOR JAPAN LOCATION
        #########################################################################
        if cities == "Prefecture":
            cities = ""
            states = states + " " + "Prefecture"
        #########################################################################
        #### IF CITIES = STATES / CITIES = COUNTRIES WHICH IS NOT ACCEPTABLE
        ########################################################################
        if (cities == states) or (cities == countries) or (cities is None):
            cities = ""

        #########################################################################
        #### IF CURRENT RESULT JUST HAS A CITY
        #########################################################################
        # try:
        #     if (cities != '') or (states == '') or (countries == ''):
        #         country_id, countries = get_country_code__using_city_only(cities)
        # except:
        #     country_id, countries = "", ""

        # try:
        #     if (len(states) == 2) or (len(states) == 3):
        #         states, countries = get_country_and_state_using_city_only(locstr)
        # except:
        #     states, countries = "", ""

    ############################################################################
    # COUNTRY CODE
    ############################################################################
    if countries:
        country_id = cid_mapper.get(countries.strip())
    else:
        country_id = ""

    try:
        if (country_id == '') and (states != ''):
            country_id, countries = get_country_code_and_country_using_state_only(states.strip())
    except:
        country_id, countries = "", ""
    ##################################################################################
    # CONTINENT / REGION CODE
    ##################################################################################
    if country_id:
        continent_code = pc.country_alpha2_to_continent_code(country_id.strip())
    else:
        continent_code = ""
    ##################################################################################
    # CONTINENT / REGION NAME
    ##################################################################################
    if continent_code:
        continent_name = pc.convert_continent_code_to_continent_name(continent_code.strip())
    else:
        continent_name = ""

    ##################################################################################
    # STATE BACK-TRANSLATION
    ##################################################################################
    # states = GoogleTranslator(source="en", target=country_id.lower()).translate(states)

    if fuzz.ratio(states, countries) > 65.:
        states = ""

    return {"city": cities,
            "state": states,
            "country": countries,
            "country_code": country_id,
            "region": continent_name,
            "region_code": continent_code}


sample = "Jalan Aria Jipang No 7"
loc = get_locations(sample)
print(loc)
