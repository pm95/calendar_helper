import re
import sys
import pytesseract
import datetime
from PIL import Image
from flask import Flask
from pprint import pprint
from icalendar import Calendar, Event


class CalendarWorker:
    def __init__(self, filename):
        self.filename = filename
        self.text = ""
        self.week_days = {day: [] for day in [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]}

    def ocr_core(self):
        # function to handle core OCR processing
        self.text = pytesseract.image_to_string(Image.open(self.filename))

    # format text data
    def text_to_events(self):
        HOUR_PATTERN = "\d+:\d+\w+M\s+-"
        text = self.text.split('\n')
        i = 0
        while i < len(text):
            key = text[i]
            if key in self.week_days:
                j = i + 1
                if j < len(text):
                    while j < len(text) and text[j] not in self.week_days:
                        txt = text[j]
                        if txt != '':
                            # make sure text is not empty character
                            if re.match(HOUR_PATTERN, txt):
                                # regex to match text with HH:MM AM/PM format
                                txt = txt + " " + text[j+1]
                                j += 1
                            self.week_days[key].append(txt)
                        j += 1
            i = j

    def format_events(self):
        CLASS_CODE_PATTERN = "[A-Z]{3}"

        for d in self.week_days:
            self.week_days[d] = {
                "raw data": self.week_days[d]
            }

        for d in self.week_days:
            text = self.week_days[d]["raw data"]

            # create empty lists for each course in each week day
            for i in range(len(text)):
                if re.match(CLASS_CODE_PATTERN, text[i]):
                    self.week_days[d][text[i]] = []

            # iterate through week day list and add data to course lists
            i = 0
            curr_key = ""
            while i < len(text):
                if re.match(CLASS_CODE_PATTERN, text[i]):
                    curr_key = text[i]
                    j = i + 1
                    while j < len(text):
                        if not re.match(CLASS_CODE_PATTERN, text[j]):
                            self.week_days[d][curr_key].append(text[j])
                        else:
                            break
                        j += 1
                    i = j
                else:
                    i += 1

            # delete un-necessary raw data array in dict
            del self.week_days[d]["raw data"]

    # # save raw text from calendar to disk
    # with open("data.txt", 'w') as fout:
    #     fout.write(text_from_image)

    def run(self):
        # run OCR core engine
        self.ocr_core()

        # gerenate events dictionary from plain-text
        self.text_to_events()

        # format events dictionary to have days as keys and classes as sub-dict keys
        self.format_events()

    def save_events_to_ics(self):
        # create iCal file from dictionary above
        cal = Calendar()

        for day in self.week_days:
            for course in self.week_days[day]:
                event = Event()

                # course location data
                location = "%s %s" % (
                    self.week_days[day][course][2],
                    self.week_days[day][course][3]
                )

                # datetime data
                time_str = self.week_days[day][course][1].split(' - ')
                dtstart_str = '2019-10-21 %s' % time_str[0]
                dtend_str = '2019-10-21 %s' % time_str[1]
                format_str = '%Y-%m-%d %I:%M%p'
                dtstart = datetime.datetime.strptime(dtstart_str, format_str)
                dtend = datetime.datetime.strptime(dtend_str, format_str)

                # course description data
                description = self.week_days[day][course][0]

                # add attributes to event object
                event.add('summary', course)
                event.add('description', description)
                event.add('location', location)
                event.add('dtstart', dtstart)
                event.add('dtend', dtend)
                event.add('rrule', {'freq': 'weekly',
                                    'byday': day[:2], 'count': 2})

                cal.add_component(event)

        with open('course_schedule.ics', 'wb') as fout:
            fout.write(cal.to_ical())

        return cal.to_ical()
