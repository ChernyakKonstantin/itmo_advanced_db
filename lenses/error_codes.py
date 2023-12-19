from enum import IntEnum


class BackendErrors(IntEnum):
    WRONG_SENSOR_LIST = 1
    WRONG_START_TIMESTAMP = 2
    WRONG_END_TIMESTAMP = 3
    NO_DATA = 4
