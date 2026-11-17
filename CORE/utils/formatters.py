# backend/utils/formatters.py
# by LECHAT Jérôme; creation date: 10/2026, last edit: 10/2026
# helped by the following AI tool(s): GEMINI (pro)
import re


def parse_price(text: str) -> float:
    if not text or str(text).strip() in ("", "-", "None"):
        return 0.0
    try:
        clean = text.strip().lower().replace('€', '').replace('htva', '').replace('ttc', '').replace('\xa0', '').replace('\u200e', '').strip()
        clean = re.sub(r"[^\d,\.]", "", clean)
        if not clean: return 0.0

        if ',' in clean and '.' in clean:
            if clean.rfind('.') < clean.rfind(','):
                clean = clean.replace('.', '').replace(',', '.')
            else:
                clean = clean.replace(',', '')
        elif ',' in clean:
            clean = clean.replace(',', '.')
        return float(clean)
    except (ValueError, TypeError):
        return 0.0

def clean_ean(raw: str) -> str:
    cleaned = "".join(filter(str.isalnum, str(raw))).upper()
    return cleaned if cleaned else "-"

def clean_mpn(raw: str, brands_list: set) -> str:
    cleaned = str(raw).lower()
    for b in sorted(brands_list, key=len, reverse=True):
        cleaned = cleaned.replace(b.lower(), "")
    return " ".join(cleaned.split()).strip().upper() or "-"

def compute_price_evolution(base: float, current: float) -> str:
    if base > 0 and current > 0:
        diff = round(current - base, 2)
        pct = round((diff / base) * 100, 1)
        if diff > 0: return f"+{diff}€ (+{pct}%)"
        elif diff < 0: return f"{diff}€ ({pct}%)"
        else: return "="
    return "-"


# === PLAYGROUND ===
if __name__ == "__main__":
    pass
