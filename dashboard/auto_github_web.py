import os
import base64
import requests

GITHUB_API = "https://api.github.com"

class GitHubWebsiteCreator:
    def __init__(self, token, username):
        self.token = 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
        self.username = foreignbandss
        self.headers = {"Authorization": f"token {self.token}"}

    # Create repo if it doesn't exist
    def create_repo(self, repo_name, private=False):
        url = f"{GITHUB_API}/user/repos"
        data = {"name": repo_name, "private": private, "auto_init": True}
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code not in [201, 422]:  # 422 = already exists
            response.raise_for_status()
        print(f"Repo ready: {repo_name}")
        return f"{self.username}/{repo_name}"

    # Create folder with a file
    def create_folder_with_file(self, repo_full_name, folder_path, file_path):
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        url = f"{GITHUB_API}/repos/{repo_full_name}/contents/{folder_path}/{os.path.basename(file_path)}"
        data = {"message": f"Add {os.path.basename(file_path)}", "content": content}
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["content"]["html_url"]

    # List files in a folder
    def list_files_in_folder(self, repo_full_name, folder_path):
        url = f"{GITHUB_API}/repos/{repo_full_name}/contents/{folder_path}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        files = response.json()
        return [{"name": f["name"], "url": f["download_url"]} for f in files]

    # Setup GitHub Pages workflow (optional)
    def setup_github_pages(self, repo_full_name):
        workflow = f"""
name: Deploy to GitHub Pages
on:
  push:
    branches:
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{{{ secrets.GITHUB_TOKEN }}}}
          publish_dir: ./
"""
        url = f"{GITHUB_API}/repos/{repo_full_name}/contents/.github/workflows/deploy.yml"
        data = {"message": "Add GitHub Pages workflow", "content": base64.b64encode(workflow.encode()).decode()}
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
