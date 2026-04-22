import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

NUM_PRODUCTS = 400
NUM_QUERIES = 120
NUM_CLICKS = 5000

CATEGORY_SPECS = {
    'leather': {
        'products': [
            ('Kigali Leather Boots',       'Handcrafted leather boots for men and women. leather boots shoes cowhide footwear'),
            ('Nyamirambo Leather Sandals',  'Traditional sandals made from genuine cowhide. leather sandals open shoes'),
            ('Kigali Leather Handbag',      'Premium leather handbag shoulder bag purse women accessory'),
            ('Huye Leather Belt',           'Genuine leather belt cowhide strap men accessory'),
            ('Musanze Leather Wallet',      'Slim leather wallet card holder purse men women'),
            ('Kigali Leather Shoes',        'Formal leather shoes loafers dress shoes men women'),
            ('Rubavu Leather Jacket',       'Handmade leather jacket coat men women fashion'),
            ('Gicumbi Leather Backpack',    'Leather backpack travel bag school bag unisex'),
        ],
        'material': 'Leather',
        'search_terms': 'leather boots shoes sandals bag handbag belt wallet purse cowhide jacket backpack'
    },
    'basketry': {
        'products': [
            ('Agaseke Peace Basket',        'Traditional agaseke basket woven peace basket Rwanda tressé panier'),
            ('Musanze Sisal Storage Basket','Handwoven sisal basket storage basket home decor woven tressé'),
            ('Gicumbi Woven Tray',          'Decorative woven tray sisal placemat table decor panier'),
            ('Bugesera Fruit Basket',       'Woven fruit basket kitchen basket bowl sisal agaseke'),
            ('Huye Market Basket',          'Large woven market basket sisal carry bag tressé panier'),
            ('Rubavu Decorative Bowl',      'Handwoven decorative bowl sisal basket home decor woven'),
        ],
        'material': 'Sisal',
        'search_terms': 'basket agaseke woven sisal weave tray bowl storage decor tressé panier'
    },
    'apparel': {
        'products': [
            ('Kitenge Dress Kigali',        'Traditional African dress kitenge fabric women clothing fashion'),
            ('Rwandan Cotton Shirt',        'Handmade cotton shirt men top African print blouse'),
            ('Musanze Wrap Skirt',          'Cotton wrap skirt kitenge women fashion clothing'),
            ('Rubavu Linen Jacket',         'Lightweight jacket cotton blazer men clothing'),
            ('Huye African Print Top',      'African print top blouse women kitenge fashion'),
            ('Kigali Dashiki Shirt',        'Dashiki shirt African men clothing cotton print'),
            ('Bugesera Cotton Dress',       'Cotton dress women African fashion clothing kitenge'),
        ],
        'material': 'Cotton',
        'search_terms': 'dress shirt clothing apparel fabric kitenge cotton jacket skirt blouse top dashiki'
    },
    'jewellery': {
        'products': [
            ('Beaded Necklace Kigali',      'Handmade beaded necklace African jewelry women accessory'),
            ('Rwandan Bead Bracelet',       'Traditional bead bracelet wrist jewelry colorful beads'),
            ('Huye Bead Earrings',          'Handcrafted bead earrings African earrings jewelry women'),
            ('Gicumbi Bead Ring',           'Beaded ring finger jewelry handmade accessory'),
            ('Musanze Beaded Anklet',       'Handmade beaded anklet ankle jewelry women accessory beads'),
            ('Kigali Bead Choker',          'Beaded choker necklace jewelry women African accessory'),
        ],
        'material': 'Beads',
        'search_terms': 'necklace bracelet earrings ring jewelry jewellery beads accessory anklet choker'
    },
    'home-decor': {
        'products': [
            ('Clay Vase Bugesera',          'Handmade clay vase pottery home decoration Rwanda'),
            ('Rwandan Clay Bowl',           'Traditional clay bowl ceramic pot kitchen decor'),
            ('Musanze Wood Sculpture',      'Hand-carved wood sculpture home decor art Rwanda'),
            ('Agaseke Wall Hanging',        'Decorative woven wall art sisal hanging home decor'),
            ('Kigali Ceramic Plate',        'Handmade ceramic plate clay pottery home decor'),
            ('Huye Woven Placemat',         'Handwoven sisal placemat table decor woven basket'),
            ('Rubavu Clay Candle Holder',   'Clay candle holder pottery home decor Rwanda handmade'),
        ],
        'material': 'Clay',
        'search_terms': 'vase bowl sculpture decoration pottery clay wood home decor art ceramic candle'
    }
}

DISTRICTS = ['Kigali', 'Bugesera', 'Musanze', 'Rubavu', 'Huye', 'Gicumbi']

QUERY_PAIRS = [
    ('leather boots',               'Kigali Leather Boots'),
    ('leather shoes',               'Kigali Leather Shoes'),
    ('leather bag',                 'Kigali Leather Handbag'),
    ('leather handbag',             'Kigali Leather Handbag'),
    ('leather backpack',            'Gicumbi Leather Backpack'),
    ('leather jacket',              'Rubavu Leather Jacket'),
    ('leather sandals',             'Nyamirambo Leather Sandals'),
    ('leather wallet',              'Musanze Leather Wallet'),
    ('agaseke basket',              'Agaseke Peace Basket'),
    ('woven basket',                'Agaseke Peace Basket'),
    ('sisal basket',                'Musanze Sisal Storage Basket'),
    ('beaded necklace',             'Beaded Necklace Kigali'),
    ('african jewelry',             'Beaded Necklace Kigali'),
    ('bead bracelet',               'Rwandan Bead Bracelet'),
    ('clay vase',                   'Clay Vase Bugesera'),
    ('african dress',               'Kitenge Dress Kigali'),
    ('kitenge dress',               'Kitenge Dress Kigali'),
    ('african shirt',               'Rwandan Cotton Shirt'),
    ('wood sculpture',              'Musanze Wood Sculpture'),
    ('ceramic plate',               'Kigali Ceramic Plate'),
    ('lether botes',                'Kigali Leather Boots'),
    ('lether bag',                  'Kigali Leather Handbag'),
    ('neklace beads',               'Beaded Necklace Kigali'),
    ('bascet agaseke',              'Agaseke Peace Basket'),
    ('afican dress',                'Kitenge Dress Kigali'),
    ('jewlery beads',               'Beaded Necklace Kigali'),
    ('cley vase',                   'Clay Vase Bugesera'),
    ('cadeau en cuir pour femme',   'Kigali Leather Handbag'),
    ('sac à main cuir',             'Kigali Leather Handbag'),
    ('bottes en cuir',              'Kigali Leather Boots'),
    ('bracelet perles',             'Rwandan Bead Bracelet'),
    ('panier tressé',               'Agaseke Peace Basket'),
    ('robe africaine',              'Kitenge Dress Kigali'),
    ('collier perles',              'Beaded Necklace Kigali'),
    ('vase argile',                 'Clay Vase Bugesera'),
    ('sac à dos cuir',              'Gicumbi Leather Backpack'),
    ("inkweto z'uruhu",             'Kigali Leather Boots'),
    ('agaseke basket Rwanda',       'Agaseke Peace Basket'),
    ('impano yacu leather',         'Kigali Leather Handbag'),
    ('inkweto nziza',               'Kigali Leather Shoes'),
]


def generate_catalog():
    """
    Generate 400 products with unique SKUs.
    Each title appears multiple times but with different
    district, price, and artisan — simulating real catalog
    variety (e.g. same product sold by different artisans).
    The recommender deduplicates by title at index-build time.
    """
    # Flatten all products across categories
    all_products = []
    for category, specs in CATEGORY_SPECS.items():
        for title, desc in specs['products']:
            all_products.append((category, specs['material'],
                                  specs['search_terms'], title, desc))

    data = []
    sku = 1000
    for i in range(NUM_PRODUCTS):
        category, material, search_terms, title, desc = \
            all_products[i % len(all_products)]   # cycle through products
        district = random.choice(DISTRICTS)
        data.append({
            'sku':             f'SKU-{sku}',
            'title':           title,
            'description':     f"{desc}. {search_terms}",
            'category':        category,
            'material':        material,
            'origin_district': district,
            'price_rwf':       random.randint(5000, 75000),
            'artisan_id':      f'ART-{random.randint(1, 50)}'
        })
        sku += 1

    df = pd.DataFrame(data)
    df.to_csv('catalog.csv', index=False)
    print(f"✅ catalog.csv       — {len(df)} products ({df['title'].nunique()} unique titles)")
    return df


def generate_queries():
    data = []
    for _ in range(NUM_QUERIES):
        query, baseline = random.choice(QUERY_PAIRS)
        data.append({'query': query, 'global_best_match': baseline})
    df = pd.DataFrame(data)
    df.to_csv('queries.csv', index=False)
    print(f"✅ queries.csv       — {len(df)} queries")
    return df


def generate_click_log():
    skus = pd.read_csv('catalog.csv')['sku'].tolist()
    data = []
    for _ in range(NUM_CLICKS):
        pos = min(int(np.random.zipf(2.0)), 50)
        data.append({
            'sku':       random.choice(skus),
            'position':  pos,
            'timestamp': pd.Timestamp.now()
        })
    df = pd.DataFrame(data)
    df.to_csv('click_log.csv', index=False)
    print(f"✅ click_log.csv     — {len(df)} click events")
    return df


if __name__ == "__main__":
    generate_catalog()
    generate_queries()
    generate_click_log()