# Set up
import requests
import sys
import pygame

output = "\n"
cities = []

pygame.init()

def return_higher(a, b):
    if a[1] > b[1]:
        return a
    else:
        return b
    
def return_lower(a, b):
    if a[1] < b[1]:
        return a
    else:
        return b

# Request
URL = "https://api.teleport.org/api/cities/"
city = input("Please input a city to search for: ")
parameters = {"search":city}
response = requests.get(URL, params=parameters)

# Check whether 
if response.status_code != 200:
    print("An error has occurred. Status code: " + str(response.status_code))
    sys.exit()
body = response.json()

# Count how many cities were found
num_cities = body['count']
if num_cities == 0:
    print("Sorry, we couldn't find any city that matches the name.")
    sys.exit()

print("Found " + str(num_cities) + " cities")

# Append to output
output += "Search results for " + city + "\n"
output += "====================\n"
output += "Cities found: " + str(num_cities) + "\n"

# Set up cities list
embedded = body['_embedded']
result = embedded['city:search-results']

for i in range(num_cities):
    city_name = result[i]['matching_full_name']
    print(str(i+1) + ": " + city_name)

city_search = input("Which city do you want to search? (Enter a list of numbers to seach multiple) ")
city_search = city_search.split(', ')

# gather data
for ind, i in enumerate(city_search):
    cities.append({})
    ind = int(ind)
    city_dict = cities[ind]
    i = int(i)-1
    
    # find city name
    city_name = result[i]['matching_full_name']
    city_dict['name'] = city_name
    print("Found name")
    pygame.time.wait(1000)
    
    # find all alternative names
    city_dict['alt_names'] = []
    alt_names = result[i]['matching_alternate_names']
    for alt_name in alt_names:
        city_dict['alt_names'].append(alt_name['name'])
    print("Found alt name")
    pygame.time.wait(1000)
    
    # find more data
    try:
        city_url = result[i]['_links']['city:item']['href']
        city_response = requests.get(city_url)
        city_body = city_response.json()
        print("Found more data")
    except KeyError:
        print("More data not found")
    pygame.time.wait(1000)
    
    # city location
    try:
        city_location = city_body['location']['latlon']
        city_dict['latlon'] = (city_location['latitude'],city_location['longitude'])
        city_dict['population'] = city_body['population']
        print("Found location and population")
    except KeyError:
        print("Location and population not found")
    pygame.time.wait(1000)
    
    # Urban Area
    try:
        city_ua = city_body['_links']['city:urban_area']['href']
        ua_response = requests.get(city_ua)
        ua_body = ua_response.json()
        continent = ua_body['continent']
        city_dict['ua'] = {}
        city_dict['ua']['name'] = ua_body['full_name']
        city_dict['ua']['mayor'] = ua_body['mayor']
        scores_url = ua_body['_links']['ua:scores']['href']
        salaries_url = ua_body['_links']['ua:salaries']['href']
        print("Found data about urban area")
        pygame.time.wait(1000)
    
    # Time
        tz_response = requests.get(city_body['_links']['city:timezone']['href'])
        tz_body = tz_response.json()
        time_response = requests.get(tz_body['_links']['tz:offsets-now']['href'])
        time_body = time_response.json()
        city_dict['tz'] = time_body['short_name']
        print("Found timezone")
        pygame.time.wait(1000)
    
    # Salary
        sa_response = requests.get(salaries_url)
        sa_body = sa_response.json()
        salaries = sa_body['salaries']
        SD = [[],[],[]]
        for job in salaries:
            job_name = job['job']['title']
            p25 = job['salary_percentiles']['percentile_25']
            p50 = job['salary_percentiles']['percentile_50']
            p75 = job['salary_percentiles']['percentile_75']
            SD[0].append((job_name, p25))
            SD[1].append((job_name, p50))
            SD[2].append((job_name, p75))
        city_dict['salary_data'] = SD
        print("Found salary data")
        pygame.time.wait(1000)

    
    # Scores
        sc_response = requests.get(scores_url)
        sc_body = sc_response.json()
        categories = sc_body['categories']
        summary = sc_body['summary']
        summary = summary.replace('<p>', '')
        summary = summary.replace('</p>', '')
        summary = summary.replace('<b>', '')
        summary = summary.replace('</b>', '')
        total_score = sc_body['teleport_city_score']
        city_dict['ua']['summary'] = summary
        city_dict['ua']['score'] = total_score
        city_dict['ua']['categories'] = categories
        print("Found scores")
        pygame.time.wait(1000)
    
    # Details
        detail_url = ua_body['_links']['ua:details']['href']
        detail_response = requests.get(detail_url)
        detail_body = detail_response.json()
        city_dict['ua']['details'] = detail_body['categories']
        print("Found details")
        pygame.time.wait(1000)
    
    # Country
        country_link = None
        city_dict['country'] = None
        country_name = city_dict['name'].split(', ')[2]
        if "(" in country_name:
            country_name = country_name.split(' (')[0]
        for country in ua_body['_links']['ua:countries']:
            if country['name'] == city_dict['name'].split(', ')[2]:
                country_link = country['href']
                city_dict['country'] = country['name']
        if isinstance(country_link, type(None)):
            city_dict['country'] = None
            print("Could not find country data")
        else:
            country_response = requests.get(country_link)
            country_body = country_response.json()
            city_dict['iso_alpha_2'] = country_body['iso_alpha2']
            city_dict['iso_alpha_3'] = country_body['iso_alpha3']
            city_dict['currency'] = country_body['currency_code']
            city_dict['country pop'] = country_body['population']
            print("Found country data")
    except KeyError:
        print("An error has occurred while searching")
        print("It may be due to the api not having enough data")
    pygame.time.wait(1000)
    

# Print output
print(output)
for i, e in enumerate(cities):
    print(str(i+1) + ": " + e['name'])
    
    # print alternative names
    try:
        if e['alt_names'] != []:
            print("\nAlternative names: ")
            for name in e['alt_names']:
                print('\t' + name)
    except KeyError:
        print()
    
    # print location
    try:
        print("\nLocation: ")
        print('\t' + str(e['latlon']))
    except KeyError:
        print()
    
    # print population
    try:
        print("\nPopulation: " + str(e['population']))
    except KeyError:
        print()
    
    # print time
    try:
        print("\nTimezone: " + e['tz'])
    except KeyError:
        print()
    
    print("="*20)
    try:
        print(e['ua']['name'])
        print("Mayor: " + e['ua']['mayor'])
        print()
        print(e['ua']['summary'])
    except KeyError:
        print()
    
    print()
    try:
        inp = input("Print all salary data? (y/n)")
        while inp not in ['y','n']:
            inp = input("Enter y or n")
        if inp == 'y':
            for i in range(len(e['salary_data'][0])):
                print(e['salary_data'][0][i][0])
                print('\tPercentile 25: ' + str(e['salary_data'][0][i][1]))
                print('\tPercentile 50: ' + str(e['salary_data'][1][i][1]))
                print('\tPercentile 75: ' + str(e['salary_data'][2][i][1]))
                pygame.time.wait(100)
        
        h_75 = ("",None)
        h_50 = ("",None)
        h_25 = ("",None)
        l_75 = ("",None)
        l_50 = ("",None)
        l_25 = ("",None)
        for i in range(len(e['salary_data'][0])):
            job_name = e['salary_data'][0][i][0]
            p25 = e['salary_data'][0][i][1]
            p50 = e['salary_data'][1][i][1]
            p75 = e['salary_data'][2][i][1]
            data25 = (job_name, p25)
            data50 = (job_name, p50)
            data75 = (job_name, p75)
            if i == 0:
                h_75 = l_75 = data75
                h_50 = l_50 = data50
                h_25 = l_25 = data25
            else:
                h_25 = return_higher(h_25, data25)
                h_50 = return_higher(h_50, data50)
                h_75 = return_higher(h_75, data75)
                l_25 = return_lower(l_25, data25)
                l_50 = return_lower(l_50, data50)
                l_75 = return_lower(l_75, data75)
                
        print("Highest 25%: " + str(h_25))
        print("Highest 50%: " + str(h_50))
        print("Highest 75%: " + str(h_75))
        print("Lowest 25%: " + str(l_25))
        print("Lowest 50%: " + str(l_50))
        print("Lowest 75%: " + str(l_75))
        print()
    except KeyError:
        print()
    
    try:
        print("Scores (out of 10): ")
        for score in e['ua']['categories']:
            print(score['name'] + ':\t' + str(score['score_out_of_10']))
            print()
    except KeyError:
        print()
    print()
    print("="*20)
    try:
        print("Details: ")
        for i, data in enumerate(e['ua']['details']):
            print(str(i+1)+": "+data['label'])
        inp = input("Which information do you want? ")
        print()
        if inp != "" and inp in [str(i+1) for i in range(len(e['ua']['details']))]:
            data = e['ua']['details'][int(inp)-1]['data']
            for each in data:
                keys = list(each.keys())
                try:
                    keys.remove("id")
                except ValueError:
                    continue
                try:
                    keys.remove("label")
                except ValueError:
                    continue
                try:
                    keys.remove("type")
                except ValueError:
                    continue
                value = keys[0]
                value = each[value]
                print(each['label'])
                print(value)
                print()
    except KeyError:
        print()
    print()
    print('='*20)
    try:
        if isinstance(e['country'], type(None)):
            print("Count not find country data")
        else:
            print(e['country'])
            print("ISO Alpha-2: " + city_dict['iso_alpha_2'])
            print("ISO Alpha-3: " + city_dict['iso_alpha_3'])
            print()
            print("Currency: " + city_dict['currency'])
            print("Population: " + str(city_dict['country pop']))
    except KeyError:
        print()
    
    print()
    print()
    print()
