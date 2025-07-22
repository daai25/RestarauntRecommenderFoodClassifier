food_to_cuisines = {
    "baklava": ["albanian", "armenian", "azerbaijani", "cypriot", "greek", "iranian", "iraqi", "jordanian", "lebanese", "syrian", "turkish"],
    "beef_carpaccio": ["italian"],
    "beef_tartare": ["belgian", "french"],
    "beet_salad": ["russian", "polish", "ukrainian", "belarusian", "german"],
    "beignets": ["french", "american"],
    "bibimbap": ["south_korean"],
    "breakfast_burrito": ["american", "mexican"],
    "bruschetta": ["italian"],
    "caesar_salad": ["mexican", "american"],
    "cannoli": ["italian"],
    "caprese_salad": ["italian"],
    "ceviche": ["peruvian", "ecuadorean", "mexican", "chilean", "colombian"],
    "cheese_plate": ["french", "swiss", "italian", "dutch"],
    "cheesecake": ["american", "german", "greek", "polish"],
    "chicken_curry": ["indian", "pakistani", "bangladeshi", "sri_lankan", "nepalese", "malaysian"],
    "chicken_quesadilla": ["mexican"],
    "chicken_wings": ["american"],
    "chocolate_cake": ["american", "german", "austrian", "swiss"],
    "chocolate_mousse": ["french"],
    "clam_chowder": ["american", "british"],
    "club_sandwich": ["american"],
    "crab_cakes": ["american"],
    "creme_brulee": ["french"],
    "croque_madame": ["french"],
    "dumplings": ["chinese", "japanese", "south_korean", "north_korean", "mongolian", "nepalese", "russian", "polish", "ukrainian"],
    "edamame": ["japanese"],
    "eggs_benedict": ["american"],
    "escargots": ["french"],
    "falafel": ["egyptian", "israeli", "jordanian", "lebanese", "syrian", "yemeni"],
    "filet_mignon": ["french", "american"],
    "fish_and_chips": ["british", "australian", "new_zealander"],
    "foie_gras": ["french"],
    "french_fries": ["belgian", "french", "american"],
    "french_onion_soup": ["french"],
    "french_toast": ["french", "american"],
    "fried_calamari": ["italian", "greek", "spanish", "portuguese"],
    "fried_rice": ["chinese", "indonesian", "filipino", "thai", "vietnamese"],
    "garlic_bread": ["italian", "american"],
    "gnocchi": ["italian"],
    "greek_salad": ["greek"],
    "grilled_cheese_sandwich": ["american", "british", "canadian"],
    "grilled_salmon": ["norwegian", "american", "canadian", "japanese"],
    "guacamole": ["mexican"],
    "gyoza": ["japanese", "chinese"],
    "hamburger": ["american", "german"],
    "hot_dog": ["american", "german"],
    "huevos_rancheros": ["mexican"],
    "hummus": ["egyptian", "israeli", "jordanian", "lebanese", "syrian", "yemeni"],
    "lasagna": ["italian"],
    "lobster_bisque": ["french"],
    "macaroni_and_cheese": ["american", "british"],
    "miso_soup": ["japanese"],
    "mussels": ["belgian", "french", "spanish", "dutch"],
    "nachos": ["mexican"],
    "omelette": ["french", "american"],
    "onion_rings": ["american"],
    "pad_thai": ["thai"],
    "paella": ["spanish"],
    "pancakes": ["american", "dutch", "british", "russian", "french"],
    "panna_cotta": ["italian"],
    "peking_duck": ["chinese"],
    "pho": ["vietnamese"],
    "pizza": ["italian", "american"],
    "pork_chop": ["american", "german", "austrian", "chinese"],
    "poutine": ["canadian"],
    "pulled_pork_sandwich": ["american"],
    "ramen": ["japanese"],
    "ravioli": ["italian"],
    "risotto": ["italian"],
    "samosa": ["indian", "pakistani", "nepalese", "bangladeshi"],
    "sashimi": ["japanese"],
    "scallops": ["french", "american", "japanese"],
    "seaweed_salad": ["japanese", "south_korean"],
    "shrimp_and_grits": ["american"],
    "spaghetti_bolognese": ["italian"],
    "spring_rolls": ["chinese", "vietnamese", "filipino", "thai"],
    "steak": ["american", "argentine", "brazilian", "australian", "british"],
    "sushi": ["japanese"],
    "tacos": ["mexican"],
    "takoyaki": ["japanese"],
    "tiramisu": ["italian"],
    "waffles": ["belgian", "american"]
}

'''print(len(food_to_cuisines))

cuisine_count = dict()
cuisine_set = set()
mapping_sum = 0
for food in food_to_cuisines:
    mapping_sum += len(food_to_cuisines[food])
    for cuisine in food_to_cuisines[food]:
        if cuisine not in cuisine_count:
            cuisine_count[cuisine] = 1
            cuisine_set.add(cuisine)
        else:
            cuisine_count[cuisine] += 1

print(cuisine_count)
#for cuisine in cuisine_set:
#    print(cuisine)
print(f"Number of Mappings: {mapping_sum}")

def extra_dumb_sort(dict):
    cuisine_list = list()
    for cuisine in dict:
        cuisine_list.append([cuisine, dict[cuisine]])
    for i in range(len(cuisine_list)):
        for j in range(i + 1, len(cuisine_list)):
            if cuisine_list[i][1] > cuisine_list[j][1]:
                temp = cuisine_list[i]
                cuisine_list[i] = cuisine_list[j]
                cuisine_list[j] = temp
    return cuisine_list

cuisine_list = extra_dumb_sort(cuisine_count)
for item in cuisine_list:
    print(f"{item[0]}: {item[1]}")'''
