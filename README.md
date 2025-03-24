# 🎮 Gaming Leaderboard System

A **Django-based gaming leaderboard system** that tracks player scores across multiple game modes, supports real-time ranking, and provides RESTful APIs for managing scores and retrieving leaderboard data.
---

## 🚀 **Features**
✅ Submit player scores via an API.  
✅ Retrieve top players' leaderboard.  
✅ Get individual player ranking.  
✅ Multi-game mode support.  
✅ Date-based and game mode-based filtering.  
✅ Pagination for leaderboard.   
✅ Webhook-compatible for real-time updates.   

---

## 🛠️ **Tech Stack**
- **Backend:** Python, Django  
- **Frontend:** Django Templates, HTML, CSS, JavaScript  
- **Database:** SQLite  
- **API:** Django REST Framework (DRF)    
- **Containerization:** Docker  
- **Deployment:** Heroku  

---
**Improvements to be done:**
- We can Implement Web sockets for real time update or run a cron which will be running every 30 seconds to update the Leaderboard
- UI/UX improvements can be
- Caching can be added if required(but we need to invalidate it whenever leaderboard rankings get updated)
- Notification service can be added to notify the Rank 1 user.
---

## 📂 **APIs**
1. Create or update a player’s score in a specific game mode by creating a game session.

**URL:**  
POST /leaderboard/submit_score/
**Request Body:**
{
  "user_id": 1,
  "score": 100,
  "game_mode": "Battle Royale"
}
**Response:**
{
  "message": "Score submitted successfully",
  "total_score": 250
}


**2. Retrieve the top 10 players' scores, filtered and sorted by rank or score.
**
**URL:**  
GET /leaderboard/top/

Query Parameters:

Parameter	Type	Description
game_modes	list	Filter by one or more game modes
start_date	date	Filter by start date
end_date	date	Filter by end date
search	string	Search by username
sort_by	string	rank or score
order	string	asc or desc
page	int	Page number for pagination

Example Request:
GET /api/leaderboard/top/?sort_by=rank&order=asc&page=2

Response:
{
  "current_page": 2,
  "total_pages": 5,
  "results": [
    {
      "rank": 11,
      "username": "Player1",
      "total_score": 450
    },
    {
      "rank": 12,
      "username": "Player2",
      "total_score": 430
    }
  ]
}

**3. Fetch a player's rank based on total score.
**
**URL:**  
GET leaderboard/rank/{user_id}/
Response:

json
Copy
Edit
{
  "user_id": 1,
  "username": "Player1",
  "rank": 5,
  "total_score": 450
}

**Steps to Run Locally:**
Clone: git@github.com:srtaj/Leaderboard.git
cd leaderboard
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver



