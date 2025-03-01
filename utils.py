"""
Utility functions for the trading simulation.
"""

import random
from bot import Bot

bot_counter = 0

def generate_random_product_names(n=10):
    """Generate a list of n unique random product names."""
    adjectives = ["Cool", "Amazing", "Fantastic", "Ultra", "Super", "Mega", "Hyper", "Smart", "Eco", "Prime"]
    nouns = ["Widget", "Gadget", "Device", "Item", "Tool", "Gear", "Product", "Instrument", "Module", "System"]
    products = {f"{random.choice(adjectives)} {random.choice(nouns)}" for _ in range(n)}
    return list(products)

def create_random_bot(engine, product_list):
    """Create and return a random Bot instance."""
    global bot_counter
    bot_counter += 1
    bot_id = f"Bot{bot_counter}"
    commodity = random.choice(product_list)
    is_seller = random.choice([True, False])
    quantity = random.randint(1, 20)
    target_price = round(engine.get_market_value(commodity), 2)
    objective = {'quantity': quantity, 'price': target_price}
    threshold = random.uniform(0.01, 0.10) if is_seller else random.uniform(0.01, 0.20)
    return Bot(bot_id, engine, commodity, objective, is_seller, 5, threshold)
