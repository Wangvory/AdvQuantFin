from datetime import datetime
from enum import Enum


class Units(Enum):
    Millisecs = 1
    Microsecs = 2
    Nanosecs = 3


def convert_dtstring_to_timestamp(dt_as_string, dt_format, result_units=Units.Nanosecs):
    dt_obj = datetime.strptime(dt_as_string, dt_format)
    if result_units == Units.Millisecs:
        return dt_obj.timestamp() * 1.0e3
    elif result_units == Units.Microsecs:
        return dt_obj.timestamp() * 1.0e6
    elif result_units == Units.Nanosecs:
        return dt_obj.timestamp() * 1.0e9
    return dt_obj.timestamp()


def convert_timestamp_to_dtstring(timestamp, timestamp_units=Units.Nanosecs):
    if timestamp_units == Units.Millisecs:
        return datetime.fromtimestamp(timestamp / 1.0e3)
    elif timestamp_units == Units.Microsecs:
        return datetime.fromtimestamp(timestamp / 1.0e6)
    elif timestamp_units == Units.Nanosecs:
        return datetime.fromtimestamp(timestamp / 1.0e9)


def driver():
    dt_as_string = '05.13.2018 18:02:46.787811'
    dt_format = '%m.%d.%Y %H:%M:%S.%f'
    print(convert_dtstring_to_timestamp(dt_as_string, dt_format, Units.Nanosecs))

    timestamp = 1526248966787810981
    print(convert_timestamp_to_dtstring(timestamp, Units.Nanosecs))


if __name__ == '__main__':
    driver()
