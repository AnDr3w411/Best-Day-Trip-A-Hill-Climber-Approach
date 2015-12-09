from Tkinter import *
from googleplaces import GooglePlaces, types
import googlemaps
import random
import copy


def run():
    interests = []
    if zooVar.get():
        interests.append(['Zoo', types.TYPE_ZOO])
    if museumVar.get():
        interests.append(['Museum', types.TYPE_MUSEUM])
    if bowlingVar.get():
        interests.append(['Bowling Alley', types.TYPE_BOWLING_ALLEY])
    if aquariumVar.get():
        interests.append(['Aquarium', types.TYPE_AQUARIUM])
    if historicVar.get():
        interests.append(['Historic Site', types.TYPE_POINT_OF_INTEREST])
    if artVar.get():
        interests.append(['Art Gallery', types.TYPE_ART_GALLERY])
    if cemeteryVar.get():
        interests.append(['Cemetery', types.TYPE_CEMETERY])
    if libraryVar.get():
        interests.append(['Library', types.TYPE_LIBRARY])

    hillclimber(apiText.get(), originEntry.get(), interests)


root = Tk()
root.minsize(width=300, height=500)

apiLabel = Label(root, text="API Key:")
apiText = Entry(root, width=50)
originLabel = Label(root, text="Origin Address:")
originEntry = Entry(root, width=50)
computeBtn = Button(root, text="Compute", command=run)
output = Text(root, height=18)


intrestsLabel = Label(root, text="Interests")
zooVar = IntVar()
museumVar = IntVar()
bowlingVar = IntVar()
aquariumVar = IntVar()
historicVar = IntVar()
artVar = IntVar()
cemeteryVar = IntVar()
libraryVar = IntVar()

zooCB = Checkbutton(root, text="Zoo", variable=zooVar)
museumCB = Checkbutton(root, text="Museum", variable=museumVar)
bowlingCB = Checkbutton(root, text="Bowling Ally", variable=bowlingVar)
aquariumCB = Checkbutton(root, text="Aquarium", variable=aquariumVar)
historicCB = Checkbutton(root, text="Historic Site", variable=historicVar)
artCB = Checkbutton(root, text="Art Gallery", variable=artVar)
cemeteryCB = Checkbutton(root, text="Cemetery", variable=cemeteryVar)
libraryCB = Checkbutton(root, text="Library", variable=libraryVar)


apiLabel.grid(row=0, sticky=E)
apiText.grid(row=0, column=1, columnspan=4)
originLabel.grid(row=1, sticky=E)
originEntry.grid(row=1, column=1, columnspan=4)
intrestsLabel.grid(row=2, columnspan=4)
zooCB.grid(row=3, sticky=W)
museumCB.grid(row=3, column=1, sticky=W)
bowlingCB.grid(row=4, sticky=W)
aquariumCB.grid(row=4, column=1, sticky=W)
historicCB.grid(row=5, sticky=W)
artCB.grid(row=5, column=1, sticky=W)
cemeteryCB.grid(row=3, column=2, sticky=W)
libraryCB.grid(row=4, column=2, sticky=W)


computeBtn.grid(row=6)
output.grid(row=7, columnspan=3)

timeDict = {}

def hillclimber(api_key, origin, interests):
    google_places = GooglePlaces(api_key)
    gmaps = googlemaps.Client(key=api_key)

    random.seed()
    originGeo = gmaps.geocode(origin)
    originGeo = origin
    # originGeo = (40.7593192, -111.8973234)
    # originGeo = (37.7548009, -122.460783)
    print originGeo
    radius = 20000
    trip_length = 5
    trip = []
    allPlaces = []

    # keywords = [['Museum', types.TYPE_MUSEUM], ['Aquarium', types.TYPE_AQUARIUM],
    #            ['Zoo', types.TYPE_ZOO], ['Historic Site', types.TYPE_POINT_OF_INTEREST],
    #            ['Bowling Alley', types.TYPE_BOWLING_ALLEY]]
    keywords = interests

    query_result = ''
    for keyword in keywords:
        query_result = google_places.nearby_search(location=originGeo, keyword=keyword[0], radius=radius, types=keyword[1])
        if query_result.has_attributions:
            print query_result.html_attributions

        for place in query_result.places:
            place.get_details()
            # cut out the unrated places and places with a lower rating to save on googleAPI queries
            if isinstance(place.rating, float) or isinstance(place.rating, int):
                if place.rating > 3:
                    allPlaces.append(place)
    for i in range(0, trip_length):
        trip.append(allPlaces[i])

    for place in trip:
        allPlaces.remove(place)


    def happiness_function(rating1, rating2, time1, time2):
        if rating1 < rating2 and (time1 + 600) >= time2:
            # print "Change Made:"
            # print "Old rating: ", rating1, " New Rating: ", rating2
            # print "Old time: ", time1, " New Time: ", time2
            return True
        else:
            return False

    print len(trip), "allPlace size: ", len(allPlaces)
    print "Original Trip:"
    totalRating = 0
    totalTime = 0
    last_location = originGeo
    last_loc_name = 'origin'
    for place in trip:
        # Returned places from a query are place summaries.
        print place.name
        # print place.geo_location
        print gmaps.reverse_geocode(place.geo_location)[0]['formatted_address']
        print place.rating
        if isinstance(place.rating, float) or isinstance(place.rating, int):
            totalRating += place.rating
        else:
            place.rating = 2.7
            totalRating += place.rating

        if last_loc_name+place.name in timeDict:
            totalTime += timeDict[last_loc_name+place.name]
        elif place.name+last_loc_name in timeDict:
            totalTime += timeDict[place.name+last_loc_name]
        else:
            new_distance = gmaps.distance_matrix(last_location, place.geo_location)
            totalTime += new_distance['rows'][0]['elements'][0]['duration']['value']
            timeDict[last_loc_name+place.name] = new_distance['rows'][0]['elements'][0]['duration']['value']

        last_location = place.geo_location
        last_loc_name = place.name
        print

    if last_loc_name+'origin' in timeDict:
        totalTime += timeDict[last_loc_name+'origin']
    elif 'origin'+last_loc_name in timeDict:
        totalTime += timeDict['origin'+last_loc_name]
    else:
        new_distance = gmaps.distance_matrix(last_location, originGeo)
        totalTime += new_distance['rows'][0]['elements'][0]['duration']['value']
        timeDict[last_loc_name+'origin'] = new_distance['rows'][0]['elements'][0]['duration']['value']

    print "Average Rating: ", totalRating/len(trip)
    print "Total Time: ", totalTime
    running = True
    best_trip = copy.deepcopy(trip)
    best_time = totalTime
    best_rating = totalRating
    totalRating = 0
    totalRating = 0
    noBetterCount = 0
    while noBetterCount < 1000:

        done = False
        distance = 0
        rating = 3
        last_location = 0
        count = 0

        while not done:
            done = True
            count += 1
            last_location = originGeo
            last_loc_name = 'origin'
            for i in range(0, len(trip)):
                if last_loc_name+trip[i].name in timeDict:
                    my_time = timeDict[last_loc_name+trip[i].name]
                elif trip[i].name+last_loc_name in timeDict:
                    my_time = timeDict[trip[i].name+last_loc_name]
                else:
                    my_distance = gmaps.distance_matrix(trip[i].geo_location, last_location)
                    my_time = my_distance['rows'][0]['elements'][0]['duration']['value']
                    timeDict[last_loc_name+place.name] = my_time
                # beginning and ending point of round trip
                for j in range(0, len(allPlaces)):
                    if i == 0 or i == len(trip)-1:
                        if trip[i].name+'origin' in timeDict:
                            new_time = timeDict[trip[i].name+'origin']
                        elif 'origin'+trip[i].name in timeDict:
                            new_time = timeDict['origin'+trip[i].name]
                        else:
                            new_distance = gmaps.distance_matrix(originGeo, trip[i].geo_location)
                            new_time = new_distance['rows'][0]['elements'][0]['duration']['value']
                            timeDict['origin'+trip[i].name] = new_time
                    else:
                        if last_loc_name+allPlaces[j].name in timeDict:
                            new_time = timeDict[last_loc_name+allPlaces[j].name]
                        elif allPlaces[j].name+last_loc_name in timeDict:
                            new_time = timeDict[allPlaces[j].name+last_loc_name]
                        else:
                            new_distance = gmaps.distance_matrix(last_location, allPlaces[j].geo_location)
                            new_time = new_distance['rows'][0]['elements'][0]['duration']['value']
                            timeDict[last_loc_name+allPlaces[j].name] = new_time
                    if happiness_function(trip[i].rating, allPlaces[j].rating, my_time, new_time):
                        allPlaces.append(trip[i])
                        trip[i] = allPlaces[j]
                        del allPlaces[j]
                        my_time = new_time
                        j -= 1
                        done = False
                last_location = trip[i].geo_location
                last_loc_name = trip[i].name
            totalTime = 0
            totalRating = 0
            last_location = originGeo
            last_loc_name = 'origin'
            for place in trip:
                # print place.name
                # print place.geo_location
                # print place.rating
                # print
                totalRating += place.rating
                if last_loc_name+place.name in timeDict:
                    totalTime += timeDict[last_loc_name+place.name]
                elif place.name+last_loc_name in timeDict:
                    totalTime += timeDict[place.name+last_loc_name]
                else:
                    new_distance = gmaps.distance_matrix(last_location, place.geo_location)
                    totalTime += new_distance['rows'][0]['elements'][0]['duration']['value']
                    timeDict[last_loc_name+place.name] = new_distance['rows'][0]['elements'][0]['duration']['value']
                last_loc_name = place.name
                last_location = place.geo_location

            # print totalTime
            # print totalRating
            if done:
                # print "Finished after ", count, " loops"
                print "Time: ", totalTime
                print "Average Rating: ", totalRating / len(trip)
            if count >= 20:
                # print "ran", count, " times"
                done = True
        if best_rating <= totalRating and best_time > totalTime:
            best_trip = copy.deepcopy(trip)
            best_rating = totalRating
            best_time = totalTime
            noBetterCount = 0
            print "New Best!!!"
            print
        elif best_rating < totalRating and best_time+600 >= totalTime:
            best_trip = copy.deepcopy(trip)
            best_rating = totalRating
            best_time = totalTime
            noBetterCount = 0
            print "New Best!!!"
            print
        else:
            noBetterCount += 1
            print "No better count: ", noBetterCount
            print

        for place in trip:
            allPlaces.append(place)
        trip_length = len(trip)
        trip = []
        for i in range(0, trip_length):
            j = random.randint(0, len(allPlaces)-1)
            trip.append(allPlaces[j])
            del allPlaces[j]

    best_rating = 0
    output_str = ""
    print "The final trip"
    for place in best_trip:
        print place.name
        address = gmaps.reverse_geocode(place.geo_location)[0]['formatted_address']
        print address
        print place.rating
        print
        best_rating += place.rating
        output_str += place.name + "  " + str(place.rating) + "\n" + address + '\n\n'
    print "Average Rating: ", best_rating/len(best_trip)
    print "Total Time: ", best_time
    print "timeDict Length: ", len(timeDict)

    output_str += "Average Rating: " + str(best_rating/len(best_trip)) + "\nTotal Time: " + str(best_time) + '\n'
    output.insert('1.0', output_str)

root.mainloop()
