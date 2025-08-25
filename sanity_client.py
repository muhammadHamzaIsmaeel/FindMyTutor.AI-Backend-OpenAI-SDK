import os
import requests
from dotenv import load_dotenv

load_dotenv()

SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
SANITY_DATASET = os.getenv("SANITY_DATASET")
SANITY_API_TOKEN = os.getenv("SANITY_API_TOKEN")

def fetch_tutors(filters):
    gender = filters.get("gender")
    location = filters.get("location")
    subject = filters.get("subject")
    mode = filters.get("mode")

    query = f'''
    *[_type == "tutor" &&
    gender match "{gender}" &&
    location match "{location}" &&
    subject match "{subject}" &&
    mode match "{mode}"
    ] {{
    _id,
    name,
    "slug": slug, 
    photo,
    subject,
    gender,
    location,
    mode,
    experience,
    contact,
    bio,           
    verified     
    }}
    '''


    url = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2023-08-01/data/query/{SANITY_DATASET}"

    headers = {
        "Authorization": f"Bearer {SANITY_API_TOKEN}"
    }

    response = requests.get(url, headers=headers, params={"query": query})

    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        return {
            "error": "Failed to fetch from Sanity",
            "details": response.text
        }
