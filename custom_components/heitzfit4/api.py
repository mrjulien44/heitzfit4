# import aiohttp
# import json

# from datetime import date, timedelta, datetime
# from typing import Any

# import logging
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.const import Platform
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.update_coordinator import TimestampDataUpdateCoordinator


# from .const import (
#     PLANNING_MAX_DAYS,
# )

# _LOGGER = logging.getLogger(__name__)

# class Heitzfit4API:
#     def __init__(self, club, username, password, nbdays):
#         self.club = club
#         self.username = username
#         self.password = password
#         self.nbdays = nbdays
#         self.token = None
#         self.clientId = None

#     async def async_sign_in(self):
#         async with aiohttp.ClientSession() as session:
#             async with session.post(
#                 f"https://app.heitzfit.com/c/{self.club}/ws/api/auth/signin",
#                 json={
#                     "email": self.username,
#                     "targetCenter": self.club,
#                     "password": self.password,
#                     "_appId": "b0b88fb90e9960f706bb"
#                 }
#             ) as response:
#                 result = await response.json()
#                 self.token = result["token"]
#                 self.clientId = result["clientId"]

#     async def async_book_activity(self, activity_id: str):
#         """Reserve an activity using the same REST payload shape as the card example."""
#         return await self._async_activity_request("POST", activity_id)

#     async def async_delete_activity(self, booking_id: str):
#         """Cancel an activity through the dedicated Heitzfit cancel route."""
#         url = f"https://app.heitzfit.com/c/{self.club}/ws/api/planning/book/{booking_id}/cancel"
#         headers = {
#             "Authorization": f"{self.token}",
#             "Content-Type": "application/json",
#         }

#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, headers=headers) as response:
#                 try:
#                     text = await response.text()
#                     if text:
#                         try:
#                             return json.loads(text)
#                         except Exception:
#                             return {"status": response.status, "text": text}
#                     return {"status": response.status}
#                 except Exception:
#                     return {"status": response.status, "text": await response.text()}

#     async def _async_activity_request(self, method: str, activity_id: str):
#         """Call the Heitzfit booking endpoint with the REST payload expected by the API."""
#         url = f"https://app.heitzfit.com/c/{self.club}/ws/api/planning/book"
#         headers = {
#             "Authorization": f"{self.token}",
#             "Content-Type": "application/json",
#         }
#         payload = {
#             "id": int(str(activity_id)),
#             "places": 1,
#             "joinQueueList": False,
#         }

#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, headers=headers, json=payload) as response:
#                 try:
#                     text = await response.text()
#                     if text:
#                         try:
#                             return json.loads(text)
#                         except Exception:
#                             return {"status": response.status, "text": text}
#                     return {"status": response.status}
#                 except Exception:
#                     return {"status": response.status, "text": await response.text()}
    
#     async def async_get_booking(self):
#         async with aiohttp.ClientSession() as session:
#             async with session.get(
#                 f"https://app.heitzfit.com/c/{self.club}/ws/api/planning/book?idClient={self.nbdays}&viewMode=0&familyActive=&familyIdClient=&familyCreatedBySelf=&include=",
#                 headers={"Authorization": f"{self.token}"}
#             ) as response:
#                 result_booking = await response.json()
#                 return {json.dumps(result_booking)}  # Adjust as needed
    
#     async def async_get_planning(self):
#         date_of_day = datetime.now().strftime("%Y-%m-%d")
#         bookings = await self.async_get_booking()
#         async with aiohttp.ClientSession() as session:
#             async with session.get(
#                 f"https://app.heitzfit.com/c/{self.club}/ws/api/planning/browse?startDate={date_of_day}&numberOfDays={self.nbdays}&idActivities=&idEmployees=&idRooms=&idGroups=&hourStart=&hourEnd=&stackBy=date&caloriesMin=&caloriesMax=&idCenter={self.club}",
#                 headers={"Authorization": f"Bearer {self.token}"}
#             ) as response:
#                 planning_days = await response.json()
#                 filtered_data = filter_fields(planning_days)
#                 updated_planning_data = add_booked_flag(filtered_data, bookings)
                
#                 return {"Planning": updated_planning_data}  # Adjust as needed

# def add_booked_flag(planning_data, booking_data):
#     #  Add booked flag to planning data
#     #  entry format of booking_data needs to be adapted, begin by [ instead of {

#     booking_data_str = str(booking_data)
#     booking_data_str=booking_data_str.replace(booking_data_str[:2],'',1)
#     booking_data_str=booking_data_str[::-1]
#     booking_data_str=booking_data_str.replace(booking_data_str[:2],'',1)
#     booking_data_str=booking_data_str[::-1]

#     booking= json.loads(booking_data_str)

#     booked_activities=set()

#     for id_planning in booking:
#         booked_activities.add(id_planning["idPlanning"])

#     for date, activities in planning_data.items():
#         for activity in activities:
#             if activity["id"] in booked_activities:
#                 activity["booked"] = True
#                 #activity["id_booking"] = booking.get(activity["id"], {}).get("id", None)
#             else:
#                 activity["booked"] = False
#                 #activity["id_booking"] = ""

#     return planning_data

# def filter_fields(data):
#     # deletion of fields that are not needed
#     fields_to_remove = {
#         "idRoom", "idEmployee", "employee", "idGroup", "idCenter", "calories", "overlapped","manualPlaces","color",
#         "_roomAuthorizedToCtr", "_taskAuthorizedToCtr", "bestContrast", "_task", "_room", "_group"
#     }

#     def filter_dict(d):
#         return {k: v for k, v in d.items() if k not in fields_to_remove}

#     filtered_data = {}
#     for date, activities in data.items():
#         filtered_activities = []
#         for activity in activities:
#             filtered_activity = filter_dict(activity)
#             filtered_activities.append(filtered_activity)
#         filtered_data[date] = filtered_activities

#     return filtered_data

import aiohttp
import json

from datetime import datetime
from typing import Any

import logging

from homeassistant.helpers.update_coordinator import (
    TimestampDataUpdateCoordinator,
)

from .const import (
    PLANNING_MAX_DAYS,
)


_LOGGER = logging.getLogger(__name__)


class Heitzfit4API:
    def __init__(self, club, username, password, nbdays):
        self.club = club
        self.username = username
        self.password = password
        self.nbdays = nbdays
        self.token = None
        self.clientId = None

    async def async_sign_in(self):
        """Authenticate the user and store the token and client identifier."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                (
                    f"https://app.heitzfit.com/c/{self.club}"
                    "/ws/api/auth/signin"
                ),
                json={
                    "email": self.username,
                    "targetCenter": self.club,
                    "password": self.password,
                    "_appId": "b0b88fb90e9960f706bb",
                },
            ) as response:
                result = await response.json()

                self.token = result["token"]
                self.clientId = result["clientId"]

    async def async_book_activity(self, activity_id: str):
        """Reserve an activity using the REST payload expected by the API."""
        return await self._async_activity_request(
            "POST",
            activity_id,
        )

    async def async_delete_activity(self, booking_id: str):
        """Cancel an activity through the dedicated Heitzfit cancel route."""
        url = (
            f"https://app.heitzfit.com/c/{self.club}"
            f"/ws/api/planning/book/{booking_id}/cancel"
        )

        headers = {
            "Authorization": f"{self.token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
            ) as response:
                text = await response.text()

                if text:
                    try:
                        return json.loads(text)
                    except (json.JSONDecodeError, TypeError):
                        return {
                            "status": response.status,
                            "text": text,
                        }

                return {
                    "status": response.status,
                }

    async def _async_activity_request(
        self,
        method: str,
        activity_id: str,
    ):
        """Call the Heitzfit booking endpoint."""
        url = (
            f"https://app.heitzfit.com/c/{self.club}"
            "/ws/api/planning/book"
        )

        headers = {
            "Authorization": f"{self.token}",
            "Content-Type": "application/json",
        }

        payload = {
            "id": int(str(activity_id)),
            "places": 1,
            "joinQueueList": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                headers=headers,
                json=payload,
            ) as response:
                text = await response.text()

                if text:
                    try:
                        return json.loads(text)
                    except (json.JSONDecodeError, TypeError):
                        return {
                            "status": response.status,
                            "text": text,
                        }

                return {
                    "status": response.status,
                }

    async def async_get_booking(self):
        """Retrieve the current bookings."""
        url = (
            f"https://app.heitzfit.com/c/{self.club}"
            "/ws/api/planning/book"
            f"?idClient={self.nbdays}"
            "&viewMode=0"
            "&familyActive="
            "&familyIdClient="
            "&familyCreatedBySelf="
            "&include="
        )

        headers = {
            "Authorization": f"{self.token}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
            ) as response:
                result_booking = await response.json()

                if isinstance(result_booking, list):
                    return result_booking

                _LOGGER.warning(
                    "Unexpected booking API response type: %s",
                    type(result_booking).__name__,
                )

                return []

    async def async_get_planning(self):
        """Retrieve planning and enrich every activity with booking data."""
        date_of_day = datetime.now().strftime("%Y-%m-%d")

        bookings = await self.async_get_booking()

        url = (
            f"https://app.heitzfit.com/c/{self.club}"
            "/ws/api/planning/browse"
            f"?startDate={date_of_day}"
            f"&numberOfDays={self.nbdays}"
            "&idActivities="
            "&idEmployees="
            "&idRooms="
            "&idGroups="
            "&hourStart="
            "&hourEnd="
            "&stackBy=date"
            "&caloriesMin="
            "&caloriesMax="
            f"&idCenter={self.club}"
        )

        headers = {
            "Authorization": f"Bearer {self.token}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
            ) as response:
                planning_days = await response.json()

        filtered_data = filter_fields(planning_days)

        updated_planning_data = add_booking_information(
            filtered_data,
            bookings,
        )

        return {
            "Planning": updated_planning_data,
        }


def normalize_identifier(value: Any) -> str | None:
    """Normalize an API identifier to make comparisons reliable."""
    if value is None:
        return None

    normalized_value = str(value).strip()

    if not normalized_value:
        return None

    return normalized_value


def add_booking_information(
    planning_data: dict[str, list[dict[str, Any]]],
    booking_data: list[dict[str, Any]] | None,
) -> dict[str, list[dict[str, Any]]]:
    """Add booked and id_booking fields to every planning activity.

    The booking API returns:
        - idPlanning: identifier of the corresponding planning activity
        - id: identifier of the booking

    For every planning activity:
        - booked is True when a matching booking exists
        - id_booking contains the booking id when booked
        - id_booking is an empty string when not booked
    """
    booking_data = booking_data or []

    booking_by_planning_id: dict[str, Any] = {}

    for booking in booking_data:
        if not isinstance(booking, dict):
            continue

        planning_id = normalize_identifier(
            booking.get("idPlanning")
        )

        booking_id = booking.get("id")

        if planning_id is None:
            continue

        if booking_id is None or booking_id == "":
            continue

        booking_by_planning_id[planning_id] = booking_id

    for planning_date, activities in planning_data.items():
        if not isinstance(activities, list):
            continue

        for activity in activities:
            if not isinstance(activity, dict):
                continue

            activity_id = normalize_identifier(
                activity.get("id")
            )

            booking_id = (
                booking_by_planning_id.get(activity_id)
                if activity_id is not None
                else None
            )

            if booking_id is not None:
                activity["booked"] = True
                activity["id_booking"] = booking_id
            else:
                activity["booked"] = False
                activity["id_booking"] = ""

    return planning_data


def add_booked_flag(
    planning_data: dict[str, list[dict[str, Any]]],
    booking_data: list[dict[str, Any]] | None,
) -> dict[str, list[dict[str, Any]]]:
    """Maintain compatibility with existing calls to add_booked_flag."""
    return add_booking_information(
        planning_data,
        booking_data,
    )


def filter_fields(data):
    """Remove fields that are not needed in the sensor attributes."""
    fields_to_remove = {
        "idRoom",
        "idEmployee",
        "employee",
        "idGroup",
        "idCenter",
        "calories",
        "overlapped",
        "manualPlaces",
        "color",
        "_roomAuthorizedToCtr",
        "_taskAuthorizedToCtr",
        "bestContrast",
        "_task",
        "_room",
        "_group",
    }

    def filter_dict(item):
        return {
            key: value
            for key, value in item.items()
            if key not in fields_to_remove
        }

    filtered_data = {}

    for planning_date, activities in data.items():
        filtered_activities = []

        for activity in activities:
            filtered_activity = filter_dict(activity)
            filtered_activities.append(filtered_activity)

        filtered_data[planning_date] = filtered_activities

    return filtered_data