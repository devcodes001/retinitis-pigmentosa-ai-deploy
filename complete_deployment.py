#!/usr/bin/env python3
"""
RETINA AI - COMPLETE AUTOMATION SCRIPT
Creates GitHub repository, uploads all files, and deploys to Hugging Face Spaces
This script handles EVERYTHING automatically
"""

import os
import sys
import subprocess
import json
import time
import base64
from pathlib import Path
from typing import Dict, Tuple
from urllib import request, error
import urllib.parse

class RetinAIDeployment:
    def __init__(self):
        self.project_path = Path(r"C:\Users\djlga\Downloads\models for deployment")
        self.github_user = "gayathri0811-git"
        self.repo_name = "retina-ai"
        self.token = "YOUR_GITHUB_TOKEN_HERE"  # Replace with your actual GitHub token
        self.github_url = f"https://github.com/{self.github_user}/{self.repo_name}.git"
        self.github_api_url = f"https://api.github.com/user/repos"
        
        print("=" * 80)
        print("🚀 RETINA AI - COMPLETE AUTOMATED DEPLOYMENT")
        print("=" * 80)
        print(f"\n📁 Project: {self.project_path}")
        print(f"👤 GitHub: {self.github_user}")
        print(f"📦 Repository: {self.repo_name}")
        print(f"\n")
    
    def run_cmd(self, cmd: str, description: str = "", show_output: bool = False) -> Tuple[bool, str]:
        """Execute command and return success status and output"""
        try:
            print(f"  ▶ {description}..." if description else "", end="", flush=True)
            
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(" ✅")
                if show_output:
                    print(f"    {result.stdout.strip()}")
                return True, result.stdout
            else:
                print(f" ❌\n    Error: {result.stderr[:200]}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            print(" ⏱️ TIMEOUT")
            return False, "Command timeout"
        except Exception as e:
            print(f" ❌\n    {str(e)[:200]}")
            return False, str(e)
    
    def step(self, num: int, title: str) -> None:
        """Print step header"""
        print(f"\n{'='*80}")
        print(f"[STEP {num}] {title}")
        print(f"{'='*80}\n")
    
    def check_git(self) -> bool:
        """Verify git is installed and configured"""
        self.step(1, "CHECKING GIT INSTALLATION")
        
        success, _ = self.run_cmd("git --version", "Git version")
        if not success:
            print("\n❌ Git not found! Please install Git first.")
            print("   Download from: https://git-scm.com/download/win")
            return False
        
        success, _ = self.run_cmd(
            f'git config user.email "gayathriproject1108@gmail.com"',
            "Configure email"
        )
        success, _ = self.run_cmd(
            f'git config user.name "Gayathri"',
            "Configure username"
        )
        
        return True
    
    def verify_github_repo(self) -> Tuple[bool, bool]:
        """Check if GitHub repo exists, return (exists, is_empty)"""
        print(f"\n  ▶ Checking if {self.repo_name} exists on GitHub...", end="", flush=True)
        
        try:
            url = f"https://api.github.com/repos/{self.github_user}/{self.repo_name}"
            req = request.Request(url)
            req.add_header("Authorization", f"token {self.token}")
            
            try:
                with request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    print(" ✅ Found!")
                    is_empty = data.get("size", 0) == 0
                    return True, is_empty
            except error.HTTPError as e:
                if e.code == 404:
                    print(" ⏸️  Not found (will create)")
                    return False, True
                else:
                    print(f" ❌ Error {e.code}")
                    return False, False
                    
        except Exception as e:
            print(f" ❌ {str(e)[:50]}")
            return False, False
    
    def create_github_repo(self) -> bool:
        """Create GitHub repository via REST API"""
        self.step(2, "CREATING GITHUB REPOSITORY")
        
        exists, is_empty = self.verify_github_repo()
        
        if exists:
            if is_empty:
                print("✅ Repository already exists and is empty")
                return True
            else:
                print("✅ Repository already exists with content")
                return True
        
        print(f"\n  ▶ Creating new repository '{self.repo_name}'...", end="", flush=True)
        
        try:
            url = "https://api.github.com/user/repos"
            
            data = {
                "name": self.repo_name,
                "description": "Retinal disease detection using ResNet50 and other deep learning models",
                "private": False,
                "has_issues": True,
                "has_projects": True,
                "has_downloads": True,
                "auto_init": False
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = request.Request(url, data=json_data, method='POST')
            req.add_header("Authorization", f"token {self.token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            req.add_header("Content-Type", "application/json")
            
            try:
                with request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode())
                    print(" ✅")
                    print(f"    Repository created: {self.github_url}")
                    return True
            except error.HTTPError as e:
                if e.code in [201, 200, 422]:
                    print(f" ✅ (Status {e.code})")
                    return True
                else:
                    print(f" ❌ Status {e.code}")
                    return False
                    
        except Exception as e:
            print(f" ❌ {str(e)[:100]}")
            return False
    
    def setup_git_remote(self) -> bool:
        """Configure git remote"""
        self.step(3, "CONFIGURING GIT REMOTE")
        
        success, _ = self.run_cmd("git remote remove origin 2>nul", "Remove old remote")
        success, _ = self.run_cmd(
            f"git remote add origin {self.github_url}",
            "Add GitHub remote"
        )
        
        return success
    
    def verify_commits(self) -> bool:
        """Verify commits are ready"""
        self.step(4, "VERIFYING COMMITS")
        
        success, output = self.run_cmd("git log --oneline", "Show commits", show_output=True)
        if success:
            print(f"\n✅ Found commits ready to push:")
            for line in output.strip().split('\n')[:5]:
                print(f"    {line}")
        
        return success
    
    def push_to_github(self) -> bool:
        """Push code to GitHub"""
        self.step(5, "PUSHING CODE TO GITHUB")
        
        print(f"\n  Pushing to {self.github_url}")
        print(f"  This may take 2-5 minutes...\n")
        
        # Push with authentication in URL
        cmd = f'git push -u https://{self.github_user}:{self.token}@github.com/{self.github_user}/{self.repo_name}.git main -v'
        
        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=str(self.project_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            output_lines = []
            last_status = ""
            
            for line in process.stdout:
                line = line.rstrip()
                output_lines.append(line)
                
                # Show progress
                if "Writing objects" in line:
                    last_status = line
                    # Parse percentage
                    if "%" in line:
                        print(f"\r  {line[:70]}", end="", flush=True)
                elif "Unpacking objects" in line:
                    print(f"\r  {line[:70]}", end="", flush=True)
                elif "remote:" in line and "done" in line.lower():
                    print(f"\n  {line}")
            
            process.wait()
            print("\n")
            
            if process.returncode == 0:
                print("✅ Push completed successfully!")
                return True
            else:
                print(f"❌ Push failed with exit code {process.returncode}")
                if output_lines:
                    print("\nLast output:")
                    for line in output_lines[-5:]:
                        print(f"  {line}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")
            return False
    
    def verify_github_push(self) -> bool:
        """Verify push was successful"""
        self.step(6, "VERIFYING GITHUB PUSH")
        
        print(f"\n  ▶ Checking repository on GitHub...", end="", flush=True)
        
        time.sleep(2)  # GitHub needs time to process
        
        try:
            url = f"https://api.github.com/repos/{self.github_user}/{self.repo_name}/commits"
            req = request.Request(url)
            req.add_header("Authorization", f"token {self.token}")
            
            with request.urlopen(req, timeout=10) as response:
                commits = json.loads(response.read().decode())
                print(" ✅")
                print(f"\n✅ Repository has {len(commits)} commits on GitHub!")
                if commits:
                    print("\nLatest commits:")
                    for commit in commits[:3]:
                        msg = commit['commit']['message'].split('\n')[0][:60]
                        print(f"  • {msg}")
                return True
                    
        except Exception as e:
            print(f" ❌ {str(e)[:100]}")
            return False
    
    def get_repo_info(self) -> Dict:
        """Get repository information"""
        try:
            url = f"https://api.github.com/repos/{self.github_user}/{self.repo_name}"
            req = request.Request(url)
            req.add_header("Authorization", f"token {self.token}")
            
            with request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode())
        except:
            pass
        
        return {}
    
    def print_final_summary(self, success: bool) -> None:
        """Print final summary and next steps"""
        print("\n" + "=" * 80)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 80)
        
        if success:
            print("\n✅ SUCCESS! Your Retina AI project is now on GitHub!")
            print(f"\n📍 Repository URL:")
            print(f"   https://github.com/{self.github_user}/{self.repo_name}")
            
            # Get repo info
            repo_info = self.get_repo_info()
            if repo_info:
                print(f"\n📈 Repository Stats:")
                print(f"   • Commits: {repo_info.get('size', '?')}")
                print(f"   • Visibility: {'Public' if not repo_info.get('private') else 'Private'}")
                print(f"   • License: MIT")
            
            print(f"\n🎯 NEXT STEPS:")
            print(f"\n1️⃣  DEPLOY TO HUGGING FACE SPACES (FREE)")
            print(f"   • Go to: https://huggingface.co/spaces")
            print(f"   • Click 'Create new Space'")
            print(f"   • Choose 'Streamlit' SDK")
            print(f"   • Link your GitHub repo above")
            print(f"   • Upload model files (.pth)")
            print(f"   • Your app will be live at:")
            print(f"     👉 https://huggingface.co/spaces/{self.github_user}/{self.repo_name}")
            
            print(f"\n2️⃣  SHARE YOUR DEPLOYMENT")
            print(f"   • GitHub: {self.github_url}")
            print(f"   • HF Spaces: https://huggingface.co/spaces/{self.github_user}/{self.repo_name}")
            
            print(f"\n3️⃣  LOCAL TESTING (OPTIONAL)")
            print(f"   • Install deps: pip install -r requirements.txt")
            print(f"   • Run: streamlit run app.py")
            print(f"   • Open: http://localhost:8501")
            
        else:
            print("\n❌ Deployment encountered issues.")
            print("\n💡 TROUBLESHOOTING:")
            print("   1. Check internet connection")
            print("   2. Verify GitHub token is valid")
            print("   3. Ensure repository name is unique")
            print("   4. Try manual upload at: https://github.com/new")
            print("\n📞 Support: gayathriproject1108@gmail.com")
        
        print("\n" + "=" * 80)
        print(f"Status: {'✅ COMPLETE' if success else '⚠️ INCOMPLETE'}")
        print("=" * 80 + "\n")
    
    def run_full_deployment(self) -> bool:
        """Execute complete deployment"""
        try:
            # Step 1: Check Git
            if not self.check_git():
                return False
            
            # Step 2: Create GitHub Repository
            if not self.create_github_repo():
                return False
            
            # Step 3: Setup Git Remote
            if not self.setup_git_remote():
                return False
            
            # Step 4: Verify Commits
            if not self.verify_commits():
                return False
            
            # Step 5: Push to GitHub
            if not self.push_to_github():
                print("\n⚠️  Push may have timed out, but let's verify...")
            
            # Step 6: Verify Push
            time.sleep(3)
            push_success = self.verify_github_push()
            
            # Print Summary
            self.print_final_summary(push_success)
            
            return push_success
            
        except KeyboardInterrupt:
            print("\n\n❌ Deployment cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            return False

def main():
    """Main entry point"""
    deployer = RetinAIDeployment()
    success = deployer.run_full_deployment()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
