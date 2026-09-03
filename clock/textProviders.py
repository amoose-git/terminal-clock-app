"""
textProviders makes the single "one call on launch/refresh"
request to whichever source config.json selects, and returns
plain display-ready text (quote/verse + attribution).
"""
import requests

requestTimeoutSeconds = 6
maxScryfallAttempts = 8

# Scryfall (and good manners generally) expects a real
# User-Agent/Accept pair — the default requests UA gets
# a 400 back, so every call here sends this instead.
requestHeaders = {
    "User-Agent": "TerminalAsciiClock/1.0 (personal project)",
    "Accept": "application/json",
}

# characters that count as "this text already has its own
# quote marks" — checked so padQuote is never stacked on
# top of text that's already quoted
openingQuoteChars = ('"', "“", "'", "‘")
closingQuoteChars = ('"', "”", "'", "’")


def padQuote(text):
    """Wraps text in quote marks, padded off the text by one space."""
    return f'" {text.strip()} "'


def isAlreadyQuoted(text):
    """True if text already opens and closes with a quote mark."""
    return text.startswith(openingQuoteChars) and text.endswith(closingQuoteChars)


def fetchScryfallFlavor():
    """Gets a random Magic card's flavor text from Scryfall, trying a
    few random cards since not every card has flavor text."""
    url = "https://api.scryfall.com/cards/random"
    for _ in range(maxScryfallAttempts):
        try:
            response = requests.get(url, headers=requestHeaders,
                                     timeout=requestTimeoutSeconds)
            response.raise_for_status()
            card = response.json()
        except requests.RequestException:
            continue

        flavor = card.get("flavor_text")
        if not flavor and "card_faces" in card:
            for face in card["card_faces"]:
                if face.get("flavor_text"):
                    flavor = face["flavor_text"]
                    break

        if flavor:
            # flavor_text sometimes already carries its own quote marks,
            # so it's only padQuote-wrapped when it isn't already quoted.
            flavor = flavor.strip()
            displayFlavor = flavor if isAlreadyQuoted(flavor) else padQuote(flavor)
            return f'{displayFlavor}\n\n— {card.get("name", "Unknown card")}'
    return "No flavored card turned up after several tries — try again."


def fetchBibleVerse():
    """Gets a random ASV verse from bible-api.com."""
    url = "https://bible-api.com/data/asv/random"
    response = requests.get(url, headers=requestHeaders, timeout=requestTimeoutSeconds)
    response.raise_for_status()
    payload = response.json()["random_verse"]

    reference = f'{payload["book"]} {payload["chapter"]}:{payload["verse"]}'
    return f'{padQuote(payload["text"])}\n— {reference} (ASV)'


def fetchZenQuote():
    """Gets a random quote from the ZenQuotes API."""
    url = "https://zenquotes.io/api/random"
    response = requests.get(url, headers=requestHeaders, timeout=requestTimeoutSeconds)
    response.raise_for_status()
    quote = response.json()[0]
    return f'{padQuote(quote["q"])}\n— {quote["a"]}'


sourceFetchers = {
    "scryfall": fetchScryfallFlavor,
    "bible": fetchBibleVerse,
    "zenquotes": fetchZenQuote,
}


def fetchDisplayText(source):
    """Runs the configured source's single fetch, with a safe fallback."""
    fetcher = sourceFetchers.get(source, fetchScryfallFlavor)
    try:
        return fetcher()
    except requests.RequestException as error:
        return f"Couldn't reach {source} right now ({error.__class__.__name__})."
