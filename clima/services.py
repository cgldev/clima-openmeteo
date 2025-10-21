from typing import Any, Dict, List, Optional
import requests
from django.core.cache import cache

GEO_BASE = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_BASE = "https://api.open-meteo.com/v1/forecast"

# Mapas de weathercode a texto (resumen)
WEATHERCODE_ES = {
    0: "Cielo despejado",
    1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna ligera", 53: "Llovizna", 55: "Llovizna intensa",
    56: "Llovizna helada ligera", 57: "Llovizna helada intensa",
    61: "Lluvia ligera", 63: "Lluvia", 65: "Lluvia intensa",
    66: "Lluvia helada ligera", 67: "Lluvia helada intensa",
    71: "Nieve ligera", 73: "Nieve", 75: "Nieve intensa",
    77: "Granos de nieve",
    80: "Chaparrones ligeros", 81: "Chaparrones", 82: "Chaparrones intensos",
    85: "Chaparrones de nieve ligeros", 86: "Chaparrones de nieve intensos",
    95: "Tormenta eléctrica",
    96: "Tormenta c/granizo ligero", 97: "Tormenta c/granizo fuerte"
}

def _get_with_cache(url: str, params: Dict[str, Any], cache_key: str, ttl: int = 300) -> Dict[str, Any]:
    data = cache.get(cache_key)
    if data is None:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        cache.set(cache_key, data, ttl)
    return data

def buscar_ciudades(nombre: str, limite: int = 5, idioma: str = "es") -> List[Dict[str, Any]]:
    """Devuelve posibles ciudades para el texto buscado."""
    if not nombre:
        return []
    params = {"name": nombre, "count": limite, "language": idioma, "format": "json"}
    js = _get_with_cache(GEO_BASE, params, cache_key=f"geo::{nombre.lower()}::{limite}::{idioma}", ttl=600)
    return js.get("results", []) or []

def pronostico(lat: float, lon: float, dias: int = 7, idioma: str = "es") -> Dict[str, Any]:
    """Devuelve clima actual + diario 7 días + algunas series horarias."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "forecast_days": dias,
        "language": idioma,
    }
    js = _get_with_cache(FORECAST_BASE, params, cache_key=f"fc::{round(lat,3)}::{round(lon,3)}::{dias}::{idioma}", ttl=300)
    return js

def texto_weathercode(code: Optional[int]) -> str:
    if code is None:
        return ""
    return WEATHERCODE_ES.get(int(code), f"Código {code}")
