"""
Movie Ratings Retriever
==========================================
Uses IMDB movie id

Fetches:
    - TMDB score + vote count             (via TMDB API)
    - RT Tomatometer                      (via OMDB API)

API Keys:
    - TMDB : https://www.themoviedb.org/settings/api
    - OMDB : http://www.omdbapi.com/apikey.aspx
"""

import os
import time
import requests
import pandas as pd
import creds

REQUEST_DELAY = 0.35

TMDB_FIND_URL = "https://api.themoviedb.org/3/find/{}"
OMDB_URL = "http://www.omdbapi.com/"

def fetch_tmdb_data(imdb_id):
    try:
        url = f"{TMDB_FIND_URL.format(imdb_id)}?api_key={creds.tmdb_api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('movie_results'):
                movie = data['movie_results'][0]
                return {
                    "TMDB_Score": movie.get("vote_average", "N/A"),
                    "TMDB_Vote_Count": movie.get("vote_count", "N/A")
                }
    except:
        pass
    return {"TMDB_Score": "N/A", "TMDB_Vote_Count": "N/A"}

def fetch_rt_tomatometer(imdb_id):
    try:
        url = f"{OMDB_URL}?i={imdb_id}&apikey={creds.omdb_api_key}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('Ratings'):
                for rating in data['Ratings']:
                    if rating.get('Source') == 'Rotten Tomatoes':
                        return {"RT_Tomatometer": rating.get('Value', 'N/A')}
        elif response.status_code == 401:
            print("OMDB API limit reached. Skipping remaining requests.")
            return {"RT_Tomatometer": "N/A"}
    except:
        pass
    return {"RT_Tomatometer": "N/A"}

def main():
    csv_path = input("Enter the path to your CSV file: ").strip()
    
    if not os.path.exists(csv_path):
        print("File not found!")
        return
    
    df = pd.read_csv(csv_path)
    all_results = []
    
    for idx, row in df.iterrows():
        imdb_id = row['id']
        title = row['title']
        
        tmdb_data = fetch_tmdb_data(imdb_id)
        rt_data = fetch_rt_tomatometer(imdb_id)
        
        # Create result with all original columns plus new ratings
        result = row.to_dict()  # Start with all original data
        result["TMDB_Score"] = tmdb_data["TMDB_Score"]
        result["TMDB_Vote_Count"] = tmdb_data["TMDB_Vote_Count"]
        result["RT_Tomatometer"] = rt_data["RT_Tomatometer"]
        
        all_results.append(result)
        print(f"{title}: TMDB={tmdb_data['TMDB_Score']}, RT={rt_data['RT_Tomatometer']}")
        
        time.sleep(REQUEST_DELAY)
    
    # Save results
    output_df = pd.DataFrame(all_results)
    base, _ = os.path.splitext(csv_path)
    out_path = base + "_with_ratings.csv"
    output_df.to_csv(out_path, index=False)
    print(f"\nResults saved to: {out_path}")

if __name__ == "__main__":
    main()
