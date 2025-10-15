import logging
from langchain_core.tools import tool
from src.services.weather_service import WeatherService

logger = logging.getLogger(__name__)

# Initialize weather service for singleton usage
weather_service = WeatherService()


@tool
def get_weather(location: str, units: str = "metric") -> str:
    """
    Get current weather information for a specific location using modern city names and with specified units.
    IMPORTANT: Use the current/modern name of the city (e.g., use "Livorno" not "Leghorn", "Istanbul" not
    "Constantinople").

    Args:
        location: The current name of the city or location (e.g., "Paris", "London", "New York", "Livorno")
        units: Units for temperature. "metric" for Celsius, "imperial" for Fahrenheit and "standard" for Kelvin.
        Default is "metric".

    Returns:
        A formatted string with current weather information including temperature,
        conditions, humidity, and wind speed in specified units.

    Example:
        get_weather("Paris", "metric") -> "Current weather in Paris, FR: Temperature: 15°C..."
        get_weather("Livorno", "metric") -> "Current weather in Livorno, IT: Temperature: 18°C..."
    """
    try:
        logger.info(f"Fetching weather for: {location}")

        # Get coordinates for the location for stability
        coords = weather_service.get_coordinates(location)

        if not coords:
            return f"I couldn't find the location '{location}'. The city name may be incorrect or not recognized. " \
                   f"Please verify the modern city name. "

        lat, lon, city_name, country = coords
        logger.info(f"Resolved '{location}' to {city_name}, {country} ({lat}, {lon})")

        # Get weather using coordinates
        weather_info = weather_service.get_weather_by_coordinates(lat, lon, city_name, country, units)

        if weather_info:
            response = weather_service.format_weather_response(weather_info)
            return response
        else:
            return f"I couldn't fetch weather information for '{city_name}'. Please try again later."

    except Exception as e:
        logger.error(f"Error in get_weather tool: {e}")
        return f"I encountered an error while fetching weather information for '{location}'. Please try again later."
