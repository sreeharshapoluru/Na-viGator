"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from math import isinf
import json, time
import random

# Helper script

def size(int_type):
   length = 0
   count = 0
   while (int_type):
       count += (int_type & 1)
       length += 1
       int_type >>= 1
   return count

def length(int_type):
   length = 0
   count = 0
   while (int_type):
       count += (int_type & 1)
       length += 1
       int_type >>= 1
   return length

def inSubset(i, s):
	while i > 0 and s > 0:
		s = s >> 1
		i -= 1
	cond = s & 1
	return cond

def remove(i, s):
	x = 1
	x = x << i
	l = length(s)
	l = 2 ** l - 1
	x = x ^ l
	#print ( "i - %d x - %d  s - %d x&s -  %d " % (i, x, s, x & s) )
	return x & s

def findPath(p):
	n = len(p[0])
	number = 2 ** n - 2
	prev = p[number][0]
	path = []
	while prev != -1:
		path.append(prev)
		number = remove(prev, number)
		prev = p[number][prev]
	reversepath = [str(path[len(path)-i-1]+1) for i in range(len(path))]
	reversepath.append("1")
	reversepath.insert(0, "1")
	return reversepath



def generateSubsets(n):
	l = []
	for i in range(2**n):
		l.append(i)
		#print(i)
	return sorted(l, key = lambda x : size(x) )


def tsp(a):
	
	n = len(a)
	l = generateSubsets(n)
	#print(l)
	cost = [ [-1 for city in range(n)] for subset in l]
	p = [ [-1 for city in range(n)] for subset in l]

	t1 = time.time()
	count = 1
	total = len(l)
	for subset in l:
		for dest in range(n):
			if not size(subset):
				cost[subset][dest] = a[0][dest]
				#p[subset][dest] = 0
			elif (not inSubset(0, subset)) and (not inSubset(dest, subset)) :
				mini = float("inf")
				for i in range(n):
					if inSubset(i, subset):
						modifiedSubset = remove(i, subset)
						val = a[i][dest] + cost[modifiedSubset][i]
						
						if val < mini:
							mini = val
							p[subset][dest] = i

				if not isinf(mini):
					cost[subset][dest] = mini
		count += 1
	global path
	path = findPath(p)
	t2 = time.time()
	diff = t2 - t1
	#print(a)
	path = [int(item)-1 for item in path]		 
	#print(path)
	#print(" => ".join(path))

	Cost = cost[2**n-2][0]
	return path,cost
	
	
## ----------------Google Integration----------------------
#---google API----
def getTime(cityName="Miami",numPlaces=3):
    cityName = cityName.lower()
    #print "fsd"
    import urllib,json
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?&query=places+of+interest+in+"+cityName+"&key=AIzaSyA2zun4OauTlifm33u0eRgT0V381pvSU0c"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    
    #return data,3
    
    places = [0 for x in range(numPlaces)]
    for i in range(numPlaces):
        places[i] = data['results'][i]['name']
    #print places
    timers = [[0 for x in range(numPlaces)] for y in range(numPlaces)]
    for i in range(numPlaces):
        for j in range(numPlaces):
            if i!=j:
                url2 = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+places[i]+","+cityName+"&destinations="+places[j]+","+cityName+"&key=AIzaSyB4uvkSAs443BkUh4Y7nj_2f9G8L8vmbxw"
                response2=urllib.urlopen(url2)
                data2 = json.loads(response2.read())
                
                #print data2['rows'][0]['elements'][0]['duration']['value']
                timers[i][j] = int(data2['rows'][0]['elements'][0]['duration']['value'])/60.0
    #places = unicode(places,"UTF-8")
    return places,timers
    
# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Itenary. . " \
                    "Please tell me where you want to go to and how many places you have in your mind? "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me how many places you want to plan the trip for?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Itenary. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def create_number_attributes(number):
    return {"number" : number}
    
def create_city_attributes(city):
    return {"city" : city}    

#session_attributes = {}

def set_number_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """
    if session.has_key('attributes'):
        session_attributes = session['attributes']
    else:
        session_attributes = {}
    card_title = intent['name']
    should_end_session = False
        
    if ('value' in intent['slots']['number'].keys() and 'value' in  intent['slots']['city'].keys()):
        number = intent['slots']['number']['value']
        city = intent['slots']['city']['value']
        session_attributes['number'] = number
        session_attributes['city'] = city
        speech_output = "You want to go to " + city + " and visit " + \
                        number + \
                        " places. Right?"
        reprompt_text = "Please tell me how many places you want to plan the trip for?"
    elif 'value' in intent['slots']['number'].keys():
        number = intent['slots']['number']['value']
        #session_attributes['number'] = number
        session_attributes.update(create_number_attributes(number))
        if session.get('attributes', {}) and "city" in session.get("attributes", {}):
            city = session['attributes']['city']
            #session_attributes = create_number_attributes(city)
            speech_output = "You want to go to " + city + " and visit " + number + " places. Right?"
            reprompt_text = "Please tell me how many places you want to plan the trip for?"
        else:
            speech_output = "Okay, you want to visit " + number + " places. Can you tell me in which city?"
            reprompt_text = "In which city?"
    elif 'value' in intent['slots']['city'].keys():
        city = intent['slots']['city']['value']
        #session_attributes['city'] = city
        session_attributes.update(create_city_attributes(city))
        if session.get('attributes', {}) and "number" in session.get("attributes", {}):
            number = session['attributes']['number']
            #session_attributes = create_number_attributes(number)
            speech_output = "You want to go to " + city + " and visit " + number + " places. Right?"
            reprompt_text = "Please tell me how many places you want to plan the trip for?"
        else:
            speech_output = "Okay, you want to visit " + city + ". Can you tell me how many places you want to visit?"
            reprompt_text = "How many places?"
    else:
        speech_output = "Sorry, Can you tell me which city do you want to visit and how many places?"
        reprompt_text = "Sorry, Can you tell me which city do you want to visit and how many places?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_number_from_session(intent, session):
    #print("sdfcd")
    session_attributes = {}
    reprompt_text = None
    if session.get('attributes', {}) and "number" in session.get('attributes', {}) and "city" in session.get('attributes', {}):
        number = session['attributes']['number']
        city = session['attributes']['city']
        places,timers = getTime(city,int(number))
        speech_output = "!!".join(places)
        #places 
        path,cost = tsp(timers)
        #cost = 0
        #= tsp(time)
        place = "If you start now from "+ places[path[0]] + "now, it takes "
        for s in range(len(path)-1):
          place += str(round(timers[path[s]][path[s+1]],2)) + " minutes to reach "+ places[path[s+1]]+" from there and  "
        place = place[:-16]
        speech_output = "Your itenary is  " + place +"."+ \
                       ". Goodbye."
        #speech_output = "hello"
        should_end_session = True
    else:
        speech_output = "I'm not sure how many places or city you want to plan the trip for. Can you please tell me the name of the city and number of places you want to visit? "
        should_end_session = False
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))




# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "CityIntent":
        return set_number_in_session(intent, session)
    elif intent_name == "WhatsMyItenaryIntent":
        return get_number_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    #print("event.session.application.applicationId=" +
         # event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])




