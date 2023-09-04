import datetime
import unittest
from unittest.mock import MagicMock, Mock, patch
import MyEventManager
from MyEventManager import *
import sys
from io import StringIO


# Add other imports here if needed


class MyEventManagerTestGet(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_get_upcoming_events_number(self):
        """
        This test case tests the inputs to get_upcoming_events() and check that the api method has been called
        successfully with the input passed into it
        """
        num_events = 2
        time = "2020-08-03T00:00:00.000000Z"

        events = self.calendar.get_upcoming_events(time, num_events)

        self.assertEqual(1, self.mock_api.events.return_value.list.return_value.execute.return_value.get.call_count)

        args, kwargs = self.mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(num_events, kwargs['maxResults'])

    def test_get_upcoming_events_none(self):
        """
        This test case tests the error handling of get_upcoming_events()
        """
        num_events = 0
        time = "2020-08-03T00:00:00.000000Z"
        with self.assertRaises(ValueError) as context:
            self.calendar.get_upcoming_events(time, num_events)

        self.assertTrue("Number of events must be at least 1." in str(context.exception))
        self.assertEqual(0, self.mock_api.events.return_value.list.return_value.execute.return_value.get.call_count)

    def test_get_past_events(self):
        """
        This test case tests that the api method is called successfully when getting past events
        """
        events = self.calendar.get_past_events()
        self.assertEqual(1, self.mock_api.events.return_value.list.return_value.execute.call_count)

    def test_get_past_events_5_years(self):
        """
        This test case tests that getting past events only gets events up to 5 years in the past
        """
        now = datetime.datetime.now().today().isoformat()

        past_date = f"{int(now[:4])-5}{now[4:10]}"

        events = self.calendar.get_past_events()
        args, kwargs = self.mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(past_date, kwargs['timeMin'][:10])

    def test_get_cancelled_past_events(self):
        """
        This test case tests that get_cancelled_past_events() successfully gets cancelled events as well as confirmed
        events by checking the showDeleted parameter in the api method
        """
        showDeleted = True
        events = self.calendar.get_cancelled_past_events()
        self.assertEqual(1, self.mock_api.events.return_value.list.return_value.execute.call_count)

        args, kwargs = self.mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(showDeleted, kwargs['showDeleted'])

    def test_get_future_events(self):
        """
        This test case tests that the api method is called successfully when getting future events
        """
        events = self.calendar.get_future_events()
        self.assertEqual(1, self.mock_api.events.return_value.list.return_value.execute.call_count)

    def test_get_future_events_5_years(self):
        """
        This test case tests that getting future events only get events up to 5 years in the future
        """
        current_date = datetime.datetime.now().today().isoformat()

        future_date = f"{int(current_date[:4])+5}{current_date[4:10]}"

        events = self.calendar.get_future_events()
        args, kwargs = self.mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(future_date, kwargs['timeMax'][:10])

    def test_navigate_by_year(self):
        """
        This test case tests the time range passed into the api method to get events are from the beginning
        of input year to the end of input year and that the api method is called successfully
        """
        current_date = datetime.date.today().isoformat()
        current_year = current_date[:4]
        self.calendar.get_events_from_year(current_year)
        self.assertEqual(1, self.mock_api.events.return_value.list.return_value.execute.call_count)

        args, kwargs = self.mock_api.events.return_value.list.call_args_list[0]
        start_of_year = f"{current_year}-01-01T00:00:00{HOUR_ADJUSTMENT}"
        end_of_year = f"{current_year}-12-31T23:59:59{HOUR_ADJUSTMENT}"
        self.assertEqual(start_of_year, kwargs["timeMin"])
        self.assertEqual(end_of_year, kwargs["timeMax"])

    def test_search_by_keyword(self):
        """
        This test case tests that the events with keyword searched are successfully listed when search_by_keyword() is
        called.
        """
        MyEventManager.get_user_keyword = MagicMock(return_value="keyword")
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.isoformat()
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        tomorrow = tomorrow.isoformat()
        event1 = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary with keyword',
                  'start': {'dateTime': yesterday}, 'reminders': {'useDefault': True}}
        event2 = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary with keyword',
                  'start': {'dateTime': tomorrow}, 'reminders': {'useDefault': True}}

        self.calendar.get_past_events = MagicMock(return_value={"items": [event1]})
        self.calendar.get_future_events = MagicMock(return_value={"items": [event2]})

        buff = StringIO()
        sys.stdout = buff
        keyword = "keyword"
        self.calendar.search_by_keyword(keyword)
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__

        date_yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date_tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        time = datetime.datetime.now().isoformat()[11:16]
        self.assertEqual(f"{date_yesterday} {time} {event1['summary']}\n"
                         f"{date_tomorrow} {time} {event2['summary']}\n", console_output)

    def test_search_by_keyword_no_result(self):
        """
        This test case tests that an appropriate message is printed when no events are found containing the keyword
        """
        self.calendar.get_past_events = MagicMock(return_value={"items": []})
        self.calendar.get_future_events = MagicMock(return_value={"items": []})

        buff = StringIO()
        sys.stdout = buff
        keyword = "keyword"
        self.calendar.search_by_keyword(keyword)
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__
        self.assertEqual("No events found.\n", console_output)


class MyEventManagerTestValidate(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_validate_attendees(self):
        """
        This test case tests the maximum number of valid attendees checking the console output and returned values from
        input validation
        """
        buff = StringIO()
        sys.stdout = buff

        with patch.object(MyEventManager, "input", side_effect=["Event Name", "Event Location",
                                                                "stso0001@student.monash.edu",
                                                                "stso0002@student.monash.edu",
                                                                "stso0003@student.monash.edu",
                                                                "stso0004@student.monash.edu",
                                                                "stso0005@student.monash.edu",
                                                                "stso0006@student.monash.edu",
                                                                "stso0007@student.monash.edu",
                                                                "stso0008@student.monash.edu",
                                                                "stso0009@student.monash.edu",
                                                                "stso0010@student.monash.edu",
                                                                "stso0011@student.monash.edu",
                                                                "stso0012@student.monash.edu",
                                                                "stso0013@student.monash.edu",
                                                                "stso0014@student.monash.edu",
                                                                "stso0015@student.monash.edu",
                                                                "stso0016@student.monash.edu",
                                                                "stso0017@student.monash.edu",
                                                                "stso0018@student.monash.edu",
                                                                "stso0019@student.monash.edu",
                                                                "stso0020@student.monash.edu",
                                                                "2050-12-31", "16:30", "2050-12-31", "17:30"]):
            valid = MyEventManager.create_event()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__

        attendees = []
        for i in range(20):
            if i < 9:
                attendees.append({"email": f"stso000{i + 1}@student.monash.edu"})
            else:
                attendees.append({"email": f"stso00{i + 1}@student.monash.edu"})
        self.assertEqual(["Event Name", "Event Location", attendees, ["2050-12-31", "2050-12-31"], ["16:30", "17:30"]],
                         valid)
        self.assertEqual("You have added the maximum number of attendees.\n", console_output)

    def test_validate_invalid_attendees(self):
        """
        This test case tests how the program behaves if the attendee email address entered does not belong to the right
        domain.
        """
        buff = StringIO()
        sys.stdout = buff
        with patch.object(MyEventManager, "input", side_effect=["Event Name", "Event Location",
                                                                "sean_tsou421@hotmail.com",
                                                                "stso0004@student.monash.edu", "",
                                                                "2050-12-31", "16:30",
                                                                "2050-12-31", "17:30"]):
            valid = MyEventManager.create_event()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__

        self.assertEqual("Attendee does not belong your native domain.\n", console_output)
        self.assertNotEqual(["Event Name", "Event Location", [{"email": "sean_tsou421@hotmail.com"}],
                             ["2050-12-31", "2050-12-31"], ["16:30", "17:30"]], valid)
        self.assertEqual(["Event Name", "Event Location", [{"email": "stso0004@student.monash.edu"}],
                          ["2050-12-31", "2050-12-31"], ["16:30", "17:30"]], valid)

    def test_validate_wrong_time_format(self):
        """
        This test case tests the wrong time formats for both start time and end time and see how the program responds.
        It also tests the upper bound for date to show that dates up to the very end of 2050 are valid.
        """
        buff = StringIO()
        sys.stdout = buff
        with patch.object(MyEventManager, "input", side_effect=["Event Name", "Event Location", "",
                                                                "2050-12-31", "4:30PM", "16:30",
                                                                "2050-12-31", "5:30PM", "17:30"]):
            valid = MyEventManager.create_event()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__

        self.assertEqual("Please enter the time in 24-hour format as prompted.\n"
                         "Please enter the time in 24-hour format as prompted.\n", console_output)
        self.assertNotEqual(["Event Name", "Event Location", [], ["2050-12-31", "2050-12-31"], ["4:30PM", "5:30PM"]],
                            valid)
        self.assertEqual(["Event Name", "Event Location", [], ["2050-12-31", "2050-12-31"], ["16:30", "17:30"]], valid)

    def test_validate_invalid_times(self):
        """
        This test case tests invalid time inputs for both start and end times and see how the system responds
        """
        buff = StringIO()
        sys.stdout = buff
        with patch.object(MyEventManager, "input", side_effect=["Event Name", "Event Location", "",
                                                                "2050-12-31", "invalid_time", "16:30",
                                                                "2050-12-31", "invalid_time", "17:30"]):
            valid = MyEventManager.create_event()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__

        self.assertEqual("Invalid input.\nInvalid input.\n", console_output)
        self.assertNotEqual(
            ["Event Name", "Event Location", [], ["2050-12-31", "2050-12-31"], ["invalid_time", "invalid_time"]],
            valid)
        self.assertEqual(["Event Name", "Event Location", [], ["2050-12-31", "2050-12-31"], ["16:30", "17:30"]], valid)

    def test_validate_year_out_of_bound(self):
        """
        This test case tests both the upper and lower boundaries of dates. The exceeding upperbound date is rejected,
        the current date (present) is tested and accepted
        """
        current_time = datetime.datetime.now().isoformat()
        current_time = current_time.split("T")
        current_date = current_time[0]
        start_time = current_time[1][:5]
        end_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).isoformat().split("T")[1][:5]
        buff = StringIO()
        sys.stdout = buff
        with patch.object(MyEventManager, "input", side_effect=["Event Name", "Event Location", "",
                                                                "2051-01-01", current_date, start_time,
                                                                current_date, end_time]):
            valid = MyEventManager.create_event()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__

        self.assertEqual("Unable to create events beyond the year 2050.\n", console_output)
        self.assertNotEqual(["Event Name", "Event Location", [], ["2051-01-01", "2051-01-01"], [start_time, end_time]],
                            valid)
        self.assertEqual(["Event Name", "Event Location", [], [current_date, current_date], [start_time, end_time]],
                         valid)

    def test_validate_date_in_the_past(self):
        """
        This test case tests the lower bound for dates by making an attempt at creating an event in the past.
        The test also tests for cases when the end time is after the start time.
        """
        today = datetime.datetime.now().isoformat()
        today = today.split("T")
        current_date = today[0]
        current_time = today[1][:5]
        bad_end_time = (datetime.datetime.now() - datetime.timedelta(minutes=1)).isoformat().split("T")[1][:5]
        end_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).isoformat().split("T")[1][:5]
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        buff = StringIO()
        sys.stdout = buff
        with patch.object(MyEventManager, "input", side_effect=["Event Name", "Event Location", "",
                                                                yesterday, current_date, current_time,
                                                                yesterday, current_date, bad_end_time, end_time]):
            valid = MyEventManager.create_event()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__

        self.assertEqual("Unable to create events in the past.\n"
                         "The ending date must be on or after the starting date.\n"
                         "The ending time must be after starting time.\n", console_output)
        self.assertNotEqual(["Event Name", "Event Location", [], [yesterday, yesterday], [current_time, end_time]],
                            valid)
        self.assertNotEqual(["Event Name", "Event Location", [], [current_date, yesterday], [current_time, end_time]],
                            valid)
        self.assertNotEqual(["Event Name", "Event Location", [], [yesterday, yesterday], [current_time, bad_end_time]],
                            valid)
        self.assertEqual(["Event Name", "Event Location", [], [current_date, current_date], [current_time, end_time]],
                         valid)


class MyEventManagerTestAdd(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_add_new_events_format_A(self):
        """
        This test case tests the first input date format when adding an event as per specs.
        """
        name = "Test Event Name"
        location = "123 Fake Street Clayton VIC 3400"
        attendees = [{"email": "stso0004@student.monash.edu"}]
        date = ["2022-12-01", "2022-12-01"]
        time = ["16:00", "17:00"]
        event = self.calendar.add_new_events(name, location, attendees, date, time)
        self.assertEqual(self.mock_api.events.return_value.insert.return_value.execute.return_value.get.call_count, 1)

    def test_add_new_events_format_B(self):
        """
        This test case tests the second input date format when adding an event as per specs to show that both date
        formats are handled properly
        """
        name = "Test Event Name"
        location = "123 Fake Street Clayton VIC 3400"
        attendees = [{"email": "stso0004@student.monash.edu"}]
        date = ["01-DEC-22", "01-DEC-22"]
        time = ["16:00", "17:00"]
        event = self.calendar.add_new_events(name, location, attendees, date, time)
        self.assertEqual(self.mock_api.events.return_value.insert.return_value.execute.return_value.get.call_count, 1)

    def test_add_new_events_return(self):
        """
        This test case tests that the add_new_events() is called correctly by showing an id is generated automatically
        even though it is not inputted.
        """
        name = "Test Event Name"
        location = "123 Fake Street Clayton VIC 3400"
        attendees = [{"email": "stso0004@student.monash.edu"}]
        date = ["01-DEC-22", "01-DEC-22"]
        time = ["16:00", "17:00"]
        event = self.calendar.add_new_events(name, location, attendees, date, time)
        self.assertIsNotNone(event["id"])

    def test_add_new_events_reminders(self):
        """
        This test case tests that the reminders have been set by checking it is not None.
        """
        name = "Test Event Name"
        location = "123 Fake Street Clayton VIC 3400"
        attendees = [{"email": "stso0004@student.monash.edu"}]
        date = ["01-DEC-22", "01-DEC-22"]
        time = ["16:00", "17:00"]
        event = self.calendar.add_new_events(name, location, attendees, date, time)
        self.assertIsNotNone(event["reminders"]["overrides"])


class MyEventManagerTestDelete(unittest.TestCase):

    def setUp(self):
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_delete_nothing(self):
        """
        This test case tests the behavior of the program if there was nothing to delete.
        """
        self.calendar.get_past_events = MagicMock(return_value={"items": []})
        e = MyEventManager.get_event_to_delete(self.calendar.get_past_events())
        res = self.calendar.delete_event(e)
        self.assertEqual("There are no events to delete.", res)

    def test_delete_method(self):
        """
        This test case tests a normal deletion of an event with a boundary case of one day in the past
        """
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.isoformat()
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': yesterday}, 'reminders': {'useDefault': True}}

        self.calendar.get_past_events = MagicMock(return_value={"items": [event]})
        with patch.object(MyEventManager, "input", side_effect=[1]):
            e = MyEventManager.get_event_to_delete(self.calendar.get_past_events())
        res = self.calendar.delete_event(e)
        self.assertEqual(1, self.mock_api.events.return_value.delete.return_value.execute.call_count)
        self.assertIsNone(res)

    def test_delete_future(self):
        """
        This test case tests a deletion of an event in the future with a boundary value of 1 second in the future.
        """
        time_now = datetime.datetime.now()
        time_future = time_now + datetime.timedelta(seconds=1)
        time_future = time_future.isoformat()
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': time_future}, 'reminders': {'useDefault': True}}
        res = self.calendar.delete_event(event)
        self.assertEqual("Cannot delete a present or future event.", res)

    def test_delete_present(self):
        """
        This test case tests the deletion of a present event.
        """
        time_now = datetime.datetime.now().isoformat()
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': time_now}, 'reminders': {'useDefault': True}}
        self.calendar.get_past_events = MagicMock(return_value={"items": []})
        res = self.calendar.delete_event(event)
        self.assertEqual("Cannot delete a present or future event.", res)


class MyEventManagerTestEdit(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_change_organizer(self):
        """
        This test case tests the functionality of changing an organizer by checking the api method call is called
        successfully with the right arguments
        """
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': '2050-09-13T11:30:00'}, 'organizer': {'email': 'stso0004@student.monash.edu'},
                 'reminders': {'useDefault': True}}
        self.calendar.get_future_events = MagicMock(return_value={"items": [event]})
        with patch.object(MyEventManager, "input", side_effect=[1, "theseantsou421@gmail.com"]):
            e = self.calendar.change_organizer()

        self.assertEqual(1, self.mock_api.events.return_value.move.return_value.execute.call_count)

        args, kwargs = self.mock_api.events.return_value.move.call_args_list[0]

        self.assertEqual("theseantsou421@gmail.com", kwargs["destination"])
        self.assertEqual(event["id"], kwargs["eventId"])

    def test_no_events_to_change(self):
        """
        This method tests the program's reponse if there are no events to modify
        """
        self.calendar.get_future_events = MagicMock(return_value={"items": []})

        buff = StringIO()
        sys.stdout = buff
        self.calendar.change_organizer()
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__

        self.assertEqual("No events found.\n", console_output)
        self.assertEqual(0, self.mock_api.events.return_value.move.return_value.execute.call_count)

    def test_cancel_event(self):
        """
        This test case tests the cancellation of a confirmed event by checking the api method is called successfully
        """
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': '2021-09-13T11:30:00'}, 'reminders': {'useDefault': True}, 'status': 'confirmed'}

        self.calendar.get_past_events = MagicMock(return_value={"items": [event]})
        with patch.object(MyEventManager, "input", side_effect=[1]):
            e = MyEventManager.get_event_to_delete(self.calendar.get_past_events())
        res = self.calendar.cancel_event(e)
        self.assertEqual(1, self.mock_api.events.return_value.update.return_value.execute.call_count)

    def test_nothing_to_cancel(self):
        """
        This test case tests the program's response if there are no events to cancel
        """
        self.calendar.get_past_events = MagicMock(return_value={"items": []})

        buff = StringIO()
        sys.stdout = buff
        e = MyEventManager.get_event_to_restore(self.calendar.get_past_events())
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__

        self.assertEqual("No events found.\n", console_output)

    def test_restore_event(self):
        """
        This test case tests the restoration of a cancelled event by checking if the api method is called successfully
        """
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': '2050-09-13T11:30:00'}, 'reminders': {'useDefault': True}, 'status': 'cancelled'}

        self.calendar.get_cancelled_past_events = MagicMock(return_value={"items": [event]})
        with patch.object(MyEventManager, "input", side_effect=[1]):
            e = MyEventManager.get_event_to_restore(self.calendar.get_cancelled_past_events())
        res = self.calendar.restore_event(e)
        self.assertEqual(1, self.mock_api.events.return_value.update.return_value.execute.call_count)

    def test_nothing_to_restore(self):
        """
        This test case tests the program's reponse if there are no events to restore
        """
        self.calendar.get_cancelled_past_events = MagicMock(return_value={"items": []})

        buff = StringIO()
        sys.stdout = buff
        e = MyEventManager.get_event_to_restore(self.calendar.get_cancelled_past_events())
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__

        self.assertEqual("No events found.\n", console_output)


class MyEventManagerTestJSON(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_import_event(self):
        """
        This test case tests the functionality of importing an event by creating a JSON file with an event, importing
        that JSON file with relevant function calls, checking if the api method is called successfully and checking
        if the event data is equivalent to what's been imported.
        """
        event = {
            'id': '79t7sfbm28ahdhn7q3it45bava',
            'summary': "Event Name",
            'location': "Test Location",
            'organizer': {
                'email': "stso0004@student.monash.edu",
            },
            'start': {
                'dateTime': '2022-09-13T11:30:00+10:00'
            },
            'end': {
                'dateTime': '2022-09-13T13:30:00+10:00'
            },
            'attendees': [],
            'reminders': {'useDefault': True}
        }
        file_name = "test_import.json"
        with open(file_name, "w") as outfile:
            json.dump(event, outfile)
        with patch.object(MyEventManager, "input", side_effect=["test_import.json"]):
            self.calendar.import_event()

        self.assertEqual(1, self.mock_api.events.return_value.import_.return_value.execute.call_count)

        file_name = open(file_name)
        json_data = json.load(file_name)
        self.assertEqual(event, json_data)
        file_name.close()

    def test_export_event(self):
        """
        This test case tests the functionality of exporting an event.
        """

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = yesterday.isoformat()
        event = {'id': '79t7sfbm28ahdhn9q4it45bava', 'summary': 'Event Summary',
                 'start': {'dateTime': yesterday}, 'reminders': {'useDefault': True}}

        self.calendar.get_past_events = MagicMock(return_value={"items": [event]})
        with patch.object(MyEventManager, "input", side_effect=[1]):
            e = MyEventManager.get_event_to_export(self.calendar.get_past_events())

        file_name = "test_export.json"
        self.calendar.export_event(event, file_name)

        file_name = open(file_name)
        json_data = json.load(file_name)
        self.assertEqual(event, json_data)
        file_name.close()

    def test_nothing_to_export(self):
        """
        This test case tests the program's response if there are no events available to be exported.
        """
        buff = StringIO()
        sys.stdout = buff
        self.calendar.get_past_events = MagicMock(return_value={"items": []})
        e = MyEventManager.get_event_to_export(self.calendar.get_past_events())
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__

        self.assertEqual("No events found.\n", console_output)
        self.assertIsNone(e)


class MyEventManagerTestHelper(unittest.TestCase):
    def setUp(self):
        self.mock_api = MagicMock()
        self.calendar = EventManager(self.mock_api)

    def test_print_no_events(self):
        """
        This test case tests the console output if there are no events to print.
        In case where there are events to print, this function has been tested in other test cases
        """
        events = []
        buff = StringIO()
        sys.stdout = buff
        MyEventManager.print_events(events)
        console_output = buff.getvalue()
        sys.stdout = sys.__stdout__

        self.assertEqual("-------------------------------------------------------------------------\n"
                         "No events found.\n"
                         "-------------------------------------------------------------------------\n", console_output)

    def test_user_choice(self):
        """
        This test case tests that the user options are printed correctly and that user choice is returned
        """
        inp = 1
        buff = StringIO()
        sys.stdout = buff
        with patch.object(MyEventManager, "input", side_effect=[inp]):
            res = MyEventManager.user_choice()
            console_output = buff.getvalue()
            sys.stdout = sys.__stdout__
        self.assertEqual("Please select from the following options:\n"
                         "1. View upcoming events\n"
                         "2. Navigate the events by year\n"
                         "3. Search event by keyword\n"
                         "4. Create a new event\n"
                         "5. Change an event's organizer\n"
                         "6. Cancel an event\n"
                         "7. Restore an event\n"
                         "8. Delete an event\n"
                         "9. Import event from JSON file\n"
                         "10. Export event from calendar into a JSON file\n"
                         "11. Exit\n", console_output)
        self.assertEqual(inp, res)

    def test_user_keyword(self):
        """
        This test case tests that user input for searched keyword is successfully retrieved
        """
        keyword = "keyword"
        with patch.object(MyEventManager, "input", side_effect=[keyword]):
            res = MyEventManager.get_user_keyword()
        self.assertEqual(keyword, res)


def main():
    get_suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTestGet)
    validate_suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTestValidate)
    delete_suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTestDelete)
    edit_suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTestEdit)
    JSON_suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTestJSON)
    helper_suite = unittest.TestLoader().loadTestsFromTestCase(MyEventManagerTestHelper)

    unittest.TextTestRunner(verbosity=2).run(get_suite)
    unittest.TextTestRunner(verbosity=2).run(validate_suite)
    unittest.TextTestRunner(verbosity=2).run(delete_suite)
    unittest.TextTestRunner(verbosity=2).run(edit_suite)
    unittest.TextTestRunner(verbosity=2).run(JSON_suite)
    unittest.TextTestRunner(verbosity=2).run(helper_suite)


if __name__ == "__main__":
    main()
