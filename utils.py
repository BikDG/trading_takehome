# utils.py
import random
from bot import Bot

bot_counter = 0

def generate_random_product_names(n=10):
    adjectives = ["Cool", "Amazing", "Fantastic", "Ultra", "Super", "Mega", "Hyper", "Smart", "Eco", "Prime"]
    nouns = ["Widget", "Gadget", "Device", "Item", "Tool", "Gear", "Product", "Instrument", "Module", "System"]
    products = set()
    while len(products) < n:
        product = f"{random.choice(adjectives)} {random.choice(nouns)}"
        products.add(product)
    return list(products)

def create_random_bot(engine, product_list):
    global bot_counter
    bot_counter += 1
    bot_id = f"Bot{bot_counter}"
    commodity = random.choice(product_list)
    is_seller = random.choice([True, False])
    quantity = random.randint(1, 20)
    target_price = round(engine.get_market_value(commodity), 2)
    objective = {'quantity': quantity, 'price': target_price}
    if is_seller:
        threshold = random.uniform(0.01, 0.10)
    else:
        threshold = random.uniform(0.01, 0.20)
    return Bot(bot_id=bot_id, engine=engine, commodity=commodity,
               objective=objective, is_seller=is_seller, time_limit=5, threshold=threshold)
