import requests
from typing import Dict, List
import coloredlogs, logging

baseURL = "https://deckofcardsapi.com/api/deck"

class Deck:

    def __init__(self):
        deck = requests.get(f"{baseURL}/new/shuffle/?deck_count=1").json()

        self.id = deck["deck_id"]
        self.remaining = deck["remaining"]
        self.piles = {}


    def draw(self, n: int):
        drawnCards = requests.get(f"{baseURL}/{self.id}/draw/?count={n}").json()

        self.remaining = drawnCards["remaining"]
        return [Card(cardDict) for cardDict in drawnCards["cards"]]


    def __truediv__(self, pileNames: List):
        n = self.remaining // len(pileNames)
        extra = self.remaining % len(pileNames)

        for i,pileName in enumerate(pileNames):
            self.createPile(pileName)
            self.piles[pileName] + self.draw(n + (i<extra))

        return self.piles

    def createPile(self, pileName):
        self.piles[pileName] = Pile(pileName, self.id)
        return self.piles[pileName]

class Card:

    def __init__(self, cardDict: Dict[str, str]):
        self.img = cardDict["image"]
        self.val = cardDict["value"]
        self.suit = cardDict["suit"]
        self.id = cardDict["code"]

    def __repr__(self):
        return str(self.id)

class Pile:

    def __init__(self, id, deckId):
        self.id = id
        self.parent = deckId
        self.remaining = 0


    def __add__(self, cards: List[Card]):

        cardsStr = "?cards=" + str(cards[0])
        for i in range(1, len(cards)):
            cardsStr += "," + cards[i].id

        requests.get(f"{baseURL}/{self.parent}/pile/{self.id}/add/{cardsStr}")

        self.remaining += len(cards)



    def pick(self, card: Card):
        """pick a card, any card"""
        if self.remaining == 0:
            logging.warning("failed card pick. No cards left")
            return None

        response = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/draw/?cards={str(card)}"
        ).json()


        if not response["success"]:
            logging.warning(response["error"])
            return None

        if len(response["cards"]) == 0:
            logging.warning("failed card pick, card list is empty")
            return None


        return Card(response["cards"][0])

    

    def draw(self, n: int):
        """draw n random cards"""
        drawnCards = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/draw/random/?count={n}"
        ).json()


        return [Card(cardDict) for cardDict in drawnCards["cards"]]





# testing
if __name__ == "__main__":
    coloredlogs.install(level=logging.INFO)

    d = Deck()

    cards = d.draw(5)
    logging.info(f"cards drawn from deck: {cards}")

    piles = d / [123,253]
    logging.info(f"pile 123 has {piles[123].remaining} cards")
    logging.info(f"pile 253 has {piles[253].remaining} cards")


    pileCard = piles[123].pick("5D")
    logging.info(f"card picked from pile: {pileCard}")

    cards = piles[253].draw(5)
    logging.info(f"cards drawn from pile: {cards}")