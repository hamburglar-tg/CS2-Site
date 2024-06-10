import random
import re

from decimal import Decimal, ROUND_HALF_UP


def calculate_percentage(game_bank, user_bank):
    if game_bank <= 0:
        return 100
    percentage = Decimal(min(user_bank, game_bank) / game_bank) * 100
    percentage = int(percentage.quantize(Decimal('1.'), rounding=ROUND_HALF_UP))

    return percentage


def generate_online():
    current_value = random.randint(75, 80)
    action = random.choice(['enter', 'leave'])
    if action == 'enter' and current_value < 80:
        current_value += 1
    elif action == 'leave' and current_value > 75:
        current_value -= 1
    return current_value

def round_decimal(number, dec_str):
    return float(Decimal(str(number)).quantize(Decimal(dec_str), rounding=ROUND_HALF_UP))

def extract_cost(item_cost_str):
    cleaned_price = float(re.sub('[^0-9,]', '', item_cost_str).replace(",", "."))
    final_price = round_decimal(cleaned_price, '0.01') if cleaned_price else 0.0
    return final_price

def extract_total(data, key):
    total_cost = 0
    if isinstance(data, dict):
        if key in data:
            value = data[key]
            if isinstance(value, str):
                total_cost += float(value.split()[0].replace(',', '.'))
            elif isinstance(value, (int, float)):
                total_cost += value
        for v in data.values():
            total_cost += extract_total(v, key)
    return round_decimal(total_cost, '0.01')
