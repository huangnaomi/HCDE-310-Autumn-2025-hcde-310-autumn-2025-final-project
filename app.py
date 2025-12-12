from flask import Flask, render_template, request
import requests
import random
from keys import YELP_API_KEY

app = Flask(__name__)
YELP_URL = "https://api.yelp.com/v3/businesses/search"

# get businesses from yelp api
def get_yelp(city, category, limit=10):
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
    # shuffle to reduce repetition
    random.shuffle(cafes)
    random.shuffle(restaurants)
    random.shuffle(sights)
    # keep track of used locations because i was getting a lot of duplicates :(
    used_cafes = set()
    used_restaurants = set()
    used_sights = set()
    itinerary = []

    for day in range(1, days + 1):
        # morning cafe
        morning = next((c for c in cafes if c["id"] not in used_cafes), None)
        if morning: used_cafes.add(morning["id"])
        morning_alts = [c for c in cafes if c["id"] not in used_cafes][:max_alternates]

        # lunch restaurant
        lunch = next((r for r in restaurants if r["id"] not in used_restaurants), None)
        if lunch: used_restaurants.add(lunch["id"])
        lunch_alts = [r for r in restaurants if r["id"] not in used_restaurants and r["id"] != lunch["id"]][:max_alternates]

        # afternoon activity
        afternoon = next((s for s in sights if s["id"] not in used_sights), None)
        if afternoon: used_sights.add(afternoon["id"])
        afternoon_alts = [s for s in sights if s["id"] not in used_sights][:max_alternates]

        # dinner restaurant - must not be same as lunch today
        valid_dinner = [r for r in restaurants if r["id"] not in used_restaurants and r["id"] != lunch["id"]]
        dinner = valid_dinner[0] if valid_dinner else None
        if dinner: used_restaurants.add(dinner["id"])
        dinner_alts = valid_dinner[1:1+max_alternates] if len(valid_dinner) > 1 else []

        # combine top & alternates
        day_plan = {
            "day": day,
            "morning": { "top": morning, "alternates": morning_alts},
            "lunch": { "top": lunch, "alternates": lunch_alts},
            "afternoon": { "top": afternoon, "alternates": afternoon_alts},
            "dinner": { "top": dinner, "alternates": dinner_alts}
        }
        itinerary.append(day_plan)

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