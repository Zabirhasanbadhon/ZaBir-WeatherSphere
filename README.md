# 🌦️ ZaBir WeatherSphere
  
# ✨ A Modern Glassmorphism Weather Dashboard

A beautiful, real-time weather dashboard built with Python, Tkinter, and the Open-Meteo API. Featuring a transparent glass interface, dynamic backgrounds, city autocomplete, and interactive hourly forecasts.

## 🌤️ Key Features

Real-Time Weather: Displays temperature, feels-like temperature, weather conditions, humidity, wind speed, and air pressure.
Smart City Search: Search for cities worldwide with autocomplete suggestions.
Interactive Hourly Forecast: Explore upcoming hourly temperatures, weather conditions, and precipitation probabilities.
Glassmorphism Interface: Transparent glass-style elements that blend naturally with the background image.
Responsive Layout: Adapts the dashboard to different application window sizes.
Automatic Weather Updates: Refreshes weather information every 10 minutes.
Dynamic Background: Uses a custom background image with a generated gradient fallback when the image is unavailable.
Keyboard Navigation: Supports keyboard controls for searching and navigating city suggestions.

## 🛠️ Technologies & Tools

Technology	Purpose
Python	Core application logic
Tkinter	Graphical user interface
Pillow (PIL)	Image processing, brightness adjustment, and glass effects
Requests	HTTP requests to weather and geocoding APIs
Threading	Background network requests for a responsive interface
Open-Meteo API	Weather forecasts and city geocoding

## ⚙️ Application Configuration

Customize the dashboard through the configuration variables in the Python source code.

Setting	Description	Default Value
APP_NAME	Application title	ZaBir WeatherSphere
BACKGROUND_IMAGE_PATH	Background image location	D:\My Projects\Weather\Clouds.jpg
DEFAULT_CITY	Initial city	Dhaka
DEFAULT_COUNTRY	Initial country	Bangladesh
WINDOW_WIDTH	Initial window width	1400
WINDOW_HEIGHT	Initial window height	900
MIN_WIDTH	Minimum window width	1000
MIN_HEIGHT	Minimum window height	700
REFRESH_INTERVAL	Automatic refresh interval	10 minutes

## 🌐 Weather API & Data Sources

ZaBir WeatherSphere uses the free Open-Meteo API to retrieve weather information and search for geographical locations.

## 🌦️ Weather Forecast API

Provides current weather conditions and hourly forecast data.

🔗 https://api.open-meteo.com/v1/forecast

## 🗺️ Geocoding API

Searches for cities and retrieves their geographical coordinates.

🔗 https://geocoding-api.open-meteo.com/v1/search

## 📊 Weather Data

The dashboard retrieves:

Current temperature and apparent temperature
Relative humidity and atmospheric pressure
Wind speed and weather conditions
Hourly temperature and apparent temperature
Hourly precipitation probability
Weather codes used to display icons and descriptions

Default units: Celsius (°C), kilometers per hour (km/h), and hectopascals (hPa).

## 🎨 User Interface & Design

The dashboard combines modern visual styling with practical weather information.

Glassmorphism: Translucent cards that blend with the background.
Custom Background: Image scaling, brightness adjustment, and a gradient fallback.
Weather Icons: Visual indicators for sunny, cloudy, rainy, snowy, and stormy conditions.
Interactive Search: Canvas-rendered search field with autocomplete suggestions.
Hourly Navigation: Previous and next arrows for browsing forecast cards.
Dynamic Layout: Dashboard elements are redrawn when the window is resized.

## 🔄 Automatic Updates & Error Handling

The application includes mechanisms to improve reliability and responsiveness.

Automatically refreshes weather data every 10 minutes.
Performs network requests in background threads.
Handles connection failures and unsuccessful API responses.
Displays an error dialog when weather data cannot be retrieved.
Provides a fallback background if the configured image is unavailable.
Handles searches that return no matching city results.
Ignores outdated search and weather responses to prevent stale results from replacing newer data.

## 📋 Default Application Settings

Property	Value
Application Name	ZaBir WeatherSphere
Default Location	Dhaka, Bangladesh
Temperature Unit	Celsius
Wind Speed Unit	km/h
Pressure Unit	hPa
Refresh Interval	10 minutes
Forecast Type	Hourly
Interface Style	Transparent Glassmorphism

## 👨‍💻 Author

**Zabir Hasan**

🌐 www.zabirhasan.com
