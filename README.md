# TrailQuest – AI-Powered Adventure Planner  

TrailQuest is a full-stack web application for **planning outdoor adventures with ease**. Whether you’re hiking, camping, or exploring new trails, TrailQuest helps you **generate, edit, and manage detailed itineraries** tailored to your preferences.  

---

## 🎯 Motivation  
Planning outdoor trips is often fragmented across multiple tools. TrailQuest streamlines the process by combining **smart itinerary generation, Google-powered location search, and profile-based storage** into one platform, so adventurers can spend more time exploring and less time planning.  

---

## 🚀 Features  

- **✨ Smart Itinerary Generator**  
  Input location, activity type, duration, difficulty, and group size to generate custom trip plans using the **OpenAI API**.  
  Each activity includes **Google Maps links** for easy navigation.  

- **📍 Google Places Autocomplete**  
  Real-time, city-filtered location suggestions powered by the **Google Places API**.  

- **📝 Itinerary Management**  
  - Dynamically edit or remove activities (AJAX JSON endpoints)  
  - Add notes to activities  
  - Save trips and revisit past itineraries in your profile  
  - Print clean, formatted itineraries  

- **📱 Responsive Design**  
  Mobile-first layout with **Bootstrap** styling and a dynamic image grid.  

- **🔒 Secure User Accounts**  
  - Authentication with personalized itinerary storage  
  - Birthdate-verified password reset flow  

---

## 🛠 Tech Stack  

**Backend**  
- Python 3  
- Django (with REST-style JSON endpoints for trip edits)  

**Frontend**  
- Django HTML templates  
- CSS3 + Bootstrap  
- JavaScript (AJAX for dynamic updates)  

**APIs & Integrations**  
- Google Places API (location autocomplete)  
- OpenAI API (gpt-4o-mini) for itinerary generation  

**Database**  
- SQLite (development)  
- PostgreSQL (production via Heroku)  

**Deployment**  
- Hosted on **Heroku**  
- Static files served with **Whitenoise**  

---
