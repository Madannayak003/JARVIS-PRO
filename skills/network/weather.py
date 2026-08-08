"""
JARVIS PRO
Weather Skill

Provides current weather information.

Uses Open-Meteo for weather data and geocoding.
No API key required.
"""

import requests

from core.registry import register
from voice.manager import speak


# =========================================================
# Configuration
# =========================================================

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 5


# =========================================================
# Weather Code Descriptions
# =========================================================

WEATHER_CODES = {
    0: "clear skies",
    1: "mainly clear skies",
    2: "partly cloudy skies",
    3: "overcast skies",

    45: "foggy conditions",
    48: "foggy conditions",

    51: "light drizzle",
    53: "moderate drizzle",
    55: "heavy drizzle",

    56: "light freezing drizzle",
    57: "heavy freezing drizzle",

    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",

    66: "light freezing rain",
    67: "heavy freezing rain",

    71: "light snow",
    73: "moderate snow",
    75: "heavy snow",

    77: "snow grains",

    80: "light rain showers",
    81: "moderate rain showers",
    82: "heavy rain showers",

    85: "light snow showers",
    86: "heavy snow showers",

    95: "a thunderstorm",
    96: "a thunderstorm with hail",
    99: "a thunderstorm with heavy hail",
}


# =========================================================
# Resolve Location
# =========================================================

def _resolve_location(location=None):
    """
    Resolve a location name into latitude/longitude.

    Examples:
        Bangalore
        Mysore
        London
        New York
    """

    if not location:
        return _detect_current_location()

    location = str(location).strip()

    if not location:
        return _detect_current_location()

    try:

        response = requests.get(
            GEOCODING_URL,
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            return None

        result = results[0]

        return {
            "name": result.get("name", location),
            "country": result.get("country", ""),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        }

    except Exception as e:

        print(
            f"[WEATHER GEOCODING ERROR] {e}"
        )

        return None


# =========================================================
# Detect Current Location
# =========================================================

def _detect_current_location():
    """
    Try to determine the current location using IP geolocation.
    """

    try:

        response = requests.get(
            "https://ipapi.co/json/",
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is None or longitude is None:
            return None

        return {
            "name": data.get(
                "city",
                "your location",
            ),
            "country": data.get(
                "country_name",
                "",
            ),
            "latitude": float(latitude),
            "longitude": float(longitude),
        }

    except Exception as e:

        print(
            f"[WEATHER LOCATION ERROR] {e}"
        )

        return None


# =========================================================
# Get Weather
# =========================================================

def _get_weather(latitude, longitude):
    """
    Fetch current weather from Open-Meteo.
    """

    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,

            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),

            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",

            "timezone": "auto",
        },

        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    return response.json()


# =========================================================
# Natural Weather Response
# =========================================================

def _build_message(location, weather):
    """
    Build a natural JARVIS response.
    """

    current = weather.get("current", {})

    temperature = current.get(
        "temperature_2m"
    )

    feels_like = current.get(
        "apparent_temperature"
    )

    humidity = current.get(
        "relative_humidity_2m"
    )

    precipitation = current.get(
        "precipitation"
    )

    wind = current.get(
        "wind_speed_10m"
    )

    weather_code = current.get(
        "weather_code"
    )

    condition = WEATHER_CODES.get(
        weather_code,
        "unknown conditions",
    )

    city = location.get(
        "name",
        "your location",
    )

    parts = []

    # -----------------------------------------------------
    # Temperature
    # -----------------------------------------------------

    if temperature is not None:

        parts.append(
            f"It's {round(temperature)} degrees"
        )

    # -----------------------------------------------------
    # Condition
    # -----------------------------------------------------

    if condition:

        parts.append(
            f"with {condition}"
        )

    message = (
        f"Currently in {city}, "
        + " ".join(parts)
        + "."
    )

    # -----------------------------------------------------
    # Feels Like
    # -----------------------------------------------------

    if feels_like is not None:

        message += (
            f" It feels like "
            f"{round(feels_like)} degrees."
        )

    # -----------------------------------------------------
    # Humidity
    # -----------------------------------------------------

    if humidity is not None:

        message += (
            f" Humidity is "
            f"{round(humidity)} percent."
        )

    # -----------------------------------------------------
    # Wind
    # -----------------------------------------------------

    if wind is not None:

        message += (
            f" Wind speed is "
            f"{round(wind)} kilometers per hour."
        )

    # -----------------------------------------------------
    # Rain
    # -----------------------------------------------------

    if precipitation is not None:

        if precipitation > 0:

            message += (
                f" There is "
                f"{precipitation} millimeters "
                "of precipitation."
            )

    return message


# =========================================================
# Weather Action
# =========================================================

def weather(data=None):
    """
    Report current weather.

    Supported data examples:

        {}

        {
            "location": "Bangalore"
        }

        {
            "city": "Mysore"
        }
    """

    if data is None:
        data = {}

    try:

        # -------------------------------------------------
        # Location
        # -------------------------------------------------

        location = (
            data.get("location")
            or data.get("city")
            or data.get("place")
        )

        print(
            f"[WEATHER] Requested location: "
            f"{location or 'current location'}"
        )

        # -------------------------------------------------
        # Resolve location
        # -------------------------------------------------

        resolved = _resolve_location(
            location
        )

        if resolved is None:

            speak(
                "I couldn't determine the location "
                "for the weather."
            )

            return False

        # -------------------------------------------------
        # Get weather
        # -------------------------------------------------

        weather_data = _get_weather(
            resolved["latitude"],
            resolved["longitude"],
        )

        # -------------------------------------------------
        # Natural response
        # -------------------------------------------------

        message = _build_message(
            resolved,
            weather_data,
        )

        speak(message)

        # -------------------------------------------------
        # Debug
        # -------------------------------------------------

        current = weather_data.get(
            "current",
            {},
        )

        print(
            f"[WEATHER] "
            f"{resolved['name']} | "
            f"{current.get('temperature_2m')}°C | "
            f"Code: {current.get('weather_code')} | "
            f"Humidity: "
            f"{current.get('relative_humidity_2m')}%"
        )

        return True

    except requests.RequestException as e:

        print(
            f"[WEATHER NETWORK ERROR] {e}"
        )

        speak(
            "I couldn't reach the weather service "
            "right now."
        )

        return False

    except Exception as e:

        print(
            f"[WEATHER ERROR] {e}"
        )

        speak(
            "I couldn't check the weather right now."
        )

        return False


# =========================================================
# Registry
# =========================================================

register(
    "weather",
    weather,
)