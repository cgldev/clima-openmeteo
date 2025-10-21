from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from .services import buscar_ciudades, pronostico, texto_weathercode

class BuscarCiudadView(TemplateView):
    template_name = "clima/buscar.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get("q") or "").strip()
        ctx["q"] = q
        ctx["resultados"] = buscar_ciudades(q, limite=8) if q else []
        return ctx


class PronosticoView(TemplateView):
    template_name = "clima/pronostico.html"

    def get(self, request, *args, **kwargs):
        # Requiere lat/lon por querystring
        try:
            lat = float(request.GET.get("lat"))
            lon = float(request.GET.get("lon"))
        except (TypeError, ValueError):
            messages.error(request, "Faltan coordenadas (lat/lon). Buscá una ciudad primero.")
            return redirect("home")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lat = float(self.request.GET.get("lat"))
        lon = float(self.request.GET.get("lon"))
        nombre = self.request.GET.get("nombre") or ""
        datos = pronostico(lat, lon, dias=7)

        # Armar bloques
        current = datos.get("current_weather") or {}
        daily = datos.get("daily") or {}

        # Lista de días para tabla
        dias = []
        times = daily.get("time") or []
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        wcode = daily.get("weathercode") or []
        prec = daily.get("precipitation_sum") or []

        for i in range(len(times)):
            dias.append({
                "fecha": times[i],
                "tmax": tmax[i] if i < len(tmax) else None,
                "tmin": tmin[i] if i < len(tmin) else None,
                "clima": texto_weathercode(wcode[i] if i < len(wcode) else None),
                "lluvia_mm": prec[i] if i < len(prec) else None,
            })

        ctx.update({
            "nombre": nombre,
            "lat": lat, "lon": lon,
            "current": current,
            "dias": dias,
        })
        return ctx

