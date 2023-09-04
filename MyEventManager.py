# Make sure you are logged into your Monash student account.
# Go to: https://developers.google.com/calendar/quickstart/python
# Click on "Enable the Google Calendar API"
# Configure your OAuth client - select "Desktop app", then proceed
# Click on "Download Client Configuration" to obtain a credential.json file
# Do not share your credential.json file with anybody else, and do not commit it to your A2 git repository.
# When app is run for the first time, you will need to sign in using your Monash student account.
# Allow the "View your calendars" permission request.
# can send calendar event invitation to a student using the student.monash.edu email.
# The app doesn't support sending events to non student or private emails such as outlook, gmail etc
# students must have their own api key
# no test cases for authentication, but authentication may required for running the app very first time.
# http://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.html


# Code adapted from https://developers.google.com/calendar/quickstart/python
from __future__ import print_function
import json
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

months = {
    "JAN": "01",
    "FEB": "02",
    "MAR": "03",
    "APR": "04",
    "MAY": "05",
    "JUN": "06",
    "JUL": "07",
    "AUG": "08",
    "SEP": "09",
    "OCT": "10",
    "NOV": "11",
    "DEC": "12"
}
HOUR_ADJUSTMENT = "+10:00"
MAX_YEAR = 2050


def get_calendar_api():
    """
    Get an object which allows you to consume the Google Calendar API.
    You do not need to worry about what this function exactly does, nor create test cases for it.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


class EventManager:
    def __init__(self, api):
        self.api = api

    def get_upcoming_events(self, starting_time, number_of_events):
        """
        Shows basic usage of the Google Calendar API.
        Prints the start and name of the next n events on the user's calendar.
        """
        if number_of_events <= 0:
            raise ValueError("Number of events must be at least 1.")

        events_result = self.api.events().list(calendarId='primary', timeMin=starting_time,
                                               maxResults=number_of_events, singleEvents=True,
                                               orderBy='startTime').execute()

        return events_result.get('items', [])

    def add_new_events(self, name, location, attendees, date, time):
        """
        Takes in VALIDATED user inputs and create an event to inserted into the calendar.
        """
        date[0] = convert_date_string(date[0])
        date[1] = convert_date_string(date[1])

        start_datetime = format_dateTime(date[0], time[0])
        end_datetime = format_dateTime(date[1], time[1])

        event = {
            'summary': name,
            'location': location,
            'start': {
                'dateTime': start_datetime,
                'timeZone': 'Australia/Melbourne',
            },
            'end': {
                'dateTime': end_datetime,
                'timeZone': 'Australia/Melbourne',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            }
        }

        event = self.api.events().insert(calendarId='primary', body=event, maxAttendees=20).execute()
        print('Event created: %s' % (event.get('summary')))

        return event

    def get_events_from_year(self, year):
        """
        Return a list of all the events from a specified year
        """
        time_min = f"{year}-01-01T00:00:00{HOUR_ADJUSTMENT}"
        time_max = f"{year}-12-31T23:59:59{HOUR_ADJUSTMENT}"
        events_response = self.api.events().list(calendarId="primary", singleEvents=True,
                                                 orderBy="startTime", timeMin=time_min,
                                                 timeMax=time_max).execute()
        return events_response.get("items", [])

    def get_past_events(self):
        """
        Get events up to 5 years in the past
        """
        time_max = datetime.datetime.utcnow().isoformat() + HOUR_ADJUSTMENT
        time_min = f"{str(int(time_max[:4]) - 5)}{time_max[4:]}"
        events_response = self.api.events().list(calendarId="primary", singleEvents=True,
                                                 orderBy="startTime", timeMin=time_min,
                                                 timeMax=time_max).execute()
        return events_response

    def get_cancelled_past_events(self):
        """
        Get all events, including cancelled events up to 5 years in the past.
        """
        time_max = datetime.datetime.utcnow().isoformat() + HOUR_ADJUSTMENT
        time_min = f"{str(int(time_max[:4]) - 5)}{time_max[4:]}"
        events_response = self.api.events().list(calendarId="primary", singleEvents=True,
                                                 orderBy="startTime", timeMin=time_min,
                                                 timeMax=time_max, showDeleted=True).execute()
        return events_response

    def get_future_events(self):
        """
        Get all events up to 5 years in the future
        """
        time_min = datetime.datetime.utcnow().isoformat() + HOUR_ADJUSTMENT
        time_max = f"{str(int(time_min[:4]) + 5)}{time_min[4:]}"
        events_response = self.api.events().list(calendarId="primary", singleEvents=True,
                                                 orderBy="startTime", timeMin=time_min,
                                                 timeMax=time_max).execute()
        return events_response

    def delete_event(self, event):
        """
        Deletes an event from the calendar
        """
        if event is not None:
            time_now = datetime.datetime.now().isoformat()
            time_now = datetime.datetime.fromisoformat(time_now)
            event_time = datetime.datetime.fromisoformat(event["start"]["dateTime"].split("+")[0])
            time_diff = time_now - event_time
            if time_diff.days > 0:
                event_id = event["id"]
                self.api.events().delete(calendarId="primary", eventId=event_id).execute()
                print("Event: ", event["summary"], " - Successfully Deleted")
            else:
                return "Cannot delete a present or future event."
        else:
            return "There are no events to delete."

    def cancel_event(self, event):
        """
        Cancel an event, can be restored
        """
        event_id = event["id"]
        event["status"] = "cancelled"
        cancelled = self.api.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        print(f"Successfully cancelled event `{event['summary']}`")
        return cancelled

    def restore_event(self, event):
        """
        Restore a cancelled event
        """
        event_id = event["id"]
        event["status"] = "confirmed"
        restored = self.api.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        print(f"Successfully restored event `{event['summary']}`")
        return restored

    def change_organizer(self):
        """
        Reassign the organizer of an event
        """
        events_response = self.get_future_events()
        items = events_response.get("items", [])

        if not items:
            print("No events found.")
        else:
            print_events(items)
            event_index = int(input("Please select an event to reassign organizer: ")) - 1
            event = events_response["items"][event_index]
            event_id = event["id"]

            assignee = input("Please enter the email address of the new organizer: ")

            # First retrieve the event from the API.
            event = self.api.events().move(
                calendarId='primary', eventId=event_id,
                destination=assignee).execute()

            print("New Organizer: ", event["organizer"]["email"])

    def search_by_keyword(self, keyword):
        """
        Search through events past and future that contain the keyword searched
        """
        events_response1 = self.get_past_events()
        past_events = events_response1.get("items", [])
        events_response2 = self.get_future_events()
        future_events = events_response2.get("items", [])
        if past_events:
            for event in past_events:
                if keyword in event["summary"]:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    date_time = start.split("T", 1)
                    print(date_time[0], date_time[1][:5], event['summary'])

        if future_events:
            for event in future_events:
                if keyword in event["summary"]:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    date_time = start.split("T", 1)
                    print(date_time[0], date_time[1][:5], event['summary'])

        if not past_events and not future_events:
            print("No events found.")

    def import_event(self):
        """
        Import a JSON file containing event details
        """
        file_name = open(input("Enter the JSON file name containing the event details: "))
        json_data = json.load(file_name)
        event_id = json_data["id"]
        name = json_data["summary"]
        location = json_data["location"]
        start_dateTime = json_data["start"]["dateTime"]
        end_dateTime = json_data["end"]["dateTime"]
        organizer_email = json_data["organizer"]["email"]
        attendees = json_data["attendees"]
        event = {
            'summary': name,
            'location': location,
            'organizer': {
                'email': organizer_email,
            },
            'start': {
                'dateTime': start_dateTime
            },
            'end': {
                'dateTime': end_dateTime
            },
            'attendees': attendees,
            'reminders': {'useDefault': True},
            'iCalUID': event_id
        }

        imported_event = self.api.events().import_(calendarId='primary', body=event).execute()
        file_name.close()

        print(f"Successfully imported event `{imported_event['summary']}`")

    def export_event(self, event, json_filename):
        """
        Exporting an event as a JSON file
        """
        with open(json_filename, "w") as outfile:
            json.dump(event, outfile)
            print(f"Successfully export event `{event['summary']}`")


def create_event():
    """
    Takes in and validate multiple user inputs upon event creation
    """
    name = input("Please provide a name for your event: ")
    location = input("Please enter the location for your event: ")
    attendees = []
    attendee = None
    while attendee != "" and len(attendees) < 20:
        attendee = input("Please the email address of an attendee (press enter if you are finished): ")
        if attendee == "":
            continue
        x = attendee.split("@")
        y = x[1].split(".")
        if "monash" in y and "edu" in y:
            attendees.append(attendee)
        else:
            attendee = None
            print("Attendee does not belong your native domain.")
        if len(attendees) == 20:
            print("You have added the maximum number of attendees.")

    attendees_lst = []
    for attendee in attendees:
        item = {"email": attendee}
        attendees_lst.append(item)

    start_date = ""
    while len(start_date) != 10:
        start_date = input("Please enter the starting date of your event (YYYY-MM-DD/DD-MON-YY): ")
        start_date = convert_date_string(start_date)
        if int(start_date[:4]) > 2050:
            start_date = ""
            print("Unable to create events beyond the year 2050.")
            continue

        date_now = datetime.date.fromisoformat(datetime.datetime.now().isoformat()[:10])
        input_date = datetime.date.fromisoformat(start_date)
        if date_now > input_date:
            start_date = ""
            print("Unable to create events in the past.")

    start_time = ""
    while len(start_time) != 5:
        start_time = input("Please enter the starting time for your event in 24-hour format (23:59): ")
        try:
            x = start_time.split(":")
            y = int(x[0])
            if len(x[0]) != 2 or len(x[1]) != 2:
                start_time = ""
                print("Please enter the time in 24-hour format as prompted.")
        except:
            start_time = ""
            print("Invalid input.")

    end_date = ""
    while len(end_date) != 10:
        end_date = input("Please enter the ending date of your event (YYYY-MM-DD/YYYY-MON-DD): ")
        end_date = convert_date_string(end_date)
        input_start_date = datetime.date.fromisoformat(start_date)
        input_end_date = datetime.date.fromisoformat(end_date)
        if input_end_date < input_start_date:
            end_date = ""
            print("The ending date must be on or after the starting date.")

    end_time = ""
    while len(end_time) != 5:
        end_time = input("Please enter the ending time for your event in 24-hour format (i.e. 23:59): ")
        try:
            x = end_time.split(":")
            y = int(x[0])
            if len(x[0]) != 2 or len(x[1]) != 2:
                end_time = ""
                print("Please enter the time in 24-hour format as prompted.")
                continue
        except:
            end_time = ""
            print("Invalid input.")
            continue

        start_dateTime = datetime.datetime.fromisoformat(format_dateTime(start_date, start_time))
        end_dateTime = datetime.datetime.fromisoformat(format_dateTime(end_date, end_time))
        if end_dateTime <= start_dateTime:
            end_time = ""
            print("The ending time must be after starting time.")

    date = [start_date, end_date]
    time = [start_time, end_time]
    valid_inputs = [name, location, attendees_lst, date, time]
    return valid_inputs


def convert_date_string(date_string):
    """
    Converts a DD-MON-YY date string to a YYYY-MM-DD date string so that it can be used
    """
    if len(date_string) == 9:
        return f"20{date_string[7:9]}-{months[date_string[3:6]]}-{date_string[:2]}"
    else:
        return date_string


def format_dateTime(date, time):
    """
    Format datetime with GMT adjustment
    """
    return f"{date}T{time}:00{HOUR_ADJUSTMENT}"


def get_user_keyword():
    """
    Get the user input for keyword to be searched
    """
    return input("Please enter a keyword to search for: ")


def get_event_to_delete(events_response):
    """
    Get the event to be deleted by printing all available events and asking for user input
    Is also used for cancelling events.
    """
    events = events_response.get("items", [])
    if not events:
        print("No events found.")
        return None
    else:
        print_events(events)
        event_index = int(input("Please select an event to delete/cancel: ")) - 1
        event = events_response["items"][event_index]
        return event


def get_event_to_restore(events_response):
    """
    Get the event to be restored by printing all cancelled events and asking for user input
    """
    events = events_response.get("items", [])
    if not events:
        print("No events found.")
        return None
    else:
        if not print_cancelled_events(events):
            event_index = int(input("Please select an event to restore: ")) - 1
            event = events_response["items"][event_index]
            return event


def get_event_to_export(events_response):
    """
    Get the event to be exported by printing all available events and asking for user input
    """
    events = events_response.get("items", [])
    if not events:
        print("No events found.")
        return None
    else:
        print_events(events)
        event_index = int(input("Please select an event to export: ")) - 1
        event = events_response["items"][event_index]
        return event


def print_cancelled_events(events):
    """
    Printing cancelled events in a formatted manner
    """
    print("-------------------------------------------------------------------------")
    for i in range(len(events)):
        if events[i]["status"] == "cancelled":
            start = events[i]['start'].get('dateTime', events[i]['start'].get('date'))
            date_time = start.split("T", 1)
            print(f"{i + 1}.", date_time[0], events[i]['summary'])
    print("-------------------------------------------------------------------------")


def print_events(events):
    """
    Printing events in a formatted manner
    """
    if not events:
        print("-------------------------------------------------------------------------")
        print('No events found.')
        print("-------------------------------------------------------------------------")
    else:
        print("-------------------------------------------------------------------------")
        for i in range(len(events)):
            start = events[i]['start'].get('dateTime', events[i]['start'].get('date'))
            date_time = start.split("T", 1)
            print(f"{i + 1}.", date_time[0], date_time[1][:5], f"GMT{date_time[1][8:14]}", events[i]['summary'])
        print("-------------------------------------------------------------------------")


def user_choice():
    """
    Getting user choice corresponding to what they want to do
    """
    print("Please select from the following options:")
    print("1. View upcoming events")
    print("2. Navigate the events by year")
    print("3. Search event by keyword")
    print("4. Create a new event")
    print("5. Change an event's organizer")
    print("6. Cancel an event")
    print("7. Restore an event")
    print("8. Delete an event")
    print("9. Import event from JSON file")
    print("10. Export event from calendar into a JSON file")
    print("11. Exit")

    choice = int(input("Please provide your selection as an integer: "))

    return choice


def main():
    """
    The main program UI (not tested in coverage)
    """
    api = get_calendar_api()
    time_now = datetime.datetime.utcnow().isoformat() + HOUR_ADJUSTMENT  # 'Z' indicates UTC time

    calendar = EventManager(api)
    choice = user_choice()  # Change to True before running. Set as False to test pipeline

    while choice != 11:
        if choice == 1:
            events = calendar.get_upcoming_events(time_now, 10)
            print_events(events)

        elif choice == 2:
            year = input("Please enter the year you wish to navigate to: ")
            events = calendar.get_events_from_year(year)
            print_events(events)

        elif choice == 3:
            keyword = get_user_keyword()
            calendar.search_by_keyword(keyword)

        elif choice == 4:
            inputs = create_event()
            event = calendar.add_new_events(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4])

        elif choice == 5:
            calendar.change_organizer()

        elif choice == 6:
            events_response = calendar.get_past_events()
            event = get_event_to_delete(events_response)
            if event is not None:
                calendar.cancel_event(event)

        elif choice == 7:
            events_response = calendar.get_cancelled_past_events()
            event = get_event_to_restore(events_response)
            if event is not None:
                calendar.restore_event(event)

        elif choice == 8:
            events_response = calendar.get_past_events()
            event = get_event_to_delete(events_response)
            if event is not None:
                calendar.delete_event(event)

        elif choice == 9:
            calendar.import_event()

        elif choice == 10:
            events_response = calendar.get_past_events()
            event = get_event_to_export(events_response)
            if event is not None:
                json_filename = input("Enter the name of file (with.json extension) to store events in: ")
                calendar.export_event(event, json_filename)

        else:
            print("Invalid input - please provide your selection as an integer listed above.")

        print()
        choice = user_choice()


# if __name__ == "__main__":  # Prevents the main() function from being called by the test suite runner
#     main()
