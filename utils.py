import re
import string
import pycountry
import locationtagger
from rapidfuzz import fuzz
import pycountry_convert as pc
from deep_translator import GoogleTranslator
from geopy.geocoders import Nominatim

cid_mapper = {country.name: country.alpha_2 for country in pycountry.countries}

def rm_num(locstr):
    locstr = re.sub(r'\d+', '', locstr)
    return ''.join(locstr)

def detect_backslash(pass_string):
    regex= re.compile('[/]')
    if(regex.search(pass_string) != None):
        sub_string = pass_string.split('/')[1].strip()
        if len(pass_string.split(',')) == 2:
            return sub_string + "," + pass_string.split(',')[-1]
        elif len(pass_string.split(',')) == 3:
            return sub_string + "," + pass_string.split(',')[-2:]
        else:
            return sub_string
    else:
        return pass_string

def detect_dash(pass_string):
    regex= re.compile('[-]')
    if(regex.search(pass_string) != None):
        sub_string = pass_string.split('-')[1].strip()
        if len(pass_string.split(',')) == 2:
            return sub_string + "," + pass_string.split(',')[-1]
        elif len(pass_string.split(',')) == 3:
            return sub_string + "," + pass_string.split(',')[-2:]
        else:
            return sub_string
    else:
        return pass_string

def detect_pipe(pass_string):
    regex= re.compile('[|]')
    if(regex.search(pass_string) != None):
        sub_string = pass_string.split('|')[1].strip()
        if len(pass_string.split(',')) == 2:
            return sub_string + "," + pass_string.split(',')[-1]
        elif len(pass_string.split(',')) == 3:
            return sub_string + "," + pass_string.split(',')[-2:]
        else:
            return sub_string
    else:
        return pass_string

def detect_and1(pass_string):
    regex= re.compile('[&]')
    if(regex.search(pass_string) != None):
        sub_string = pass_string.split('&')[1].strip()
        if len(pass_string.split(',')) == 2:
            return sub_string + "," + pass_string.split(',')[-1]
        elif len(pass_string.split(',')) == 3:
            return sub_string + "," + pass_string.split(',')[-2:]
        else:
            return sub_string
    else:
        return pass_string

def get_state_country(citystr):
    geolocator = Nominatim(user_agent="geopy1", timeout=3)
    location = geolocator.geocode(citystr)
    location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)
    address = location.raw['address']
    state = address.get('state', None)
    country = address.get('country', None)
    return state, country

def get_city_state_countries_from_road(roadstr):
    geolocator = Nominatim(user_agent="geopy2", timeout=3)
    location = geolocator.geocode(roadstr)
    addr = location.address
    addr = addr.split(',')
    country = addr[-1]
    state = addr[-3]
    city = addr[-4]
    return city, state, country

def get_country_code_and_country_using_state_only(statestr):
    try:
        geolocator = Nominatim(user_agent="geopy3",timeout=3)

        location = geolocator.geocode(statestr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country_code = address.get('country_code', '').upper()
        country = address.get('country', '')
        return country_code, country
    except:
        pass


def get_country_code__using_city_only(citystr):
    try:
        geolocator = Nominatim(user_agent="geopy4", timeout=3)

        location = geolocator.geocode(citystr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        country_code = address.get('country_code', '').upper()
        country = address.get('country', '')
        country = GoogleTranslator(source='auto', target='en').translate(country)
        return country_code, country
    except:
        pass

def get_country_and_state_using_city_only(citystr):
    try:
        geolocator = Nominatim(user_agent="geopy5", timeout=3)

        location = geolocator.geocode(citystr)
        location = geolocator.reverse("{}, {}".format(str(location.raw['lat']), str(location.raw['lon'])), exactly_one=True)

        address = location.raw['address']
        state = address.get('state', '')
        country = address.get('country', '')
        return state, country
    except:
        pass