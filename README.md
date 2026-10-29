🌦️ ZaBir WeatherSphere

ZaBir WeatherSphere is a modern weather dashboard built with Python and Tkinter. It features a transparent glass-style interface, a background image, real-time weather information, and an interactive hourly forecast.

✨ Features
Current Weather: Displays temperature, feels-like temperature, weather conditions, humidity, wind speed, and air pressure.
City Search: Search for cities worldwide using the Open-Meteo Geocoding API.
Autocomplete Suggestions: Displays matching cities with their administrative regions and countries.
Hourly Forecast: Shows upcoming hourly temperatures, weather conditions, precipitation probability, and feels-like temperatures.
Interactive Navigation: Navigate through hourly forecast cards using previous and next arrows.
Glassmorphism UI: Transparent glass-style elements that blend with the background image.
Responsive Dashboard: Adjusts the layout based on the application window size.
Automatic Refresh: Updates weather information every 10 minutes.
Fallback Background: Generates a gradient background if the specified background image is unavailable.
🛠️ Technologies Used
Python — Application logic
Tkinter — Graphical user interface
Pillow (PIL) — Background image processing, transparency effects, and image rendering
Requests — HTTP requests to weather and geocoding APIs
Threading — Background network requests to keep the interface responsive
Open-Meteo API — Weather forecasts and city geocoding

⚙️ Configuration

The application settings can be customized in the configuration section of the Python code.

APP_NAME — Application window title
BACKGROUND_IMAGE_PATH — Path to the background image
DEFAULT_CITY — Default city (Dhaka)
DEFAULT_COUNTRY — Default country (Bangladesh)
WINDOW_WIDTH and WINDOW_HEIGHT — Initial window dimensions
MIN_WIDTH and MIN_HEIGHT — Minimum window dimensions
REFRESH_INTERVAL — Automatic refresh interval, set to 10 minutes

🌐 API Data Sources

The application uses the following Open-Meteo endpoints:

Weather Forecast: https://api.open-meteo.com/v1/forecast
Geocoding: https://geocoding-api.open-meteo.com/v1/search

Weather data includes current conditions and hourly forecasts. API requests use automatic timezone detection, Celsius temperatures, and wind speed in kilometers per hour.

📋 Default Settings
Default Location: Dhaka, Bangladesh
Temperature Unit: Celsius (°C)
Wind Speed Unit: Kilometers per hour (km/h)
Automatic Refresh: Every 10 minutes
Interface: Transparent glass-style weather dashboard

🛡️ Error Handling

The application handles:

Missing or invalid background images
Unsuccessful API requests and connection errors
City searches with no matching results
Weather data retrieval failures
Invalid or incomplete API responses

## 👨‍💻 Author

**Zabir Hasan**

🌐 https://www.zabirhasan.com
