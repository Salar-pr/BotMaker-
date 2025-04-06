from rich.console import Console
from rich.table import Table
from rich import box
import time
import requests
import os
import shutil
from datetime import datetime, timedelta

IDEA_FLOW_ART = """
\033[38;5;208m
██╗██╗  ██╗██╗        ███████╗██╗      ██████╗ ██╗    ██╗███████╗██████╗ 
██║╚██╗██╔╝██║        ██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝██╔══██╗
██║ ╚███╔╝ ██║        █████╗  ██║     ██║   ██║██║ █╗ ██║█████╗  ██████╔╝
██║ ██╔██╗ ██║        ██╔══╝  ██║     ██║   ██║██║███╗██║██╔══╝  ██╔══██╗
██║██╔╝ ██╗██║███████╗██║     ███████╗╚██████╔╝╚███╔███╔╝███████╗██║  ██║
╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝
\033[0m                                                                        
"""

print(IDEA_FLOW_ART)

console = Console()
YOUTUBE_API_KEY = "AIzaSyAeX11rZka_G36cQGP6np3kA-SHK5pD5o0"
TMDB_API_KEY = "44d09a665d39ee0f40eff386f12496ca"

def main_menu():
    console.print("\n1. Analyze YouTube Videos", style="bold green")
    console.print("2. Analyze Movies/TV Shows", style="bold blue")
    console.print("3. Clean Desktop Entries", style="bold magenta")
    console.print("4. Exit\n", style="bold red")

def get_search_topic():
    console.print("\n🎬 What videos would you like to analyze?", style="bold cyan")
    return input("Enter your search topic: ").strip()

def get_time_period_choice():
    console.print("\n📅 Select time period:", style="bold cyan")
    choices = ["today", "this week", "this month", "this year", "all time"]
    for i, period in enumerate(choices, 1):
        console.print(f"{i}. {period.title()}", style="green")
    while True:
        try:
            choice = int(input("\nEnter time period (1-5): "))
            if 1 <= choice <= 5:
                return choices[choice-1]
            console.print("⚠️ Invalid choice", style="bold yellow")
        except ValueError:
            console.print("⚠️ Please enter a number", style="bold yellow")

def get_media_search():
    console.print("\n🎥 What movie/TV show would you like to analyze?", style="bold cyan")
    return input("Enter title: ").strip()

def get_tmdb_results(search_term, media_type='tv'):
    url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {
        'api_key': TMDB_API_KEY,
        'query': search_term,
        'include_adult': 'false'
    }
    try:
        response = requests.get(url, params=params)
        results = response.json().get('results', [])
        return sorted(results, key=lambda x: x.get('vote_average', 0), reverse=True)
    except Exception as e:
        console.print(f"⚠️ API Error: {str(e)}", style="bold red")
        return []

def display_results_table(results, title):
    table = Table(
        title=f"\n🎬 {title}",
        box=box.ROUNDED,
        header_style="bold blue",
        title_style="bold cyan"
    )
    table.add_column("#", style="bold", width=3)
    table.add_column("Title", width=30)
    table.add_column("Type", width=8)
    table.add_column("Rating", justify="center")
    table.add_column("Release Date", justify="center")
    table.add_column("Popularity", justify="right")
    
    for idx, item in enumerate(results, 1):
        media_type = "TV" if 'first_air_date' in item else "Movie"
        release_date = item.get('first_air_date') or item.get('release_date', 'N/A')
        table.add_row(
            str(idx),
            item.get('name') or item.get('title', 'N/A'),
            media_type,
            f"⭐ {item.get('vote_average', 'N/A')}",
            release_date,
            f"{item.get('popularity', 0):.1f}"
        )
    console.print(table)
    return len(results)

def get_selection(max_items):
    while True:
        try:
            choice = int(input(f"\nEnter selection (1-{max_items} or 0 to cancel): "))
            if 0 <= choice <= max_items:
                return choice
            console.print("⚠️ Invalid selection", style="bold yellow")
        except ValueError:
            console.print("⚠️ Please enter a number", style="bold yellow")

def display_media_details(media_id, media_type):
    url = f"https://api.themoviedb.org/3/{media_type}/{media_id}"
    params = {'api_key': TMDB_API_KEY}
    try:
        details = requests.get(url, params=params).json()
        table = Table(box=box.ROUNDED, header_style="bold magenta")
        
        table.add_column("Category", style="bold", width=15)
        table.add_column("Details", width=50)
        
        if media_type == 'tv':
            table.add_row("Title", details.get('name', 'N/A'))
            table.add_row("Seasons", str(details.get('number_of_seasons', 'N/A')))
            table.add_row("Episodes", str(details.get('number_of_episodes', 'N/A')))
            table.add_row("Status", details.get('status', 'N/A'))
            table.add_row("Networks", ", ".join([n['name'] for n in details.get('networks', [])]))
        else:
            table.add_row("Title", details.get('title', 'N/A'))
            table.add_row("Runtime", f"{details.get('runtime', 0)} mins")
            table.add_row("Budget", f"${details.get('budget', 0):,}")
            table.add_row("Revenue", f"${details.get('revenue', 0):,}")
        
        table.add_row("Overview", details.get('overview', 'N/A'))
        table.add_row("Homepage", details.get('homepage', 'N/A'))
        table.add_row("TMDB Link", f"https://www.themoviedb.org/{media_type}/{media_id}")
        
        console.print(table)
    except Exception as e:
        console.print(f"⚠️ Error getting details: {str(e)}", style="bold red")

def media_analysis_flow():
    search_term = get_media_search()
    with console.status(f"Searching for '{search_term}'..."):
        results = get_tmdb_results(search_term, 'tv') + get_tmdb_results(search_term, 'movie')
    
    if not results:
        console.print(f"\n🔴 No results found for '{search_term}'", style="bold red")
        return
    
    count = display_results_table(results, f"Results for '{search_term}'")
    console.print("\nℹ️ Select an item to view details (0 to cancel)", style="italic")
    selection = get_selection(count)
   
    if selection == 0:
        return
    
    selected = results[selection-1]
    media_type = 'tv' if 'first_air_date' in selected else 'movie'
    with console.status("Fetching details..."):
        display_media_details(selected['id'], media_type)

def clean_desktop_entries():
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        temp_dir = os.path.join(desktop, "AnalysisTemp")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            console.print("\n🧹 Cleaned desktop temporary files!", style="bold green")
        else:
            console.print("\n🔍 No temporary files found", style="bold yellow")
    except Exception as e:
        chonsole.print(f"\n⚠️ Cleanup error: {str(e)}", style="bold red")

def main():
    console.print("\nWelcome to Media Analysis Pro!", style="bold blue")
    while True:
        main_menu()
        choice = input("\nEnter option (1-4): ")
        
        if choice == '1':
            search_term = get_search_topic()
            time_period = get_time_period_choice()
            # YouTube analysis logic here
            
        elif choice == '2':
            media_analysis_flow()
            
        elif choice == '3':
            console.print("\n🧹 This will remove temporary analysis files", style="bold yellow")
            if input("Confirm? (y/n): ").lower() == 'y':
                clean_desktop_entries()
                
        elif choice == '4':
            console.print("\n👋 Thank you for using Media Analysis Pro!", style="bold green")
            break
            
        else:
            console.print("\n⚠️ Invalid option", style="bold yellow")

if __name__ == "__main__":
    main()

