import random
from ai import call_gpt

class MathGridGame:
    def __init__(self, width=30, height=6, teleports=10):
        self.width = width
        self.height = height
        self.kerel = (0, height - 1)
        self.energy = 10
        self.gold = 0
        self.score = 0
        self.inventory = []
        self.potions = set()
        self.shields = set()
        self.traps = set()
        self.shield_active = False
        self.teleports_left = teleports
        self.golds = set()
        self.stations = set()
        self.enemies = []
        self.init_board()18 miles

    def init_board(self):
        while len(self.golds) < 10:
            pos = (random.randint(1, self.width - 2), random.randint(1, self.height - 2))
            if pos != self.kerel:
                self.golds.add(pos)
        while len(self.stations) < 6:
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if pos not in self.golds and pos != self.kerel:
                self.stations.add(pos)
        while len(self.potions) < 2:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if pos not in self.golds and pos not in self.stations and pos != self.kerel:
                self.potions.add(pos)
        while len(self.shields) < 1:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if pos not in self.golds and pos not in self.stations and pos not in self.potions and pos != self.kerel:
                self.shields.add(pos)
        while len(self.traps) < 2:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if pos not in self.golds and pos not in self.stations and pos not in self.potions and pos not in self.shields and pos != self.kerel:
                self.traps.add(pos)
        self.enemies = self.generate_enemies(self.kerel, self.width, self.height)

    def generate_enemies(self, kerel, width, height, num_enemies=8):
        positions = set()
        while len(positions) < num_enemies:
            pos = (random.randint(0, width-1), random.randint(0, height-1))
            if pos != kerel:
                positions.add(pos)
        enemies = []
        for pos in positions:
            enemies.append({"pos": pos})
        return enemies

    def move_enemies(self):
        directions = [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]
        new_positions = set()
        for enemy in self.enemies:
            possible_moves = []
            for dx, dy in directions:
                nx, ny = enemy['pos'][0] + dx, enemy['pos'][1] + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) != self.kerel and (nx, ny) not in new_positions:
                    possible_moves.append((nx, ny))
            if possible_moves:
                enemy['pos'] = random.choice(possible_moves)
            new_positions.add(enemy['pos'])

    def draw_grid(self):
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                pos = (x, y)
                if pos == self.kerel:
                    row += "K "
                elif pos in [e['pos'] for e in self.enemies]:
                    row += "E "
                elif pos in self.golds:
                    row += "$ "
                elif pos in self.stations:
                    row += "S "
                elif pos in self.potions:
                    row += "P "
                elif pos in self.shields:
                    row += "H "
                elif pos in self.traps:
                    row += "T "
                else:
                    row += ". "
            print(row)
        print()

    def print_legend(self):
        print("Legend: K=Kerel, E=Enemy, $=Gold, S=Station, .=Empty, P=Potion, H=Shield, T=Trap")

    def print_help(self):
        print("Controls: U=up, D=down, L=left, R=right, T=teleport")
        print("Goal: Collect all gold by solving math, avoid enemies, and manage energy!")
        print("Trade gold for energy at stations. Type T to teleport to a random empty cell (max 10 times).")

    def is_game_over(self):
        if self.energy <= 0:
            print("❌ Kerel ran out of energy. Game over!")
            return True
        if self.kerel in [e['pos'] for e in self.enemies] and not self.shield_active:
            print("\U0001f480 You were caught by an enemy!")
            return True
        if not self.golds:
            print("\U0001f3c6 You collected all the gold! Victory!")
            return True
        return False

    def handle_move(self, move):
        dx, dy = 0, 0
        if move == 'U':
            dy = -1
        elif move == 'D':
            dy = 1
        elif move == 'L':
            dx = -1
        elif move == 'R':
            dx = 1
        else:
            print("Invalid input! Use U/D/L/R/T for movement.")
            return False
        new_pos = (self.kerel[0] + dx, self.kerel[1] + dy)
        if 0 <= new_pos[0] < self.width and 0 <= new_pos[1] < self.height:
            self.kerel = new_pos
            self.energy -= 1
            self.score += 1
            print(f"You moved to {self.kerel}.")
            return True
        else:
            print("❌ Wall hit!")
            return False

    def handle_teleport(self):
        if self.teleports_left > 0:
            occupied = [self.kerel] + [e['pos'] for e in self.enemies] + list(self.golds) + list(self.stations) + list(self.potions) + list(self.shields) + list(self.traps)
            empty_cells = [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in occupied]
            if empty_cells:
                self.kerel = random.choice(empty_cells)
                self.teleports_left -= 1
                print(f"You teleported to {self.kerel}!")
            else:
                print("No empty cells to teleport to!")
        else:
            print("No teleports left!")

    def handle_cell(self):
        if self.kerel in [e['pos'] for e in self.enemies]:
            if self.shield_active:
                print("\U0001f6e1\ufe0f Your shield protected you from the enemy!")
                self.shield_active = False
            else:
                print("\U0001f480 You were caught by an enemy!")
                self.energy = 0  # End game
        if self.kerel in self.golds:
            print("\u2728 You found a gold coin! Solve a math problem to collect it:")
            question, answer = generate_gpt_question()
            user_input = input(f"{question} = ")
            try:
                if int(user_input.strip()) == answer:
                    print("\u2705 Correct! You collected the coin.")
                    self.gold += 1
                    self.golds.remove(self.kerel)
                    self.score += 10
                else:
                    print(f"\u274c Wrong answer. The correct answer was {answer}. No gold for you.")
            except:
                print(f"\u274c Invalid input. The correct answer was {answer}. Missed the chance.")
        if self.kerel in self.stations:
            if self.gold > 0:
                choice = input("\u26a1 Trade 1 gold for 5 energy? (Y/N): ").strip().upper()
                if choice == 'Y':
                    self.gold -= 1
                    self.energy += 5
                    print("\U0001f50b Energy recharged!")
        if self.kerel in self.potions:
            print("\U0001f9ea You found a potion! Restores 5 energy when used.")
            self.inventory.append("Potion")
            self.potions.remove(self.kerel)
        if self.kerel in self.shields:
            print("\U0001f6e1\ufe0f You found a shield! Protects from one enemy hit.")
            self.inventory.append("Shield")
            self.shields.remove(self.kerel)
        if self.kerel in self.traps:
            print("\U0001f4a5 You stepped on a trap! Lose 3 energy.")
            self.energy -= 3
            self.score -= 5
            self.traps.remove(self.kerel)

def generate_gpt_question():
    topics = [
        "Arithmetic", "Algebra", "Geometry", "Modern Math",
        "Number System", "Time", "Distance", "Speed"
    ]
    topic = random.choice(topics)
    prompt = (
        f"Generate a unique, short, creative, and non-repetitive math word problem from the topic: {topic}. "
        f"The question must require a numerical answer. Vary the structure and content from previous outputs. "
        f"Make sure it is not too long to read. "
        f"Format exactly like this:\nQuestion: <your question>\nAnswer: <numerical answer>\n"
    )
    response = call_gpt(prompt)
    question = ""
    answer = None
    if isinstance(response, str):
        lines = response.strip().splitlines()
        for line in lines:
            if line.startswith("Question:"):
                question = line[len("Question:"):].strip()
            elif line.startswith("Answer:"):
                answer_str = line[len("Answer:"):].strip()
                try:
                    answer = int(answer_str)
                except ValueError:
                    try:
                        answer = float(answer_str)
                    except ValueError:
                        answer = answer_str
    elif isinstance(response, dict):
        question = response.get("question", "")
        answer = response.get("answer", None)
    return question, answer

def main():
    print("""
    =====================================================
    🏰 WELCOME TO KEREL'S MATH GRID ADVENTURE! 🏰
    -----------------------------------------------------
    You are Kerel (K), an explorer in a dangerous world.
    Your goal: Collect all the gold ($) by solving math problems!
    Avoid enemies (E), use stations (S) to recharge, and find potions (P), shields (H), and beware of traps (T).
    Every move costs energy. If you run out, it's game over!
    You have a special power: you can TELEPORT up to 10 times to a random empty cell! Use 'T' to teleport.
    Good luck!
    =====================================================
    """)
    game = MathGridGame()
    game.print_legend()
    print("Type 'H' for help at any time.\n")
    while True:
        print(f"🪫 Energy: {game.energy} | 💰 Gold: {game.gold} | Gold left: {len(game.golds)} | Stations left: {len(game.stations)} | 🌀 Teleports left: {game.teleports_left}")
        game.draw_grid()
        if game.is_game_over():
            break
        move = input("Move (U=up, D=down, L=left, R=right, T=Teleport, or H for help): ").strip().upper()
        if move == 'H':
            game.print_help()
            continue
        elif move == 'T':
            game.handle_teleport()
        else:
            moved = game.handle_move(move)
            if not moved:
                continue
        game.handle_cell()
        game.move_enemies()
        print("-" * 35)
    print(f"🏆 Final Score: {game.score}")

if __name__ == '__main__':
    while True:
        main()
        again = input("Play again? (Y/N): ").strip().upper()
        if again != 'Y':
            print("Thanks for playing!")
            break
