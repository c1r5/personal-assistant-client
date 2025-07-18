# tools/time_tools.py

from datetime import datetime, timedelta
import pytz
import dateparser
import locale

def _get_localized_datetime(timezone: str, lang: str):
    """Helper to get datetime object and set locale."""
    locale_map = {
        "pt": "pt_BR.UTF-8",
        "en": "en_US.UTF-8",
        "es": "es_ES.UTF-8",
        # Add other language mappings as needed
    }
    target_locale = locale_map.get(lang, "en_US.UTF-8")

    try:
        original_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, target_locale)
    except locale.Error:
        # Fallback if locale is not supported on the system
        original_locale = None

    now = datetime.now(pytz.timezone(timezone))
    return now, original_locale

def _restore_locale(original_locale):
    """Helper to restore the original locale."""
    if original_locale:
        try:
            locale.setlocale(locale.LC_TIME, original_locale)
        except locale.Error:
            pass # Ignore errors on restore

def get_current_time(timezone: str = "America/Sao_Paulo", lang: str = "pt") -> str:
    """
    Gets the current time for a given timezone and formats it for the specified language.
    """
    now, original_locale = _get_localized_datetime(timezone, lang)
    try:
        if lang == "pt":
            # Manual fallback para nomes de dia e mês
            dias = {
                "Monday": "segunda-feira",
                "Tuesday": "terça-feira",
                "Wednesday": "quarta-feira",
                "Thursday": "quinta-feira",
                "Friday": "sexta-feira",
                "Saturday": "sábado",
                "Sunday": "domingo",
            }
            meses = {
                "January": "janeiro",
                "February": "fevereiro",
                "March": "março",
                "April": "abril",
                "May": "maio",
                "June": "junho",
                "July": "julho",
                "August": "agosto",
                "September": "setembro",
                "October": "outubro",
                "November": "novembro",
                "December": "dezembro",
            }

            dia_semana_en = now.strftime("%A")
            mes_en = now.strftime("%B")

            dia_semana = dias.get(dia_semana_en, dia_semana_en)
            mes = meses.get(mes_en, mes_en)

            response = f"São {now.strftime('%H:%M')} de {dia_semana}, {now.strftime('%d')} de {mes} de {now.strftime('%Y')} (fuso horário: {now.strftime('%Z')})."
        else:
            response = now.strftime("It is currently %H:%M on %A, %B %d, %Y (timezone: %Z).")
        return response
    finally:
        _restore_locale(original_locale)

def get_day_of_week(date_str: str, lang: str = "pt") -> str:
    """
    Gets the day of the week for a given date string (e.g., "2024-07-17").
    """
    now, original_locale = _get_localized_datetime("UTC", lang) # Timezone doesn't matter here
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if lang == "pt":
            response = date.strftime(f"A data {date_str} cai em uma %A.")
        else:
            response = date.strftime(f"That date falls on a %A.")
        return response
    except Exception as e:
        return f"Error parsing date: {str(e)}"
    finally:
        _restore_locale(original_locale)

def parse_date_query(question: str, timezone: str = "America/Sao_Paulo", lang: str = "pt") -> str:
    """
    Parses a natural language query about a date and returns a formatted date string.
    """
    now, original_locale = _get_localized_datetime(timezone, lang)
    try:
        settings = {"PREFER_DATES_FROM": "current_period", "TIMEZONE": timezone}
        parsed = dateparser.parse(question, settings=settings)
        if not parsed:
            return "Não foi possível entender a data." if lang == "pt" else "Could not understand the date."

        if lang == "pt":
            response = parsed.strftime("Isso é %A, %d de %B de %Y.")
        else:
            response = parsed.strftime("That is %A, %B %d, %Y.")
        return response
    except Exception as e:
        return f"Error parsing question: {str(e)}"
    finally:
        _restore_locale(original_locale)

def calculate_future_date(days: int = 0, weeks: int = 0, timezone: str = "America/Sao_Paulo", lang: str = "pt") -> str:
    """
    Calculates a future date by adding days and/or weeks to the current date in a specific timezone.
    """
    now, original_locale = _get_localized_datetime(timezone, lang)
    try:
        future = now + timedelta(days=days + weeks * 7)

        if lang == "pt":
            # Fallback manual para português
            dias = {
                "Monday": "segunda-feira",
                "Tuesday": "terça-feira",
                "Wednesday": "quarta-feira",
                "Thursday": "quinta-feira",
                "Friday": "sexta-feira",
                "Saturday": "sábado",
                "Sunday": "domingo",
            }
            meses = {
                "January": "janeiro",
                "February": "fevereiro",
                "March": "março",
                "April": "abril",
                "May": "maio",
                "June": "junho",
                "July": "julho",
                "August": "agosto",
                "September": "setembro",
                "October": "outubro",
                "November": "novembro",
                "December": "dezembro",
            }

            dia_semana_en = future.strftime("%A")
            mes_en = future.strftime("%B")

            dia_semana = dias.get(dia_semana_en, dia_semana_en)
            mes = meses.get(mes_en, mes_en)

            response = f"Isso será em uma {dia_semana}, {future.strftime('%d')} de {mes} de {future.strftime('%Y')}."
        else:
            response = future.strftime("That will be a %A, %B %d, %Y.")
        return response
    finally:
        _restore_locale(original_locale)
