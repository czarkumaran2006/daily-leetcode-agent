import os
import random
import requests
from datetime import datetime
from plyer import notification

URL = "https://leetcode.com/graphql"

def fetch_from_leetcode(query, variables=None):
    """Helper function to send requests to LeetCode's API."""
    try:
        response = requests.post(URL, json={'query': query, 'variables': variables or {}})
        return response.json().get('data', {})
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_official_daily():
    """Fetches the official LeetCode problem of the day."""
    query = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            link
            question {
                questionFrontendId
                title
                titleSlug
                difficulty
            }
        }
    }
    """
    data = fetch_from_leetcode(query)
    if data and 'activeDailyCodingChallengeQuestion' in data:
        q = data['activeDailyCodingChallengeQuestion']['question']
        return {
            "id": q['questionFrontendId'],
            "title": q['title'],
            "slug": q['titleSlug'],
            "difficulty": q['difficulty'],
            "link": f"https://leetcode.com{data['activeDailyCodingChallengeQuestion']['link']}"
        }
    return None

def get_random_bonus_problem():
    """Fetches a random problem from the top 1000 free problems."""
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList(categorySlug: $categorySlug, limit: $limit, filters: $filters) {
            questions {
                questionFrontendId
                title
                titleSlug
                difficulty
            }
        }
    }
    """
    # Ask for 1000 standard algorithms
    variables = {"categorySlug": "", "limit": 1000, "filters": {}}
    data = fetch_from_leetcode(query, variables)
    
    if data and 'problemsetQuestionList' in data:
        questions = data['problemsetQuestionList']['questions']
        # Pick a random one
        q = random.choice(questions)
        return {
            "id": q['questionFrontendId'],
            "title": q['title'],
            "slug": q['titleSlug'],
            "difficulty": q['difficulty'],
            "link": f"https://leetcode.com/problems/{q['titleSlug']}/"
        }
    return None

def create_template(folder_name, prob_type, prob_data, date_str):
    """Creates a standardized python folder and file structure."""
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, "solution.py")
    
    if not os.path.exists(file_path):
        template = f'"""\nLeetCode {prob_data["id"]}: {prob_data["title"]} ({prob_type})\n'
        template += f'Difficulty: {prob_data["difficulty"]}\n'
        template += f'Link: {prob_data["link"]}\n'
        template += f'Date: {date_str}\n"""\n\n'
        template += "def solve():\n    # Write your code here\n    pass\n\nif __name__ == '__main__':\n    solve()\n"
        
        with open(file_path, "w") as f:
            f.write(template)
        return True
    return False

def main():
    date_str = datetime.today().strftime('%Y-%m-%d')
    problems_created = []

    # 1. Process Problem 1: Official Daily
    daily_prob = get_official_daily()
    if daily_prob:
        folder_1 = f"daily_challenges/{date_str}_1_official_{daily_prob['slug']}"
        if create_template(folder_1, "Official Daily", daily_prob, date_str):
            problems_created.append(f"1. {daily_prob['title']} ({daily_prob['difficulty']})")

    # 2. Process Problem 2: Bonus Random Problem
    bonus_prob = get_random_bonus_problem()
    if bonus_prob:
        folder_2 = f"daily_challenges/{date_str}_2_bonus_{bonus_prob['slug']}"
        if create_template(folder_2, "Bonus Challenge", bonus_prob, date_str):
            problems_created.append(f"2. {bonus_prob['title']} ({bonus_prob['difficulty']})")

    # 3. Fire Desktop Notification
    if problems_created:
        notification_text = "\n".join(problems_created)
        notification.notify(
            title="📚 New LeetCode Problems Ready!",
            message=notification_text,
            app_name="LeetCode Agent",
            timeout=10 # Notification stays for 10 seconds
        )
        print("🎉 Folders created and desktop notification sent!")
    else:
        print("👉 Today's folders were already generated.")

if __name__ == "__main__":
    main()