import os
import re
from git import Repo

def sync_with_git_repo(folder_path, repo_name):
    print("Syncing with git repo...", folder_path, repo_name)
    repo = Repo.init(folder_path)
    repo.config_writer().set_value("user", "name", "The Stanford Daily Bot").release()
    repo.config_writer().set_value("user", "email", "tech@stanforddaily.com").release()
    origin = repo.create_remote('origin', f"git@bitbucket.org:thestanforddaily/{repo_name}.git")
    repo.git.add(A=True)
    repo.index.commit("Updates")
    repo.git.push("--force", "origin", "HEAD:master")

for century in filter(os.path.isdir, os.listdir(".")):
    if not re.match(r'^\d{2}xx$', century):
        continue
    for decade in os.listdir(century):
        if not os.path.isdir(os.path.join(century, decade)): continue
        sync_with_git_repo(os.path.join(century, decade), decade)
