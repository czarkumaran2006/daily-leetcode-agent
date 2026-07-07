import os
import json
import requests
from google import genai

# Initialize the Gemini Client (Make sure GEMINI_API_KEY is set in your environment variables)
client = genai.Client()

def get_daily_problem():
    """Fetches the daily LeetCode problem via GraphQL API"""
    url = "https://leetcode.com/graphql"
    query = """
    query questionOfToday {
        activeDailyCodingChallengeQuestion {
            date
            question {
                questionFrontendId
                title
                titleSlug
                content
                difficulty
            }
        }
    }
    """
    response = requests.post(url, json={'query': query})
    if response.status_code == 200:
        data = response.json()
        return data['data']['activeDailyCodingChallengeQuestion']['question']
    raise Exception("Failed to fetch LeetCode daily problem.")

def generate_solution(title, difficulty, content):
    """Uses Gemini to generate an optimized Python solution and explanation"""
    prompt = f"""
    You are an expert competitive programmer. Solve the following LeetCode problem.
    Provide the response strictly in two parts:
    1. The Python 3 code block.
    2. A brief, bulleted explanation of the time and space complexity.

    Problem: {title} ({difficulty})
    Description: {content}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

def send_notification(webhook_url, message):
    """Sends a ping to Discord or Telegram when complete"""
    if webhook_url:
        requests.post(webhook_url, json={"content": message})

def main():
    try:
        # 1. Fetch problem
        prob = get_daily_problem()
        title = prob['title']
        slug = prob['titleSlug']
        
        print(f"Fetched today's problem: {title}")

        # 2. Generate solution
        solution = generate_solution(title, prob['difficulty'], prob['content'])
        
        # 3. Save to file
        folder = f"solutions/{slug}"
        os.makedirs(folder, exist_ok=True)
        
        with open(f"{folder}/solution.py", "w", encoding="utf-8") as f:
            f.write(solution)
            
        print("Solution successfully generated and saved.")
        
        # 4. Notify (Optional)
        discord_webhook = os.getenv("NOTIFICATION_WEBHOOK")
        send_notification(discord_webhook, f"✅ **LeetCode Agent Success!**\nSolved: *{title}* ({prob['difficulty']})\nCode pushed to GitHub.")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        discord_webhook = os.getenv("NOTIFICATION_WEBHOOK")
        send_notification(discord_webhook, f"❌ **LeetCode Agent Failed!**\nError: {str(e)}")

if __name__ == "__main__":
    main()
