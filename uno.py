## TODO:
## 
## - Show the top card right after showing whose turn it is
## - Allow commands for spelling out the entire word instead of
##   using abbreviations (e.g. Accept `.red` as well as `.r`)
## - UNO should be mentioned when only one card is left in hand
## - non-command PM to UnlikeBot during ongoing UNO game works like `.send`
## - mention when the deck runs out and discard pile goes into deck

from enum import Enum
import random
from random import shuffle
import discord

client = None   # discord.Client
players = []    # list of Player
channel = None  # discord.Channel
game = None     # Game

class CardColor(Enum):
    """Enumeration of colors of UNO cards."""
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4
    BLACK = 5


class CardType(Enum):
    """Enumeration of types of UNO cards."""
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    SKIP = 10
    REVERSE = 11
    DRAW_TWO = 12
    WILD = 13
    WILD_DRAW_FOUR = 14


class Card:
    """
    An UNO card.

    Attributes:
    color(CardColor)
    type (CardType)
    """
    def __init__(self, color, type):
        """
        Constructor of the card.

        Arguments:
        color(CardColor)
        type (CardType)
        """
        self.color = color
        self.type = type

    def __str__(self):
        """String representation of the card.

        Return:
        String
        """
        s = ""
        # Add the color of the card
        if self.color == CardColor["RED"]:
            s += "[R]"
        elif self.color == CardColor["YELLOW"]:
            s += "[Y]"
        elif self.color == CardColor["GREEN"]:
            s += "[G]"
        elif self.color == CardColor["BLUE"]:
            s += "[B]"
        # Add the type of the card
        if self.type == CardType["ZERO"]:
            s += "(0)"
        elif self.type == CardType["ONE"]:
            s += "(1)"
        elif self.type == CardType["TWO"]:
            s += "(2)"
        elif self.type == CardType["THREE"]:
            s += "(3)"
        elif self.type == CardType["FOUR"]:
            s += "(4)"
        elif self.type == CardType["FIVE"]:
            s += "(5)"
        elif self.type == CardType["SIX"]:
            s += "(6)"
        elif self.type == CardType["SEVEN"]:
            s += "(7)"
        elif self.type == CardType["EIGHT"]:
            s += "(8)"
        elif self.type == CardType["NINE"]:
            s += "(9)"
        elif self.type == CardType["SKIP"]:
            s += "(S)"
        elif self.type == CardType["REVERSE"]:
            s += "(R)"
        elif self.type == CardType["DRAW_TWO"]:
            s += "(D2)"
        elif self.type == CardType["WILD"]:
            s += "[W]"
        else:
            s += "[WD4]"
        return s

    def __repr__(self):
        """
        Repr representation of the card.

        Return:
        String
        """
        return self.__str__()
            
    def equals(self, card):
        """
        Determines if self is the same card as 'card'

        Argument:
        card(Card): card for comparing
        
        Return:
        bool
        """
        return (self.color == card.color and self.type == card.type)

    def equals_color(self, card):
        """
        Determines if self has the same color as 'card'

        Argument:
        card(Card): card for comparing

        Return:
        bool
        """
        return self.color == card.color

    def equals_type(self, card):
        """
        Determines if self has same type as 'card'

        Argument:
        card(Card): card for comparing

        Return:
        bool
        """
        return self.type == card.type

    def get_color(self):
        """
        Returns the color

        Return:
        CardColor
        """
        return self.color

    def get_type(self):
        """
        Returns the type

        Return:
        CardType
        """
        return self.type

    def get_compare_key(self):
        """
        Returns the key for comparing multiple cards

        Return:
        int
        """
        return self.color.value * 100 + self.type.value
        

class Player:
    """
    An UNO player.

    Attributes:
    cards(list of Card): UNO cards in hand
    score(int):          Score accumulated during the set of UNO games
    user (discord.User): User object represented
    """
    def __init__(self, user):
        """
        Constructor of the player.

        Argument:
        user(discord.User)
        """
        self.cards = []
        self.score = 0
        self.user = user

    def receive_card(self, card):
        """
        Adds 'card' to the player's hand.

        Argument:
        card(Card)
        """
        self.cards.append(card)

    def discard_card(self, index):
        """
        Gets rid of player's card with given index.

        Argument:
        index(int)
        """
        del(self.cards[index])

    def get_hand(self):
        """
        Returns a string representation of all cards in hand.

        Return:
        str
        """
        index = 1
        str_repr = "```\n"
        for card in self.cards:
            str_repr += str(index) + "." + str(card) + "  "
            index += 1
        str_repr += "```"
        return str_repr

    def get_cards(self):
        """
        Returns the list of cards the player has.
        
        Return:
        list of Card
        """
        return self.cards

    def shuffle_cards(self):
        """Shuffles the cards in hand."""
        shuffle(self.cards)

    def add_score(self, score):
        """
        Adds to the player's current score.

        Argument:
        score(int)
        """
        self.score += score

    def get_score(self):
        """
        Returns the player's current score.

        Return:
        int
        """
        return self.score

    def reset_cards(self):
        """Empties the player's current hand."""
        self.cards = []

    def sort_cards(self):
        """Sorts the player's current cards."""
        self.cards = sorted(self.cards, key=Card.get_compare_key)

    def get_user(self):
        """
        Returns the user represented by this player.

        Return:
        discord.User
        """
        return self.user


class Game:
    """
    A single UNO game.

    Attributes:
    players              (list of Player): Players playing the game
    deck                 (list of Card)  : Cards on deck
    discard              (list of Card)  : Pile of discarded cards
    wild_color           (CardColor)     : Color called upon playing wild card,
                                           or Black if no wild card is played
    winner_index         (int)           : Index of the player who plays the
                                           last card in hand, or -1 if there is
                                           none
    clockwise            (bool)          : Whether to proceed to next turn in
                                           clockwise order. if false, then the
                                           order is counterclockwise.
    turn                 (int)           : Index of the player who has the
                                           current turn
    is_wild_during_init  (bool)          : Flag of whether the first discarded
                                           card is a Wild card
    is_playing_wild      (bool)          : Flag of whether the current player is
                                           playing a Wild card
    is_playing_wd4       (bool)          : Flag of whether the current player is
                                           playing a Wild Draw Four card
    is_checking_challenge(bool)          : Flag of whether the Wild Four card is
                                           challenged
    is_drawing           (bool)          : Flag of whether the current player is
                                           drawing a card
    is_legal_wd4         (bool)          : Flag of whether a legal Wild Draw
                                           Four card was played
    wd4_player_index     (int)           : Index of the player who is playing a
                                           Wild Draw Four card, or -1 if nobody
                                           is playing a Wild Draw Four card
    """
    def __init__(self, players):
        """
        Constructor of Game.

        Argument:
        players(list of Player)
        """
        self.players = players
        self.deck = []
        self.discard = []
        self.wild_color = CardColor["BLACK"]
        self.winner_index = -1
        self.clockwise = True
        self.turn = 1
        self.is_wild_during_init = False
        self.is_playing_wild = False
        self.is_playing_wd4 = False
        self.is_checking_challenge = False
        self.is_drawing = False
        self.is_legal_wd4 = False
        self.wd4_player_index = -1
        self.__init_deck__()
        # Distribute seven cards to every player
        for player in self.players:
            player.reset_cards()
            for time in range(7):
                self.__give_topdeck_to_player__(player)
            player.sort_cards()
        # Discard a card from the top of the deck
        self.__discard_topdeck__()
        # If the discarded card is Wild Draw Four, shuffle and discard again
        while self.discard[-1].equals(
                Card(CardColor["BLACK"], CardType["WILD_DRAW_FOUR"])):
            self.deck.append(self.discard[-1])
            del(self.discard[-1])
            self.__shuffle_deck__()
            self.__discard_topdeck__()
        # Cases where the first discard is an action card
        if self.discard[-1].get_type() == CardType["SKIP"]:
            self.__next_turn__()
        elif self.discard[-1].get_type() == CardType["DRAW_TWO"]:
            self.__give_topdeck_to_player__(self.players[self.turn])
            self.__give_topdeck_to_player__(self.players[self.turn])
            self.players[self.turn].sort_cards()
            self.__next_turn__()
        elif self.discard[-1].get_type() == CardType["REVERSE"]:
            self.clockwise = False
            self.__next_turn__()
        elif self.discard[-1].get_type() == CardType["WILD"]:
            self.is_wild_during_init = True

    def __init_deck__(self):
        """Fill the deck with a full deck of UNO cards."""
        # Add the colored cards
        for color in range(1, 5):
            self.deck.append(Card(CardColor(color), CardType["ZERO"]))
            for type in range(1, 13):
                for time in range(2):
                    self.deck.append(Card(CardColor(color), CardType(type)))
        # Add Wild cards and Wild Draw Four cards
        for time in range(4):
            self.deck.append(Card(CardColor["BLACK"], CardType["WILD"]))
            self.deck.append(
                    Card(CardColor["BLACK"], CardType["WILD_DRAW_FOUR"]))
        self.__shuffle_deck__()

    def __shuffle_deck__(self):
        """Shuffles the current deck"""
        shuffle(self.deck)

    def __give_topdeck_to_player__(self, player):
        """
        Adds the top card from the deck to player's hand.

        Argument:
        player(Player): The player receiving the topdeck

        Return:
        bool: False if the deck ran out of cards, True otherwise
        """
        # Move discarded cards to the deck if the deck is empty
        if not self.deck:
            self.deck = self.discard[:-1]
            self.__shuffle_deck__()
            self.discard = [self.discard[-1]]
            # Ran out of cards from deck/discard, so player cannot draw
            if not self.deck:
                return False
        player.receive_card(self.deck[-1])
        del(self.deck[-1])
        return True

    def __discard_topdeck__(self):
        """Discard the top card from the deck."""
        self.discard.append(self.deck[-1])
        del(self.deck[-1])

    def __discard_player_card__(self, player, card_index):
        """
        Discard the player's card with the given index.

        Argument:
        player    (Player): The player from whom the card is to be discarded
        card_index(int)   : The index of the card to discard
        """
        self.discard.append(player.get_cards()[card_index])
        player.discard_card(card_index)

    def __next_turn__(self):
        """Proceed to the next player's turn."""
        if self.clockwise:
            self.turn += 1
            if self.turn >= len(self.players):
                self.turn -= len(self.players)
        else:
            self.turn -= 1
            if self.turn < 0:
                self.turn += len(self.players)

    def __can_be_played__(self, card):
        """
        Determines if the card can currently be played.

        Return:
        bool: True if the card can be played, False otherwise
        """
        if (self.wild_color != CardColor["BLACK"]
                and card.get_color() == self.wild_color):
            return True
        if card.equals_color(self.discard[-1]):
            return True
        if card.equals_type(self.discard[-1]):
            return True
        if card.get_color() == CardColor["BLACK"]:
            return True
        return False

    async def __play_card__(self, index):
        """
        Play the card of the given index.

        Argument:
        index(int): Index of the card
        """
        card = self.players[self.turn].get_cards()[index]
        self.__discard_player_card__(self.players[self.turn], index)
        num_cards_in_hand = len(self.players[self.turn].get_cards())
        msg_str = "**"
        msg_str += self.players[self.turn].get_user().name
        msg_str += "** has played `"
        msg_str += str(card)
        msg_str += "` and now has **"
        msg_str += str(num_cards_in_hand)
        msg_str += " card"
        if num_cards_in_hand != 1:
            msg_str += "s"
        msg_str += "** in hand."
        await announce([self.players[self.turn]], msg_str)
        turn_before = self.turn
        # Skip card
        if card.get_type() == CardType["SKIP"]:
            self.__next_turn__()
            await announce(
                    [self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "**'s turn is skipped.")
            await message_player(
                    self.players[self.turn],
                    "Your turn has been skipped.")
            self.__next_turn__()
            self.wild_color = CardColor["BLACK"]
        # Draw Two card
        elif card.get_type() == CardType["DRAW_TWO"]:
            self.__next_turn__()
            count = 0
            for i in range(2):
                if self.__give_topdeck_to_player__(self.players[self.turn]):
                    count += 1
                else:
                    break
            announce_str = ""
            pm_str = ""
            if count == 0:
                announce_str += ("**"
                        + self.players[self.turn].get_user().name
                        + "** tried to draw two cards, but the deck ran out of "
                        + "cards.")
                pm_str += ("You tried to draw two cards, but the deck ran out "
                        + "of cards, so you could not draw any.")
            elif count == 1:
                announce_str += ("**"
                        + self.players[self.turn].get_user().name
                        + "** tried to draw two cards, but only one card was "
                        + "drawn, since the deck ran out of cards.")
                pm_str += ("You have drawn `"
                        + str(self.players[self.turn].get_cards()[-1])
                        + "`, but you could not draw any more cards because the"
                        + " deck ran out of cards.")
            else:
                announce_str += ("**"
                        + self.players[self.turn].get_user().name
                        + "** drew two cards.")
                pm_str += ("You have drawn `"
                        + str(self.players[self.turn].get_cards()[-2])
                        + "` and `"
                        + str(self.players[self.turn].get_cards()[-1])
                        + "`.")
            announce_str += " Their turn is skipped."
            pm_str += " Your turn is skipped."
            await announce([self.players[self.turn]], announce_str)
            await message_player(self.players[self.turn], pm_str)
            self.players[self.turn].sort_cards()
            self.__next_turn__()
            self.wild_color = CardColor["BLACK"]
        # Reverse card
        elif card.get_type() == CardType["REVERSE"]:
            # Acts the same way as Skip card if there are only two players
            if len(self.players) == 2:
                self.__next_turn__()
                await announce(
                        [self.players[self.turn]],
                        "**"
                        + self.players[self.turn].get_user().name
                        + "**'s turn is skipped.")
                await message_player(
                        self.players[self.turn],
                        "Your turn is skipped.")
                self.__next_turn__()
            else:
                await announce([], "The order has been reversed.")
                if self.clockwise:
                    self.clockwise = False
                else:
                    self.clockwise = True
                self.__next_turn__()
            self.wild_color = CardColor["BLACK"]
        # Wild card
        elif card.get_type() == CardType["WILD"]:
            await announce(
                    [self.players[self.turn]],
                    "Waiting for **"
                    + self.players[self.turn].get_user().name
                    + "** to choose a color...")
            await message_player(
                    self.players[self.turn],
                    "Choose a color by typing `.r`(red), `.y`(yellow), "
                    + "`.g`(green), or `.b`(blue).")
            self.is_playing_wild = True
        # Wild Draw Four card
        elif card.get_type() == CardType["WILD_DRAW_FOUR"]:
            # Determine if Wild Draw Four card is legal
            self.is_legal_wd4 = True
            for card_it in self.players[self.turn].get_cards():
                if card_it.get_color() == CardColor["BLACK"]:
                    continue
                elif card_it.get_color() == self.wild_color:
                    self.is_legal_wd4 = False
                    break
                elif card_it.equals_color(self.discard[-2]):
                    self.is_legal_wd4 = False
                    break
            self.wild_color = CardColor["BLACK"]
            await announce(
                    [self.players[self.turn]],
                    "Waiting for **"
                    + self.players[self.turn].get_user().name
                    + "** to choose a color...")
            await message_player(
                    self.players[self.turn],
                    "Choose a color by typing `.r`(red), `.y`(yellow), "
                    + "`.g`(green), or `.b`(blue).")
            self.is_playing_wd4 = True
        # A non-action card
        else:
            self.__next_turn__()
            self.wild_color = CardColor["BLACK"]
        # If the player wins the match
        if not self.players[turn_before].get_cards():
            self.winner_index = turn_before

    async def announce_if_first_discard_wild(self):
        """
        If the first discarded card is Wild card, announces so

        Return:
        bool: True if the first discarded card is a Wild card, False otherwise
        """
        if self.is_wild_during_init:
            await announce(
                    [self.players[self.turn]],
                    "The first discarded card is a wild card. **"
                    + self.players[self.turn].get_user().name
                    + "** will choose a color.")
            await message_player(
                    self.players[self.turn],
                    "The first discarded card is a wild card. Choose a color by"
                    + " typing `.r`(red), `.y`(yellow), `.g`(green), or "
                    + "`.b`(blue).")
            return True
        return False
    
    async def run(self, message):
        """Runs the game with the given message.

        Argument:
        message(Discord.message): Message to process

        Return:
        bool: False if the game has ended this turn, True otherwise
        """
        # Process only the command given by the current player
        if message.author != self.players[self.turn].get_user():
            return True
        content = message.content.lower()
        command = content.split()[0]
        # Choosing a color for Wild card (discarded prior to starting the game)
        if self.is_wild_during_init:
            if command not in [".r", ".y", ".g", ".b"]:
                await message_player(self.players[self.turn], "Invalid input.")
                return True
            color_index = [".r", ".y", ".g", ".b"].index(command)
            self.wild_color = CardColor(color_index + 1)
            await announce([self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "** has called `"
                    + self.wild_color.name
                    + "` as the wild color.")
            self.is_wild_during_init = False
            await self.announce_turn()
        # Choosing a color when a Wild card is played
        elif self.is_playing_wild:
            if command not in [".r", ".y", ".g", ".b"]:
                await message_player(self.players[self.turn], "Invalid input.")
                return True
            color_index = [".r", ".y", ".g", ".b"].index(command)
            self.wild_color = CardColor(color_index + 1)
            await announce([self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "** has called "
                    + self.wild_color.name
                    + " as the wild color.")
            self.__next_turn__()
            await self.announce_turn()
            self.is_playing_wild = False
            # If the wild card was the last card, end the game
            if self.winner_index != -1:
                return False
        # Choosing a color for WD4
        elif self.is_playing_wd4: 
            if command not in [".r", ".y", ".g", ".b"]:
                await message_player(self.players[self.turn], "Invalid input.")
                return True
            color_index = [".r", ".y", ".g", ".b"].index(command)
            self.wild_color = CardColor(color_index + 1)
            await announce([self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "** has called `"
                    + self.wild_color.name
                    + "` as the wild color.")
            self.wd4_player_index = self.turn
            self.__next_turn__()
            await announce([self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "** may challenge this Wild Draw Four. Waiting for their "
                    + "response...")
            await message_player(self.players[self.turn],
                    "You are about to draw four cards and be skipped. The Wild "
                    + "Draw Four is legal if and only if the player has no "
                    + "card that can be played. Will you challenge **"
                    + self.players[self.wd4_player_index].get_user().name
                    + "**'s Wild Draw Four? Answer by `.y`(yes) or "
                    + "`.n`(no).")
            self.is_playing_wd4 = False
            self.is_checking_challenge = True
        # Waiting for reply regarding whether to challenge the WD4
        elif self.is_checking_challenge:
            if command not in [".y", ".n"]:
                await message_player(self.players[self.turn], "Invalid input.")
                return True
            # If challenged
            if command == ".y":
                await announce(
                        [self.players[self.turn],
                                self.players[self.wd4_player_index]],
                        "**"
                        + self.players[self.turn].get_user().name
                        + "** has challenged **"
                        + self.players[self.wd4_player_index].get_user().name
                        + "**'s Wild Draw Four.")
                await message_player(self.players[self.wd4_player_index],
                        "Your Wild Draw Four card has been challenged by **"
                        + self.players[self.turn].get_user().name
                        + "**. They will be shown your hand to prove whether "
                        + "your play was legal or not.")
                await message_player(self.players[self.turn],
                        "**"
                        + self.players[self.wd4_player_index].get_user().name
                        + "**'s hand is:"
                        + self.players[self.wd4_player_index].get_hand())
                # If challenge is not successful
                if self.is_legal_wd4:
                    await announce([], "The Wild Draw Four was legal.")
                    await announce([self.players[self.turn]],
                            "**"
                            + self.players[self.turn].get_user().name
                            + "** draws six cards.")
                    pm_str = ("You have drawn the following six cards:```\n")
                    for i in range(6):
                        if not self.__give_topdeck_to_player__(
                                self.players[self.turn]):
                            break
                        pm_str += str(self.players[self.turn].get_cards()[-1])
                        pm_str += "\n"
                    pm_str += "```"
                    await message_player(self.players[self.turn], pm_str)
                    self.players[self.turn].sort_cards()
                # If challenge is successful
                else:
                    await announce([], "The Wild Draw Four was illegal.")
                    await announce([self.players[self.wd4_player_index]],
                            "**"
                            + self.players[
                                self.wd4_player_index].get_user().name
                            + "** draws four cards.")
                    pm_str = ("You have drawn the following four cards:```\n")
                    for i in range(4):
                        if not self.__give_topdeck_to_player__(
                                self.players[self.wd4_player_index]):
                            break
                        pm_str += str(self.players[
                            self.wd4_player_index].get_cards()[-1])
                        pm_str += "\n"
                    pm_str += "```"
                    await message_player(
                            self.players[self.wd4_player_index],
                            pm_str)
                    self.players[self.wd4_player_index].sort_cards()
                    self.winner_index = -1
            # If not challenged
            else:
                await announce([self.players[self.turn]],
                        "**"
                        + self.players[self.turn].get_user().name
                        + "** draws four cards.")
                pm_str = ("You have drawn the following four cards:```\n")
                for i in range(4):
                    if not self.__give_topdeck_to_player__(
                            self.players[self.turn]):
                        break
                    pm_str += str(self.players[self.turn].get_cards()[-1])
                    pm_str += "\n"
                pm_str += "```"
                await message_player(self.players[self.turn], pm_str)
                self.players[self.turn].sort_cards()
            await announce([self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "** is skipped.")
            await message_player(
                    self.players[self.turn],
                    "Your turn is skipped.")
            self.__next_turn__()
            self.is_legal_wd4 = False
            self.wd4_player_index = -1
            self.is_checking_challenge = False
            if self.winner_index != -1:
                return False
            await self.announce_turn()
        # The current player chose to draw
        elif self.is_drawing:
            if command not in [".k", ".keep", ".p", ".play"]:
                await message_player(self.players[self.turn], "Invalid input.")
                return True
            new_card = self.players[self.turn].get_cards()[-1]
            # Only play the card if the card can be played
            if command in [".p", ".play"]:
                if self.__can_be_played__(new_card):
                    self.is_drawing = False
                    await self.__play_card__(-1)
                    if (not self.is_playing_wild
                            and not self.is_playing_wd4):
                        if self.winner_index != -1:
                            return False
                        await self.announce_turn()
                    return True
                await message_player(
                        self.players[self.turn],
                        "This card cannot be played. You have no choice "
                        + "but to keep this card.")
            # Keep the card
            await announce(
                    [self.players[self.turn]],
                    "**"
                    + self.players[self.turn].get_user().name
                    + "** is keeping the drawn card.")
            self.players[self.turn].sort_cards()
            self.__next_turn__()
            await self.announce_turn()
            self.is_drawing = False
        # Normal state
        else:
            if ((not content.strip())
                    or (command not in [".p", ".play", ".d", ".draw"])):
                await message_player(self.players[self.turn], "Invalid input.")
                return True
            # Choosing a card to play
            elif command in [".p", ".play"]:
                if len(content.split()) < 2:
                    await message_player(
                            self.players[self.turn],
                            "Invalid input.")
                    return True
                try:
                    index = int(eval(content.split()[1])) - 1
                except:
                    await message_player(
                            self.players[self.turn],
                            "Invalid input.")
                    return True
                if (index < 0 
                        or index >= len(self.players[self.turn].get_cards())):
                    await message_player(
                            self.players[self.turn], 
                           "Index out of range.")
                    return True
                player_card = self.players[self.turn].get_cards()[index]
                if self.__can_be_played__(player_card):
                    await self.__play_card__(index)
                    if (not self.is_playing_wild and not self.is_playing_wd4):
                        if self.winner_index != -1:
                            return False
                        await self.announce_turn()
                else:
                    await message_player(
                            self.players[self.turn],
                            "This card cannot be played.")
            # Case of drawing a card
            else:
                if not self.__give_topdeck_to_player__(
                        self.players[self.turn]):
                    await announce(
                            [self.players[self.turn]],
                            "**"
                            + self.players[self.turn].get_user().name
                            + "** has tried to draw a card, but the deck has "
                            + "run out of cards.")
                    await message_player(
                            self.players[self.turn],
                            "You tried to draw a card, but the deck has run out"
                            " of cards.")
                    self.__next_turn__()
                    await self.announce_turn()
                    return True
                new_card = self.players[self.turn].get_cards()[-1]
                await announce(
                        [self.players[self.turn]],
                        "**"
                        + self.players[self.turn].get_user().name
                        + "** has drawn a card. Waiting for their next "
                        + "action...")
                await message_player(
                        self.players[self.turn],
                        "You have drawn `"
                        + str(new_card)
                        + "`. Type `.k(eep)` or `.p(lay)`.")
                self.is_drawing = True
        return True

    async def announce_turn(self):
        """Announces whose turn it is currently"""
        announce_str = (
                "It is now **"
                + self.players[self.turn].get_user().name
                + "**'s turn, with last discarded card being `"
                + str(self.discard[-1])
                + "`.")
        if self.wild_color != CardColor["BLACK"]:
            announce_str += (
                    " The color for Wild card is **"
                    + self.wild_color.name
                    + "**.")
        await announce([self.players[self.turn]], announce_str)
        pm_str = (
                "It is now ***your*** turn. You have the following cards:"
                + self.players[self.turn].get_hand()
                + "\nThe last discarded card is `"
                + str(self.discard[-1])
                + "`.\n Choose a card to play (`.p <card index>`) or draw a "
                + "card (`.d`).")
        if self.wild_color != CardColor["BLACK"]:
            pm_str += (
                    " The color for Wild card is **"
                    + self.wild_color.name
                    + "**.")
        await message_player(self.players[self.turn], pm_str)

    async def request_hand(self, user):
        """
        Shows the players their own hand upon request

        Argument:
        user(discord.User): The user who requested their hand
        """
        index = -1
        for i in range(len(self.players)):
            if self.players[i].get_user() == user:
                index = i
                break
        # If the requesting user is not playing this game
        if index == -1:
            return
        await message_player(
                self.players[index],
                "Your cards are:" + self.players[index].get_hand())

    async def request_turn(self, user):
        """
        Shows whose turn it currently is

        Argument:
        user(discord.User): The user who requested the turn
        """
        content = "```\n"
        if self.clockwise:
            content += "Left to right\n"
        else:
            content += "Right to left\n"
        for i in range(len(self.players)):
            if i == self.turn:
                content += "**" + self.players[i].get_user().name + "**"
            else:
                content += self.players[i].get_user().name
            content += "(" + str(len(self.players[i].get_cards())) + " cards) "
        content += "```"
        await client.send_message(user, content)

    async def request_last_discard(self, user):
        """
        Shows the last discarded card

        Argument:
        user(discord.User): The user who requested the last discard
        """
        pm_str = ("The last discarded card is `"
                + str(self.discard[-1])
                + "`.")
        if self.wild_color != CardColor["BLACK"]:
            pm_str += (" The color for Wild card is **"
                    + self.wild_color.name
                    + "**.")
        await client.send_message(user, pm_str)

    def game_end(self):
        """
        Add the score to the winner

        Return:
        int: Index of the player who wins the game
        """
        score = 0
        winner = self.players[self.winner_index]
        for player in self.players:
            if player == winner:
                continue
            for card in player.get_cards():
                if card.get_type() == CardType["ONE"]:
                    score += 1
                elif card.get_type() == CardType["TWO"]:
                    score += 2
                elif card.get_type() == CardType["THREE"]:
                    score += 3
                elif card.get_type() == CardType["FOUR"]:
                    score += 4
                elif card.get_type() == CardType["FIVE"]:
                    score += 5
                elif card.get_type() == CardType["SIX"]:
                    score += 6
                elif card.get_type() == CardType["SEVEN"]:
                    score += 7
                elif card.get_type() == CardType["EIGHT"]:
                    score += 8
                elif card.get_type() == CardType["NINE"]:
                    score += 9
                elif card.get_type() in [CardType["SKIP"],
                        CardType["DRAW_TWO"],
                        CardType["REVERSE"]]:
                    score += 20
                elif card.get_type() in [CardType["WILD"],
                        CardType["WILD_DRAW_FOUR"]]:
                    score += 50
        self.players[self.winner_index].add_score(score)
        return self.winner_index


async def announce(except_players, content):
    """
    Sends a message to the channel and players except for specified players

    Arguments:
    except_players(list of Player): Players to not send messages to
    content       (str)           : The content of the message
    """
    global players, client, channel
    for player in players:
        if player in except_players:
            continue
        await client.send_message(player.user, content)
    await client.send_message(channel, content)


async def message_player(player, content):
    """
    Sends a PM to the specified player

    Arguments:
    player (Player): Player to send PM to
    content(str)   : Content of the message
    """
    await client.send_message(player.user, content)


async def start(input_players, input_client, input_channel):
    """
    Initializes the UNO game

    Arguments:
    input_players(list of discord.User): Users who are joining the game
    input_client (discord.Client)      : Bot client
    input_channel(discord.Channel)     : The main channel to announce the
                                         current game at
    """
    global client, players, channel, game
    print(str(channel))
    client = input_client
    players = []
    for input_player in input_players:
        players.append(Player(input_player))
    channel = input_channel
    await announce([], "The game is starting up...")
    await announce([input_players],
            "The game is played by entering commands to the bot"
            + " by PM. Please check the PM with the bot for instructions. "
            + "Enter `.unohelp` for further help.")
    game = Game(players)
    if not await game.announce_if_first_discard_wild():
        await game.announce_turn()
    

async def send_help(user):
    """
    Sends help regarding the general in-game commands

    Argument:
    user(discord.User): User requesting for help
    """
    global client
    await client.send_message(
            user,
            "```\n.p <card index> - During your turn, plays a card with the "
            + "given index.\n"
            + ".d - During your turn, draws a card for you.\n"
            + ".hand - Shows what cards you currently have.\n"
            + ".turn - Shows whose turn it currently is and how many cards they"
            + " have.\n"
            + ".last - Shows which card was discarded last.\n"
            + ".send <message> - Sends <message> to everybody and the "
            + "channel.\n"
            + ".ustop - Stops the current game.\n"
            + ".unohelp - You probably already know this.```")
            


async def process_message(message):
    """
    Processes a message sent by PM to the bot client

    Argument:
    message(discord.Message): The message to process
    """
    global players, game
    index = -1
    for i in range(len(players)):
        if message.author == players[i].get_user():
            index = i
            break
    command = message.content.split()[0]
    if command == ".ustop":
        if index != -1:
            await announce(
                    [players[index]],
                    "**"
                    + players[index].get_user().name
                    + "** has stopped the game.")
            await message_player(players[index], "The game has stopped.")
            return False
    elif command == ".hand":
        if index != -1:
            await game.request_hand(message.author)
    elif command == ".turn":
        await game.request_turn(message.author)
    elif command == ".last":
        await game.request_last_discard(message.author)
    elif command in [".send", ".s"]:
        if index != -1:
            split_str = ""
            if command == ".send":
                split_str = message.content[5:].strip()
            else:
                split_str = message.content[2:].strip()
            await announce(
                    [players[index]],
                    "**["
                    + players[index].get_user().name
                    + "]** "
                    + split_str)
    elif command == ".unohelp":
        await send_help(message.author)
    elif index != -1:
        if not await game.run(message):
            winner_index = game.game_end()
            await announce(
                    [],
                    "The game is over. **"
                    + players[winner_index].get_user().name
                    + "** wins with "
                    + str(players[winner_index].get_score())
                    + " points!")
            return False
    return True
