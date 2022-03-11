from typing import Dict, List, Union

import coloredlogs
import logging
import requests

baseURL = "https://deckofcardsapi.com/api/deck"


class Deck:

    def __init__(self):
        deck = requests.get(f"{baseURL}/new/shuffle/?deck_count=1").json()

        self.id: str = deck['deck_id']
        self.remaining: int = deck['remaining']
        self.piles: Dict[Union[int, str], Pile] = {}

    def draw(self, n: int):
        """
        draw n cards from the deck

        :param n: number of cards to draw
        :return: a list of Card objects that have been drawn from the deck
        """
        drawn_cards = requests.get(f"{baseURL}/{self.id}/draw/?count={n}").json()

        self.remaining = drawn_cards['remaining']
        return [Card(cardDict) for cardDict in drawn_cards['cards']]

    def div(self, pile_names: List[Union[int, str]]):
        """
        Divide a deck evenly into piles,

        :param pile_names: A list of pile names
        :return: A dictionary of all the piles in the deck
        """
        n = self.remaining // len(pile_names)
        extra = self.remaining % len(pile_names)

        for i, pileName in enumerate(pile_names):
            self.createPile(pileName)
            self.piles[pileName].add(
                self.draw(min(n + (i < extra), 24))
            )

        return self.piles

    def createPile(self, pile_name: Union[int, str]):
        """
        Create a pile given a name

        :param pile_name: name of the pile
        :return: The pile that was just created
        """
        self.piles[pile_name] = Pile(pile_name, self.id)
        return self.piles[pile_name]


class Card:

    def __init__(self, card_dict: Dict[str, str]):
        self.img = card_dict['image']
        self.val = card_dict['value']
        self.suit = card_dict['suit']
        self.id = card_dict['code']

    def __repr__(self):
        return str(self.id)

    def __int__(self):
        num_char = self.id[0]
        conversion_dict = {"0": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        if num_char in conversion_dict.keys():
            return conversion_dict[num_char]
        return int(num_char)

    def __gt__(self, other):
        self_num = int(self)
        try:
            return self_num > int(other)
        except TypeError:
            return self_num > other

    def __eq__(self, other):
        self_num = int(self)
        try:
            return self_num == int(other)
        except TypeError:
            return self_num == other

    def __ge__(self, other):
        return self > other or self == other


class Pile:

    def __init__(self, pile_id, deck_id):
        self.id = pile_id
        self.parent = deck_id
        self.remaining = 0

    def add(self, pile_cards: List[Card]):
        """
        adds a list of cards to self Pile

        :param pile_cards: List of cards or card codes to add
        :return: False if failed, True if success
        """

        if None in pile_cards:
            logging.warning("failed to add cards, None detected")
            return False

        cards_str = "?cards=" + str(pile_cards[0])
        for i in range(1, len(pile_cards)):
            cards_str += "," + pile_cards[i].id

        requests.get(f"{baseURL}/{self.parent}/pile/{self.id}/add/{cards_str}")

        self.remaining += len(pile_cards)
        return True

    def __repr__(self):
        pile_json = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/list"
        ).json()

        if not pile_json['success']:
            return "<Empty Pile>"

        return str([x['code'] for x in pile_json['piles'][str(self.id)]['cards']])

    def toList(self):
        """
        :return: a list of Cards that are in the pile
        """
        pile_json = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/list"
        ).json()

        if not pile_json['success']:
            return []

        return [Card(cardDict) for cardDict in pile_json['piles'][str(self.id)]['cards']]

    def pick(self, card: Union[Card, str]):
        """
        pick a card, any card

        :param card: Card object or card code of the card you want to pull from the pile
        :returns: Card picked or None if card failed
        """
        if self.remaining == 0:
            logging.warning("failed card pick. No cards left")
            return None

        response = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/draw/?cards={str(card)}"
        ).json()

        if not response['success']:
            logging.warning(response['error'])
            return None

        if len(response['cards']) == 0:
            logging.warning("failed card pick, card list is empty")
            return None

        return Card(response['cards'][0])

    def draw(self, n: int):
        """
        draw n random cards from the Pile

        :param n: number of cards to draw
        :return: a list of Card objects that have been drawn from the pile
        """
        drawn_cards = requests.get(
            f"{baseURL}/{self.parent}/pile/{self.id}/draw/random/?count={n}"
        ).json()

        return [Card(cardDict) for cardDict in drawn_cards['cards']]


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
