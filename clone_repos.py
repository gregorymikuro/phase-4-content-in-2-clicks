import os
import subprocess
import shutil
from typing import List, Tuple

class RepoManager:
    def __init__(self, repo_info_file: str):
        self.repo_info_file = repo_info_file
        self.repos = self.parse_repo_file()
        self.failed_clones = []
        self.failed_renames = []

    def parse_repo_file(self) -> List[Tuple[str, str, str]]:
        repos = []
        current_day = None
        with open(self.repo_info_file, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("Day"):
                    current_day = line.replace(" ", "-")
                elif line:
                    number, url = line.split(" ", 1)
                    repos.append((current_day, number, url))
        return repos

    def clone_repo(self, url: str, dest: str) -> bool:
        try:
            subprocess.run(['git', 'clone', url, dest], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def rename_folder(self, folder_path: str, new_name: str) -> bool:
        new_folder_path = os.path.join(os.path.dirname(folder_path), new_name)
        try:
            os.rename(folder_path, new_folder_path)
            return True
        except OSError:
            return False

    def process_repos(self, repos: List[Tuple[str, str, str]]):
        for day, number, url in repos:
            folder_name = url.split('/')[-1]
            new_folder_name = folder_name.replace("dsc", number).replace("ds", number)
            day_path = os.path.join(os.getcwd(), day)
            os.makedirs(day_path, exist_ok=True)
            repo_path = os.path.join(day_path, folder_name)
            new_repo_path = os.path.join(day_path, new_folder_name)
            
            if not self.clone_repo(url, repo_path):
                self.failed_clones.append((day, number, url))
            elif not self.rename_folder(repo_path, new_folder_name):
                self.failed_renames.append((day, number, url, folder_name))

    def process_first_8_days(self):
        first_8_days_repos = [repo for repo in self.repos if int(repo[1]) <= 8]
        self.process_repos(first_8_days_repos)

    def process_remaining_days(self):
        remaining_days_repos = [repo for repo in self.repos if int(repo[1]) > 8]
        self.process_repos(remaining_days_repos)

    def report_failures(self):
        if self.failed_clones:
            print("Below are repositories that didn’t download:")
            for day, number, url in self.failed_clones:
                print(f"Day {day}, Number {number}, Link {url}")
            print("Consider cloning them manually.")
        
        if self.failed_renames:
            print("Below are repositories that didn’t change names:")
            for day, number, url, folder_name in self.failed_renames:
                print(f"Day {day}, Number {number}, Link {url}, Folder {folder_name}")
            print("Consider renaming them manually.")

def main():
    repo_manager = RepoManager('repositories.txt')
    repo_manager.process_first_8_days()
    repo_manager.process_remaining_days()
    repo_manager.report_failures()

if __name__ == "__main__":
    main()
