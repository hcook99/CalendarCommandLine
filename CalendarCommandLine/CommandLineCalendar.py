import datetime
import time
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os.path


SCOPES = 'https://www.googleapis.com/auth/calendar'


def main():
    # checks to see if credentials token is in directory for api information
    if not (os.path.isfile('credentials.json') or (os.path.isfile('token.json'))):
        f = open('credentials.json', 'x')
        clientId = input('Enter cilentID from google api: ')
        privateKey = input('Enter private key: ')
        credentialsJson = '{\"installed\":{\"client_id\":\"' + clientId + '\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://www.googleapis.com/oauth2/v3/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_secret\":\"' + privateKey + '\",\"redirect_uris\":[\"urn:ietf:wg:oauth:2.0:oob\",\"http://localhost\"]}}'
        f.write(credentialsJson)
        f.close()

    storeCreds = file.Storage('token.json')
    credentials = storeCreds.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, storeCreds)
    authenticate = build('calendar', 'v3', http=credentials.authorize(Http()))

    requestType = input('Would you like to add an event or view events for a day(add or get)')
    timeZones = time.tzname[0]

    # ask user for day to add event and summary of event and adds it to calendar if add is selected
    if requestType == 'add':
        dateStart = input('What day is the event(enter as month/day/year):')
        month, day, year = dateStart.split('/')
        dateStart = year + '-' + month + '-' + day + 'T'
        dateEnd = input('What day does the event end if same day just type same:')
        if dateEnd.lower() == 'same':
            dateEnd = dateStart
        else:
            month, day, year = dateEnd.split('/')
            dateEnd = year + '-' + month + '-' + day + 'T'
        timeDate = input('What time is the event(enter as 7:00 AM-7:00 PM):')
        timeStart, timeEnd = timeDate.split('-')

        timeStartIn = datetime.datetime.strptime(timeStart, '%I:%M %p')
        timeStartOut = datetime.datetime.strftime(timeStartIn, "%H:%M:%S")
        timeEndIn = datetime.datetime.strptime(timeEnd, '%I:%M %p')
        timeEndOut = datetime.datetime.strftime(timeEndIn, "%H:%M:%S")
        dateStart += timeStartOut
        dateEnd += timeEndOut
        summary = input('Summary of Event: ')
        event = {

            'summary': summary,

            'start': {
                'dateTime': dateStart,
                'timeZone': timeZones
            },
            'end': {
                'dateTime': dateEnd,
                'timeZone': timeZones
            }
        }
        event = authenticate.events().insert(calendarId='primary', body=event).execute()
        print('Created!')

    # if get is requested will get events for a day from calendar
    elif requestType == 'get':
        dateStart = input('What day\'s events would you like to see(enter as month/day/year):')
        month, day, year = dateStart.split('/')
        dateStart = year + '-' + month + '-' + day+'T00:00:00Z'
        dateTomorrow = datetime.datetime(int(year),int(month), int(day)) + datetime.timedelta(days=1)
        dateTomorrow = datetime.datetime.strftime(dateTomorrow,'%Y-%m-%d')
        dateTomorrow +='T00:00:00Z'
        eventsR = authenticate.events().list(calendarId='primary', timeMin=dateStart, timeMax=dateTomorrow, singleEvents=True, orderBy='startTime').execute()
        events = eventsR.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime')
            end = event['end'].get('dateTime')
            start = start.split('T')[1]
            start = start.split('-')[0]
            start = datetime.datetime.strptime(start,'%H:%M:%S')
            start = start.strftime('%I:%M %p')
            end = end.split('T')[1]
            end = end.split('-')[0]
            end = datetime.datetime.strptime(end, '%H:%M:%S')
            end = end.strftime('%I:%M %p')
            print(start + '-' + end, event['summary'])
    else:
        'Invalid response'


main()
