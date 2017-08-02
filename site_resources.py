import scrapers

ressources_reference = {
    "Zeit": {
       "feedurl": "https://newsfeed.zeit.de/all",
       "scraper": scrapers.zeit_comments
    },
    "Handelsblatt": {
        "feedurl": {
            "http://www.handelsblatt.com/contentexport/feed/schlagzeilen",
            "http://www.handelsblatt.com/contentexport/feed/wirtschaft",
            "http://www.handelsblatt.com/contentexport/feed/top-themen",
            "http://www.handelsblatt.com/contentexport/feed/finanzen",
            "http://www.handelsblatt.com/contentexport/feed/unternehmen",
            "http://www.handelsblatt.com/contentexport/feed/politik",
            "http://www.handelsblatt.com/contentexport/feed/technologie",
            "http://www.handelsblatt.com/contentexport/feed/panorama",
            "http://www.handelsblatt.com/contentexport/feed/sport",
            "http://www.handelsblatt.com/contentexport/feed/hbfussball"},
        "scraper": scrapers.handelsblatt_comments
    },
    "TZ": {
        "feedurl": {
         "http://www.tz.de/politik/rssfeed.rdf",
         "https://www.tz.de/wirtschaft/rssfeed.rdf",
         "https://www.tz.de/welt/rssfeed.rdf",
         "https://www.tz.de/outdoor/rssfeed.rdf",
         "https://www.tz.de/leben/rssfeed.rdf",
         "https://www.tz.de/tv/rssfeed.rdf",
         "https://www.tz.de/kino/rssfeed.rdf",
         "https://www.tz.de/muenchen/rssfeed.rdf",
         "https://www.tz.de/bayern/rssfeed.rdf",
         "https://www.tz.de/sport/rssfeed.rdf",
         "https://www.tz.de/stars/rssfeed.rdf",
         "https://www.tz.de/reise/rssfeed.rdf",
         "https://www.tz.de/auto/rssfeed.rdf",
        },
        "scraper": scrapers.tz_comments
    },
    "Merkur": {
        "feedurl": {
         "http://www.merkur.de/politik/rssfeed.rdf",
         "https://www.merkur.de/lokales/rssfeed.rdf",
         "https://www.merkur.de/bayern/rssfeed.rdf",
         "https://www.merkur.de/wirtschaft/rssfeed.rdf",
         "https://www.merkur.de/sport/rssfeed.rdf",
         "https://www.merkur.de/welt/rssfeed.rdf",
         "https://www.merkur.de/kultur/rssfeed.rdf",
         "https://www.merkur.de/boulevard/rssfeed.rdf",
         "https://www.merkur.de/tv/rssfeed.rdf",
         "https://www.merkur.de/leben/rssfeed.rdf",
         "https://www.merkur.de/auto/rssfeed.rdf",
         "https://www.merkur.de/outdoor/rssfeed.rdf",
         "https://www.merkur.de/reise/rssfeed.rdf",
         "https://www.merkur.de/meinung/rssfeed.rdf",
         "https://www.merkur.de/kino/rssfeed.rdf",
        },
        "scraper": scrapers.merkur_comments
    },
    "NOZ": {
        "feedurl": {
         "http://www.noz.de/rss/ressort/Politik",
         "https://www.noz.de/rss/ressort/Fußball",
         "https://www.noz.de/rss/ressort/Sport",
         "https://www.noz.de/rss/ressort/Wirtschaft",
         "https://www.noz.de/rss/ressort/Kultur",
         "https://www.noz.de/rss/ressort/Medien",
         "https://www.noz.de/rss/ressort/Vermischtes",
         "https://www.noz.de/rss/ressort/Nordrhein-Westfalen",
        },
        "scraper": scrapers.noz_comments
    },
    "FAZ": {
        "feedurl": {
         "http://www.faz.net/rss/aktuell/",
         "http://www.faz.net/rss/aktuell/politik/",
         "http://www.faz.net/rss/aktuell/wirtschaft/",
         "http://www.faz.net/rss/aktuell/feuilleton/",
         "http://www.faz.net/rss/aktuell/sport/",
         "http://www.faz.net/rss/aktuell/lebensstil/",
         "http://www.faz.net/rss/aktuell/gesellschaft/",
         "http://www.faz.net/rss/aktuell/finanzen/",
         "http://www.faz.net/rss/aktuell/technik-motor/",
         "http://www.faz.net/rss/aktuell/wissen/",
         "http://www.faz.net/rss/aktuell/reise/",
         "http://www.faz.net/rss/aktuell/beruf-chance/",
         "http://www.faz.net/rss/aktuell/rhein-main/",
        },
        "scraper": scrapers.faz_comments
    },
    "NW": {
        "feedurl":
        "http://www.nw-news.de/_export/nw/rss_nachrichten/index.rss",
        "scraper": scrapers.nw_comments
    },
    "RP": {
        "feedurl": {
         "http://www.rp-online.de/feed.rss",
         "http://www.rp-online.de/politik/feed.rss",
         "http://www.rp-online.de/wirtschaft/feed.rss",
         "http://www.rp-online.de/panorama/feed.rss",
         "http://www.rp-online.de/sport/feed.rss",
         "http://www.rp-online.de/kultur/feed.rss",
         "http://www.rp-online.de/leben/gesundheit/feed.rss",
         "http://www.rp-online.de/digitales/feed.rss",
         "http://www.rp-online.de/leben/auto/feed.rss",
         "http://www.rp-online.de/leben/reisen/feed.rss",
         "http://www.rp-online.de/leben/beruf/feed.rss",
         },
        "scraper": scrapers.rp_comments
        },
    "TA": {
        "feedurl": "http://www.thueringer-allgemeine.de/" +
        "startseite/-/rss/OPg4/feed.rss",
        "scraper": scrapers.ta_comments
    },
    "Welt": {
        "feedurl": {
         "http://www.welt.de/feeds/latest.rss",
         "https://www.welt.de/feeds/topnews.rss",
         "https://www.welt.de/feeds/section/mediathek.rss",
         "https://www.welt.de/feeds/section/politik.rss",
         "https://www.welt.de/feeds/section/wirtschaft.rss",
         "https://www.welt.de/feeds/section/finanzen.rss",
         "https://www.welt.de/feeds/section/wirtschaft/webwelt.rss",
         "https://www.welt.de/feeds/section/kultur.rss",
         "https://www.welt.de/feeds/section/sport.rss",
         "https://www.welt.de/feeds/section/icon.rss",
         "https://www.welt.de/feeds/section/gesundheit.rss",
         "https://www.welt.de/feeds/section/vermischtes.rss",
         "https://www.welt.de/feeds/section/motor.rss",
         "https://www.welt.de/feeds/section/reise.rss",
         "https://www.welt.de/feeds/section/regional.rss",
         "https://www.welt.de/feeds/section/debatte.rss",
         },
        "scraper": scrapers.welt_comments
     },
    "Spiegel": {
        "feedurl": "http://www.spiegel.de/schlagzeilen/index.rss",
        "scraper": scrapers.spiegel_comments
     },
    "TAZ": {
        "feedurl": {
            "http://taz.de/Politik/!p4615;rss/",
            "http://taz.de/!p4608;rss/",
            "http://taz.de/Oeko/!p4610;rss/",
            "http://taz.de/Gesellschaft/!p4611;rss/",
            "http://taz.de/Kultur/!p4639;rss/",
            "http://taz.de/Sport/!p4646;rss/",
            "http://taz.de/Berlin/!p4649;rss/",
            "http://taz.de/Nord/!p4650;rss/",
            "http://taz.de/Wahrheit/!p4644;rss/"
            },
        "scraper": scrapers.taz_comments
     }
}
