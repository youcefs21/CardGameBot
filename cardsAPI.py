from typing import Dict, List

import coloredlogs
import logging
import requests

baseURL = "https://deckofcardsapi.com/api/deck"


class Deck:

    def __init__(self):
        deck = requests.get(f"{baseURL}/new/shuffle/?deck_count=1").json()

        self.id = deck["deck_id"]
        self.remaining = deck["remaining"]
        self.piles = {}

    def draw(self, n: int):
        drawn_cards = requests.get(f"{baseURL}/{self.id}/draw/?count={n}").json()

        self.remaining = drawn_cards["remaining"]
        return [Card(cardDict) for cardDict in drawn_cards["cards"]]

    def div(self, pile_names: List):
        n = self.remaining // len(pile_names)
        extra = self.remaining % len(pile_names)

        for i, pileName in enumerate(pile_names):
            self.createPile(pileName)
            self.piles[pileName] + self.draw(min(n + (i < extra), 24))

        return self.piles

    def createPile(self, pile_name):
        self.piles[pile_name] = Pile(pile_name, self.id)
        return self.piles[pile_name]


class Card:

    def __init__(self, card_dict: Dict[str, str]):
        self.img = card_dict["image"]
        self.val = card_dict["value"]
        self.suit = card_dict["suit"]
        self.id = card_dict["code"]

    def __repr__(self):
        return str(self.id)


class Pile:

    def __init__(self, id, deckId):
        self.id = id
        self.parent = deckId
        self.remaining = 0

    def __add__(self, cards: List[Card]):

        if None in cards:
            logging.warning("failed to add cards, None detected")
            return False

        cards_str = "?cards=" + str(cards[0])
        for i in range(1, len(cards)):
            cards_str += "," + cards[i].id

        requests.get(f"{baseURL}/{self.parent}/pile/{self.id}/add/{cards_str}")

        self.remaining += len(cards)
        return True

    def __repr__(self):
        pile_json = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/list"
        ).json()

        if not pile_json["success"]:
            return "<Empty Pile>"

        return str([x["code"] for x in pile_json["piles"][str(self.id)]["cards"]])

    def toList(self):
        pile_json = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/list"
        ).json()

        if not pile_json["success"]:
            return []

        return [Card(cardDict) for cardDict in pile_json["piles"][str(self.id)]["cards"]]

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
        drawn_cards = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/draw/random/?count={n}"
        ).json()

        return [Card(cardDict) for cardDict in drawn_cards["cards"]]


# testing
if __name__ == "__main__":
    coloredlogs.install(level=logging.INFO)

    d = Deck()

    cards = d.draw(5)
    logging.info(f"cards drawn from deck: {cards}")

    piles = d.div([123, 253])
    logging.info(f"pile 123 has {piles[123].remaining} cards")
    logging.info(f"pile 253 has {piles[253].remaining} cards")

    pileCard = piles[123].pick("5D")
    logging.info(f"card picked from pile: {pileCard}")

    cards = piles[253].draw(5)
    logging.info(f"cards drawn from pile: {cards}")
