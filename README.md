# HCDE-310-Autumn-2025-hcde-310-autumn-2025-final-project
This is my final project for HCDE 310: A Yelp API Itinerary Planner. Instructions for how to sign up for a Yelp API key is in keys.txt.



Project Proposal/Description:

The Yelp Itinerary Planner allows a user to input a city (location) and the duration of their trip. It will then pull business data from the Yelp API to create a travel itinerary of suggested places to visit, with variety and high ratings. 

For each day of the trip, it provides recommendations in the following categories:
- Morning: Cafes
- Lunch: Restaurants
- Afternoon: Activities including arts, landmarks, museums, shopping, and/or parks
- Dinner: Restaurants
Each category has a top suggestion along with three alternate options (if applicable) to give the user more choices. Recommendations are pulled from the Yelp API and filtered to avoid repetition/duplicates across the planner.

Technicalities:
- Backend: Flask for server-side and API requests
- API use: Yelp Fusion API to fetch business data (photos, ratings, categories, etc.)
- Frontend: HTML/CSS templates for display and user input
- Logic: Shuffle business data to add variety and avoid duplicates, provide alternate suggestions for more choice, and generate itinerary based on user-inputted location and trip length.

