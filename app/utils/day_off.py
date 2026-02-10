from enum import Enum


class DayOffStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
