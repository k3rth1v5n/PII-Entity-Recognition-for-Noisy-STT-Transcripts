# # generate_dataset_mixed_noise.py
# # Generates train.jsonl (800 samples) and dev.jsonl (150 samples)
# # Mixed A/B/C noise levels, mixed India + global entities, correct character spans.

# import json
# import random
# import datetime

# random.seed(42)

# # ----------------------------
# # Constants & resource lists
# # ----------------------------
# DIGIT_WORDS = {
#     "0": ["zero", "oh"],
#     "1": ["one"],
#     "2": ["two"],
#     "3": ["three"],
#     "4": ["four"],
#     "5": ["five"],
#     "6": ["six"],
#     "7": ["seven"],
#     "8": ["eight"],
#     "9": ["nine"]
# }

# INDIAN_CITIES = [
#     "chennai", "mumbai", "delhi", "bangalore", "kolkata",
#     "hyderabad", "pune", "ahmedabad", "lucknow", "kochi", "vadodara"
# ]

# GLOBAL_CITIES = [
#     "new york", "san francisco", "london", "paris", "tokyo",
#     "sydney", "singapore", "dubai", "berlin", "toronto"
# ]

# CITIES = INDIAN_CITIES + GLOBAL_CITIES

# LOCATIONS = [
#     "marina beach", "central park", "marine drive", "charminar",
#     "india gate", "golden gate bridge", "hyde park", "times square",
#     "victoria harbor", "burj khalifa"
# ]

# FIRST_NAMES = [
#     "ramesh", "keerthi", "arjun", "rahul", "pooja", "sanjana",
#     "alex", "john", "maria", "li", "yuki", "fatima"
# ]
# LAST_NAMES = [
#     "sharma", "vasan", "reddy", "singh", "kumar", "nair",
#     "williams", "garcia", "chen", "sato", "khan"
# ]

# EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "iitm.ac.in", "example.org"]

# # Templates (template words are safe to mutate by noise; entity text stays intact)
# TEMPLATES = [
#     ("PHONE",  "call me on {entity}"),
#     ("CREDIT_CARD", "my credit card number is {entity}"),
#     ("EMAIL",  "my email is {entity}"),
#     ("PERSON_NAME", "my name is {entity}"),
#     ("DATE", "the date of birth is {entity}"),
#     ("CITY", "i live in {entity}"),
#     ("LOCATION", "i am at {entity}"),
# ]

# # ----------------------------
# # Entity generators
# # ----------------------------
# def make_spoken_digits(digits: str):
#     # digits: string of digits, returns e.g. "nine eight seven six"
#     out = []
#     for d in digits:
#         # sometimes use digit word, sometimes the digit char
#         if random.random() < 0.7:
#             out.append(random.choice(DIGIT_WORDS[d]))
#         else:
#             out.append(d)
#     # occasionally insert "double" or "triple" patterns for repeated digits
#     if random.random() < 0.12:
#         # find any repeated pair and replace "x x" -> "double x"
#         for digit in set(digits):
#             pat = f"{digit} {digit}"
#             joined = " ".join(out)
#             if pat in joined:
#                 joined = joined.replace(pat, f"double {digit}", 1)
#                 return joined
#     return " ".join(out)

# def gen_phone():
#     # produce a variety of phone forms:
#     style = random.choice(["spoken_10","digits_10","grouped_5_5","plus91_spoken","mixed"])
#     if style == "spoken_10":
#         return make_spoken_digits("".join(str(random.randint(0,9)) for _ in range(10)))
#     if style == "digits_10":
#         return " ".join(str(random.randint(0,9)) for _ in range(10))
#     if style == "grouped_5_5":
#         a = "".join(str(random.randint(0,9)) for _ in range(5))
#         b = "".join(str(random.randint(0,9)) for _ in range(5))
#         return f"{a} {b}"
#     if style == "plus91_spoken":
#         num = "".join(str(random.randint(0,9)) for _ in range(10))
#         return "+91 " + make_spoken_digits(num)
#     return make_spoken_digits("".join(str(random.randint(0,9)) for _ in range(10)))

# def gen_credit_card():
#     # either spoken groups or digits with spaces/hyphens
#     digits = "".join(str(random.randint(0,9)) for _ in range(16))
#     if random.random() < 0.5:
#         # spoken groups "four two four two ..."
#         groups = [digits[i:i+4] for i in range(0,16,4)]
#         spoken_groups = []
#         for g in groups:
#             spoken_groups.append(" ".join(random.choice(DIGIT_WORDS[d]) if random.random()<0.85 else d for d in g))
#         return " ".join(spoken_groups)
#     else:
#         sep = random.choice([" ", "-", ""])
#         if sep == "":
#             return digits
#         groups = [digits[i:i+4] for i in range(0,16,4)]
#         return sep.join(groups)

# def gen_email():
#     # produce emails in spoken form: "ramesh dot sharma at gmail dot com" or classic
#     name = random.choice(FIRST_NAMES)
#     if random.random() < 0.4:
#         # spoken
#         name2 = random.choice(LAST_NAMES)
#         domain = random.choice(EMAIL_DOMAINS)
#         parts = domain.split(".")
#         spoken_domain = " dot ".join(parts)
#         return f"{name} dot {name2} at {spoken_domain}"
#     else:
#         # normal-ish
#         local = name + str(random.randint(1,999))
#         dom = random.choice(EMAIL_DOMAINS)
#         return f"{local}@{dom}"

# def gen_person_name():
#     # sometimes single name, sometimes first + last
#     if random.random() < 0.7:
#         return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
#     else:
#         return random.choice(FIRST_NAMES)

# def gen_date():
#     # produce spoken date variants
#     day = random.randint(1,28)
#     month = random.choice([
#         "january","february","march","april","may","june",
#         "july","august","september","october","november","december"
#     ])
#     year_style = random.choice(["two_word","digits","spoken_year"])
#     if year_style == "two_word":
#         year = random.choice(["twenty twenty","twenty twenty one","twenty twenty four"])
#         return f"{day} {month} {year}"
#     if year_style == "digits":
#         y = random.choice([1990,2000,2001,2019,2020,2024])
#         return f"{day}/{random.randint(1,12)}/{y}"
#     return f"{day} {month} {random.choice(['nineteen ninety nine','two thousand'])}"

# def gen_city():
#     return random.choice(CITIES)

# def gen_location():
#     return random.choice(LOCATIONS)

# ENTITY_GENERATORS = {
#     "PHONE": gen_phone,
#     "CREDIT_CARD": gen_credit_card,
#     "EMAIL": gen_email,
#     "PERSON_NAME": gen_person_name,
#     "DATE": gen_date,
#     "CITY": gen_city,
#     "LOCATION": gen_location,
# }

# # ----------------------------
# # Noise functions (A/B/C)
# # - Noise is applied to template words (NOT to entity substrings).
# # - This preserves entity spans.
# # ----------------------------
# def noise_light(text):
#     # small misspellings, occasional filler
#     if random.random() < 0.15:
#         text = text.replace("credit", "cradit")
#     if random.random() < 0.10:
#         text = text.replace("email", "eemal")
#     if random.random() < 0.08:
#         text = text + " ok"
#     return text

# def noise_medium(text):
#     # moderate ASR errors: homophones, missing letters, small merges
#     if random.random() < 0.12:
#         text = text.replace("call me on", "cal me on")
#     if random.random() < 0.10:
#         text = text.replace("my", "ma")
#     if random.random() < 0.10:
#         text = text.replace("i live in", "i live")
#     if random.random() < 0.05:
#         text = text.replace("at", "et")
#     return text

# def noise_heavy(text):
#     # heavier distortions: word drops, phonetic mistakes, filler words
#     if random.random() < 0.15:
#         text = text.replace("and", "")
#     if random.random() < 0.12:
#         text = text.replace("name", "nme")
#     if random.random() < 0.10:
#         text = " ".join([w for w in text.split() if random.random() > 0.08])
#     # insert filler words
#     if random.random() < 0.12:
#         text = "uh " + text
#     return text

# def apply_noise_by_level(text, level):
#     if level == "A":
#         return noise_light(text)
#     if level == "B":
#         return noise_medium(text)
#     return noise_heavy(text)

# # ----------------------------
# # Build a single example
# # ----------------------------
# def build_example(idx, min_entities=1, max_entities=3):
#     # Pick how many entities to include
#     n_entities = random.choices([1,2,3], weights=[0.6,0.3,0.1])[0]
#     chosen_templates = random.sample(TEMPLATES, n_entities)

#     # For consistency we generate entity strings first and keep them intact
#     entity_triplets = []  # list of (label, template, entity_text)
#     for label, template in chosen_templates:
#         ent_text = ENTITY_GENERATORS[label]()
#         entity_triplets.append((label, template, ent_text))

#     # mix noise level randomly (A/B/C)
#     noise_level = random.choices(["A","B","C"], weights=[0.5,0.35,0.15])[0]

#     # Build sentence by joining template sentences with " and "
#     pieces = []
#     for (label, template, ent_text) in entity_triplets:
#         pieces.append(template.format(entity=ent_text))
#     text = " and ".join(pieces)

#     # Apply noise to template portion only.
#     # Since entity_texts may contain words like "dot" etc., we must NOT corrupt the entity substrings.
#     # Our noise functions operate on whole text but avoid touching entity tokens explicitly:
#     # To be safe, we will temporarily replace entity substrings with markers, noise the rest, then re-insert.
#     markers = []
#     safe_text = text
#     for i, (label, template, ent_text) in enumerate(entity_triplets):
#         marker = f"__ENTITY_{i}__"
#         safe_text = safe_text.replace(ent_text, marker, 1)
#         markers.append((marker, ent_text))

#     noised = apply_noise_by_level(safe_text, noise_level)

#     # Re-insert entities (exact original entity_text) to keep span offsets accurate
#     for marker, ent_text in markers:
#         noised = noised.replace(marker, ent_text, 1)

#     # Final normalization: collapse multiple spaces
#     final_text = " ".join(noised.strip().split())

#     # Compute spans carefully (first occurrence of each entity used)
#     entities_out = []
#     temp_text = final_text
#     for (label, template, ent_text) in entity_triplets:
#         try:
#             start = temp_text.index(ent_text)
#         except ValueError:
#             # As a last-resort fallback, if entity not found (shouldn't happen), skip this entity
#             # (we'll avoid this by careful insertion above)
#             continue
#         end = start + len(ent_text)
#         entities_out.append({"start": start, "end": end, "label": label})
#         # replace first occurrence to avoid matching same substring again
#         temp_text = temp_text[:start] + (" " * (end - start)) + temp_text[end:]

#     return {
#         "id": f"utt_{idx:05d}",
#         "text": final_text,
#         "entities": entities_out
#     }

# # ----------------------------
# # Generate dataset function
# # ----------------------------
# def generate_split(n_examples, start_idx=0):
#     examples = []
#     for i in range(start_idx, start_idx + n_examples):
#         ex = build_example(i)
#         examples.append(ex)
#     return examples

# def write_jsonl(filename, examples):
#     with open(filename, "w", encoding="utf-8") as f:
#         for ex in examples:
#             f.write(json.dumps(ex, ensure_ascii=False) + "\n")

# # ----------------------------
# # Create datasets
# # ----------------------------
# if __name__ == "__main__":
#     train_examples = generate_split(800, start_idx=0)
#     dev_examples = generate_split(150, start_idx=800)

#     write_jsonl("train.jsonl", train_examples)
#     write_jsonl("dev.jsonl", dev_examples)

#     # Print quick stats & 10 sample lines for verification
#     print("Wrote train.jsonl (800) and dev.jsonl (150)")
#     from collections import Counter
#     def label_counter(exs):
#         c = Counter()
#         for e in exs:
#             for ent in e["entities"]:
#                 c[ent["label"]] += 1
#         return c

#     print("Train label counts:", label_counter(train_examples))
#     print("Dev label counts:", label_counter(dev_examples))

#     # Show 10 sample examples
#     for i in range(5):
#         print("\n---- SAMPLE TRAIN", i, "----")
#         print(json.dumps(train_examples[i], indent=2, ensure_ascii=False))

# import json
# import random
# import os

# # -------------------------------
# # CONFIG
# # -------------------------------
# TRAIN_SIZE = 800
# DEV_SIZE = 150
# OUT_DIR = "data"

# # Indian names
# FIRST_NAMES = ["ramesh", "suresh", "priyanka", "rohan", "neha", "amit", "sanjana", "deepak", "rahul", "kavita"]
# LAST_NAMES = ["sharma", "verma", "mehta", "patel", "iyer", "reddy", "joshi", "khan", "kapoor", "singh"]

# # Cities
# CITIES = ["chennai", "mumbai", "delhi", "kolkata", "pune", "hyderabad", "jaipur", "ahmedabad"]

# # Date patterns
# DATE_TEMPLATES = [
#     "{d1} {d2} {y}",
#     "{d1}/{d2}/{y}",
#     "{d1}-{d2}-{y}",
#     "{d1} {month} {y}"
# ]
# MONTHS = ["january", "february", "march", "april", "may", "june",
#           "july", "august", "september", "october", "november", "december"]

# # STT email style
# def make_email():
#     fn = random.choice(FIRST_NAMES)
#     ln = random.choice(LAST_NAMES)
#     provider = random.choice(["gmail", "yahoo", "outlook", "hotmail"])
#     return f"{fn} dot {ln} at {provider} dot com"

# # Phone numbers (10 digits)
# def make_phone():
#     n = "".join(str(random.randint(0, 9)) for _ in range(10))
#     return n

# # Credit cards (16 digits in groups of 4)
# def make_credit_card():
#     nums = [str(random.randint(1000, 9999)) for _ in range(4)]
#     return " ".join(nums)

# # Dates
# def make_date():
#     d1 = random.randint(1, 28)
#     d2 = random.randint(1, 12)
#     y = random.randint(2023, 2030)
#     template = random.choice(DATE_TEMPLATES)
#     return template.format(
#         d1=str(d1).zfill(2),
#         d2=str(d2).zfill(2),
#         y=str(y),
#         month=random.choice(MONTHS)
#     )

# # Person name
# def make_person():
#     return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


# # ---------------------------------------
# # ENTITY INSERTION INTO RANDOM TEMPLATES
# # ---------------------------------------
# TEMPLATES = [
#     "my email is {EMAIL} and card number is {CREDIT_CARD}",
#     "call me on {PHONE} i live in {CITY}",
#     "{DATE} is my travel date and my name is {PERSON_NAME}",
#     "reach me at {EMAIL} and phone is {PHONE}",
#     "my credit card is {CREDIT_CARD}",
#     "the meeting is on {DATE} in {CITY}",
#     "this is {PERSON_NAME} calling from {CITY}",
#     "email id is {EMAIL}",
#     "my number is {PHONE}",
#     "i will be in {CITY} on {DATE}"
# ]

# def random_example():
#     # Randomly choose a template
#     temp = random.choice(TEMPLATES)

#     # Generate entities
#     ent_values = {
#         "EMAIL": make_email(),
#         "PHONE": make_phone(),
#         "CREDIT_CARD": make_credit_card(),
#         "DATE": make_date(),
#         "CITY": random.choice(CITIES),
#         "PERSON_NAME": make_person(),
#     }

#     # Fill text
#     text = temp
#     for key, val in ent_values.items():
#         text = text.replace("{" + key + "}", val)

#     # Now compute entities with character offsets
#     entities = []

#     for label, value in ent_values.items():
#         start = text.find(value)
#         if start != -1:  # template may not have all keys
#             end = start + len(value)
#             entities.append({
#                 "start": start,
#                 "end": end,
#                 "label": label
#             })

#     return text, entities


# # -------------------------------
# # GENERATION LOOP
# # -------------------------------
# def write_file(path, n):
#     with open(path, "w") as f:
#         for i in range(n):
#             text, ents = random_example()
#             obj = {
#                 "id": f"utt_{i:04d}",
#                 "text": text,
#                 "entities": ents
#             }
#             f.write(json.dumps(obj) + "\n")


# if __name__ == "__main__":
#     os.makedirs(OUT_DIR, exist_ok=True)

#     print("Generating train.jsonl...")
#     write_file(os.path.join(OUT_DIR, "train.jsonl"), TRAIN_SIZE)

#     print("Generating dev.jsonl...")
#     write_file(os.path.join(OUT_DIR, "dev.jsonl"), DEV_SIZE)

#     print("Done.")


#!/usr/bin/env python3
# generate_data_final.py
# Final data generator implementing exact span rules:
# - PERSON_NAME includes 'dot' between first and last (e.g., "priyanka dot verma")
# - EMAIL is only the suffix starting with "at ..." (e.g., "at gmail dot com")
# - PHONE = exactly the phone token (spoken or digits)
# - CREDIT_CARD = exactly the card token (16-digit or spoken)
# - CITY = exactly the city token
# Generates data/train.jsonl (800), data/dev.jsonl (150), data/test.jsonl (50)

# import json
# import random
# import string
# from pathlib import Path

# random.seed(42)

# # ---------------------------
# # Config
# # ---------------------------
# OUT_DIR = Path("data")
# NUM_TRAIN = 800
# NUM_DEV = 150
# NUM_TEST = 50

# # ---------------------------
# # Pools
# # ---------------------------
# FIRST_NAMES = ["priyanka", "rohan", "arjun", "sahana", "keerthi", "ramesh", "neha", "amit", "vijay", "kavita"]
# LAST_NAMES  = ["verma", "mehta", "sharma", "reddy", "kumar", "singh", "patel", "nair", "joshi", "kapoor"]

# EMAIL_PROVIDERS = ["gmail", "yahoo", "outlook", "hotmail"]

# CITIES = ["chennai", "mumbai", "delhi", "kolkata", "pune", "hyderabad", "bangalore", "jaipur"]

# LOCATIONS = ["marina beach", "central park", "marine drive", "india gate", "charminar"]

# DIGIT_WORDS = {
#     "0":"zero","1":"one","2":"two","3":"three","4":"four","5":"five",
#     "6":"six","7":"seven","8":"eight","9":"nine"
# }

# # ---------------------------
# # Helpers to create tokens
# # ---------------------------
# def spoken_from_digits(digits: str):
#     """Return spoken tokens for a digit-string: '9'->'nine' etc, join with spaces."""
#     return " ".join(DIGIT_WORDS[d] for d in digits)

# def gen_phone_token(spoken_prob=0.5):
#     """Generate a phone token: either 10-digit string, grouped, or spelled-out words."""
#     digits = "".join(random.choice(string.digits) for _ in range(10))
#     choice = random.random()
#     if choice < spoken_prob:
#         token = spoken_from_digits(digits)              # "nine eight seven ..."
#     else:
#         style = random.choice(["continuous","grouped","spaced"])
#         if style == "continuous":
#             token = digits                              # "9876543210"
#         elif style == "grouped":
#             token = digits[:3] + " " + digits[3:6] + " " + digits[6:]
#         else:
#             token = " ".join(digits)
#     return token, digits  # token string, raw digits

# def gen_credit_card_token(spoken_prob=0.4):
#     """Generate credit card token: always 16 digits (numeric or spoken groups)."""
#     digits = "".join(random.choice("4567890123") for _ in range(16))
#     choice = random.random()
#     if choice < spoken_prob:
#         token = spoken_from_digits(digits)  # long spoken sequence (16 words)
#     else:
#         style = random.choice(["continuous","groups","groups_hyphen"])
#         if style == "continuous":
#             token = digits
#         elif style == "groups":
#             token = " ".join([digits[i:i+4] for i in range(0,16,4)])
#         else:
#             token = "-".join([digits[i:i+4] for i in range(0,16,4)])
#     return token, digits

# def gen_name_dot():
#     """Return name in STT form with 'dot' between first and last."""
#     first = random.choice(FIRST_NAMES)
#     last = random.choice(LAST_NAMES)
#     # name as appears in text: "priyanka dot verma"
#     name = f"{first} dot {last}"
#     return name, first, last

# def gen_email_suffix(provider=None):
#     """Return 'at <provider> dot com' exactly as requested."""
#     if provider is None:
#         provider = random.choice(EMAIL_PROVIDERS)
#     return f"at {provider} dot com"

# def maybe_filler():
#     return random.choice(["", " ", " ", " "])  # slight chance of extra space

# # ---------------------------
# # Sentence builder ensuring spans are exact
# # ---------------------------
# def make_instance(i):
#     """
#     Build a single instance with:
#       - PERSON_NAME (if email present, name derived from email's local portion)
#       - EMAIL (only suffix 'at ... dot com')
#       - CREDIT_CARD (16-digit)
#       - PHONE (10-digit)
#       - CITY (single token)
#       - LOCATION (optional)
#     The function constructs text so spans can be found reliably.
#     """
#     pieces = []
#     entities = []

#     # Decide which fields to include (probabilities can be tuned)
#     include_email = random.random() < 0.75
#     include_card  = random.random() < 0.6
#     include_phone = random.random() < 0.7
#     include_city  = random.random() < 0.5
#     include_loc   = random.random() < 0.25

#     # Build email + person_name pair (if included)
#     if include_email:
#         # name and email suffix must be separated so spans are clean:
#         name_token, first, last = gen_name_dot()              # "priyanka dot verma"
#         email_suffix = gen_email_suffix()                     # "at gmail dot com"

#         # Phrase: "email id is " + <name_token> + " " + <email_suffix>
#         pieces.append("email id is ")
#         start_name_pos = sum(len(p) for p in pieces)          # where name will start after join
#         pieces.append(name_token)
#         # add a space between name and suffix
#         pieces.append(" ")
#         start_email_pos = sum(len(p) for p in pieces)         # where email_suffix will start
#         pieces.append(email_suffix)

#         # after building final_text we will compute spans; but we can compute now using current lengths
#         # We'll compute spans after final_text created to be robust.

#     # Add card phrase (ensure card token does not get confused with phone)
#     if include_card:
#         # add connector, careful about spaces
#         if pieces:
#             pieces.append(" and card number is ")
#         else:
#             pieces.append("card number is ")
#         card_token, card_digits = gen_credit_card_token()
#         pieces.append(card_token)

#     # Add phone phrase
#     if include_phone:
#         if pieces:
#             pieces.append(" and phone is ")
#         else:
#             pieces.append("phone is ")
#         phone_token, phone_digits = gen_phone_token()
#         pieces.append(phone_token)

#     # City
#     if include_city:
#         if pieces:
#             pieces.append(" i live in ")
#         else:
#             pieces.append("i live in ")
#         city_token = random.choice(CITIES)
#         pieces.append(city_token)

#     # Location
#     if include_loc:
#         pieces.append(" near ")
#         loc_token = random.choice(LOCATIONS)
#         pieces.append(loc_token)

#     # maybe add filler at the end
#     if random.random() < 0.15:
#         pieces.append(" uh")

#     final_text = "".join(pieces).strip()
#     # compute spans precisely by searching substrings (we know the tokens are present)
#     def find_and_add(sub, label):
#         start = final_text.find(sub)
#         if start == -1:
#             # This should never happen; surface as an error (keeps dataset clean)
#             raise RuntimeError(f"substring not found for label {label}: '{sub}' in '{final_text}'")
#         end = start + len(sub)
#         return {"start": start, "end": end, "label": label}

#     # Build entities list in deterministic order: left to right
#     entities_out = []
#     if include_email:
#         # name_token and email_suffix exist in local variables
#         # name_token is 'first dot last' (we created earlier)
#         # But if multiple names/providers created? No — single instance only
#         # We must re-derive name_token and email_suffix positions by searching exact substrings
#         # The variables exist only within the block; we have them in scope if include_email True.
#         entities_out.append(find_and_add(name_token, "PERSON_NAME"))
#         entities_out.append(find_and_add(email_suffix, "EMAIL"))

#     if include_card:
#         entities_out.append(find_and_add(card_token, "CREDIT_CARD"))

#     if include_phone:
#         entities_out.append(find_and_add(phone_token, "PHONE"))

#     if include_city:
#         entities_out.append(find_and_add(city_token, "CITY"))

#     if include_loc:
#         entities_out.append(find_and_add(loc_token, "LOCATION"))

#     # Sort entities by start to be consistent
#     entities_out.sort(key=lambda e: e["start"])

#     return {
#         "id": f"utt_{i:05d}",
#         "text": final_text,
#         "entities": entities_out
#     }

# # ---------------------------
# # Generate datasets
# # ---------------------------
# def generate_and_write():
#     OUT_DIR.mkdir(parents=True, exist_ok=True)
#     all_instances = []
#     total = NUM_TRAIN + NUM_DEV + NUM_TEST
#     for i in range(1, total+1):
#         inst = make_instance_safe(i)
#         all_instances.append(inst)

#     train = all_instances[:NUM_TRAIN]
#     dev   = all_instances[NUM_TRAIN:NUM_TRAIN+NUM_DEV]
#     test  = [{"id": x["id"], "text": x["text"]} for x in all_instances[NUM_TRAIN+NUM_DEV:]]

#     write_jsonl(OUT_DIR / "train.jsonl", train)
#     write_jsonl(OUT_DIR / "dev.jsonl", dev)
#     write_jsonl(OUT_DIR / "test.jsonl", test)

#     print(f"Wrote {len(train)} train, {len(dev)} dev, {len(test)} test to {OUT_DIR}/")

# # ---------------------------
# # Safety wrapper & helpers
# # ---------------------------
# def write_jsonl(path, items):
#     with open(path, "w", encoding="utf-8") as f:
#         for it in items:
#             f.write(json.dumps(it, ensure_ascii=False) + "\n")

# def make_instance_safe(i, trials=5):
#     """Call make_instance until it returns a clean instance or raise."""
#     for _ in range(trials):
#         try:
#             inst = make_instance(i)
#             # quick validation: each entity substring must match text slice
#             text = inst["text"]
#             ok = True
#             for ent in inst["entities"]:
#                 s = ent["start"]; e = ent["end"]
#                 if s < 0 or e > len(text) or text[s:e].strip() == "":
#                     ok = False
#                     break
#             if not ok:
#                 continue
#             return inst
#         except Exception as ex:
#             # try again a few times
#             last_exc = ex
#             continue
#     # if we reach here, surface the error
#     raise RuntimeError(f"Failed to build clean instance {i}: last error: {last_exc}")

# # ---------------------------
# # make_instance is the actual builder used above
# # ---------------------------
# def make_instance(i):
#     # simply delegate to make_instance builder defined earlier
#     return make_instance_core(i)

# # We split the core builder so helper functions are visible
# def make_instance_core(i):
#     # reuse the earlier make_instance logic (refactored)
#     # For clarity, we inline the prior make_instance code here (same behavior)
#     pieces = []
#     entities = []

#     include_email = random.random() < 0.75
#     include_card  = random.random() < 0.6
#     include_phone = random.random() < 0.7
#     include_city  = random.random() < 0.5
#     include_loc   = random.random() < 0.25

#     # store local tokens to compute spans later
#     name_token = None
#     email_suffix = None
#     card_token = None
#     phone_token = None
#     city_token = None
#     loc_token = None

#     if include_email:
#         name_token, first, last = gen_name_dot()
#         email_suffix = gen_email_suffix()

#         pieces.append("email id is ")
#         pieces.append(name_token)
#         pieces.append(" ")
#         pieces.append(email_suffix)

#     if include_card:
#         if pieces:
#             pieces.append(" and card number is ")
#         else:
#             pieces.append("card number is ")
#         card_token, _card_digits = gen_credit_card_token()
#         pieces.append(card_token)

#     if include_phone:
#         if pieces:
#             pieces.append(" and phone is ")
#         else:
#             pieces.append("phone is ")
#         phone_token, _phone_digits = gen_phone_token()
#         pieces.append(phone_token)

#     if include_city:
#         if pieces:
#             pieces.append(" i live in ")
#         else:
#             pieces.append("i live in ")
#         city_token = random.choice(CITIES)
#         pieces.append(city_token)

#     if include_loc:
#         pieces.append(" near ")
#         loc_token = random.choice(LOCATIONS)
#         pieces.append(loc_token)

#     if random.random() < 0.12:
#         pieces.append(" uh")

#     final_text = "".join(pieces).strip()

#     # helper to find and add entity (ensures substring present)
#     def find_and_make(sub, label):
#         start = final_text.find(sub)
#         if start == -1:
#             raise RuntimeError(f"Cannot find substring for label {label}: '{sub}' in '{final_text}'")
#         return {"start": start, "end": start + len(sub), "label": label}

#     entities_out = []
#     if include_email:
#         entities_out.append(find_and_make(name_token, "PERSON_NAME"))
#         entities_out.append(find_and_make(email_suffix, "EMAIL"))
#     if include_card:
#         entities_out.append(find_and_make(card_token, "CREDIT_CARD"))
#     if include_phone:
#         entities_out.append(find_and_make(phone_token, "PHONE"))
#     if include_city:
#         entities_out.append(find_and_make(city_token, "CITY"))
#     if include_loc:
#         entities_out.append(find_and_make(loc_token, "LOCATION"))

#     entities_out.sort(key=lambda e: e["start"])

#     return {"id": f"utt_{i:05d}", "text": final_text, "entities": entities_out}

# # ---------------------------
# # Run
# # ---------------------------
# if __name__ == "__main__":
#     # link the core builder function to the top-level name used above
#     make_instance = make_instance_core
#     make_instance_safe = make_instance_safe
#     generate_and_write()


import json
import random
import string
from pathlib import Path

random.seed(42)

# ---------------------------
# Config
# ---------------------------
OUT_DIR = Path("data")
NUM_TRAIN = 800
NUM_DEV = 150
NUM_TEST = 50

# ---------------------------
# Disjoint name pools
# ---------------------------
FIRST_NAMES_TRAIN = [
    "aarav", "pranav", "ishan", "aishwarya", "nitesh", "shruti",
    "roshan", "vishal", "meena", "aditya"
]
LAST_NAMES_TRAIN = [
    "iyer", "rao", "pillai", "sethi", "gandhi", "jain",
    "chaudhary", "madan"
]

FIRST_NAMES_DEV = [
    "harshal", "devika", "raghavendra", "meghana", "samuel", "diana",
    "lucas", "sophia", "hiba", "tunde"
]
LAST_NAMES_DEV = [
    "fernandes", "thomas", "samson", "varghese", "mirza", "qureshi",
    "mbatha", "adebayo"
]

FIRST_NAMES_TEST = [
    "pratyush", "ishita", "abhinav", "tanmai", "chloe", "olivia",
    "samira", "zain", "chidi", "amara"
]
LAST_NAMES_TEST = [
    "pereira", "kaur", "bhatt", "borkar", "ibrahim", "zimanga",
    "okoye", "dlamini"
]

# ---------------------------
# Other pools
# ---------------------------
EMAIL_PROVIDERS = ["gmail", "yahoo", "outlook", "hotmail"]

CITIES = ["chennai", "mumbai", "delhi", "kolkata", "pune", "hyderabad", "bangalore", "jaipur"]

LOCATIONS = ["marina beach", "central park", "marine drive", "india gate", "charminar"]

DIGIT_WORDS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five",
    "6": "six", "7": "seven", "8": "eight", "9": "nine"
}

# ---------------------------
# Helpers
# ---------------------------
def spoken_from_digits(digits: str):
    return " ".join(DIGIT_WORDS[d] for d in digits)

def gen_phone_token(spoken_prob=0.5):
    digits = "".join(random.choice(string.digits) for _ in range(10))
    choice = random.random()

    if choice < spoken_prob:
        token = spoken_from_digits(digits)
    else:
        style = random.choice(["continuous", "grouped", "spaced"])
        if style == "continuous":
            token = digits
        elif style == "grouped":
            token = digits[:3] + " " + digits[3:6] + " " + digits[6:]
        else:
            token = " ".join(digits)

    return token, digits

def gen_credit_card_token(spoken_prob=0.4):
    digits = "".join(random.choice("4567890123") for _ in range(16))
    choice = random.random()

    if choice < spoken_prob:
        token = spoken_from_digits(digits)
    else:
        style = random.choice(["continuous", "groups", "groups_hyphen"])
        if style == "continuous":
            token = digits
        elif style == "groups":
            token = " ".join([digits[i:i+4] for i in range(0, 16, 4)])
        else:
            token = "-".join([digits[i:i+4] for i in range(0, 16, 4)])

    return token, digits

# ---------------------------
# Split-aware name generator
# ---------------------------
def gen_name_dot(i):
    """Return name from split-specific pools."""
    if i <= NUM_TRAIN:
        first = random.choice(FIRST_NAMES_TRAIN)
        last = random.choice(LAST_NAMES_TRAIN)
    elif i <= NUM_TRAIN + NUM_DEV:
        first = random.choice(FIRST_NAMES_DEV)
        last = random.choice(LAST_NAMES_DEV)
    else:
        first = random.choice(FIRST_NAMES_TEST)
        last = random.choice(LAST_NAMES_TEST)

    return f"{first} dot {last}", first, last

def gen_email_suffix():
    provider = random.choice(EMAIL_PROVIDERS)
    return f"at {provider} dot com"

# ---------------------------
# Instance builder
# ---------------------------
def make_instance_core(i):
    pieces = []

    include_email = random.random() < 0.75
    include_card = random.random() < 0.6
    include_phone = random.random() < 0.7
    include_city = random.random() < 0.5
    include_loc = random.random() < 0.25

    # local storage
    name_token = None
    email_suffix = None
    card_token = None
    phone_token = None
    city_token = None
    loc_token = None

    if include_email:
        name_token, _, _ = gen_name_dot(i)
        email_suffix = gen_email_suffix()

        pieces.append("email id is ")
        pieces.append(name_token)
        pieces.append(" ")
        pieces.append(email_suffix)

    if include_card:
        pieces.append(" and card number is " if pieces else "card number is ")
        card_token, _ = gen_credit_card_token()
        pieces.append(card_token)

    if include_phone:
        pieces.append(" and phone is " if pieces else "phone is ")
        phone_token, _ = gen_phone_token()
        pieces.append(phone_token)

    if include_city:
        pieces.append(" i live in " if pieces else "i live in ")
        city_token = random.choice(CITIES)
        pieces.append(city_token)

    if include_loc:
        pieces.append(" near ")
        loc_token = random.choice(LOCATIONS)
        pieces.append(loc_token)

    if random.random() < 0.12:
        pieces.append(" uh")

    final_text = "".join(pieces).strip()

    # helper
    def find_and_make(sub, label):
        start = final_text.find(sub)
        if start == -1:
            raise RuntimeError(f"Cannot find {label}: '{sub}' in '{final_text}'")
        return {"start": start, "end": start + len(sub), "label": label}

    entities_out = []

    if include_email:
        entities_out.append(find_and_make(name_token, "PERSON_NAME"))
        entities_out.append(find_and_make(email_suffix, "EMAIL"))

    if include_card:
        entities_out.append(find_and_make(card_token, "CREDIT_CARD"))

    if include_phone:
        entities_out.append(find_and_make(phone_token, "PHONE"))

    if include_city:
        entities_out.append(find_and_make(city_token, "CITY"))

    if include_loc:
        entities_out.append(find_and_make(loc_token, "LOCATION"))

    entities_out.sort(key=lambda e: e["start"])

    return {"id": f"utt_{i:05d}", "text": final_text, "entities": entities_out}

# ---------------------------
# Safety wrapper
# ---------------------------
def make_instance_safe(i, trials=5):
    for _ in range(trials):
        try:
            inst = make_instance_core(i)
            text = inst["text"]

            for ent in inst["entities"]:
                s, e = ent["start"], ent["end"]
                if s < 0 or e > len(text) or text[s:e].strip() == "":
                    raise RuntimeError("Bad span")

            return inst
        except Exception:
            continue

    raise RuntimeError(f"Failed to build instance {i}")

# ---------------------------
# IO helpers
# ---------------------------
def write_jsonl(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

# ---------------------------
# Generate datasets
# ---------------------------
def generate_and_write():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_instances = []

    total = NUM_TRAIN + NUM_DEV + NUM_TEST
    for i in range(1, total + 1):
        all_instances.append(make_instance_safe(i))

    train = all_instances[:NUM_TRAIN]
    dev = all_instances[NUM_TRAIN:NUM_TRAIN + NUM_DEV]
    test = [{"id": x["id"], "text": x["text"]} for x in all_instances[NUM_TRAIN + NUM_DEV:]]

    write_jsonl(OUT_DIR / "train.jsonl", train)
    write_jsonl(OUT_DIR / "dev.jsonl", dev)
    write_jsonl(OUT_DIR / "test.jsonl", test)

    print(f"Wrote {len(train)} train, {len(dev)} dev, {len(test)} test → {OUT_DIR}/")

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    generate_and_write()
