#!/usr/bin/env python3
"""Script to generate randomized, backdated git commits to populate the GitHub contribution graph."""

import subprocess
import random
from datetime import datetime, timedelta

def run_git(args):
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running git {' '.join(args)}: {result.stderr}")
        return False
    return True

def generate_contributions(days_back=35):
    print(f"Generating contributions for the past {days_back} days...")
    
    # Commit messages to make it look realistic
    messages = [
        "refactor: optimize rendering logic",
        "docs: update API documentation",
        "fix: resolve WebRTC connection timeout",
        "feat: add multi-agent coordination support",
        "chore: clean up unused dependencies",
        "test: add unit tests for agent pipeline",
        "style: improve responsive layout on mobile",
        "perf: optimize asset load performance",
        "fix: handle webhook verification failures",
        "feat: integrate Claude workflow actions",
        "refactor: clean up terminal card styles",
        "docs: add setup guide for snake game"
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    current_date = start_date
    total_commits = 0
    
    while current_date <= end_date:
        # Avoid commit generation on certain days to make it look organic
        # (e.g. fewer commits on weekends)
        is_weekend = current_date.weekday() >= 5
        if is_weekend:
            commit_count = random.randint(0, 3)
        else:
            commit_count = random.randint(3, 8) # High activity on weekdays
            
        for _ in range(commit_count):
            hour = random.randint(9, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            commit_time = current_date.replace(hour=hour, minute=minute, second=second)
            date_str = commit_time.strftime("%Y-%m-%d %H:%M:%S")
            message = random.choice(messages)
            
            # Set environment variables for backdating
            env_args = [
                "-c", f"user.name=Shivam Chopra",
                "-c", f"user.email=mailshivamchopra@gmail.com",
                "commit",
                "--allow-empty",
                "-m", message,
                "--date", date_str
            ]
            
            if run_git(env_args):
                total_commits += 1
                
        current_date += timedelta(days=1)
        
    print(f"Successfully generated {total_commits} backdated commits locally!")
    print("To push these to GitHub and update your graph, run:")
    print("  git push origin main")
    print("If you want to revert these local commits before pushing, run:")
    print("  git reset --hard origin/main")

if __name__ == "__main__":
    generate_contributions(35)
