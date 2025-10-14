import requests
from typing import Dict, Optional, Tuple
import logging
from src.config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL, OPENWEATHER_GEO_URL

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""

    def __init__(self):
        """Initialize the weather service"""
        if not OPENWEATHER_API_KEY:
            logger.error("OpenWeatherMap API key not configured")
            raise ValueError("OPENWEATHERMAP_API_KEY not set in environment")

        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL
        self.geo_url = OPENWEATHER_GEO_URL

    def get_coordinates(self, location: str, limit: int = 1) -> Optional[Tuple[float, float, str, str]]:
        """
        Get coordinates for a location using OpenWeatherMap Geocoding API

        Args:
            location: City name (e.g., "Paris", "London", "New York")
            limit: Number of results to return (default: 1)

        Returns:
            Tuple of (latitude, longitude, city_name, country_code) or None if not found
        """
        try:
            params = {
                'q': location,
                'limit': limit,
                'appid': self.api_key
            }

            response = requests.get(self.geo_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data:
                logger.error(f"Location not found: {location}")
                return None

            # Get the first result
            location_data = data[0]
            lat = location_data['lat']
            lon = location_data['lon']
            city_name = location_data['name']
            country = location_data.get('country', 'Unknown')

            logger.info(f"Coordinates found for {location}: {lat}, {lon}")
            return lat, lon, city_name, country

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching coordinates for {location}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching coordinates for {location}: {e}")
            return None

    def get_weather(self, location: str, units: str = "metric") -> Optional[Dict]:
        """
        Get current weather for a location

        Args:
            location: City name (e.g., "Paris", "London", "New York")
            units: Temperature units - "metric" (Celsius), "imperial" (Fahrenheit), "standard" (Kelvin)

        Returns:
            Dictionary with weather information or None if error
        """
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': units
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract relevant weather information
            weather_info = {
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'wind_speed': data['wind']['speed'],
                'units': units
            }

            logger.info(f"Weather data fetched for {location}: {weather_info['temperature']}°")
            return weather_info

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Location not found: {location}")
                return None
            else:
                logger.error(f"HTTP error fetching weather for {location}: {e}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching weather for {location}: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching weather for {location}: {e}")
            return None

    def get_weather_by_coordinates(self, lat: float, lon: float, city_name: str, country: str, units: str = "metric") -> Optional[Dict]:
        """
        Get current weather using latitude and longitude

        Args:
            lat: Latitude
            lon: Longitude
            city_name: City name
            country: Country code
            units: Temperature units - "metric" (Celsius), "imperial" (Fahrenheit), "standard" (Kelvin)

        Returns:
            Dictionary with weather information or None if error occurs
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': units
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract relevant weather information
            weather_info = {
                'location': city_name,
                'country': country,
                'latitude': lat,
                'longitude': lon,
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'wind_speed': data['wind']['speed'],
                'units': units
            }

            logger.info(f"Weather data fetched for {city_name} ({lat}, {lon}): {weather_info['temperature']}°")
            return weather_info

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching weather for coordinates ({lat}, {lon}): {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching weather for coordinates ({lat}, {lon}): {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error fetching weather for coordinates ({lat}, {lon}): {e}")
            return None

    def format_weather_response(self, weather_info: Dict) -> str:
        """
        Format weather information into a human-readable string

        Args:
            weather_info: Weather data dictionary

        Returns:
            Formatted weather description
        """
        if not weather_info:
            return "Unable to fetch weather information."

        location = weather_info['location']
        country = weather_info['country']
        temp = weather_info['temperature']
        feels_like = weather_info['feels_like']
        description = weather_info['description']
        humidity = weather_info['humidity']
        wind_speed = weather_info['wind_speed']
        units = weather_info['units']

        # Determine temperature unit symbol
        temp_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        wind_unit = "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"

        response = (
            f"Current weather in {location}, {country}:\n"
            f"Temperature: {temp}{temp_symbol} (feels like {feels_like}{temp_symbol})\n"
            f"Conditions: {description.capitalize()}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} {wind_unit}"
        )

        return response

    def get_weather_for_multiple_locations(self, locations: list[str]) -> Dict[str, Optional[Dict]]:
        """
        Get weather for multiple locations

        Args:
            locations: List of city names

        Returns:
            Dictionary mapping location names to weather info
        """
        results = {}
        for location in locations:
            results[location] = self.get_weather(location)

        return results
