import CONFIG
import sys
import pyqrcode
from pprint import pprint
from CalendarWorker import CalendarWorker


# generate ical file from screenshot
calWorker = CalendarWorker(sys.argv[1])
calWorker.run()
ics_file = calWorker.save_events_to_ics()

# generate QR code logic
ics_file = str(ics_file.decode('utf-8'))
big_code = pyqrcode.create(
    ics_file,
    error='L',
    version=34,
    mode='binary'
)
big_code.png(
    CONFIG.QR_CODE_FILE,
    scale=6,
    module_color=[
        0, 0, 0, 255],
    background=[0xff, 0xff, 0xff]
)
