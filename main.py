import re
import sys
import pytesseract
import datetime
from PIL import Image
from flask import Flask
from pprint import pprint
from icalendar import Calendar, Event


# core function definitions
def ocr_core(filename):
    # function to handle core OCR processing
    text = pytesseract.image_to_string(Image.open(filename))
    return text


# format text data
def text_to_events(text: str, events: dict):
    HOUR_PATTERN = "\d+:\d+\w+M\s+-"
    text = text.split('\n')
    i = 0
    while i < len(text):
        key = text[i]
        if key in events:
            j = i + 1
            if j < len(text):
                while j < len(text) and text[j] not in events:
                    txt = text[j]
                    if txt != '':
                        # make sure text is not empty character
                        if re.match(HOUR_PATTERN, txt):
                            # regex to match text with HH:MM AM/PM format
                            txt = txt + " " + text[j+1]
                            j += 1
                        events[key].append(txt)
                    j += 1
        i = j
    return events


def format_events(week_days: dict):
    CLASS_CODE_PATTERN = "[A-Z]{3}"

    for d in week_days:
        week_days[d] = {
            "raw data": week_days[d]
        }

    for d in week_days:
        text = week_days[d]["raw data"]

        # create empty lists for each course in each week day
        for i in range(len(text)):
            if re.match(CLASS_CODE_PATTERN, text[i]):
                week_days[d][text[i]] = []

        # iterate through week day list and add data to course lists
        i = 0
        curr_key = ""
        while i < len(text):
            if re.match(CLASS_CODE_PATTERN, text[i]):
                curr_key = text[i]
                j = i + 1
                while j < len(text):
                    if not re.match(CLASS_CODE_PATTERN, text[j]):
                        week_days[d][curr_key].append(text[j])
                    else:
                        break
                    j += 1
                i = j
            else:
                i += 1

        # delete un-necessary raw data array in dict
        del week_days[d]["raw data"]

    return week_days



# define events per weekday
week_days = {day: [] for day in [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]}

# save text from calendar onto variable
text_from_image = ocr_core(sys.argv[1])

# save raw text from calendar to disk
with open("data.txt", 'w') as fout:
    fout.write(text_from_image)

# gerenate events dictionary from plain-text
week_days = text_to_events(text_from_image, week_days)

# format events dictionary to have days as keys and classes as sub-dict keys
week_days = format_events(week_days)


# create iCal file from dictionary above
cal = Calendar()

for day in week_days:
    for course in week_days[day]:
        event = Event()

        # course location data
        location = "%s %s" % (
            week_days[day][course][2],
            week_days[day][course][3]
        )

        # datetime data
        time_str = week_days[day][course][1].split(' - ')
        dtstart_str = '2019-10-21 %s' % time_str[0]
        dtend_str = '2019-10-21 %s' % time_str[1]
        format_str = '%Y-%m-%d %I:%M%p'
        dtstart = datetime.datetime.strptime(dtstart_str, format_str)
        dtend = datetime.datetime.strptime(dtend_str, format_str)

        # course description data
        description = week_days[day][course][0]

        # add attributes to event object
        event.add('summary', course)
        event.add('description', description)
        event.add('location', location)
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('rrule', {'freq': 'weekly', 'byday': day[:2], 'count': 2})

        cal.add_component(event)

with open('course_schedule.ics', 'wb') as fout:
    fout.write(cal.to_ical())
