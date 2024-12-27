import schedule
import time
import json
import random
from datetime import datetime

def auto_shop():
    try:
        with open('Logic/offers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i in range(12):
            if i <= 5:
                new_offer = {
                    'ID': [8, 0, 0],
                    'OfferTitle': "daily",
                    'Cost': random.randint(10, 228),
                    'OldCost': 0,
                    'Multiplier': [random.randint(1, 100), 0, 0],
                    'BrawlerID': [random.randint(1, 32), 0, 0],
                    'SkinID': [0, 0, 0],
                    'WhoBuyed': [],
                    'Timer': 86400,
                    'OfferBGR': "offer_gems",
                    'ShopType': 1,
                    'ShopDisplay': 1
                }
                data[i] = new_offer
            else:
                with open('config.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                skins = settings['Skins']
                random_skin = random.choice(skins)
                skins.remove(random_skin)
                settings['Skins'] = skins
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
                new_offer = {
                    'ID': [4, 0, 0],
                    'OfferTitle': "DAILY SKIN",
                    'Cost': random.randint(10, 228),
                    'OldCost': 0,
                    'Multiplier': [0, 0, 0],
                    'BrawlerID': [0, 0, 0],
                    'SkinID': [random_skin, 0, 0],
                    'WhoBuyed': [],
                    'Timer': 86400,
                    'OfferBGR': "offer_gems",
                    'ShopType': 0,
                    'ShopDisplay': 0
                }
                data[i] = new_offer
        with open('Logic/offers.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"{datetime.now()}: Акции успешно обновлены!")
    except Exception as e:
        print(f"Ошибка обновления акций: {e}")

def schedule_auto_shop():
    auto_shop()  # Esegui una volta subito per testare

    # Pianifica l'aggiornamento alle 23:15 ogni giorno
    schedule.every().day.at("23:15").do(auto_shop)
    print("Авто-магазин успешно запланирован на 23:15.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_auto_shop()
