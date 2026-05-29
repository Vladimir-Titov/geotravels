from enum import StrEnum


class GeoApifyPlaceCategory(StrEnum):
    """Geoapify Places API category keys.

    Source: https://apidocs.geoapify.com/docs/places/#categories
    """

    description: str

    def __new__(cls, value: str, description: str = ''):
        category = str.__new__(cls, value)
        category._value_ = value
        category.description = description
        return category

    ACCOMMODATION = (
        'accommodation',
        'Place to stay or live',
    )

    ACCOMMODATION_APARTMENT = (
        'accommodation.apartment',
        '',
    )

    ACCOMMODATION_CHALET = (
        'accommodation.chalet',
        '',
    )

    ACCOMMODATION_GUEST_HOUSE = (
        'accommodation.guest_house',
        '',
    )

    ACCOMMODATION_HOSTEL = (
        'accommodation.hostel',
        '',
    )

    ACCOMMODATION_HOTEL = (
        'accommodation.hotel',
        '',
    )

    ACCOMMODATION_HUT = (
        'accommodation.hut',
        '',
    )

    ACCOMMODATION_MOTEL = (
        'accommodation.motel',
        '',
    )

    ACTIVITY = (
        'activity',
        'Clubs, community centers',
    )

    ACTIVITY_COMMUNITY_CENTER = (
        'activity.community_center',
        '',
    )

    ACTIVITY_EVENTS_VENUE = (
        'activity.events_venue',
        '',
    )

    ACTIVITY_HACKERSPACE = (
        'activity.hackerspace',
        '',
    )

    ACTIVITY_SPORT_CLUB = (
        'activity.sport_club',
        '',
    )

    AIRPORT = (
        'airport',
        'Facility for aircraft operations, including takeoffs, landings, and maintenance',
    )

    AIRPORT_AIRFIELD = (
        'airport.airfield',
        'Area for aircraft operations, can range from simple to complex facilities',
    )

    AIRPORT_GLIDING = (
        'airport.gliding',
        'Designed for glider operations, may include winches or tow planes',
    )

    AIRPORT_INTERNATIONAL = (
        'airport.international',
        'Handles international flights with customs and immigration facilities',
    )

    AIRPORT_MILITARY = (
        'airport.military',
        'Dedicated to armed forces use',
    )

    AIRPORT_PRIVATE = (
        'airport.private',
        'Owned by individuals or entities, not open to the public, for private aviation',
    )

    AIRPORT_TERMINAL = (
        'airport.terminal',
        '',
    )

    COMMERCIAL = (
        'commercial',
        'Places where one can buy or sell things',
    )

    COMMERCIAL_AGRARIAN = (
        'commercial.agrarian',
        '',
    )

    COMMERCIAL_ANTIQUES = (
        'commercial.antiques',
        '',
    )

    COMMERCIAL_ART = (
        'commercial.art',
        '',
    )

    COMMERCIAL_BABY_GOODS = (
        'commercial.baby_goods',
        '',
    )

    COMMERCIAL_BAG = (
        'commercial.bag',
        '',
    )

    COMMERCIAL_BOOKS = (
        'commercial.books',
        '',
    )

    COMMERCIAL_CHEMIST = (
        'commercial.chemist',
        '',
    )

    COMMERCIAL_CLOTHING = (
        'commercial.clothing',
        '',
    )

    COMMERCIAL_CLOTHING_ACCESSORIES = (
        'commercial.clothing.accessories',
        '',
    )

    COMMERCIAL_CLOTHING_CLOTHES = (
        'commercial.clothing.clothes',
        '',
    )

    COMMERCIAL_CLOTHING_KIDS = (
        'commercial.clothing.kids',
        '',
    )

    COMMERCIAL_CLOTHING_MEN = (
        'commercial.clothing.men',
        '',
    )

    COMMERCIAL_CLOTHING_SHOES = (
        'commercial.clothing.shoes',
        '',
    )

    COMMERCIAL_CLOTHING_SPORT = (
        'commercial.clothing.sport',
        '',
    )

    COMMERCIAL_CLOTHING_UNDERWEAR = (
        'commercial.clothing.underwear',
        '',
    )

    COMMERCIAL_CLOTHING_WOMEN = (
        'commercial.clothing.women',
        '',
    )

    COMMERCIAL_CONVENIENCE = (
        'commercial.convenience',
        '',
    )

    COMMERCIAL_DEPARTMENT_STORE = (
        'commercial.department_store',
        '',
    )

    COMMERCIAL_DISCOUNT_STORE = (
        'commercial.discount_store',
        '',
    )

    COMMERCIAL_ELEKTRONICS = (
        'commercial.elektronics',
        '',
    )

    COMMERCIAL_ENERGY = (
        'commercial.energy',
        '',
    )

    COMMERCIAL_EROTIC = (
        'commercial.erotic',
        '',
    )

    COMMERCIAL_FLORIST = (
        'commercial.florist',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK = (
        'commercial.food_and_drink',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_BAKERY = (
        'commercial.food_and_drink.bakery',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_BUTCHER = (
        'commercial.food_and_drink.butcher',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_CHEESE_AND_DAIRY = (
        'commercial.food_and_drink.cheese_and_dairy',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_CHOCOLATE = (
        'commercial.food_and_drink.chocolate',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_COFFEE_AND_TEA = (
        'commercial.food_and_drink.coffee_and_tea',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_CONFECTIONERY = (
        'commercial.food_and_drink.confectionery',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_DELI = (
        'commercial.food_and_drink.deli',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_DRINKS = (
        'commercial.food_and_drink.drinks',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_FARM = (
        'commercial.food_and_drink.farm',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_FROZEN_FOOD = (
        'commercial.food_and_drink.frozen_food',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_FRUIT_AND_VEGETABLE = (
        'commercial.food_and_drink.fruit_and_vegetable',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_HEALTH_FOOD = (
        'commercial.food_and_drink.health_food',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_HONEY = (
        'commercial.food_and_drink.honey',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_ICE_CREAM = (
        'commercial.food_and_drink.ice_cream',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_NUTS = (
        'commercial.food_and_drink.nuts',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_ORGANIC = (
        'commercial.food_and_drink.organic',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_PASTA = (
        'commercial.food_and_drink.pasta',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_RICE = (
        'commercial.food_and_drink.rice',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_SEAFOOD = (
        'commercial.food_and_drink.seafood',
        '',
    )

    COMMERCIAL_FOOD_AND_DRINK_SPICES = (
        'commercial.food_and_drink.spices',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR = (
        'commercial.furniture_and_interior',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR_BATHROOM = (
        'commercial.furniture_and_interior.bathroom',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR_BED = (
        'commercial.furniture_and_interior.bed',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR_CARPET = (
        'commercial.furniture_and_interior.carpet',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR_CURTAIN = (
        'commercial.furniture_and_interior.curtain',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR_KITCHEN = (
        'commercial.furniture_and_interior.kitchen',
        '',
    )

    COMMERCIAL_FURNITURE_AND_INTERIOR_LIGHTING = (
        'commercial.furniture_and_interior.lighting',
        '',
    )

    COMMERCIAL_GARDEN = (
        'commercial.garden',
        '',
    )

    COMMERCIAL_GAS = (
        'commercial.gas',
        '',
    )

    COMMERCIAL_GIFT_AND_SOUVENIR = (
        'commercial.gift_and_souvenir',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY = (
        'commercial.health_and_beauty',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_COSMETICS = (
        'commercial.health_and_beauty.cosmetics',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_HEARING_AIDS = (
        'commercial.health_and_beauty.hearing_aids',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_HERBALIST = (
        'commercial.health_and_beauty.herbalist',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_MEDICAL_SUPPLY = (
        'commercial.health_and_beauty.medical_supply',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_OPTICIAN = (
        'commercial.health_and_beauty.optician',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_PHARMACY = (
        'commercial.health_and_beauty.pharmacy',
        '',
    )

    COMMERCIAL_HEALTH_AND_BEAUTY_WIGS = (
        'commercial.health_and_beauty.wigs',
        '',
    )

    COMMERCIAL_HOBBY = (
        'commercial.hobby',
        '',
    )

    COMMERCIAL_HOBBY_ANIME = (
        'commercial.hobby.anime',
        '',
    )

    COMMERCIAL_HOBBY_ART = (
        'commercial.hobby.art',
        '',
    )

    COMMERCIAL_HOBBY_BREWING = (
        'commercial.hobby.brewing',
        '',
    )

    COMMERCIAL_HOBBY_COLLECTING = (
        'commercial.hobby.collecting',
        '',
    )

    COMMERCIAL_HOBBY_GAMES = (
        'commercial.hobby.games',
        '',
    )

    COMMERCIAL_HOBBY_MODEL = (
        'commercial.hobby.model',
        '',
    )

    COMMERCIAL_HOBBY_MUSIC = (
        'commercial.hobby.music',
        '',
    )

    COMMERCIAL_HOBBY_PHOTO = (
        'commercial.hobby.photo',
        '',
    )

    COMMERCIAL_HOBBY_SEWING_AND_KNITTING = (
        'commercial.hobby.sewing_and_knitting',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE = (
        'commercial.houseware_and_hardware',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS = (
        'commercial.houseware_and_hardware.building_materials',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS_DOORS = (
        'commercial.houseware_and_hardware.building_materials.doors',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS_FLOORING = (
        'commercial.houseware_and_hardware.building_materials.flooring',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS_GLAZIERY = (
        'commercial.houseware_and_hardware.building_materials.glaziery',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS_PAINT = (
        'commercial.houseware_and_hardware.building_materials.paint',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS_TILES = (
        'commercial.houseware_and_hardware.building_materials.tiles',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_BUILDING_MATERIALS_WINDOWS = (
        'commercial.houseware_and_hardware.building_materials.windows',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_DOITYOURSELF = (
        'commercial.houseware_and_hardware.doityourself',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_FIREPLACE = (
        'commercial.houseware_and_hardware.fireplace',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_HARDWARE_AND_TOOLS = (
        'commercial.houseware_and_hardware.hardware_and_tools',
        '',
    )

    COMMERCIAL_HOUSEWARE_AND_HARDWARE_SWIMMING_POOL = (
        'commercial.houseware_and_hardware.swimming_pool',
        '',
    )

    COMMERCIAL_JEWELRY = (
        'commercial.jewelry',
        '',
    )

    COMMERCIAL_KIOSK = (
        'commercial.kiosk',
        '',
    )

    COMMERCIAL_MARKETPLACE = (
        'commercial.marketplace',
        '',
    )

    COMMERCIAL_NEWSAGENT = (
        'commercial.newsagent',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT = (
        'commercial.outdoor_and_sport',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_BICYCLE = (
        'commercial.outdoor_and_sport.bicycle',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_DIVING = (
        'commercial.outdoor_and_sport.diving',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_FISHING = (
        'commercial.outdoor_and_sport.fishing',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_GOLF = (
        'commercial.outdoor_and_sport.golf',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_HUNTING = (
        'commercial.outdoor_and_sport.hunting',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_SKI = (
        'commercial.outdoor_and_sport.ski',
        '',
    )

    COMMERCIAL_OUTDOOR_AND_SPORT_WATER_SPORTS = (
        'commercial.outdoor_and_sport.water_sports',
        '',
    )

    COMMERCIAL_PET = (
        'commercial.pet',
        '',
    )

    COMMERCIAL_PYROTECHNICS = (
        'commercial.pyrotechnics',
        '',
    )

    COMMERCIAL_SECOND_HAND = (
        'commercial.second_hand',
        '',
    )

    COMMERCIAL_SHOPPING_MALL = (
        'commercial.shopping_mall',
        '',
    )

    COMMERCIAL_SMOKING = (
        'commercial.smoking',
        '',
    )

    COMMERCIAL_STATIONERY = (
        'commercial.stationery',
        '',
    )

    COMMERCIAL_SUPERMARKET = (
        'commercial.supermarket',
        '',
    )

    COMMERCIAL_TICKETS_AND_LOTTERY = (
        'commercial.tickets_and_lottery',
        '',
    )

    COMMERCIAL_TOY_AND_GAME = (
        'commercial.toy_and_game',
        '',
    )

    COMMERCIAL_TRADE = (
        'commercial.trade',
        '',
    )

    COMMERCIAL_VEHICLE = (
        'commercial.vehicle',
        '',
    )

    COMMERCIAL_VIDEO_AND_MUSIC = (
        'commercial.video_and_music',
        '',
    )

    COMMERCIAL_WATCHES = (
        'commercial.watches',
        '',
    )

    COMMERCIAL_WEAPONS = (
        'commercial.weapons',
        '',
    )

    COMMERCIAL_WEDDING = (
        'commercial.wedding',
        '',
    )

    CATERING = (
        'catering',
        'Places of public catering: restaurants, cafes, bars, etc.',
    )

    CATERING_BAR = (
        'catering.bar',
        '',
    )

    CATERING_BIERGARTEN = (
        'catering.biergarten',
        '',
    )

    CATERING_CAFE = (
        'catering.cafe',
        '',
    )

    CATERING_CAFE_BUBBLE_TEA = (
        'catering.cafe.bubble_tea',
        '',
    )

    CATERING_CAFE_CAKE = (
        'catering.cafe.cake',
        '',
    )

    CATERING_CAFE_COFFEE = (
        'catering.cafe.coffee',
        '',
    )

    CATERING_CAFE_COFFEE_SHOP = (
        'catering.cafe.coffee_shop',
        '',
    )

    CATERING_CAFE_CREPE = (
        'catering.cafe.crepe',
        '',
    )

    CATERING_CAFE_DESSERT = (
        'catering.cafe.dessert',
        '',
    )

    CATERING_CAFE_DONUT = (
        'catering.cafe.donut',
        '',
    )

    CATERING_CAFE_FROZEN_YOGURT = (
        'catering.cafe.frozen_yogurt',
        '',
    )

    CATERING_CAFE_ICE_CREAM = (
        'catering.cafe.ice_cream',
        '',
    )

    CATERING_CAFE_TEA = (
        'catering.cafe.tea',
        '',
    )

    CATERING_CAFE_WAFFLE = (
        'catering.cafe.waffle',
        '',
    )

    CATERING_FAST_FOOD = (
        'catering.fast_food',
        '',
    )

    CATERING_FAST_FOOD_BURGER = (
        'catering.fast_food.burger',
        '',
    )

    CATERING_FAST_FOOD_FISH_AND_CHIPS = (
        'catering.fast_food.fish_and_chips',
        '',
    )

    CATERING_FAST_FOOD_HOT_DOG = (
        'catering.fast_food.hot_dog',
        '',
    )

    CATERING_FAST_FOOD_KEBAB = (
        'catering.fast_food.kebab',
        '',
    )

    CATERING_FAST_FOOD_NOODLE = (
        'catering.fast_food.noodle',
        '',
    )

    CATERING_FAST_FOOD_PITA = (
        'catering.fast_food.pita',
        '',
    )

    CATERING_FAST_FOOD_PIZZA = (
        'catering.fast_food.pizza',
        '',
    )

    CATERING_FAST_FOOD_RAMEN = (
        'catering.fast_food.ramen',
        '',
    )

    CATERING_FAST_FOOD_SALAD = (
        'catering.fast_food.salad',
        '',
    )

    CATERING_FAST_FOOD_SANDWICH = (
        'catering.fast_food.sandwich',
        '',
    )

    CATERING_FAST_FOOD_SOUP = (
        'catering.fast_food.soup',
        '',
    )

    CATERING_FAST_FOOD_TACOS = (
        'catering.fast_food.tacos',
        '',
    )

    CATERING_FAST_FOOD_TAPAS = (
        'catering.fast_food.tapas',
        '',
    )

    CATERING_FAST_FOOD_WINGS = (
        'catering.fast_food.wings',
        '',
    )

    CATERING_FOOD_COURT = (
        'catering.food_court',
        '',
    )

    CATERING_ICE_CREAM = (
        'catering.ice_cream',
        '',
    )

    CATERING_PUB = (
        'catering.pub',
        '',
    )

    CATERING_RESTAURANT = (
        'catering.restaurant',
        '',
    )

    CATERING_RESTAURANT_AFGHAN = (
        'catering.restaurant.afghan',
        '',
    )

    CATERING_RESTAURANT_AFRICAN = (
        'catering.restaurant.african',
        '',
    )

    CATERING_RESTAURANT_AMERICAN = (
        'catering.restaurant.american',
        '',
    )

    CATERING_RESTAURANT_ARAB = (
        'catering.restaurant.arab',
        '',
    )

    CATERING_RESTAURANT_ARGENTINIAN = (
        'catering.restaurant.argentinian',
        '',
    )

    CATERING_RESTAURANT_ASIAN = (
        'catering.restaurant.asian',
        '',
    )

    CATERING_RESTAURANT_AUSTRIAN = (
        'catering.restaurant.austrian',
        '',
    )

    CATERING_RESTAURANT_BALKAN = (
        'catering.restaurant.balkan',
        '',
    )

    CATERING_RESTAURANT_BARBECUE = (
        'catering.restaurant.barbecue',
        '',
    )

    CATERING_RESTAURANT_BAVARIAN = (
        'catering.restaurant.bavarian',
        '',
    )

    CATERING_RESTAURANT_BEEF_BOWL = (
        'catering.restaurant.beef_bowl',
        '',
    )

    CATERING_RESTAURANT_BELGIAN = (
        'catering.restaurant.belgian',
        '',
    )

    CATERING_RESTAURANT_BOLIVIAN = (
        'catering.restaurant.bolivian',
        '',
    )

    CATERING_RESTAURANT_BRAZILIAN = (
        'catering.restaurant.brazilian',
        '',
    )

    CATERING_RESTAURANT_BURGER = (
        'catering.restaurant.burger',
        '',
    )

    CATERING_RESTAURANT_CARIBBEAN = (
        'catering.restaurant.caribbean',
        '',
    )

    CATERING_RESTAURANT_CHICKEN = (
        'catering.restaurant.chicken',
        '',
    )

    CATERING_RESTAURANT_CHILI = (
        'catering.restaurant.chili',
        '',
    )

    CATERING_RESTAURANT_CHINESE = (
        'catering.restaurant.chinese',
        '',
    )

    CATERING_RESTAURANT_CROATIAN = (
        'catering.restaurant.croatian',
        '',
    )

    CATERING_RESTAURANT_CUBAN = (
        'catering.restaurant.cuban',
        '',
    )

    CATERING_RESTAURANT_CURRY = (
        'catering.restaurant.curry',
        '',
    )

    CATERING_RESTAURANT_CZECH = (
        'catering.restaurant.czech',
        '',
    )

    CATERING_RESTAURANT_DANISH = (
        'catering.restaurant.danish',
        '',
    )

    CATERING_RESTAURANT_DUMPLING = (
        'catering.restaurant.dumpling',
        '',
    )

    CATERING_RESTAURANT_ETHIOPIAN = (
        'catering.restaurant.ethiopian',
        '',
    )

    CATERING_RESTAURANT_EUROPEAN = (
        'catering.restaurant.european',
        '',
    )

    CATERING_RESTAURANT_FILIPINO = (
        'catering.restaurant.filipino',
        '',
    )

    CATERING_RESTAURANT_FISH = (
        'catering.restaurant.fish',
        '',
    )

    CATERING_RESTAURANT_FISH_AND_CHIPS = (
        'catering.restaurant.fish_and_chips',
        '',
    )

    CATERING_RESTAURANT_FRENCH = (
        'catering.restaurant.french',
        '',
    )

    CATERING_RESTAURANT_FRITURE = (
        'catering.restaurant.friture',
        '',
    )

    CATERING_RESTAURANT_GEORGIAN = (
        'catering.restaurant.georgian',
        '',
    )

    CATERING_RESTAURANT_GERMAN = (
        'catering.restaurant.german',
        '',
    )

    CATERING_RESTAURANT_GREEK = (
        'catering.restaurant.greek',
        '',
    )

    CATERING_RESTAURANT_HAWAIIAN = (
        'catering.restaurant.hawaiian',
        '',
    )

    CATERING_RESTAURANT_HUNGARIAN = (
        'catering.restaurant.hungarian',
        '',
    )

    CATERING_RESTAURANT_INDIAN = (
        'catering.restaurant.indian',
        '',
    )

    CATERING_RESTAURANT_INDONESIAN = (
        'catering.restaurant.indonesian',
        '',
    )

    CATERING_RESTAURANT_INTERNATIONAL = (
        'catering.restaurant.international',
        '',
    )

    CATERING_RESTAURANT_IRISH = (
        'catering.restaurant.irish',
        '',
    )

    CATERING_RESTAURANT_ITALIAN = (
        'catering.restaurant.italian',
        '',
    )

    CATERING_RESTAURANT_JAMAICAN = (
        'catering.restaurant.jamaican',
        '',
    )

    CATERING_RESTAURANT_JAPANESE = (
        'catering.restaurant.japanese',
        '',
    )

    CATERING_RESTAURANT_KEBAB = (
        'catering.restaurant.kebab',
        '',
    )

    CATERING_RESTAURANT_KOREAN = (
        'catering.restaurant.korean',
        '',
    )

    CATERING_RESTAURANT_LATIN_AMERICAN = (
        'catering.restaurant.latin_american',
        '',
    )

    CATERING_RESTAURANT_LEBANESE = (
        'catering.restaurant.lebanese',
        '',
    )

    CATERING_RESTAURANT_MALAY = (
        'catering.restaurant.malay',
        '',
    )

    CATERING_RESTAURANT_MALAYSIAN = (
        'catering.restaurant.malaysian',
        '',
    )

    CATERING_RESTAURANT_MEDITERRANEAN = (
        'catering.restaurant.mediterranean',
        '',
    )

    CATERING_RESTAURANT_MEXICAN = (
        'catering.restaurant.mexican',
        '',
    )

    CATERING_RESTAURANT_MOROCCAN = (
        'catering.restaurant.moroccan',
        '',
    )

    CATERING_RESTAURANT_NEPALESE = (
        'catering.restaurant.nepalese',
        '',
    )

    CATERING_RESTAURANT_NOODLE = (
        'catering.restaurant.noodle',
        '',
    )

    CATERING_RESTAURANT_ORIENTAL = (
        'catering.restaurant.oriental',
        '',
    )

    CATERING_RESTAURANT_PAKISTANI = (
        'catering.restaurant.pakistani',
        '',
    )

    CATERING_RESTAURANT_PERSIAN = (
        'catering.restaurant.persian',
        '',
    )

    CATERING_RESTAURANT_PERUVIAN = (
        'catering.restaurant.peruvian',
        '',
    )

    CATERING_RESTAURANT_PITA = (
        'catering.restaurant.pita',
        '',
    )

    CATERING_RESTAURANT_PIZZA = (
        'catering.restaurant.pizza',
        '',
    )

    CATERING_RESTAURANT_PORTUGUESE = (
        'catering.restaurant.portuguese',
        '',
    )

    CATERING_RESTAURANT_RAMEN = (
        'catering.restaurant.ramen',
        '',
    )

    CATERING_RESTAURANT_REGIONAL = (
        'catering.restaurant.regional',
        '',
    )

    CATERING_RESTAURANT_RUSSIAN = (
        'catering.restaurant.russian',
        '',
    )

    CATERING_RESTAURANT_SANDWICH = (
        'catering.restaurant.sandwich',
        '',
    )

    CATERING_RESTAURANT_SEAFOOD = (
        'catering.restaurant.seafood',
        '',
    )

    CATERING_RESTAURANT_SOUP = (
        'catering.restaurant.soup',
        '',
    )

    CATERING_RESTAURANT_SPANISH = (
        'catering.restaurant.spanish',
        '',
    )

    CATERING_RESTAURANT_STEAK_HOUSE = (
        'catering.restaurant.steak_house',
        '',
    )

    CATERING_RESTAURANT_SUSHI = (
        'catering.restaurant.sushi',
        '',
    )

    CATERING_RESTAURANT_SWEDISH = (
        'catering.restaurant.swedish',
        '',
    )

    CATERING_RESTAURANT_SYRIAN = (
        'catering.restaurant.syrian',
        '',
    )

    CATERING_RESTAURANT_TACOS = (
        'catering.restaurant.tacos',
        '',
    )

    CATERING_RESTAURANT_TAIWANESE = (
        'catering.restaurant.taiwanese',
        '',
    )

    CATERING_RESTAURANT_TAPAS = (
        'catering.restaurant.tapas',
        '',
    )

    CATERING_RESTAURANT_TEX_MEX = (
        'catering.restaurant.tex-mex',
        '',
    )

    CATERING_RESTAURANT_THAI = (
        'catering.restaurant.thai',
        '',
    )

    CATERING_RESTAURANT_TURKISH = (
        'catering.restaurant.turkish',
        '',
    )

    CATERING_RESTAURANT_UKRAINIAN = (
        'catering.restaurant.ukrainian',
        '',
    )

    CATERING_RESTAURANT_UZBEK = (
        'catering.restaurant.uzbek',
        '',
    )

    CATERING_RESTAURANT_VIETNAMESE = (
        'catering.restaurant.vietnamese',
        '',
    )

    CATERING_RESTAURANT_WESTERN = (
        'catering.restaurant.western',
        '',
    )

    CATERING_RESTAURANT_WINGS = (
        'catering.restaurant.wings',
        '',
    )

    CATERING_TAPROOM = (
        'catering.taproom',
        'Place where you can sample draught cask beer',
    )

    EMERGENCY = (
        'emergency',
        'General category for emergency-related infrastructure',
    )

    EMERGENCY_ACCESS_POINT = (
        'emergency.access_point',
        'Marked access point for rescue or emergency services',
    )

    EMERGENCY_AIR_RESCUE_SERVICE = (
        'emergency.air_rescue_service',
        'Air rescue service base (helicopter/air ambulance)',
    )

    EMERGENCY_AMBULANCE_STATION = (
        'emergency.ambulance_station',
        'Base for ambulances and emergency medical response teams',
    )

    EMERGENCY_ASSEMBLY_POINT = (
        'emergency.assembly_point',
        'Safe meeting area designated for people to gather during emergencies',
    )

    EMERGENCY_BLEED_CONTROL_KIT = (
        'emergency.bleed_control_kit',
        'Bleed control kit for severe hemorrhage management',
    )

    EMERGENCY_CONTROL_CENTRE = (
        'emergency.control_centre',
        'Emergency control center for coordination and dispatch',
    )

    EMERGENCY_DEFIBRILLATOR = (
        'emergency.defibrillator',
        'AED (Automated External Defibrillator) for cardiac emergencies',
    )

    EMERGENCY_DISASTER_HELP_POINT = (
        'emergency.disaster_help_point',
        'Designated disaster help/assembly point',
    )

    EMERGENCY_DISASTER_RESPONSE = (
        'emergency.disaster_response',
        'Disaster response coordination site or depot',
    )

    EMERGENCY_DRINKING_WATER = (
        'emergency.drinking_water',
        'Emergency drinking water supply point',
    )

    EMERGENCY_DRY_RISER_INLET = (
        'emergency.dry_riser_inlet',
        'Dry riser inlet connection for firefighters',
    )

    EMERGENCY_EMERGENCY_WARD_ENTRANCE = (
        'emergency.emergency_ward_entrance',
        'Entrance to a hospital emergency department',
    )

    EMERGENCY_FIRE_ALARM_BOX = (
        'emergency.fire_alarm_box',
        'Manual fire alarm call point (alarm box)',
    )

    EMERGENCY_FIRE_DETECTION_SYSTEM = (
        'emergency.fire_detection_system',
        'Fire detection or alarm system components',
    )

    EMERGENCY_FIRE_EXTINGUISHER = (
        'emergency.fire_extinguisher',
        'Portable device used to put out small fires',
    )

    EMERGENCY_FIRE_FLAPPER = (
        'emergency.fire_flapper',
        'Fire beater/flapper tool station for wildfire control',
    )

    EMERGENCY_FIRE_HOSE = (
        'emergency.fire_hose',
        'Fixed fire hose or hose reel for firefighting',
    )

    EMERGENCY_FIRE_HYDRANT = (
        'emergency.fire_hydrant',
        'Device that provides water supply for firefighting',
    )

    EMERGENCY_FIRE_LOOKOUT = (
        'emergency.fire_lookout',
        'Fire lookout tower or observation point',
    )

    EMERGENCY_FIRE_SERVICE_INLET = (
        'emergency.fire_service_inlet',
        'Inlet connection for fire services to pump water into a building system',
    )

    EMERGENCY_FIRE_WATER_POND = (
        'emergency.fire_water_pond',
        'Pond or reservoir reserved for firefighting water supply',
    )

    EMERGENCY_FIRST_AID = (
        'emergency.first_aid',
        'First aid station providing immediate medical assistance',
    )

    EMERGENCY_FIRST_AID_KIT = (
        'emergency.first_aid_kit',
        'First aid kit location with basic medical supplies',
    )

    EMERGENCY_KEY_DEPOT = (
        'emergency.key_depot',
        'Key depot/safe for emergency access keys',
    )

    EMERGENCY_LANDING_SITE = (
        'emergency.landing_site',
        'Designated landing site for emergency services (often helicopter)',
    )

    EMERGENCY_LIFE_RING = (
        'emergency.life_ring',
        'Life ring or buoy station for water rescue',
    )

    EMERGENCY_LIFEGUARD = (
        'emergency.lifeguard',
        'Lifeguard post for rescue and supervision',
    )

    EMERGENCY_LIFEGUARD_BASE = (
        'emergency.lifeguard_base',
        'Main base for lifeguard services',
    )

    EMERGENCY_MARINE_RESCUE = (
        'emergency.marine_rescue',
        'Marine rescue service station',
    )

    EMERGENCY_MOUNTAIN_RESCUE = (
        'emergency.mountain_rescue',
        'Mountain rescue base or hut',
    )

    EMERGENCY_PHONE = (
        'emergency.phone',
        'Emergency telephone for immediate communication with authorities',
    )

    EMERGENCY_RESCUE_BOX = (
        'emergency.rescue_box',
        'Rescue equipment box with emergency tools',
    )

    EMERGENCY_SIREN = (
        'emergency.siren',
        'Warning siren for civil defense and emergency alerts',
    )

    EMERGENCY_SLIPWAY = (
        'emergency.slipway',
        'Slipway used for launching rescue boats',
    )

    EMERGENCY_SUCTION_POINT = (
        'emergency.suction_point',
        'Designated spot where fire trucks can extract water, e.g., from ponds',
    )

    EMERGENCY_WATER_RESCUE = (
        'emergency.water_rescue',
        'Water rescue service base or station',
    )

    EMERGENCY_WATER_TANK = (
        'emergency.water_tank',
        'Storage tank for emergency water supply, especially for firefighting',
    )

    EDUCATION = (
        'education',
        'Place that provides learning spaces and learning environments',
    )

    EDUCATION_COLLEGE = (
        'education.college',
        '',
    )

    EDUCATION_DRIVING_SCHOOL = (
        'education.driving_school',
        '',
    )

    EDUCATION_LANGUAGE_SCHOOL = (
        'education.language_school',
        '',
    )

    EDUCATION_LIBRARY = (
        'education.library',
        '',
    )

    EDUCATION_MUSIC_SCHOOL = (
        'education.music_school',
        '',
    )

    EDUCATION_SCHOOL = (
        'education.school',
        '',
    )

    EDUCATION_UNIVERSITY = (
        'education.university',
        '',
    )

    CHILDCARE = (
        'childcare',
        'Place that provides care of children service while parents are working',
    )

    CHILDCARE_KINDERGARTEN = (
        'childcare.kindergarten',
        '',
    )

    ENTERTAINMENT = (
        'entertainment',
        'Place that where one can spend free time with amusement',
    )

    ENTERTAINMENT_ACTIVITY_PARK = (
        'entertainment.activity_park',
        '',
    )

    ENTERTAINMENT_ACTIVITY_PARK_CLIMBING = (
        'entertainment.activity_park.climbing',
        '',
    )

    ENTERTAINMENT_ACTIVITY_PARK_TRAMPOLINE = (
        'entertainment.activity_park.trampoline',
        '',
    )

    ENTERTAINMENT_AMUSEMENT_ARCADE = (
        'entertainment.amusement_arcade',
        '',
    )

    ENTERTAINMENT_AQUARIUM = (
        'entertainment.aquarium',
        '',
    )

    ENTERTAINMENT_BOWLING_ALLEY = (
        'entertainment.bowling_alley',
        '',
    )

    ENTERTAINMENT_CINEMA = (
        'entertainment.cinema',
        '',
    )

    ENTERTAINMENT_CULTURE = (
        'entertainment.culture',
        '',
    )

    ENTERTAINMENT_CULTURE_ARTS_CENTRE = (
        'entertainment.culture.arts_centre',
        '',
    )

    ENTERTAINMENT_CULTURE_GALLERY = (
        'entertainment.culture.gallery',
        '',
    )

    ENTERTAINMENT_CULTURE_THEATRE = (
        'entertainment.culture.theatre',
        '',
    )

    ENTERTAINMENT_ESCAPE_GAME = (
        'entertainment.escape_game',
        '',
    )

    ENTERTAINMENT_FLYING_FOX = (
        'entertainment.flying_fox',
        '',
    )

    ENTERTAINMENT_MINIATURE_GOLF = (
        'entertainment.miniature_golf',
        '',
    )

    ENTERTAINMENT_MUSEUM = (
        'entertainment.museum',
        '',
    )

    ENTERTAINMENT_PLANETARIUM = (
        'entertainment.planetarium',
        '',
    )

    ENTERTAINMENT_THEME_PARK = (
        'entertainment.theme_park',
        '',
    )

    ENTERTAINMENT_WATER_PARK = (
        'entertainment.water_park',
        '',
    )

    ENTERTAINMENT_ZOO = (
        'entertainment.zoo',
        '',
    )

    HEALTHCARE = (
        'healthcare',
        'Places that provides healthcare services: hospitals, clinics and more',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS = (
        'healthcare.clinic_or_praxis',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_ALLERGOLOGY = (
        'healthcare.clinic_or_praxis.allergology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_CARDIOLOGY = (
        'healthcare.clinic_or_praxis.cardiology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_DERMATOLOGY = (
        'healthcare.clinic_or_praxis.dermatology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_ENDOCRINOLOGY = (
        'healthcare.clinic_or_praxis.endocrinology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_GASTROENTEROLOGY = (
        'healthcare.clinic_or_praxis.gastroenterology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_GENERAL = (
        'healthcare.clinic_or_praxis.general',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_GYNAECOLOGY = (
        'healthcare.clinic_or_praxis.gynaecology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_OCCUPATIONAL = (
        'healthcare.clinic_or_praxis.occupational',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_OPHTHALMOLOGY = (
        'healthcare.clinic_or_praxis.ophthalmology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_ORTHOPAEDICS = (
        'healthcare.clinic_or_praxis.orthopaedics',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_OTOLARYNGOLOGY = (
        'healthcare.clinic_or_praxis.otolaryngology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_PAEDIATRICS = (
        'healthcare.clinic_or_praxis.paediatrics',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_PSYCHIATRY = (
        'healthcare.clinic_or_praxis.psychiatry',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_PULMONOLOGY = (
        'healthcare.clinic_or_praxis.pulmonology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_RADIOLOGY = (
        'healthcare.clinic_or_praxis.radiology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_RHEUMATOLOGY = (
        'healthcare.clinic_or_praxis.rheumatology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_TRAUMA = (
        'healthcare.clinic_or_praxis.trauma',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_UROLOGY = (
        'healthcare.clinic_or_praxis.urology',
        '',
    )

    HEALTHCARE_CLINIC_OR_PRAXIS_VASCULAR_SURGERY = (
        'healthcare.clinic_or_praxis.vascular_surgery',
        '',
    )

    HEALTHCARE_DENTIST = (
        'healthcare.dentist',
        '',
    )

    HEALTHCARE_DENTIST_ORTHODONTICS = (
        'healthcare.dentist.orthodontics',
        '',
    )

    HEALTHCARE_HOSPITAL = (
        'healthcare.hospital',
        '',
    )

    HEALTHCARE_PHARMACY = (
        'healthcare.pharmacy',
        '',
    )

    HERITAGE = (
        'heritage',
        '',
    )

    HERITAGE_UNESCO = (
        'heritage.unesco',
        '',
    )

    HIGHWAY = (
        'highway',
        'Roads, varying from small roads to major routes.',
    )

    HIGHWAY_BUSWAY = (
        'highway.busway',
        'Dedicated lanes or roads for bus traffic, often in urban areas',
    )

    HIGHWAY_CYCLEWAY = (
        'highway.cycleway',
        'Designated paths for bicycles, separate from vehicular traffic lanes',
    )

    HIGHWAY_FOOTWAY = (
        'highway.footway',
        'Paths designated for pedestrian use only, no vehicular traffic',
    )

    HIGHWAY_LIVING_STREET = (
        'highway.living_street',
        'Roads with very low speed limits, prioritizing pedestrians and cyclists',
    )

    HIGHWAY_MOTORWAY = (
        'highway.motorway',
        'High-capacity roads for fast, long-distance travel with controlled access',
    )

    HIGHWAY_MOTORWAY_JUNCTION = (
        'highway.motorway.junction',
        'Intersections or exits on motorways, often with ramps',
    )

    HIGHWAY_MOTORWAY_LINK = (
        'highway.motorway.link',
        'Ramps or roads connecting to or from a motorway',
    )

    HIGHWAY_PATH = (
        'highway.path',
        'General paths for walking, cycling, and sometimes equestrian use',
    )

    HIGHWAY_PEDESTRIAN = (
        'highway.pedestrian',
        'Areas primarily intended for pedestrian traffic, often in commercial zones',
    )

    HIGHWAY_PRIMARY = (
        'highway.primary',
        'Major roads connecting large towns or cities, important for regional traffic',
    )

    HIGHWAY_PRIMARY_LINK = (
        'highway.primary.link',
        'Short connectors between primary roads and other road types',
    )

    HIGHWAY_PUBLIC = (
        'highway.public',
        'Roads open to the general public, encompassing a wide range of types',
    )

    HIGHWAY_RESIDENTIAL = (
        'highway.residential',
        'Roads within residential areas, primarily for local access',
    )

    HIGHWAY_SECONDARY = (
        'highway.secondary',
        'Roads connecting smaller towns, less important than primary roads',
    )

    HIGHWAY_SECONDARY_LINK = (
        'highway.secondary.link',
        'Connectors between secondary roads and adjacent road types',
    )

    HIGHWAY_ROUNDABOUT = (
        'highway.roundabout',
        '',
    )

    HIGHWAY_SERVICE = (
        'highway.service',
        'Roads providing access to buildings, service areas, or other facilities',
    )

    HIGHWAY_TERTIARY = (
        'highway.tertiary',
        'Roads linking villages and local centers, less traffic than secondary roads',
    )

    HIGHWAY_TERTIARY_LINK = (
        'highway.tertiary.link',
        'Small connectors between tertiary roads and other roads',
    )

    HIGHWAY_TRACK = (
        'highway.track',
        'Unpaved or rough paths primarily used for agricultural or forestry purposes',
    )

    HIGHWAY_TRUNK = (
        'highway.trunk',
        'Major roads with high traffic volume, often linking major cities',
    )

    HIGHWAY_TRUNK_LINK = (
        'highway.trunk.link',
        'Ramps or links between trunk roads and other types',
    )

    LEISURE = (
        'leisure',
        'Places where one can relax and unwind',
    )

    LEISURE_PARK = (
        'leisure.park',
        '',
    )

    LEISURE_PARK_GARDEN = (
        'leisure.park.garden',
        '',
    )

    LEISURE_PARK_NATURE_RESERVE = (
        'leisure.park.nature_reserve',
        '',
    )

    LEISURE_PICNIC = (
        'leisure.picnic',
        '',
    )

    LEISURE_PICNIC_BBQ = (
        'leisure.picnic.bbq',
        '',
    )

    LEISURE_PICNIC_PICNIC_SITE = (
        'leisure.picnic.picnic_site',
        '',
    )

    LEISURE_PICNIC_PICNIC_TABLE = (
        'leisure.picnic.picnic_table',
        '',
    )

    LEISURE_PLAYGROUND = (
        'leisure.playground',
        '',
    )

    LEISURE_SPA = (
        'leisure.spa',
        '',
    )

    LEISURE_SPA_PUBLIC_BATH = (
        'leisure.spa.public_bath',
        '',
    )

    LEISURE_SPA_SAUNA = (
        'leisure.spa.sauna',
        '',
    )

    MAN_MADE = (
        'man_made',
        'The man-made category is used to identify anything that was constructed by humans',
    )

    MAN_MADE_BREAKWATER = (
        'man_made.breakwater',
        '',
    )

    MAN_MADE_BRIDGE = (
        'man_made.bridge',
        '',
    )

    MAN_MADE_LIGHTHOUSE = (
        'man_made.lighthouse',
        '',
    )

    MAN_MADE_PIER = (
        'man_made.pier',
        '',
    )

    MAN_MADE_TOWER = (
        'man_made.tower',
        '',
    )

    MAN_MADE_WATER_TOWER = (
        'man_made.water_tower',
        '',
    )

    MAN_MADE_WATERMILL = (
        'man_made.watermill',
        '',
    )

    MAN_MADE_WINDMILL = (
        'man_made.windmill',
        '',
    )

    MARITIME = (
        'maritime',
        'Maritime places and infrastructure',
    )

    MARITIME_MARINA = (
        'maritime.marina',
        '',
    )

    WATERWAY = (
        'waterway',
        'Waterway features and infrastructure',
    )

    WATERWAY_CHANNELS = (
        'waterway.channels',
        '',
    )

    WATERWAY_HYDRAULIC_STRUCTURES = (
        'waterway.hydraulic_structures',
        '',
    )

    WATERWAY_NAVIGATION = (
        'waterway.navigation',
        '',
    )

    WATERWAY_RIVER_SYSTEM = (
        'waterway.river_system',
        '',
    )

    WATERWAY_WATER_POINT = (
        'waterway.water_point',
        '',
    )

    WATERWAY_WHITEWATER = (
        'waterway.whitewater',
        '',
    )

    NATURAL = (
        'natural',
        'Places where one can enjoy nature, explore natural phenomena',
    )

    NATURAL_COASTAL = (
        'natural.coastal',
        '',
    )

    NATURAL_DESERT = (
        'natural.desert',
        '',
    )

    NATURAL_FOREST = (
        'natural.forest',
        '',
    )

    NATURAL_HEATH_MOOR = (
        'natural.heath_moor',
        '',
    )

    NATURAL_MOUNTAIN = (
        'natural.mountain',
        '',
    )

    NATURAL_MOUNTAIN_CAVE_ENTRANCE = (
        'natural.mountain.cave_entrance',
        '',
    )

    NATURAL_MOUNTAIN_CLIFF = (
        'natural.mountain.cliff',
        '',
    )

    NATURAL_MOUNTAIN_FELL = (
        'natural.mountain.fell',
        '',
    )

    NATURAL_MOUNTAIN_GLACIER = (
        'natural.mountain.glacier',
        '',
    )

    NATURAL_MOUNTAIN_HILL = (
        'natural.mountain.hill',
        '',
    )

    NATURAL_MOUNTAIN_PEAK = (
        'natural.mountain.peak',
        '',
    )

    NATURAL_MOUNTAIN_ROCK = (
        'natural.mountain.rock',
        '',
    )

    NATURAL_MOUNTAIN_VOLCANO = (
        'natural.mountain.volcano',
        '',
    )

    NATURAL_PROTECTED_AREA = (
        'natural.protected_area',
        '',
    )

    NATURAL_SAND = (
        'natural.sand',
        '',
    )

    NATURAL_SAND_DUNE = (
        'natural.sand.dune',
        '',
    )

    NATURAL_WATER = (
        'natural.water',
        '',
    )

    NATURAL_WATER_BAY = (
        'natural.water.bay',
        '',
    )

    NATURAL_WATER_GEYSER = (
        'natural.water.geyser',
        '',
    )

    NATURAL_WATER_HOT_SPRING = (
        'natural.water.hot_spring',
        '',
    )

    NATURAL_WATER_REEF = (
        'natural.water.reef',
        '',
    )

    NATURAL_WATER_RIVER_SYSTEM = (
        'natural.water.river_system',
        '',
    )

    NATURAL_WATER_SEA = (
        'natural.water.sea',
        '',
    )

    NATURAL_WATER_SPRING = (
        'natural.water.spring',
        '',
    )

    NATURAL_WATER_WHITEWATER = (
        'natural.water.whitewater',
        '',
    )

    NATURAL_WETLAND = (
        'natural.wetland',
        '',
    )

    NATIONAL_PARK = (
        'national_park',
        'National parks',
    )

    OFFICE = (
        'office',
        'An office of a business, company, administration, or organization',
    )

    OFFICE_ACCOUNTANT = (
        'office.accountant',
        '',
    )

    OFFICE_ADVERTISING_AGENCY = (
        'office.advertising_agency',
        '',
    )

    OFFICE_ARCHITECT = (
        'office.architect',
        '',
    )

    OFFICE_ASSOCIATION = (
        'office.association',
        '',
    )

    OFFICE_CHARITY = (
        'office.charity',
        '',
    )

    OFFICE_COMPANY = (
        'office.company',
        '',
    )

    OFFICE_CONSULTING = (
        'office.consulting',
        '',
    )

    OFFICE_COWORKING = (
        'office.coworking',
        '',
    )

    OFFICE_DIPLOMATIC = (
        'office.diplomatic',
        '',
    )

    OFFICE_EDUCATIONAL_INSTITUTION = (
        'office.educational_institution',
        '',
    )

    OFFICE_EMPLOYMENT_AGENCY = (
        'office.employment_agency',
        '',
    )

    OFFICE_ENERGY_SUPPLIER = (
        'office.energy_supplier',
        '',
    )

    OFFICE_ESTATE_AGENT = (
        'office.estate_agent',
        '',
    )

    OFFICE_FINANCIAL = (
        'office.financial',
        '',
    )

    OFFICE_FINANCIAL_ADVISOR = (
        'office.financial_advisor',
        '',
    )

    OFFICE_FORESTRY = (
        'office.forestry',
        '',
    )

    OFFICE_FOUNDATION = (
        'office.foundation',
        '',
    )

    OFFICE_GOVERNMENT = (
        'office.government',
        '',
    )

    OFFICE_GOVERNMENT_ADMINISTRATIVE = (
        'office.government.administrative',
        '',
    )

    OFFICE_GOVERNMENT_AGRICULTURE = (
        'office.government.agriculture',
        '',
    )

    OFFICE_GOVERNMENT_CADASTER = (
        'office.government.cadaster',
        '',
    )

    OFFICE_GOVERNMENT_CUSTOMS = (
        'office.government.customs',
        '',
    )

    OFFICE_GOVERNMENT_EDUCATION = (
        'office.government.education',
        '',
    )

    OFFICE_GOVERNMENT_EMBASSY = (
        'office.government.embassy',
        '',
    )

    OFFICE_GOVERNMENT_ENVIRONMENT = (
        'office.government.environment',
        '',
    )

    OFFICE_GOVERNMENT_FORESTRY = (
        'office.government.forestry',
        '',
    )

    OFFICE_GOVERNMENT_HEALTHCARE = (
        'office.government.healthcare',
        '',
    )

    OFFICE_GOVERNMENT_LEGISLATIVE = (
        'office.government.legislative',
        '',
    )

    OFFICE_GOVERNMENT_MIGRATION = (
        'office.government.migration',
        '',
    )

    OFFICE_GOVERNMENT_MINISTRY = (
        'office.government.ministry',
        '',
    )

    OFFICE_GOVERNMENT_PROSECUTOR = (
        'office.government.prosecutor',
        '',
    )

    OFFICE_GOVERNMENT_PUBLIC_SERVICE = (
        'office.government.public_service',
        '',
    )

    OFFICE_GOVERNMENT_REGISTER_OFFICE = (
        'office.government.register_office',
        '',
    )

    OFFICE_GOVERNMENT_SOCIAL_SECURITY = (
        'office.government.social_security',
        '',
    )

    OFFICE_GOVERNMENT_SOCIAL_SERVICES = (
        'office.government.social_services',
        '',
    )

    OFFICE_GOVERNMENT_TAX = (
        'office.government.tax',
        '',
    )

    OFFICE_GOVERNMENT_TRANSPORTATION = (
        'office.government.transportation',
        '',
    )

    OFFICE_INSURANCE = (
        'office.insurance',
        '',
    )

    OFFICE_IT = (
        'office.it',
        '',
    )

    OFFICE_LAWYER = (
        'office.lawyer',
        '',
    )

    OFFICE_LOGISTICS = (
        'office.logistics',
        '',
    )

    OFFICE_NEWSPAPER = (
        'office.newspaper',
        '',
    )

    OFFICE_NON_PROFIT = (
        'office.non_profit',
        '',
    )

    OFFICE_NOTARY = (
        'office.notary',
        '',
    )

    OFFICE_POLITICAL_PARTY = (
        'office.political_party',
        '',
    )

    OFFICE_RELIGION = (
        'office.religion',
        '',
    )

    OFFICE_RESEARCH = (
        'office.research',
        '',
    )

    OFFICE_SECURITY = (
        'office.security',
        '',
    )

    OFFICE_TAX_ADVISOR = (
        'office.tax_advisor',
        '',
    )

    OFFICE_TELECOMMUNICATION = (
        'office.telecommunication',
        '',
    )

    OFFICE_TRAVEL_AGENT = (
        'office.travel_agent',
        '',
    )

    OFFICE_WATER_UTILITY = (
        'office.water_utility',
        '',
    )

    PARKING = (
        'parking',
        'Places where one can park a car',
    )

    PARKING_BICYCLES = (
        'parking.bicycles',
        '',
    )

    PARKING_CARS = (
        'parking.cars',
        '',
    )

    PARKING_CARS_MULTISTOREY = (
        'parking.cars.multistorey',
        '',
    )

    PARKING_CARS_ROOFTOP = (
        'parking.cars.rooftop',
        '',
    )

    PARKING_CARS_SURFACE = (
        'parking.cars.surface',
        '',
    )

    PARKING_CARS_UNDERGROUND = (
        'parking.cars.underground',
        '',
    )

    PARKING_MOTORCYCLE = (
        'parking.motorcycle',
        '',
    )

    PARKING_MULTISTOREY = (
        'parking.multistorey',
        '',
    )

    PARKING_ROOFTOP = (
        'parking.rooftop',
        '',
    )

    PARKING_SURFACE = (
        'parking.surface',
        '',
    )

    PARKING_UNDERGROUND = (
        'parking.underground',
        '',
    )

    PET = (
        'pet',
        'Places that can be interesting for pet owners',
    )

    PET_ANIMAL_BOARDING = (
        'pet.animal_boarding',
        '',
    )

    PET_ANIMAL_SHELTER = (
        'pet.animal_shelter',
        '',
    )

    PET_CREMATORIUM = (
        'pet.crematorium',
        'Crematoria dedicated to pets',
    )

    PET_DOG_PARK = (
        'pet.dog_park',
        '',
    )

    PET_SERVICE = (
        'pet.service',
        '',
    )

    PET_SHOP = (
        'pet.shop',
        '',
    )

    PET_VETERINARY = (
        'pet.veterinary',
        '',
    )

    POWER = (
        'power',
        'Infrastructure related to the generation and distribution of electrical energy',
    )

    POWER_GENERATOR = (
        'power.generator',
        'Facilities where electrical power is generated from various energy sources',
    )

    POWER_GENERATOR_BIOMASS = (
        'power.generator.biomass',
        '',
    )

    POWER_GENERATOR_COAL = (
        'power.generator.coal',
        '',
    )

    POWER_GENERATOR_GAS = (
        'power.generator.gas',
        '',
    )

    POWER_GENERATOR_GEOTHERMAL = (
        'power.generator.geothermal',
        '',
    )

    POWER_GENERATOR_HYDRO = (
        'power.generator.hydro',
        '',
    )

    POWER_GENERATOR_NUCLEAR = (
        'power.generator.nuclear',
        '',
    )

    POWER_GENERATOR_OIL = (
        'power.generator.oil',
        '',
    )

    POWER_GENERATOR_SOLAR = (
        'power.generator.solar',
        '',
    )

    POWER_GENERATOR_WIND = (
        'power.generator.wind',
        '',
    )

    POWER_LINE = (
        'power.line',
        'High-voltage transmission lines for distributing electricity over long distances',
    )

    POWER_MINOR_LINE = (
        'power.minor_line',
        'Smaller power lines for local electricity distribution, often within neighborhoods',
    )

    POWER_PLANT = (
        'power.plant',
        'Industrial facilities where electrical power is generated from various energy sources.',
    )

    POWER_PLANT_BIOMASS = (
        'power.plant.biomass',
        '',
    )

    POWER_PLANT_COAL = (
        'power.plant.coal',
        '',
    )

    POWER_PLANT_GAS = (
        'power.plant.gas',
        '',
    )

    POWER_PLANT_GEOTHERMAL = (
        'power.plant.geothermal',
        '',
    )

    POWER_PLANT_HYDRO = (
        'power.plant.hydro',
        '',
    )

    POWER_PLANT_NUCLEAR = (
        'power.plant.nuclear',
        '',
    )

    POWER_PLANT_OIL = (
        'power.plant.oil',
        '',
    )

    POWER_PLANT_SOLAR = (
        'power.plant.solar',
        '',
    )

    POWER_PLANT_WASTE = (
        'power.plant.waste',
        '',
    )

    POWER_PLANT_WIND = (
        'power.plant.wind',
        '',
    )

    POWER_SUBSTATION = (
        'power.substation',
        'Facilities that transform voltage levels for distribution and transmission of electricity',
    )

    POWER_TRANSFORMER = (
        'power.transformer',
        'Devices within power systems that change the voltage level of electricity for distribution',
    )

    PRODUCTION = (
        'production',
        'Sites and facilities where goods and products are manufactured or processed',
    )

    PRODUCTION_BEEKEEPER = (
        'production.beekeeper',
        '',
    )

    PRODUCTION_BREWERY = (
        'production.brewery',
        'Establishments where beer is produced through the fermentation of ingredients',
    )

    PRODUCTION_CHEESE = (
        'production.cheese',
        'Facilities specialized in the production and aging of various types of cheese',
    )

    PRODUCTION_DISTILLERY = (
        'production.distillery',
        '',
    )

    PRODUCTION_FACTORY = (
        'production.factory',
        'Large industrial buildings where raw materials are transformed into finished goods',
    )

    PRODUCTION_POTTERY = (
        'production.pottery',
        'Workshops or factories where clay products, such as pottery and ceramics, are made',
    )

    PRODUCTION_WINERY = (
        'production.winery',
        'Facilities dedicated to the production of wine, from grape processing to bottling',
    )

    RAILWAY = (
        'railway',
        'Tracks and infrastructure for train transportation and services',
    )

    RAILWAY_CONSTRUCTION = (
        'railway.construction',
        'Railway tracks and infrastructure currently under construction',
    )

    RAILWAY_FUNICULAR = (
        'railway.funicular',
        'Railways on steep slopes using cable traction for uphill and downhill travel',
    )

    RAILWAY_LIGHT_RAIL = (
        'railway.light_rail',
        'Urban rail systems that are lighter and faster than traditional trams',
    )

    RAILWAY_SUBWAY = (
        'railway.subway',
        'Urban, underground railway systems for mass transit',
    )

    RAILWAY_SURFACE = (
        'railway.surface',
        'Railways located at ground level, including most conventional train tracks',
    )

    RAILWAY_TRAIN = (
        'railway.train',
        'Tracks used by conventional overground trains for passenger and freight services',
    )

    RAILWAY_TRAM = (
        'railway.tram',
        'City-based light rail systems running on streets and dedicated lines',
    )

    RAILWAY_UNDERGROUND = (
        'railway.underground',
        'Railways located below the surface, typically in urban areas for mass transit',
    )

    RENTAL = (
        'rental',
        'Places where one can rent things',
    )

    RENTAL_BICYCLE = (
        'rental.bicycle',
        '',
    )

    RENTAL_BOAT = (
        'rental.boat',
        '',
    )

    RENTAL_CAR = (
        'rental.car',
        '',
    )

    RENTAL_SKI = (
        'rental.ski',
        '',
    )

    RENTAL_STORAGE = (
        'rental.storage',
        '',
    )

    SERVICE = (
        'service',
        'Places that provide services to the public',
    )

    SERVICE_AMBULANCE_STATION = (
        'service.ambulance_station',
        'Base for ambulances and emergency medical response teams',
    )

    SERVICE_ADVERTISING = (
        'service.advertising',
        '',
    )

    SERVICE_ADVERTISING_BILLBOARD = (
        'service.advertising.billboard',
        '',
    )

    SERVICE_ADVERTISING_COLUMN = (
        'service.advertising.column',
        '',
    )

    SERVICE_BEAUTY = (
        'service.beauty',
        '',
    )

    SERVICE_BEAUTY_HAIRDRESSER = (
        'service.beauty.hairdresser',
        '',
    )

    SERVICE_BEAUTY_MASSAGE = (
        'service.beauty.massage',
        '',
    )

    SERVICE_BEAUTY_SPA = (
        'service.beauty.spa',
        '',
    )

    SERVICE_BEAUTY_TANNING_SALON = (
        'service.beauty.tanning_salon',
        '',
    )

    SERVICE_BEAUTY_TATTOO = (
        'service.beauty.tattoo',
        '',
    )

    SERVICE_BLACKSMITH = (
        'service.blacksmith',
        '',
    )

    SERVICE_BOOKMAKER = (
        'service.bookmaker',
        '',
    )

    SERVICE_CARPENTER = (
        'service.carpenter',
        '',
    )

    SERVICE_CHIMNEY_SWEEPER = (
        'service.chimney_sweeper',
        '',
    )

    SERVICE_CLEANING = (
        'service.cleaning',
        '',
    )

    SERVICE_CLEANING_DRY_CLEANING = (
        'service.cleaning.dry_cleaning',
        '',
    )

    SERVICE_CLEANING_LAUNDRY = (
        'service.cleaning.laundry',
        '',
    )

    SERVICE_CLEANING_LAVOIR = (
        'service.cleaning.lavoir',
        '',
    )

    SERVICE_CREMATORIUM = (
        'service.crematorium',
        'Human and pet cremation services',
    )

    SERVICE_CREMATORIUM_HUMAN = (
        'service.crematorium.human',
        'Cremation services for humans',
    )

    SERVICE_CREMATORIUM_PET = (
        'service.crematorium.pet',
        'Cremation services dedicated to pets',
    )

    SERVICE_ELECTRICIAN = (
        'service.electrician',
        '',
    )

    SERVICE_ESTATE_AGENT = (
        'service.estate_agent',
        '',
    )

    SERVICE_FINANCIAL = (
        'service.financial',
        '',
    )

    SERVICE_FINANCIAL_ATM = (
        'service.financial.atm',
        '',
    )

    SERVICE_FINANCIAL_BANK = (
        'service.financial.bank',
        '',
    )

    SERVICE_FINANCIAL_BUREAU_DE_CHANGE = (
        'service.financial.bureau_de_change',
        '',
    )

    SERVICE_FINANCIAL_MONEY_LENDER = (
        'service.financial.money_lender',
        '',
    )

    SERVICE_FINANCIAL_MONEY_TRANSFER = (
        'service.financial.money_transfer',
        '',
    )

    SERVICE_FINANCIAL_PAYMENT_TERMINAL = (
        'service.financial.payment_terminal',
        '',
    )

    SERVICE_FIRE_STATION = (
        'service.fire_station',
        'Facility where fire service personnel and equipment are based',
    )

    SERVICE_FUNERAL_DIRECTORS = (
        'service.funeral_directors',
        '',
    )

    SERVICE_FUNERAL_HALL = (
        'service.funeral_hall',
        'Funeral halls and chapels',
    )

    SERVICE_KEY_CUTTER = (
        'service.key_cutter',
        '',
    )

    SERVICE_LOCKSMITH = (
        'service.locksmith',
        '',
    )

    SERVICE_METAL_CONSTRUCTION = (
        'service.metal_construction',
        '',
    )

    SERVICE_MORTUARY = (
        'service.mortuary',
        'Mortuaries and morgues',
    )

    SERVICE_PHOTOGRAPHER = (
        'service.photographer',
        '',
    )

    SERVICE_PLACE_OF_MOURNING = (
        'service.place_of_mourning',
        'Dedicated mourning or wake facilities',
    )

    SERVICE_POLICE = (
        'service.police',
        '',
    )

    SERVICE_POST = (
        'service.post',
        '',
    )

    SERVICE_POST_BOX = (
        'service.post.box',
        '',
    )

    SERVICE_POST_OFFICE = (
        'service.post.office',
        '',
    )

    SERVICE_POST_PARCEL_LOCKER = (
        'service.post.parcel_locker',
        '',
    )

    SERVICE_RECYCLING = (
        'service.recycling',
        '',
    )

    SERVICE_RECYCLING_BIN = (
        'service.recycling.bin',
        '',
    )

    SERVICE_RECYCLING_CENTRE = (
        'service.recycling.centre',
        '',
    )

    SERVICE_RECYCLING_CONTAINER = (
        'service.recycling.container',
        '',
    )

    SERVICE_SHOEMAKER = (
        'service.shoemaker',
        '',
    )

    SERVICE_SOCIAL_FACILITY = (
        'service.social_facility',
        'Places that provide social services, such as counseling, support groups, and other '
        'assistance to people in need, often run by government or non-profit organizations',
    )

    SERVICE_SOCIAL_FACILITY_CLOTHERS = (
        'service.social_facility.clothers',
        '',
    )

    SERVICE_SOCIAL_FACILITY_DAY_CARE = (
        'service.social_facility.day_care',
        '',
    )

    SERVICE_SOCIAL_FACILITY_FOOD = (
        'service.social_facility.food',
        '',
    )

    SERVICE_SOCIAL_FACILITY_NURSING_HOME = (
        'service.social_facility.nursing_home',
        '',
    )

    SERVICE_SOCIAL_FACILITY_RETIREMENT_HOME = (
        'service.social_facility.retirement_home',
        '',
    )

    SERVICE_SOCIAL_FACILITY_SHELTER = (
        'service.social_facility.shelter',
        '',
    )

    SERVICE_TAILOR = (
        'service.tailor',
        '',
    )

    SERVICE_TAXI = (
        'service.taxi',
        '',
    )

    SERVICE_TRAVEL_AGENCY = (
        'service.travel_agency',
        '',
    )

    SERVICE_VEHICLE = (
        'service.vehicle',
        '',
    )

    SERVICE_VEHICLE_CAR_WASH = (
        'service.vehicle.car_wash',
        '',
    )

    SERVICE_VEHICLE_CHARGING_STATION = (
        'service.vehicle.charging_station',
        '',
    )

    SERVICE_VEHICLE_FUEL = (
        'service.vehicle.fuel',
        '',
    )

    SERVICE_VEHICLE_REPAIR = (
        'service.vehicle.repair',
        '',
    )

    SERVICE_VEHICLE_REPAIR_CAR = (
        'service.vehicle.repair.car',
        '',
    )

    SERVICE_VEHICLE_REPAIR_MOTORCYCLE = (
        'service.vehicle.repair.motorcycle',
        '',
    )

    SERVICE_WATCHMAKER = (
        'service.watchmaker',
        '',
    )

    TOURISM = (
        'tourism',
        'Places that can be interesting for tourists',
    )

    TOURISM_ATTRACTION = (
        'tourism.attraction',
        '',
    )

    TOURISM_ATTRACTION_ARTWORK = (
        'tourism.attraction.artwork',
        '',
    )

    TOURISM_ATTRACTION_ARTWORK_MURAL = (
        'tourism.attraction.artwork.mural',
        '',
    )

    TOURISM_ATTRACTION_ARTWORK_SCULPTURE = (
        'tourism.attraction.artwork.sculpture',
        '',
    )

    TOURISM_ATTRACTION_ARTWORK_STATUE = (
        'tourism.attraction.artwork.statue',
        '',
    )

    TOURISM_ATTRACTION_CLOCK = (
        'tourism.attraction.clock',
        '',
    )

    TOURISM_ATTRACTION_FOUNTAIN = (
        'tourism.attraction.fountain',
        '',
    )

    TOURISM_ATTRACTION_VIEWPOINT = (
        'tourism.attraction.viewpoint',
        '',
    )

    TOURISM_INFORMATION = (
        'tourism.information',
        '',
    )

    TOURISM_INFORMATION_MAP = (
        'tourism.information.map',
        '',
    )

    TOURISM_INFORMATION_OFFICE = (
        'tourism.information.office',
        '',
    )

    TOURISM_INFORMATION_RANGER_STATION = (
        'tourism.information.ranger_station',
        '',
    )

    TOURISM_SIGHTS = (
        'tourism.sights',
        '',
    )

    TOURISM_SIGHTS_ARCHAEOLOGICAL_SITE = (
        'tourism.sights.archaeological_site',
        '',
    )

    TOURISM_SIGHTS_BATTLEFIELD = (
        'tourism.sights.battlefield',
        '',
    )

    TOURISM_SIGHTS_BUILDING = (
        'tourism.sights.building',
        '',
    )

    TOURISM_SIGHTS_BRIDGE = (
        'tourism.sights.bridge',
        '',
    )

    TOURISM_SIGHTS_CASTLE = (
        'tourism.sights.castle',
        '',
    )

    TOURISM_SIGHTS_CITY_GATE = (
        'tourism.sights.city_gate',
        '',
    )

    TOURISM_SIGHTS_CITY_HALL = (
        'tourism.sights.city_hall',
        '',
    )

    TOURISM_SIGHTS_CONFERENCE_CENTRE = (
        'tourism.sights.conference_centre',
        '',
    )

    TOURISM_SIGHTS_FORT = (
        'tourism.sights.fort',
        '',
    )

    TOURISM_SIGHTS_LIGHTHOUSE = (
        'tourism.sights.lighthouse',
        '',
    )

    TOURISM_SIGHTS_MANOR = (
        'tourism.sights.manor',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL = (
        'tourism.sights.memorial',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_AIRCRAFT = (
        'tourism.sights.memorial.aircraft',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_BOUNDARY_STONE = (
        'tourism.sights.memorial.boundary_stone',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_LOCOMOTIVE = (
        'tourism.sights.memorial.locomotive',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_MILESTONE = (
        'tourism.sights.memorial.milestone',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_MONUMENT = (
        'tourism.sights.memorial.monument',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_NECROPOLIS = (
        'tourism.sights.memorial.necropolis',
        'Historical necropolises',
    )

    TOURISM_SIGHTS_MEMORIAL_PILLORY = (
        'tourism.sights.memorial.pillory',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_RAILWAY_CAR = (
        'tourism.sights.memorial.railway_car',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_SHIP = (
        'tourism.sights.memorial.ship',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_TANK = (
        'tourism.sights.memorial.tank',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_TOMB = (
        'tourism.sights.memorial.tomb',
        '',
    )

    TOURISM_SIGHTS_MEMORIAL_TUMULUS = (
        'tourism.sights.memorial.tumulus',
        'Burial mounds and tumuli',
    )

    TOURISM_SIGHTS_MEMORIAL_WAYSIDE_CROSS = (
        'tourism.sights.memorial.wayside_cross',
        '',
    )

    TOURISM_SIGHTS_MINE = (
        'tourism.sights.mine',
        '',
    )

    TOURISM_SIGHTS_MONASTERY = (
        'tourism.sights.monastery',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP = (
        'tourism.sights.place_of_worship',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_CATHEDRAL = (
        'tourism.sights.place_of_worship.cathedral',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_CHAPEL = (
        'tourism.sights.place_of_worship.chapel',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_CHURCH = (
        'tourism.sights.place_of_worship.church',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_MOSQUE = (
        'tourism.sights.place_of_worship.mosque',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_SHRINE = (
        'tourism.sights.place_of_worship.shrine',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_SYNAGOGUE = (
        'tourism.sights.place_of_worship.synagogue',
        '',
    )

    TOURISM_SIGHTS_PLACE_OF_WORSHIP_TEMPLE = (
        'tourism.sights.place_of_worship.temple',
        '',
    )

    TOURISM_SIGHTS_RUINES = (
        'tourism.sights.ruines',
        '',
    )

    TOURISM_SIGHTS_TOWER = (
        'tourism.sights.tower',
        '',
    )

    TOURISM_SIGHTS_WINDMILL = (
        'tourism.sights.windmill',
        '',
    )

    TOURISM_SIGHTS_WRECK = (
        'tourism.sights.wreck',
        '',
    )

    RELIGION = (
        'religion',
        'Places that are associated with a particular faith or religious institution, such as '
        'churches, mosques, synagogues, temples, and other places of worship',
    )

    RELIGION_PLACE_OF_WORSHIP = (
        'religion.place_of_worship',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_BUDDHISM = (
        'religion.place_of_worship.buddhism',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_CHRISTIANITY = (
        'religion.place_of_worship.christianity',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_HINDUISM = (
        'religion.place_of_worship.hinduism',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_ISLAM = (
        'religion.place_of_worship.islam',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_JUDAISM = (
        'religion.place_of_worship.judaism',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_MULTIFAITH = (
        'religion.place_of_worship.multifaith',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_SHINTO = (
        'religion.place_of_worship.shinto',
        '',
    )

    RELIGION_PLACE_OF_WORSHIP_SIKHISM = (
        'religion.place_of_worship.sikhism',
        '',
    )

    CAMPING = (
        'camping',
        'Places that provide outdoor activity including overnight stay',
    )

    CAMPING_CAMP_PITCH = (
        'camping.camp_pitch',
        '',
    )

    CAMPING_CAMP_SITE = (
        'camping.camp_site',
        '',
    )

    CAMPING_CARAVAN_SITE = (
        'camping.caravan_site',
        '',
    )

    CAMPING_SUMMER_CAMP = (
        'camping.summer_camp',
        '',
    )

    AMENITY = (
        'amenity',
        'Small amenities, that can be useful in different situations',
    )

    AMENITY_DRINKING_WATER = (
        'amenity.drinking_water',
        '',
    )

    AMENITY_GIVE_BOX = (
        'amenity.give_box',
        'Places where people can donate or leave items for others to take for free, often found in '
        'public spaces or community centers',
    )

    AMENITY_GIVE_BOX_BOOKS = (
        'amenity.give_box.books',
        '',
    )

    AMENITY_GIVE_BOX_FOOD = (
        'amenity.give_box.food',
        '',
    )

    AMENITY_TOILET = (
        'amenity.toilet',
        '',
    )

    AMENITY_TOILET_CHANGING_TABLE = (
        'amenity.toilet.changing_table',
        '',
    )

    BEACH = (
        'beach',
        'A shore of a body of water covered by sand, gravel, or larger rock fragments',
    )

    BEACH_BEACH_RESORT = (
        'beach.beach_resort',
        '',
    )

    ADULT = (
        'adult',
        'Places that provide entertainments for adults, sometimes with a sexual context',
    )

    ADULT_ADULT_GAMING_CENTRE = (
        'adult.adult_gaming_centre',
        '',
    )

    ADULT_BROTHEL = (
        'adult.brothel',
        '',
    )

    ADULT_CASINO = (
        'adult.casino',
        '',
    )

    ADULT_NIGHTCLUB = (
        'adult.nightclub',
        '',
    )

    ADULT_STRIPCLUB = (
        'adult.stripclub',
        '',
    )

    ADULT_SWINGERCLUB = (
        'adult.swingerclub',
        '',
    )

    BUILDING = (
        'building',
        'Stand alone buildings and places',
    )

    BUILDING_ACCOMMODATION = (
        'building.accommodation',
        '',
    )

    BUILDING_CATERING = (
        'building.catering',
        '',
    )

    BUILDING_COLLEGE = (
        'building.college',
        '',
    )

    BUILDING_COMMERCIAL = (
        'building.commercial',
        '',
    )

    BUILDING_DORMITORY = (
        'building.dormitory',
        '',
    )

    BUILDING_DRIVING_SCHOOL = (
        'building.driving_school',
        '',
    )

    BUILDING_ENTERTAINMENT = (
        'building.entertainment',
        '',
    )

    BUILDING_FACILITY = (
        'building.facility',
        '',
    )

    BUILDING_GARAGE = (
        'building.garage',
        '',
    )

    BUILDING_HEALTHCARE = (
        'building.healthcare',
        '',
    )

    BUILDING_HISTORIC = (
        'building.historic',
        '',
    )

    BUILDING_HOLIDAY_HOUSE = (
        'building.holiday_house',
        '',
    )

    BUILDING_INDUSTRIAL = (
        'building.industrial',
        '',
    )

    BUILDING_KINDERGARTEN = (
        'building.kindergarten',
        '',
    )

    BUILDING_MILITARY = (
        'building.military',
        '',
    )

    BUILDING_OFFICE = (
        'building.office',
        '',
    )

    BUILDING_PARKING = (
        'building.parking',
        '',
    )

    BUILDING_PLACE_OF_WORSHIP = (
        'building.place_of_worship',
        '',
    )

    BUILDING_PRISON = (
        'building.prison',
        '',
    )

    BUILDING_PUBLIC_AND_CIVIL = (
        'building.public_and_civil',
        '',
    )

    BUILDING_RESIDENTIAL = (
        'building.residential',
        '',
    )

    BUILDING_SCHOOL = (
        'building.school',
        '',
    )

    BUILDING_SERVICE = (
        'building.service',
        '',
    )

    BUILDING_SPA = (
        'building.spa',
        '',
    )

    BUILDING_SPORT = (
        'building.sport',
        '',
    )

    BUILDING_TOILET = (
        'building.toilet',
        '',
    )

    BUILDING_TOURISM = (
        'building.tourism',
        '',
    )

    BUILDING_TRANSPORTATION = (
        'building.transportation',
        '',
    )

    BUILDING_UNIVERSITY = (
        'building.university',
        '',
    )

    SKI = (
        'ski',
        'Infrastructure objects related to downhill skiing sport kinds',
    )

    SKI_LIFT = (
        'ski.lift',
        '',
    )

    SKI_LIFT_CABLE_CAR = (
        'ski.lift.cable_car',
        '',
    )

    SKI_LIFT_CHAIR_LIFT = (
        'ski.lift.chair_lift',
        '',
    )

    SKI_LIFT_GONDOLA = (
        'ski.lift.gondola',
        '',
    )

    SKI_LIFT_MAGIC_CARPET = (
        'ski.lift.magic_carpet',
        '',
    )

    SKI_LIFT_MIXED_LIFT = (
        'ski.lift.mixed_lift',
        '',
    )

    SKI_LIFT_TOW_LINE = (
        'ski.lift.tow_line',
        '',
    )

    SPORT = (
        'sport',
        'Infrastructure objects related to different sport kinds',
    )

    SPORT_DIVE_CENTRE = (
        'sport.dive_centre',
        '',
    )

    SPORT_DOJO = (
        'sport.dojo',
        '',
    )

    SPORT_FISHING = (
        'sport.fishing',
        '',
    )

    SPORT_FITNESS = (
        'sport.fitness',
        '',
    )

    SPORT_FITNESS_FITNESS_CENTRE = (
        'sport.fitness.fitness_centre',
        '',
    )

    SPORT_FITNESS_FITNESS_STATION = (
        'sport.fitness.fitness_station',
        '',
    )

    SPORT_FITNESS_GYM = (
        'sport.fitness.gym',
        '',
    )

    SPORT_GOLF_COURSE = (
        'sport.golf_course',
        '',
    )

    SPORT_HORSE_RIDING = (
        'sport.horse_riding',
        '',
    )

    SPORT_ICE_RINK = (
        'sport.ice_rink',
        '',
    )

    SPORT_PITCH = (
        'sport.pitch',
        '',
    )

    SPORT_SHOOTING = (
        'sport.shooting',
        '',
    )

    SPORT_SKATEBOARD = (
        'sport.skateboard',
        '',
    )

    SPORT_SPORTS_CENTRE = (
        'sport.sports_centre',
        '',
    )

    SPORT_SPORTS_HALL = (
        'sport.sports_hall',
        '',
    )

    SPORT_STADIUM = (
        'sport.stadium',
        '',
    )

    SPORT_SWIMMING_POOL = (
        'sport.swimming_pool',
        '',
    )

    SPORT_TRACK = (
        'sport.track',
        '',
    )

    PUBLIC_TRANSPORT = (
        'public_transport',
        'Public transport stations and stops',
    )

    PUBLIC_TRANSPORT_AERIALWAY = (
        'public_transport.aerialway',
        '',
    )

    PUBLIC_TRANSPORT_BUS = (
        'public_transport.bus',
        '',
    )

    PUBLIC_TRANSPORT_FERRY = (
        'public_transport.ferry',
        '',
    )

    PUBLIC_TRANSPORT_LIGHT_RAIL = (
        'public_transport.light_rail',
        '',
    )

    PUBLIC_TRANSPORT_MONORAIL = (
        'public_transport.monorail',
        '',
    )

    PUBLIC_TRANSPORT_PLATFORM = (
        'public_transport.platform',
        '',
    )

    PUBLIC_TRANSPORT_SUBWAY = (
        'public_transport.subway',
        '',
    )

    PUBLIC_TRANSPORT_SUBWAY_ENTRANCE = (
        'public_transport.subway.entrance',
        '',
    )

    PUBLIC_TRANSPORT_TRAIN = (
        'public_transport.train',
        '',
    )

    PUBLIC_TRANSPORT_TRAM = (
        'public_transport.tram',
        '',
    )

    ADMINISTRATIVE = (
        'administrative',
        'Administrative boundary',
    )

    ADMINISTRATIVE_CITY_LEVEL = (
        'administrative.city_level',
        '',
    )

    ADMINISTRATIVE_CONTINENT_LEVEL = (
        'administrative.continent_level',
        '',
    )

    ADMINISTRATIVE_COUNTRY_LEVEL = (
        'administrative.country_level',
        '',
    )

    ADMINISTRATIVE_COUNTRY_PART_LEVEL = (
        'administrative.country_part_level',
        '',
    )

    ADMINISTRATIVE_COUNTY_LEVEL = (
        'administrative.county_level',
        '',
    )

    ADMINISTRATIVE_DISTRICT_LEVEL = (
        'administrative.district_level',
        '',
    )

    ADMINISTRATIVE_NEIGHBOURHOOD_LEVEL = (
        'administrative.neighbourhood_level',
        '',
    )

    ADMINISTRATIVE_STATE_LEVEL = (
        'administrative.state_level',
        '',
    )

    ADMINISTRATIVE_SUBURB_LEVEL = (
        'administrative.suburb_level',
        '',
    )

    POSTAL_CODE = (
        'postal_code',
        'Postcode boundary',
    )

    POLITICAL = (
        'political',
        'Political boundary',
    )

    LOW_EMISSION_ZONE = (
        'low_emission_zone',
        'Low emission zone',
    )

    POPULATED_PLACE = (
        'populated_place',
        'Place where people live',
    )

    POPULATED_PLACE_ALLOTMENTS = (
        'populated_place.allotments',
        '',
    )

    POPULATED_PLACE_BOROUGH = (
        'populated_place.borough',
        '',
    )

    POPULATED_PLACE_CITY = (
        'populated_place.city',
        '',
    )

    POPULATED_PLACE_CITY_BLOCK = (
        'populated_place.city_block',
        '',
    )

    POPULATED_PLACE_COUNTY = (
        'populated_place.county',
        '',
    )

    POPULATED_PLACE_DISTRICT = (
        'populated_place.district',
        '',
    )

    POPULATED_PLACE_HAMLET = (
        'populated_place.hamlet',
        '',
    )

    POPULATED_PLACE_MUNICIPALITY = (
        'populated_place.municipality',
        '',
    )

    POPULATED_PLACE_NEIGHBOURHOOD = (
        'populated_place.neighbourhood',
        '',
    )

    POPULATED_PLACE_PROVINCE = (
        'populated_place.province',
        '',
    )

    POPULATED_PLACE_QUARTER = (
        'populated_place.quarter',
        '',
    )

    POPULATED_PLACE_REGION = (
        'populated_place.region',
        '',
    )

    POPULATED_PLACE_STATE = (
        'populated_place.state',
        '',
    )

    POPULATED_PLACE_SUBDISTRICT = (
        'populated_place.subdistrict',
        '',
    )

    POPULATED_PLACE_SUBURB = (
        'populated_place.suburb',
        '',
    )

    POPULATED_PLACE_TOWN = (
        'populated_place.town',
        '',
    )

    POPULATED_PLACE_TOWNSHIP = (
        'populated_place.township',
        '',
    )

    POPULATED_PLACE_UNPOPULATED_LOCALITY = (
        'populated_place.unpopulated_locality',
        '',
    )

    POPULATED_PLACE_VILLAGE = (
        'populated_place.village',
        '',
    )

    MEMORIAL = (
        'memorial',
        'Generic memorial points of interest',
    )

    MEMORIAL_BUDDHIST = (
        'memorial.buddhist',
        'Buddhist memorial sites',
    )

    MEMORIAL_CEMETERY = (
        'memorial.cemetery',
        'Cemeteries and burial complexes',
    )

    MEMORIAL_CEMETERY_SECTOR = (
        'memorial.cemetery.sector',
        'Individual sectors inside large cemeteries',
    )

    MEMORIAL_CHRISTIAN = (
        'memorial.christian',
        'Christian memorial sites',
    )

    MEMORIAL_CHRISTIAN_CATHOLIC = (
        'memorial.christian.catholic',
        'Catholic memorial sites',
    )

    MEMORIAL_CHRISTIAN_ORTHODOX = (
        'memorial.christian.orthodox',
        'Orthodox memorial sites',
    )

    MEMORIAL_CHRISTIAN_PROTESTANT = (
        'memorial.christian.protestant',
        'Protestant memorial sites',
    )

    MEMORIAL_GRAVEYARD = (
        'memorial.graveyard',
        'Graveyards without formal boundaries',
    )

    MEMORIAL_HINDU = (
        'memorial.hindu',
        'Hindu memorial sites',
    )

    MEMORIAL_JEWISH = (
        'memorial.jewish',
        'Jewish memorial grounds',
    )

    MEMORIAL_MUSLIM = (
        'memorial.muslim',
        'Muslim memorial grounds',
    )
