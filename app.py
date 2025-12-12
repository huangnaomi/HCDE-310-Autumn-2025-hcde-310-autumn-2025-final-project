from flask import Flask, render_template, request
import requests
import random
from keys import YELP_API_KEY

app = Flask(__name__)
YELP_URL = "https://api.yelp.com/v3/businesses/search"

# get businesses from yelp api
def get_yelp(city, category, limit=20):
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    params = {
        "location": city,
        "categories": category,
        "limit": limit,
        "sort_by": "rating"
    }

    try:
        response = requests.get(YELP_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching data: HTTP {response.status_code}")
            return []
        return response.json().get("businesses", [])
    except requests.exceptions.RequestException as e:
        print("Network error while trying to reach Yelp API.")
        print(f"Reason: {e}")
        return []

# function for afternoon activities w/ multiple categories to prevent repetition
def get_afternoon_activities(city):
    categories = ["arts", "landmarks", "museums", "shopping", "parks"]
    activities = []
    for category in categories:
        activities.extend(get_yelp(city, category))
    # remove duplicates by biz id
    unique_activities = {b["id"]: b for b in activities}
    return list(unique_activities.values())

# build daily itinerary & prevent duplicates
def build_itinerary(days, cafes, restaurants, sights, max_alternates=3):
    #shuffle to prevent repetition
    random.shuffle(cafes)
    random.shuffle(restaurants)
    random.shuffle(sights)

    used_tops = set()
    itinerary = []

    def pick_top_and_alts(items, max_alts=3, exclude_ids=set()):
        # unique top picks, but alternates can repeat (otherwise need a lot of api data)
        top = next((i for i in items if i["id"] not in used_tops and i["id"] not in exclude_ids), None)
        if top:
            used_tops.add(top["id"])
        alternates = random.sample([i for i in items if top and i["id"] != top["id"]],
                                   min(max_alts, len([i for i in items if top and i["id"] != top["id"]])))
        return top, alternates

    for day in range(1, days + 1):
        morning, morning_alts = pick_top_and_alts(cafes, max_alternates)
        lunch, lunch_alts = pick_top_and_alts(restaurants, max_alternates)
        afternoon, afternoon_alts = pick_top_and_alts(sights, max_alternates)
        # exclude lunch so it won't be the same as dinner
        dinner, dinner_alts = pick_top_and_alts(restaurants, max_alternates, exclude_ids={lunch["id"]})

        itinerary.append({
            "day": day,
            "morning": {"top": morning, "alternates": morning_alts},
            "lunch": {"top": lunch, "alternates": lunch_alts},
            "afternoon": {"top": afternoon, "alternates": afternoon_alts},
            "dinner": {"top": dinner, "alternates": dinner_alts},
        })

    return itinerary


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/results", methods=["POST"])
def results():
    city = request.form.get("city")
    days = int(request.form.get("days"))

    cafes = get_yelp(city, "cafes")
    restaurants = get_yelp(city, "restaurants")
    sights = get_afternoon_activities(city)

    itinerary = build_itinerary(days, cafes, restaurants, sights, max_alternates=3)

    return render_template("results.html", city=city, days=days, itinerary=itinerary)

if __name__ == "__main__":
    app.run(debug=True)