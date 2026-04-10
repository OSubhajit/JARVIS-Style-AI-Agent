# plugins/lifestyle_tools.py — Lifestyle: Food, Travel, Random Utilities

import os, random, json
from datetime import datetime, timedelta
from plugins.advanced_ai import _ai


# ══ FOOD & COOKING ════════════════════════════════════════════════════════════
def recipe_from_ingredients(ingredients, cuisine="any"):
    return _ai(f"Create a recipe using these ingredients: {ingredients}\n"
               f"Cuisine preference: {cuisine}\n"
               f"Include: dish name, servings, prep/cook time, ingredients with quantities, step-by-step instructions, tips.")

def recipe_substitute(ingredient, reason="unavailable"):
    return _ai(f"Suggest 3 substitutes for {ingredient} in cooking ({reason}).\n"
               f"For each: name, conversion ratio, best use cases, taste differences.")

def meal_plan_week(diet_type="balanced", people=1, budget="medium"):
    return _ai(f"Create a 7-day meal plan for {people} person(s).\n"
               f"Diet: {diet_type} | Budget: {budget}\n"
               f"Include: breakfast, lunch, dinner, snack. Add shopping list at end.")

def nutrition_info(food, quantity="100g"):
    return _ai(f"Provide approximate nutritional information for {quantity} of {food}:\n"
               f"Calories, protein, carbs, fat, fiber, vitamins, minerals. Format as a table.")

def cooking_conversion(amount, from_unit, to_unit):
    CONVERSIONS = {
        ("cup","ml"): 236.6, ("ml","cup"): 1/236.6,
        ("tbsp","ml"): 14.79, ("ml","tbsp"): 1/14.79,
        ("tsp","ml"): 4.93, ("ml","tsp"): 1/4.93,
        ("oz","g"): 28.35, ("g","oz"): 1/28.35,
        ("lb","kg"): 0.453, ("kg","lb"): 2.205,
        ("cup","tbsp"): 16, ("tbsp","cup"): 1/16,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key in CONVERSIONS:
        result = float(amount) * CONVERSIONS[key]
        return f"🥄 {amount} {from_unit} = {result:.2f} {to_unit}"
    return f"No conversion found: {from_unit} → {to_unit}"

def food_pairing(food):
    return _ai(f"What foods, drinks, and ingredients pair well with {food}? "
               f"Explain why each pairing works. Give 8 suggestions.")

def calorie_burn(activity, duration_min, weight_kg=70):
    MET = {
        "walking":3.5,"running":9.8,"cycling":7.5,"swimming":8.0,"yoga":3.0,
        "pushups":8.0,"squats":5.0,"dancing":6.0,"football":10.0,"cricket":5.0,
    }
    met = MET.get(activity.lower(), 5.0)
    cal = met * float(weight_kg) * int(duration_min) / 60
    return f"🏃 Calories burned: {cal:.0f} kcal ({activity}, {duration_min}min, {weight_kg}kg)"

def bmi_diet_plan(bmi, goal="maintain"):
    return _ai(f"I have a BMI of {bmi}. Create a personalized diet plan to {goal} weight.\n"
               f"Include: daily calorie target, macros, foods to eat/avoid, meal timing tips.")


# ══ TRAVEL ════════════════════════════════════════════════════════════════════
def travel_itinerary(destination, days, budget="medium", style="balanced"):
    return _ai(f"Create a detailed {days}-day travel itinerary for {destination}.\n"
               f"Budget: {budget} | Travel style: {style}\n"
               f"Include: daily schedule, attractions, food recommendations, transport, estimated costs, tips.")

def packing_list(destination, days, season, activities):
    return _ai(f"Create a complete packing list for:\n"
               f"Destination: {destination} | Duration: {days} days | Season: {season}\n"
               f"Activities: {activities}\n"
               f"Organize by category. Mark essentials with ⭐")

def travel_budget_calculator(destination, days):
    return _ai(f"Estimate the travel budget for {days} days in {destination} for 1 person.\n"
               f"Break down by: accommodation, food, transport, activities, miscellaneous.\n"
               f"Give budget/mid-range/luxury estimates in INR.")

def visa_requirements(from_country, to_country):
    return _ai(f"What are the visa requirements for a {from_country} citizen traveling to {to_country}?\n"
               f"Include: visa type, duration, requirements, processing time, fees, tips.")

def currency_tips(destination):
    return _ai(f"Give practical currency and money tips for traveling to {destination}:\n"
               f"Local currency, exchange tips, card acceptance, tipping culture, budget tips.")

def local_phrases(language, count=20):
    return _ai(f"Give {count} essential phrases in {language} for travelers.\n"
               f"Include: greeting, asking directions, ordering food, shopping, emergencies.\n"
               f"Format: English | {language} | Pronunciation")

def best_time_to_visit(destination):
    return _ai(f"What is the best time to visit {destination}?\n"
               f"Include: month-by-month breakdown, weather, crowds, events, prices, what to avoid.")

def travel_insurance_guide(trip_type="international"):
    return _ai(f"Explain what to look for in {trip_type} travel insurance.\n"
               f"Cover: types, coverage to ensure, what's usually excluded, tips for India travelers.")


# ══ DAILY UTILITIES ════════════════════════════════════════════════════════════
def days_until(target_date):
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d")
        diff   = (target - datetime.now()).days
        return (f"📅 Days until {target_date}: {diff} days\n"
                f"  That's {diff//7} weeks and {diff%7} days\n"
                f"  Date: {target.strftime('%A, %B %d, %Y')}")
    except Exception as e:
        return f"Date error: {e} (format: YYYY-MM-DD)"

def age_calculator(birthdate):
    try:
        bd    = datetime.strptime(birthdate, "%Y-%m-%d")
        today = datetime.today()
        years = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        months= (today.month - bd.month) % 12
        days  = (today - bd.replace(year=today.year)).days % 30
        total_days = (today - bd).days
        return (f"🎂 Age for {birthdate}:\n"
                f"  Age     : {years} years, {months} months, {days} days\n"
                f"  Days    : {total_days:,} total days lived\n"
                f"  Weeks   : {total_days//7:,} weeks\n"
                f"  Next birthday: {bd.replace(year=today.year+1).strftime('%A, %B %d, %Y')}")
    except Exception as e:
        return f"Date error: {e}"

def date_difference(date1, date2):
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        diff = abs((d2 - d1).days)
        return (f"📅 Date difference:\n"
                f"  {date1} → {date2}\n"
                f"  = {diff} days = {diff//7} weeks = {diff/30.44:.1f} months = {diff/365.25:.2f} years")
    except Exception as e:
        return f"Date error: {e}"

def what_day_is(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_str} is a {d.strftime('%A, %B %d, %Y')}"
    except Exception as e:
        return f"Date error: {e}"

def countdown_to_event(event_name, date_str):
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d")
        diff   = (target - datetime.now()).days
        return (f"⏳ Countdown to {event_name}:\n"
                f"  {diff} days remaining\n"
                f"  {diff//7} weeks and {diff%7} days\n"
                f"  Date: {target.strftime('%A, %B %d, %Y')}")
    except Exception as e:
        return f"Error: {e}"

def random_activity():
    ACTIVITIES = [
        "Take a 10-minute walk outside 🚶","Try a new recipe 🍳","Read for 30 minutes 📚",
        "Call a friend or family member 📱","Learn 5 new words in a language 🌍",
        "Do 20 minutes of stretching 🧘","Write in a journal ✍️","Watch a TED talk 🎥",
        "Declutter one drawer 🗂️","Try a new workout 💪","Meditate for 10 minutes 🧠",
        "Draw or doodle something 🎨","Practice a musical instrument 🎵",
        "Cook a dish from another culture 🍜","Watch a documentary 🎬",
    ]
    return f"🎲 Random activity suggestion:\n  {random.choice(ACTIVITIES)}"

def inspirational_quote():
    return _ai("Give me one powerful, original inspirational quote. Just the quote and author, nothing else.")

def this_day_in_history():
    today = datetime.now()
    return _ai(f"Tell me 3 interesting things that happened on {today.strftime('%B %d')} in history. Be specific with years.")

def fun_facts(topic="random"):
    return _ai(f"Tell me 5 surprising and little-known fun facts about: {topic}")

def riddle():
    return _ai("Give me one clever riddle with its answer hidden below. Format:\nRiddle: ...\n\nAnswer (hidden below)\n||spoiler|| ...")

def would_you_rather():
    return _ai("Create one interesting 'Would you rather' question with two difficult choices. Explain the dilemma.")

def personality_quiz(trait="leadership"):
    return _ai(f"Create a 5-question personality quiz to assess {trait} style.\n"
               f"Each question has 4 options A-D. Include scoring guide at end.")


# ══ PRODUCTIVITY LIFE HACKS ══════════════════════════════════════════════════
def life_hack(problem):
    return _ai(f"Give me 5 practical life hacks or tips for: {problem}\n"
               f"Be specific, actionable, and original.")

def decision_matrix(options, criteria):
    return _ai(f"Create a decision matrix to help choose between: {options}\n"
               f"Evaluation criteria: {criteria}\n"
               f"Rate each option on each criterion (1-10). Give final recommendation.")

def eisenhower_matrix(tasks):
    return _ai(f"Categorize these tasks using the Eisenhower Matrix:\n{tasks}\n\n"
               f"Quadrant 1: Urgent & Important (Do Now)\n"
               f"Quadrant 2: Not Urgent & Important (Schedule)\n"
               f"Quadrant 3: Urgent & Not Important (Delegate)\n"
               f"Quadrant 4: Not Urgent & Not Important (Eliminate)")

def smart_goal(goal):
    return _ai(f"Convert this goal into a SMART goal:\n'{goal}'\n\n"
               f"Specific | Measurable | Achievable | Relevant | Time-bound\n"
               f"Then break it into 5 actionable weekly steps.")

def habit_stacking(existing_habit, new_habit):
    return _ai(f"Create a habit stacking plan:\n"
               f"Existing habit: {existing_habit}\nNew habit to add: {new_habit}\n"
               f"Give implementation intention, cue-routine-reward, and first 7 days plan.")
