import random
import time
from ai import call_gpt

NUM_DECKS = 6
CUT_CARD_POSITION = 60  # number of cards before end to reshuffle

# Global card shoe
shoe = []
cut_card_reached = False

# AI memory: keep last 5 rounds
ai_memory = []
ai_logs = []

# Card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def init_shoe():
    """Create and shuffle a new shoe with 6 decks."""
    global shoe, cut_card_reached
    single_deck = list(card_values.keys()) * 4
    shoe = single_deck * NUM_DECKS
    random.shuffle(shoe)
    cut_card_reached = False

def deal_card():
    global shoe
    if len(shoe) <= 1:  # protect against empty or 1-card shoe
        print("\n🔄 Shoe is empty or too small. Reshuffling...\n")
        shoe = create_shuffled_shoe()
    return shoe.pop()


def calculate_score(hand):
    score = 0
    ace_count = 0
    for c in hand:
        score += card_values[c]
        if c == 'A':
            ace_count += 1
    while score > 21 and ace_count:
        score -= 10
        ace_count -= 1
    return score

def check_blackjack(hand):
    return calculate_score(hand) == 21 and len(hand) == 2

def get_ai_decision(hand, score, dealer_card):
    history = "\n".join(ai_memory[-5:]) or "— no memory —"
    prompt = (
        "You are an expert Blackjack AI describing your own thought process.\n\n"
        f"Memory of past rounds:\n{history}\n"
        f"Current round:\n- My hand: {hand} (score = {score})\n"
        f"- Dealer shows: {dealer_card}\n\n"
        "Use first-person 'If I ...' statements. think and compare. make sure it should be more than the player's total but less than 21, for example:\n"
        "1) If I hit and draw a low card (2-6) with my present score , then ...\n"
        "2) If I hit and draw a high card (7-A), then ...\n"
        "3) If I stand now, then ...\n"
        "4) If the dealer’s up-card is strong, then ...\n"
        "Finally, on a new line, write DECISION: HIT or DECISION: STAND.\nDo not include anything else.\n"
    )
    for attempt in range(3):
        response = call_gpt(prompt)
        lines = [ln.strip() for ln in response.strip().split("\n") if ln.strip()]
    
        hypos = [ln for ln in lines if ln.lower().startswith("if i") or (ln and ln[0].isdigit())]
        decision_line = next((ln.upper() for ln in lines if ln.upper().startswith("DECISION:")), "")
    
        if len(hypos) >= 3 and decision_line:
            print("\n--| 🤖 Dealer says:")
            for ln in hypos:
                print("   " + ln)
            print("   " + decision_line)
            ai_memory.append(f"{hand} vs {dealer_card} → {decision_line}")
            return 'hit' if 'HIT' in decision_line else 'stand'
    
            print(f"--| ⚠️ Attempt {attempt + 1}: insufficient hypotheticals or missing decision, retrying...")

# Fallback
        print("--| ⚠️ Failed to parse. Using fallback strategy.")
        return 'hit' if score < 18 else 'stand'


def player_turn():
    hand = [deal_card()]
    score = calculate_score(hand)
    print("\nYour cards:", hand, "Score:", score)
    while score < 21:
        choice = input("Hit (y) or Stand (n)? ").strip().lower()
        if choice == 'y':
            hand.append(deal_card())
            score = calculate_score(hand)
            print("Your cards:", hand, "Score:", score)
        elif choice == 'n':
            break
        else:
            print("Invalid input. Enter 'y' or 'n'.")
    return hand, score

def ai_turn(player_hand, player_score):
    hand = [deal_card(), deal_card()]
    print("\nDealer shows:", hand[0])
    time.sleep(1)

    if check_blackjack(hand):
        return hand, 21

    while True:
        score = calculate_score(hand)
        if score >= 21:
            break
        dec = get_ai_decision(hand, score, hand[0])
        if dec == 'hit':
            card = deal_card()
            hand.append(card)
            print("Dealer draws:", card, "Score:", calculate_score(hand))
            time.sleep(1)
        else:
            break

    return hand, calculate_score(hand)

def get_bet(chips):
    while True:
        try:
            bet = int(input(f"\nYou have {chips} chips. Place your bet: "))
            if 1 <= bet <= chips:
                return bet
            print("Invalid bet. Must be between 1 and your total.")
        except ValueError:
            print("Enter a valid number.")

def play_round(chips):
    global cut_card_reached
    if cut_card_reached:
        print("\n🔄 Reshuffling shoe...")
        init_shoe()

    bet = get_bet(chips)
    ph, ps = player_turn()

    if check_blackjack(ph):
        dh = [deal_card(), deal_card()]
        print("\nDealer shows:", dh[0])
        if check_blackjack(dh):
            print("Both have Blackjack! It's a tie.")
            return 'tie', chips
        else:
            print("Blackjack! You win 1.5x your bet.")
            return 'player', chips + int(bet * 1.5)

    if ps > 21:
        print("You busted! Dealer wins.")
        return 'ai', chips - bet

    print("\n=== Dealer's Turn ===")
    ah, ascore = ai_turn(ph, ps)

    print("\n=== Final Results ===")
    print("You:   ", ph, "→", ps)
    print("Dealer:", ah, "→", ascore)

    if ascore > 21 or ps > ascore:
        print("You win this round! 🎉")
        return 'player', chips + bet
    elif ps < ascore:
        print("Dealer wins this round.")
        return 'ai', chips - bet
    else:
        print("Tie round.")
        return 'tie', chips

def print_summary(wins, chips, rounds):
    print("\n=== Game Summary ===")
    print("Rounds played:", rounds)
    print("Wins: You =", wins['player'], "| Dealer =", wins['ai'], "| Ties =", wins['tie'])
    print("Final chips:", chips)

def init_shoe():
    """Create and shuffle a new shoe with 6 decks, properly mixed to avoid bias."""
    global shoe, cut_card_reached
    single_deck = list(card_values.keys()) * 6
    shoe = []
    for _ in range(NUM_DECKS):
        deck = single_deck.copy()
        random.shuffle(deck)  # Shuffle each deck before combining
        shoe.extend(deck)
    random.shuffle(shoe)  # Shuffle final combined shoe
    cut_card_reached = False

def main():
    print("=== Welcome to Fair COT Blackjack ===")
    wins = {'player': 0, 'ai': 0, 'tie': 0}
    rounds = 0
    chips = 100
    init_shoe()

    while chips > 0:
        res, chips = play_round(chips)
        rounds += 1
        wins[res] += 1
        print(f"Scoreboard — You: {wins['player']} | Dealer: {wins['ai']} | Chips: {chips} (Round {rounds})")
        if input("Play again? (y/n): ").strip().lower() != 'y':
            break

    print("\n=== Game Over ===")
    print_summary(wins, chips, rounds)

if __name__ == '__main__':
    main()    