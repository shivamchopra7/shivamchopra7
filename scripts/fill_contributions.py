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
        # Determine day type using probabilities to create realistic variation
        roll = random.random()
        if roll < 0.15:
            # Extreme crunch day: 15 to 30 commits (heavy spikes)
            commit_count = random.randint(15, 30)
        elif roll < 0.50:
            # Normal busy day: 5 to 10 commits
            commit_count = random.randint(5, 10)
        elif roll < 0.80:
            # Low activity day: 1 to 3 commits (some blips)
            commit_count = random.randint(1, 3)
        else:
            # Day off: 0 commits (gaps)
            commit_count = 0
            
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
