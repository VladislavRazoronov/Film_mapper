from pyrecord import Record
from geopy import Nominatim
import folium
import time

film_info = Record.create_type('film_info','name','location')

def convert_to_coordinates(location):
    """
    Converts location name into its longitude
    and latitude
    >>> convert_to_coordinates('Coventry, West Midlands, England, UK')
    (52.4081812, -1.510477)
    """
    geolocator = Nominatim(user_agent="my_app")
    loc = geolocator.geocode(location)
    time.sleep(1)
    if loc == None:
        return None
    return (loc.latitude,loc.longitude)

def read_locations(year,filename):
    """
    Reads film years,names and locations from file
    """
    with open(filename,encoding='utf-8',errors='ignore') as file:
        line = file.readline()
        while not line.startswith("LOCATION"):
            line = file.readline()
        file.readline()
        data = file.readlines()
        films = []
        for el in data:
            if el.startswith('----------'):
                break
            line_list = el.split('\t')
            line_list = list(filter(lambda x: x != '',line_list))
            film_year = el.split('(')[1].split(')')[0][:4] 
            if film_year != year or '{' in el:
                continue
            coordinates = convert_to_coordinates(line_list[1].strip('\n'))
            if coordinates == None: continue
            value = [film_info(el.split('(')[0].replace('\"','').replace("\'",''),coordinates)] 
            films.extend(value)
    return films

def find_closest(coordinates,films):
    """
    (tuple, list)->tuple
    Finds closest film location to given coordinates
    and removes element from list
    """
    dist_min = 10000000000000000000000000
    for el in films:
        dist = (el.location[0]-coordinates[0])**2 + (el.location[1]-coordinates[1])**2
        if dist < dist_min:
            dist_min = dist
            el_min = el
    films.remove(el_min)
    return el_min

if __name__ == '__main__':
    year = input('Please enter year that films were released: ')
    loc = input('Please enter coordinates(split with space): ').split(' ')
    loc = list(map(float,loc))
    print("Generating map...")
    film_map = folium.Map(location=loc)
    films = read_locations(year,'locations1.list')
    closest_films = []
    print('Adding markers...')
    markers = folium.FeatureGroup('Markers')
    for i in range(10 if len(films)>10 else len(films)):
        closest_films.append(find_closest(loc,films))
    for el in closest_films:
        folium.Marker(el.location,el.name).add_to(markers)
    film_map.add_child(markers)
    folium.LayerControl().add_to(film_map)
    film_map.save('Film_map.html')
    print("Finished, open Film_map.html for result")
