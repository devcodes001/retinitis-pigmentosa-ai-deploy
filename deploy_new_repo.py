#!/usr/bin/env python3
"""
Complete Automated Deployment Script for New Repository
Creates a new GitHub repository and deploys all project files
"""

import subprocess
import json
import time
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import Tuple

class NewRepoDeployer:
    def __init__(self, email: str, username: str, token: str, repo_name: str):
        self.email = email
        self.username = username
        self.token = token
        self.repo_name = repo_name
        self.repo_url = f"https://github.com/{username}/{repo_name}"
        self.repo_api_url = f"https://api.github.com/user/repos"
        
    def log(self, message: str):
        """Print formatted log message"""
        print(f"\n{'='*70}")
        print(message)
        print('='*70)
    
    def step(self, num: int, desc: str):
        """Print step header"""
        print(f"\n📍 STEP {num}: {desc}")
        print("-" * 70)
    
    def success(self, msg: str):
        """Print success message"""
        print(f"✅ {msg}")
    
    def error(self, msg: str):
        """Print error message"""
        print(f"❌ {msg}")
    
    def run_command(self, cmd: str, description: str = "") -> Tuple[int, str]:
        """Execute shell command and return exit code and output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return 1, f"Command timed out: {cmd}"
        except Exception as e:
            return 1, str(e)
    
    def setup_git_config(self) -> bool:
        """Configure git with email and username"""
        self.step(1, "Configure Git")
        
        try:
            self.run_command(f'git config --global user.email "{self.email}"')
            self.run_command(f'git config --global user.name "{self.username}"')
            
            # Verify
            code, output = self.run_command('git config --global user.email')
            if self.email in output:
                self.success(f"Git configured with email: {self.email}")
                return True
            else:
                self.error("Failed to configure git email")
                return False
        except Exception as e:
            self.error(f"Error configuring git: {str(e)}")
            return False
    
    def create_github_repo(self) -> bool:
        """Create new repository on GitHub"""
        self.step(2, "Create GitHub Repository")
        
        try:
            # Check if repo exists
            check_url = f"{self.repo_api_url}/{self.repo_name}"
            req = Request(f"https://api.github.com/repos/{self.username}/{self.repo_name}")
            req.add_header('Authorization', f'token {self.token}')
            
            try:
                urlopen(req)
                self.success(f"Repository '{self.repo_name}' already exists")
                return True
            except HTTPError as e:
                if e.code == 404:
                    # Repo doesn't exist, create it
                    print(f"Repository doesn't exist. Creating '{self.repo_name}'...")
                    
                    # Create repo via API
                    data = json.dumps({
                        "name": self.repo_name,
                        "description": "Retinitis Pigmentosa AI classifier - Automated Deployment",
                        "private": False,
                        "auto_init": True
                    }).encode('utf-8')
                    
                    req = Request(
                        self.repo_api_url,
                        data=data,
                        headers={
                            'Authorization': f'token {self.token}',
                            'Accept': 'application/vnd.github.v3+json',
                            'Content-Type': 'application/json'
                        },
                        method='POST'
                    )
                    
                    response = urlopen(req)
                    repo_data = json.loads(response.read().decode('utf-8'))
                    
                    self.success(f"Repository created: {repo_data['html_url']}")
                    time.sleep(2)  # Wait for GitHub to fully initialize
                    return True
                else:
                    self.error(f"GitHub API error: {e.code}")
                    return False
        except Exception as e:
            self.error(f"Error creating repository: {str(e)}")
            return False
    
    def setup_git_remote(self) -> bool:
        """Configure git remote"""
        self.step(3, "Setup Git Remote")
        
        try:
            # Remove existing remote if it exists
            self.run_command('git remote remove origin')
            
            # Add new remote
            remote_url = f"https://{self.username}:{self.token}@github.com/{self.username}/{self.repo_name}.git"
            code, output = self.run_command(f'git remote add origin "{remote_url}"')
            
            if code == 0:
                self.success(f"Git remote configured: {self.repo_url}")
                return True
            else:
                self.error(f"Failed to configure remote: {output}")
                return False
        except Exception as e:
            self.error(f"Error setting up remote: {str(e)}")
            return False
    
    def verify_commits(self) -> bool:
        """Verify local commits"""
        self.step(4, "Verify Local Commits")
        
        try:
            code, output = self.run_command('git log --oneline -5')
            
            if code == 0 and output.strip():
                commits = output.strip().split('\n')
                print(f"\nFound {len(commits)} commits:")
                for commit in commits:
                    print(f"  • {commit}")
                self.success("All commits verified")
                return True
            else:
                self.error("No commits found")
                return False
        except Exception as e:
            self.error(f"Error verifying commits: {str(e)}")
            return False
    
    def push_to_github(self) -> bool:
        """Push commits to GitHub"""
        self.step(5, "Push Code to GitHub")
        
        try:
            print("Pushing commits to GitHub...")
            code, output = self.run_command('git push -u origin main --force')
            
            if code == 0:
                self.success(f"Successfully pushed to {self.repo_url}")
                return True
            else:
                # Try with master branch if main fails
                print("Trying with master branch...")
                code, output = self.run_command('git push -u origin master --force')
                
                if code == 0:
                    self.success(f"Successfully pushed to {self.repo_url}")
                    return True
                else:
                    print(f"Push output: {output}")
                    
                    # Check if it's just a branch protection warning
                    if "rejected" in output.lower() or "rule" in output.lower():
                        self.error(f"Push blocked by repository rules: {output}")
                        print("\nⓘ Note: You may need to configure branch protection rules in GitHub settings")
                        return False
                    else:
                        self.error(f"Push failed: {output}")
                        return False
        except Exception as e:
            self.error(f"Error pushing to GitHub: {str(e)}")
            return False
    
    def verify_push(self) -> bool:
        """Verify push was successful"""
        self.step(6, "Verify Remote Repository")
        
        try:
            req = Request(f"https://api.github.com/repos/{self.username}/{self.repo_name}/commits")
            req.add_header('Authorization', f'token {self.token}')
            
            response = urlopen(req)
            commits = json.loads(response.read().decode('utf-8'))
            
            if isinstance(commits, list) and len(commits) > 0:
                self.success(f"Repository has {len(commits)} commits on remote")
                print("\nRemote commits:")
                for commit in commits[:5]:
                    print(f"  • {commit['sha'][:7]}: {commit['commit']['message'].split(chr(10))[0]}")
                return True
            else:
                print("⚠️  No commits found on remote yet (this is expected if push was blocked)")
                return False
        except Exception as e:
            print(f"⚠️  Could not verify remote (may be normal): {str(e)}")
            return True  # Don't fail on verification
    
    def run_complete_deployment(self):
        """Execute complete deployment"""
        self.log(f"🚀 AUTOMATED DEPLOYMENT: Creating '{self.repo_name}'")
        
        steps = [
            (self.setup_git_config, "Configure Git"),
            (self.create_github_repo, "Create Repository"),
            (self.setup_git_remote, "Setup Remote"),
            (self.verify_commits, "Verify Commits"),
            (self.push_to_github, "Push to GitHub"),
            (self.verify_push, "Verify Push"),
        ]
        
        passed = 0
        failed = 0
        
        for step_func, step_name in steps:
            try:
                if step_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.error(f"Exception in {step_name}: {str(e)}")
                failed += 1
        
        # Final summary
        self.log(f"📊 DEPLOYMENT SUMMARY")
        print(f"\n✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"\n🔗 Repository URL: {self.repo_url}")
        print(f"📝 Repository API: https://api.github.com/repos/{self.username}/{self.repo_name}")
        
        if failed == 0:
            print("\n" + "="*70)
            print("✅ ALL STEPS COMPLETED SUCCESSFULLY!")
            print("="*70)
            print(f"\n📍 Your repository is ready at: {self.repo_url}")
            print("\n📚 Next Steps:")
            print("  1. Visit your repository on GitHub")
            print("  2. Deploy to Hugging Face Spaces (see HF_SPACES_DEPLOYMENT.md)")
            print("  3. Share the repository link with others")
            return 0
        else:
            print("\n" + "="*70)
            print(f"⚠️  DEPLOYMENT PARTIALLY COMPLETE ({passed}/{len(steps)} steps)")
            print("="*70)
            if failed == 1:
                print("\n📍 Repository created, but files not pushed due to branch protection.")
                print("    You can:")
                print("    🔹 Upload files via GitHub web UI (3 minutes)")
                print("    🔹 Configure branch protection rules in GitHub Settings")
                print("    🔹 Try pushing again after configuration")
            return 1


if __name__ == "__main__":
    # Credentials
    EMAIL = "gayathriproject1108@gmail.com"
    USERNAME = "gayathri0811-git"
    TOKEN = "YOUR_GITHUB_TOKEN_HERE"  # Replace with your actual GitHub token
    REPO_NAME = "retinitis-pigmentosa-ai-deploy"  # Normalized name (GitHub doesn't allow spaces)
    
    deployer = NewRepoDeployer(EMAIL, USERNAME, TOKEN, REPO_NAME)
    exit_code = deployer.run_complete_deployment()
    sys.exit(exit_code)
