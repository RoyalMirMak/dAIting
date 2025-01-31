import json
import random
from faker import Faker
from datetime import datetime, timedelta
import re

fake = Faker()

universities = [
    "Harvard University", "Stanford University", "Massachusetts Institute of Technology",
    "University of Cambridge", "University of Oxford", "California Institute of Technology",
    "Princeton University", "Yale University", "University of Chicago", "Columbia University"
]
with open('prompt_fake_bio.txt', 'r') as f:
    prompt = f.read()

cnt = 0


def generate_profile():
    global cnt
    age = random.randint(18, 50)
    gender = random.choice(["MALE", "FEMALE"])
    interested_in = random.choice(["MALE", "FEMALE"])
    school = random.choice(universities)
    profile_p1 = {
        "ageAtUpload": age,
        "gender": gender,
        "region": fake.country(),
        "jobTitle": fake.job(),
        "school": school,
        "educationLevel": random.choice(
            ["Has high school and/or college education", "Has college education", "Has postgraduate education"]),
    }
    profile_str = str(profile_p1)
    response = make_gpt_request(prompt + profile_str, 1.4)
    # print(response)

    if response.startswith("Bio:"):
        response = response[4:]
    try:
        bio, interests = response.split('#')
    except Exception as e:
        print(response)
        print(e)
        return
    bio = bio.strip()
    # print(bio)
    match = re.search(r'\[(.*?)\]', interests)
    interests = []
    if match:
        result = match.group(1)
        try:
            interests = list(eval(result))
        except Exception as e:
            print(interests)
            print(e)
            pass
    print(f"Success in generating {cnt}th profile")
    cnt += 1
    profile_p2 = {
        "computed": False,
        "tinderId": fake.sha256(),
        "createdAt": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
        "updatedAt": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
        "birthDate": fake.date_of_birth(minimum_age=age, maximum_age=age).isoformat() + "T00:00:00.000Z",
        "ageAtLastUsage": age + random.randint(1, 5),
        "createDate": fake.date_time_between(start_date='-10y', end_date='-5y').isoformat() + "Z",
        "activeTime": fake.date_time_between(start_date='-1y', end_date='now').isoformat() + "Z",
        "genderStr": gender[0],
        "city": fake.city(),
        "country": None,
        "interests": None,
        "sexual_orientations": "",
        "descriptors": [
            {"name": "Height", "choices": [f"{random.randint(5, 6)}' {random.randint(0, 11)}\""],
             "visibility": "public"},
            {"name": "Languages I Know",
             "choices": random.sample(["English", "Spanish", "French", "German", "Chinese", "Japanese", "Russian"],
                                      random.randint(1, 3)), "visibility": "public"},
            {"name": "Basics", "choices": [random.choice(
                ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
                 "Aquarius", "Pisces"])], "visibility": "public"},
            {"name": "Basics", "choices": [random.choice(["High School", "Bachelors", "Masters", "PhD"])],
             "visibility": "public"},
            {"name": "Basics", "choices": [random.choice(["I want children", "I don't want children", "Not sure yet"])],
             "visibility": "public"},
            {"name": "Basics", "choices": [random.choice(["Vaccinated", "Not vaccinated"])], "visibility": "public"},
            {"name": "Basics", "choices": [random.choice(
                ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP",
                 "ISFP", "ESTP", "ESFP"])], "visibility": "public"},
            {"name": "Lifestyle",
             "choices": [random.choice(["Socially on weekends", "Socially on weekdays", "Not social"])],
             "visibility": "public"},
            {"name": "Lifestyle", "choices": [random.choice(["Non-smoker", "Smoker"])], "visibility": "public"},
            {"name": "Relationship Goals",
             "choices": [random.choice(["Short-term, open to long", "Long-term, open to short", "Not sure yet"])],
             "visibility": "public"}
        ],
        "instagramConnected": random.choice([True, False]),
        "spotifyConnected": random.choice([True, False]),
        "jobTitleDisplayed": random.choice([True, False]),
        "company": fake.company(),
        "companyDisplayed": random.choice([True, False]),
        "schoolDisplayed": random.choice([True, False]),
        "college": [],
        "jobsRaw": [{"title": {"name": fake.job(), "displayed": random.choice([True, False])},
                     "company": {"name": fake.company(), "displayed": random.choice([True, False])}}],
        "schoolsRaw": [{"name": school, "displayed": random.choice([True, False]),
                        "metadata_id": f"int_{random.randint(10000, 99999)}"}],
        "ageFilterMin": random.randint(18, 30),
        "ageFilterMax": random.randint(31, 50),
        "interestedIn": interested_in,
        "interestedInStr": interested_in[0],
        "genderFilter": interested_in,
        "genderFilterStr": interested_in[0],
        "swipestatsVersion": "SWIPESTATS_3",
        "userId": fake.uuid4(),
        "firstDayOnApp": fake.date_time_between(start_date='-10y', end_date='-5y').isoformat() + "Z",
        "lastDayOnApp": fake.date_time_between(start_date='-1y', end_date='now').isoformat() + "Z",
        "daysInProfilePeriod": random.randint(100, 5000),
        "profileMeta": {
            "id": fake.uuid4(),
            "from": fake.date_time_between(start_date='-10y', end_date='-5y').isoformat() + "Z",
            "to": fake.date_time_between(start_date='-1y', end_date='now').isoformat() + "Z",
            "daysInProfilePeriod": random.randint(100, 5000),
            "daysActiveOnApp": random.randint(100, 2000),
            "daysNotActiveOnApp": random.randint(100, 2000),
            "appOpensTotal": random.randint(1000, 20000),
            "swipeLikesTotal": random.randint(1000, 30000),
            "swipeSuperLikesTotal": random.randint(10, 500),
            "swipePassesTotal": random.randint(1000, 20000),
            "combinedSwipesTotal": random.randint(2000, 40000),
            "messagesSentTotal": random.randint(100, 5000),
            "messagesReceivedTotal": random.randint(100, 5000),
            "matchesTotal": random.randint(100, 5000),
            "noMatchesTotal": random.randint(1000, 20000),
            "daysYouSwiped": random.randint(100, 2000),
            "daysYouMessaged": random.randint(100, 2000),
            "daysAppOpenedNoSwipe": random.randint(100, 2000),
            "daysAppOpenedNoMessage": random.randint(100, 2000),
            "daysAppOpenedNoSwipeOrMessage": random.randint(100, 2000),
            "matchRateForPeriod": round(random.uniform(0.1, 0.5), 2),
            "likeRateForPeriod": round(random.uniform(0.5, 0.9), 2),
            "likeRatio": round(random.uniform(1.0, 1.5), 2),
            "messagesSentRateForPeriod": round(random.uniform(0.1, 0.5), 2),
            "messagesSentRatio": round(random.uniform(1.0, 1.5), 2),
            "averageMatchesPerDay": random.randint(1, 10),
            "averageAppOpensPerDay": random.randint(1, 10),
            "averageSwipeLikesPerDay": random.randint(1, 10),
            "averageSwipePassesPerDay": random.randint(1, 10),
            "averageMessagesSentPerDay": random.randint(1, 10),
            "averageMessagesReceivedPerDay": random.randint(1, 10),
            "averageSwipesPerDay": random.randint(1, 10),
            "medianMatchesPerDay": random.randint(0, 5),
            "medianAppOpensPerDay": random.randint(0, 5),
            "medianSwipeLikesPerDay": random.randint(0, 5),
            "medianSwipePassesPerDay": random.randint(0, 5),
            "medianMessagesSentPerDay": random.randint(0, 5),
            "medianMessagesReceivedPerDay": random.randint(0, 5),
            "medianSwipesPerDay": random.randint(0, 5),
            "peakMatches": random.randint(10, 100),
            "peakMatchesDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "peakAppOpens": random.randint(10, 100),
            "peakAppOpensDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "peakSwipeLikes": random.randint(100, 1000),
            "peakSwipeLikesDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "peakSwipePasses": random.randint(100, 1000),
            "peakSwipePassesDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "peakMessagesSent": random.randint(10, 100),
            "peakMessagesSentDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "peakMessagesReceived": random.randint(10, 100),
            "peakMessagesReceivedDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "peakCombinedSwipes": random.randint(100, 1000),
            "peakCombinedSwipesDate": fake.date_time_between(start_date='-5y', end_date='now').isoformat() + "Z",
            "dailySwipeLimitsReached": random.randint(10, 100),
            "longestActivePeriodInDays": random.randint(100, 5000),
            "longestInactivePeriodInDays": random.randint(0, 100),
            "numberOfConversations": random.randint(100, 2000),
            "numberOfConversationsWithMessages": random.randint(100, 2000),
            "maxConversationMessageCount": random.randint(10, 200),
            "longestConversationInDays": random.randint(10, 2000),
            "messageCountInLongestConversationInDays": random.randint(1, 10),
            "longestConversationInDaysTwoWeekMax": random.randint(10, 30),
            "messageCountInConversationTwoWeekMax": random.randint(10, 50),
            "averageConversationMessageCount": random.randint(1, 10),
            "averageConversationLengthInDays": random.randint(1, 10),
            "medianConversationMessageCount": random.randint(1, 5),
            "medianConversationLengthInDays": random.randint(1, 10),
            "numberOfOneMessageConversations": random.randint(10, 100),
            "percentageOfOneMessageConversations": random.randint(10, 50),
            "nrOfGhostingsAfterInitialMatch": random.randint(10, 100),
            "tinderProfileId": fake.sha256(),
            "hingeProfileId": None,
            "tinderProfileIdByMonth": None,
            "tinderProfileIdByYear": None
        }
    }
    profile_p1["bio"] = bio
    profile_p1["bioOriginal"] = bio
    profile_p1["user_interests"] = interests
    profile = {**profile_p1, **profile_p2}
    return profile


PROFILE_NUMBER = 100
profiles = [generate_profile() for _ in range(PROFILE_NUMBER)]

with open('generated_profiles.json', 'w') as f:
    json.dump(profiles, f, indent=4)

print(f"{cnt} profiles generated and saved to 'generated_profiles.json'")