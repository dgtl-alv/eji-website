"""Locations section: Boost Charge stats, static map, charger types (after alvaauto.com/locations)."""
import json, os

MAPS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "maps.json")))


def locations(lg):
    pre = "" if lg == "en" else "../"
    en = lg == "en"
    stats = [
        ("483", "Locations" if en else "Lokasi"),
        ("1,037" if en else "1.037", "Connectors" if en else "Konektor"),
        ("974", "Devices" if en else "Perangkat"),
    ]
    app = "Applicable for:" if en else "Dapat digunakan untuk:"
    cn3 = "CERVO and N3 Lineup" if en else "CERVO dan N3 Lineup"
    chargers = [
        ("logo-charging-alva-bc.webp", "4kW", "Charge 10%-50% in less than 30 minutes" if en else "Isi 10%-50% dalam kurang dari 30 menit", "charging-alva-4kw.webp", cn3),
        ("logo-charging-alva-bc.webp", "3kW", "Charge 20%-80% in less than 1 hour" if en else "Isi 20%-80% dalam kurang dari 1 jam", "charging-alva-3kw.webp", cn3),
        ("logo-charging-alva-bc.webp", "2kW", "Charge 20%-80% in less than 1 hour" if en else "Isi 20%-80% dalam kurang dari 1 jam", "charging-alva-2kw.webp", cn3),
        ("logo-charging-alva.webp", "", "Basic charging model for all ALVA lineup." if en else "Model pengisian daya dasar untuk semua lineup ALVA.", "charging-alva-v2.webp", "All ALVA lineup" if en else "Semua lineup ALVA"),
    ]
    stat_html = "\n".join(
        f'        <div class="stat-card"><span class="stat-num">{n}</span><span class="stat-label">{l}</span></div>'
        for n, l in stats)
    cards = []
    for logo, kw, desc, img, fit in chargers:
        alt = "ALVA Boost Charge Station" if kw else "ALVA Charging Station"
        kw_html = f'<span class="kw">{kw}</span>' if kw else ""
        cards.append(
            f'        <div class="charger">\n'
            f'          <div class="charger-inner">\n'
            f'            <div class="charger-text">\n'
            f'              <img class="charger-logo" src="{pre}assets/{logo}" alt="{alt}">\n'
            f'              <div class="charger-spec">{kw_html}<span>{desc}</span></div>\n'
            f'            </div>\n'
            f'            <img class="charger-img" src="{pre}assets/{img}" alt="" loading="lazy">\n'
            f'          </div>\n'
            f'          <div class="charger-foot"><span>{app}</span><b>{fit}</b></div>\n'
            f'        </div>')
    sid = "locations" if en else "lokasi"
    kicker = "Discover ALVA's charging solutions that meet your needs." if en else "Temukan solusi pengisian daya ALVA sesuai kebutuhanmu."
    h2 = "Charge Anytime, Anywhere." if en else "Isi Daya Kapan Saja, Di Mana Saja."
    note = ("Each dot is an ALVA charging location. Locations as of November 2026; some locations share the same point."
            if en else
            "Setiap titik adalah lokasi pengisian daya ALVA. Data lokasi per November 2026; beberapa lokasi berada di titik yang sama.")
    return (
        f'  <section id="{sid}">\n'
        f'    <div class="wrap">\n'
        f'      <div class="section-head center">\n'
        f'        <p class="kicker">{kicker}</p>\n'
        f'        <h2>{h2}</h2>\n'
        f'      </div>\n\n'
        f'      <div class="boost-head"><img src="{pre}assets/BOOST-CHARGE-STATION-black.png" alt=""><span>BOOST CHARGE STATION</span></div>\n'
        f'      <div class="stat-cards">\n{stat_html}\n      </div>\n\n'
        f'      <div class="map-card">\n'
        f'        <div class="map-main">{MAPS["main"]}</div>\n'
        f'        <div class="map-inset"><div class="inset-title">Jabodetabek</div>{MAPS["inset"]}</div>\n'
        f'      </div>\n'
        f'      <p class="note">{note}</p>\n\n'
        f'      <div class="chargers">\n' + "\n".join(cards) + '\n      </div>\n'
        f'    </div>\n'
        f'  </section>\n\n')
