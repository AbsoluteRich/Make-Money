# ================================= SETUP =================================
import json
from os.path import exists, getsize
from random import randint as random
from sys import exit
from datetime import datetime


# Big class
class Item:
    def __init__(self, itemname, description, price, nature=None, stock=0):
        self.itemname = itemname
        self.description = description
        self.price = price
        self.nature = True if nature is not None else False
        self.stock = stock

    def buy(self, quantity=1):
        global coins

        if self.nature is True:
            if self.stock < 1:
                if self.price > coins:
                    print(f"You don't have enough money, the item costs ${self.price} and you only have ${coins}")
                else:
                    coins -= self.price
                    self.stock += 1
            else:
                print("You've already bought this ability")
        else:
            if (self.price * quantity) > coins:
                print(
                    f"You don't have enough money, the item costs ${self.price * quantity} and you only have ${coins}")
            else:
                coins -= self.price * quantity
                self.stock += quantity

    def check(self):
        if self.stock > 0:
            return True
        else:
            return False

    def display(self):
        print(f"{self.itemname}\n{self.description}")
        if self.nature is True:
            if self.stock >= 1:
                print("Unlocked")
            else:
                print(f"Locked for ${self.price}")
        else:
            print(f"Costs ${self.price} for one, you have {self.stock}")
        print("")


# Default values, should be overwritten
coins = 50
debt = 0
devmode = None
runs = 0

# Other variables, most of these should also be overwritten
rng = 0
earning = 0
debt_penalty = None

# Passive income
AutoTyper = Item("Money Printer",
                 "A small compositor to help you collect money. Earns $50 every time the screen refreshes.",
                 50)

# Abilities
BackroomDeals = Item("Backroom Deals",
                     "Contact some shady authorities to reduce your debt penalty.",
                     1000, "Ability")

WeightedChip = Item("Weighted Chip",
                    "Do you feel lucky? Chance to activate multipliers that increase or negate your gambling income.",
                    1000, "Ability")


# ================================= FUNCTIONS =================================
# (they need to be defined after the shop items are)
def earn(income, suppress=False, isloan=False):
    global coins, debt, debt_penalty, earning

    # BACKROOM DEALS LOGIC
    if BackroomDeals.check() is True:
        debt_penalty = 0.25
    else:
        debt_penalty = 0.5

    if debt != 0:
        earning = round(income * debt_penalty)
        coins += earning
        debt -= earning

        if not suppress:
            print(f"You earned ${earning}")
            if BackroomDeals.check() is True:
                print("losing only a quarter of it to debt")
            else:
                print("losing half of it to debt")
    else:
        coins += income
        if not suppress:
            print(f"You earned ${income}")

    if isloan is True:
        debt += income


def create_checksum(numbers):
    if (numbers / 2).is_integer() is True:
        return [len(str(numbers)), "/", int(numbers / 2)]
    else:
        decimal = str(numbers / 2).split(".")[1]
        return [len(str(numbers)), "%", int(decimal)]


def create_sum():
    global sum_of_numbers, line
    sum_of_numbers = 0  # Sum thing
    for line in save_file:
        try:
            if save_file[line] is not True and save_file[line] is not False:
                sum_of_numbers += save_file[line]
        except TypeError:
            continue


def update_save():
    # Anti-sets the variables (this is a dumb solution)
    save_file["coins"] = coins
    save_file["debt"] = debt
    save_file["autoTyper"] = AutoTyper.stock
    save_file["backroomDeals"] = BackroomDeals.stock
    save_file["weightedChip"] = WeightedChip.stock
    save_file["runs"] = runs

    # This needs to go last, no matter what
    create_sum()
    save_file["checksum"] = create_checksum(sum_of_numbers)

    # Writes to file
    if save_file.get("DO_NOT_ENABLE_SAVE_REWRITE") is True:
        print("File not written to.")
    else:
        global f  # Fuck this in particular
        with open("save.json", "w") as f:
            f.write(json.dumps(save_file, indent=4))


def log(message):
    if not exists("logs.txt"):
        with open("logs.txt", "x"):
            pass

    global f
    with open("logs.txt", "a") as f:
        print(f"[{datetime.now()}] {message}", file=f)


def force_exit(error, prompt=True):
    if prompt is True:
        input(f"{error} ")
    log(error)
    update_save()
    exit(error)


# ================================= FILE SHIT =================================
# Creates file
if not (exists("save.json")) or getsize("save.json") == 0:
    with open("save.json", "w") as f:
        # The dictionary
        default = {
            "checksum": [],
            "runs": runs,
            "coins": coins,
            "debt": debt,
            "autoTyper": AutoTyper.stock,
            "backroomDeals": BackroomDeals.stock,
            "weightedChip": WeightedChip.stock
        }

        # Creates checksum
        sum_of_numbers = 0
        for line in default:  # Sum thing
            try:
                if default[line] is not True and default[line] is not False:
                    sum_of_numbers += default[line]
            except TypeError:
                continue
        default["checksum"] = create_checksum(sum_of_numbers)

        # Writes to file
        f.write(json.dumps(default, indent=4))

# Reads save_file
with open("save.json", "r") as f:
    save_file = json.loads(f.read())

# Sets the variables
coins = save_file["coins"]
debt = save_file["debt"]
devmode = True if save_file.get("DO_NOT_ENABLE_DEV_MODE") is True else False
runs = save_file["runs"]

AutoTyper.stock = save_file["autoTyper"]
BackroomDeals.stock = save_file["backroomDeals"]
WeightedChip.stock = save_file["weightedChip"]

# Checks the checksum
if save_file.get("DO_NOT_ENABLE_IGNORE_CHECKSUM") is True:
    print("Checksum ignored.")
else:
    create_sum()

    # Checks for length
    if save_file["checksum"][0] == len(str(sum_of_numbers)):
        if devmode:
            print("Check 1: Length complete")
    else:
        force_exit(f"Invalid length, "
                   f"got '{save_file['checksum'][0]}'")

    # Checks for valid symbol
    if save_file["checksum"][1] == "/" or save_file["checksum"][1] == "%":
        if devmode:
            print("Check 2: Symbol complete")
    else:
        force_exit(f"Invalid symbol, "
                   f"got '{save_file['checksum'][1]}'")

    # Finally, checks if the maths works out
    if save_file["checksum"][1] == "/":
        if sum_of_numbers / 2 == save_file["checksum"][2]:
            if devmode:
                print("Check 3: Division complete")
        else:
            force_exit(f"Invalid division, "
                       f"got '{save_file['checksum'][2]}'")

    elif save_file["checksum"][1] == "%":
        if str(sum_of_numbers / 2).split('.')[1] == str(save_file["checksum"][2]):
            if devmode:
                print("Check 3: Decimal complete")
        else:
            force_exit(f"Invalid decimal, "
                       f"got '{save_file['checksum'][2]}'")

    else:
        force_exit(f"Invalid symbol further into execution, got '{save_file['checksum'][1]}'")

if save_file.get("DO_NOT_ENABLE_CLOSE_SUPPRESSION") is True:
    print("Close protection disabled.")
else:
    try:
        # https://stackoverflow.com/questions/29269436/disable-close-button-of-console-window
        import win32console
        import win32gui
        import win32con

        hwnd = win32console.GetConsoleWindow()
        if hwnd:
            hMenu = win32gui.GetSystemMenu(hwnd, 0)
            if hMenu:
                win32gui.DeleteMenu(hMenu, win32con.SC_CLOSE, win32con.MF_BYCOMMAND)
    except Exception as err:
        print("An error has occurred while trying to initialise close protection. See logs for more info.")
        log(err)
# ================================= MAIN PROGRAM =================================
runs += 1

if devmode:
    print("")

if runs < 2:
    print("Thank you for downloading my deadly virus!")
    print("To close the program, earn $5000 and type win")
    print("")

print("Make Money [Version 1.0.0]")
print("(c) AbsoluteRich. All rights reserved.")
print("Type 'help' for a list of commands.")

while True:
    try:
        update_save()
        # AUTO TYPER LOGIC
        if AutoTyper.check() is True:
            earn(25 * AutoTyper.stock, suppress=True)
            print(f"You earned ${25 * AutoTyper.stock} with your Auto Typer")

        if debt < 0:
            earn(abs(debt), suppress=True)
            print(f"Overflow debt has been converted to ${abs(debt)}")
            debt = 0

        """
        if float(coins).is_integer() is True:
            coins = int(coins)
        if float(debt).is_integer() is True:
            debt = int(debt)
        """

        print(f"You have ${coins}")
        if debt > 0:
            print(f"You owe ${debt} in debt")

        choice = input(">>").casefold().strip()

        match choice:
            case "gamble":
                if coins - 100 >= 0:
                    coins -= 100

                    # WEIGHTED CHIP LOGIC
                    if WeightedChip.check() is True:
                        temp = random(1, 3)

                        if temp == 1:
                            rng = random(1, 5)
                            if rng <= 2:  # 1 and 2
                                print("Unlucky! x0.5 earnings")
                                earn(250)
                            elif rng == 3:  # 3
                                print("Even chance! No change to earnings")
                                earn(500)
                            elif rng > 3:  # 4 and 5
                                print("Lucky! x2 earnings")
                                earn(1000)
                        else:
                            print("Haha you lost")

                    else:
                        if random(1, 3) == 1:
                            print("Wow!")
                            earn(500)
                        else:
                            print("Haha you lost")
                else:
                    print(f"Gamble costs 100 coins and you have ${coins}")

            case "loan":
                if debt <= 0:
                    earn(1000, suppress=False, isloan=True)
                else:
                    print("Pay off your debts to borrow more money")

            case "work":
                earn(random(50, 100))

            case "shop" | "inventory" | "inv":
                AutoTyper.display()
                BackroomDeals.display()
                WeightedChip.display()

                choice = input("Would you like to buy? ").casefold().strip()
                if choice in ["true", "1", "t", "y", "yes", "yeah", "yup", "certainly", "uh-huh"]:
                    choice = input("What would you like to buy? (1/2/3) ").casefold().strip()
                    match choice:
                        case "1":
                            print(f"You have ${coins}")
                            choice2 = input("How much? Leave blank to cancel. ")

                            try:
                                choice2 = int(choice2)
                            except ValueError:
                                print("Invalid type.")

                            AutoTyper.buy(choice2)

                        case "2":
                            BackroomDeals.buy()
                        case "3":
                            WeightedChip.buy()
                        case _:
                            print("Invalid number.")

            case "debug":
                if devmode is True:
                    choice = input("(list/coins/runs/file) >>").casefold().strip()
                    match choice:
                        case "list":
                            # https://www.geeksforgeeks.org/viewing-all-defined-variables-in-python/
                            all_variables = dir()

                            for name in all_variables:
                                if not name.startswith('__'):
                                    print(f"{name}: {eval(name)} ({type(name)})")

                        case "coins":
                            choice = int(input(""))
                            coins += choice

                        case "runs":
                            print(f"Current value: {runs}\nSave file: {save_file['runs']}")
                            choice = int(input("Editing current value: "))
                            runs = choice

                        case "file":
                            for line in save_file:
                                print(f"{line}: {save_file[line]}")
                else:
                    force_exit("Not a chance")

            case "win":
                if coins >= 5000:
                    print("You have $5000!")
                    choice = input("Win? ").casefold().strip()

                    if choice in ["true", "1", "t", "y", "yes", "yeah", "yup", "certainly", "uh-huh"]:

                        if exists("You win!.png"):
                            filename = "You win! - Exported.png"
                            print("Greedy ass you already have a certificate")
                            print("Guess you'll get another one")

                            coins -= 5000
                            update_save()

                            print("Importing modules...")
                            from urllib.request import urlretrieve as download

                            print("Downloading your prize...")
                            download("https://raw.githubusercontent.com/AbsoluteRich/Make-Money/"
                            "main/src/Certificate%20of%20-%20Exported.PNG", f"{filename}")

                            print(f"Done. Check the program directory for '{filename}'.")
                            input("Press Enter and the program will spontaneously combust. ")
                            force_exit("You won (again)", prompt=False)

                        elif exists("You win! - Exported.png"):
                            force_exit("")

                        else:
                            filename = "You win!.png"
                            coins -= 5000
                            update_save()

                            print("Importing modules...")
                            from urllib.request import urlretrieve as download

                            print("Downloading your prize...")
                            download("https://raw.githubusercontent.com/AbsoluteRich/Make-Money/"
                            "main/src/Certificate%20of.PNG", f"{filename}")

                            print(f"Done. Check the program directory for '{filename}'.")
                            input("Press Enter and the program will spontaneously combust. ")
                            force_exit("You won, what else is there to read in the logs", prompt=False)
                else:
                    print("You need $5000 to win!")

            case "help":
                commands = {
                    "gamble": "High risk, high reward",
                    "loan": "Gain an instant burst of money, but you need to pay it off over time",
                    "work": "Make money",
                    "shop": "Buy wares",
                    "debug": "Don't even try",
                    "win": "Only one way to find out",
                    "help": "This message",
                    "inventory/inv": "Equivalent to shop",
                }

                print("All commands:")
                for line in sorted(commands):
                    print(f"    • {line}: {commands[line]}")
                print("Commands are not case sensitive.")

            case _:
                print("Invalid input, type 'help' for a list of commands")

        print("")

    except Exception as err:
        print("An error has occurred. See logs for more info.")
        log(f"{type(err).__name__}: {err}")
