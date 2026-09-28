#!/usr/bin/env python3
"""
GitHub Repository Push Script
Push Retina AI project to GitHub using GitHub API and git commands
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timeout',
            'success': False
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }

def main():
    repo_path = r"C:\Users\djlga\Downloads\models for deployment"
    github_url = "https://github.com/gayathri0811-git/retina-ai.git"
    token = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_PAT_HERE")  # set via env var
    username = "gayathri0811-git"
    
    print("=" * 70)
    print("🚀 RETINA AI - GITHUB DEPLOYMENT SCRIPT")
    print("=" * 70)
    print(f"\n📁 Project: {repo_path}")
    print(f"🔗 Repository: {github_url}")
    print(f"👤 User: {username}\n")
    
    os.chdir(repo_path)
    
    # Step 1: Check Git Status
    print("[1/5] Checking Git Status...")
    status_result = run_command("git status")
    if not status_result['success']:
        print("❌ ERROR: Unable to check git status")
        print(status_result['stderr'])
        return False
    print("✅ Git repository ready")
    print(f"  └─ {status_result['stdout'].split(chr(10))[0]}")
    
    # Step 2: Check commits
    print("\n[2/5] Verifying Commits...")
    commits_result = run_command("git log --oneline -3")
    if commits_result['success']:
        commits = commits_result['stdout'].strip().split('\n')
        print(f"✅ Found {len(commits)} recent commits:")
        for commit in commits:
            print(f"  └─ {commit}")
    
    # Step 3: Verify Remote
    print("\n[3/5] Verifying Remote Configuration...")
    remote_result = run_command("git remote -v")
    if remote_result['success']:
        print("✅ Remote configured:")
        for line in remote_result['stdout'].strip().split('\n'):
            if line:
                print(f"  └─ {line}")
    
    # Step 4: Check for large files
    print("\n[4/5] Checking for Large Files...")
    files_result = run_command("git ls-files -s")
    large_files = []
    if files_result['success']:
        for line in files_result['stdout'].strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 4:
                    size_bytes = int(parts[2])
                    size_mb = size_bytes / (1024 * 1024)
                    if size_mb > 50:
                        large_files.append((parts[-1], size_mb))
        
        if large_files:
            print("⚠️  Large files detected:")
            for fname, size in large_files:
                print(f"  └─ {fname}: {size:.2f} MB")
        else:
            print("✅ No excessively large files in index")
    
    # Step 5: Push to GitHub
    print("\n[5/5] Pushing to GitHub...")
    print("This may take a few minutes depending on your internet speed...\n")
    
    push_cmd = f'git push https://{username}:{token}@github.com/{username}/retina-ai.git main -v'
    
    # Run with shell to get real-time output
    try:
        process = subprocess.Popen(
            push_cmd,
            shell=True,
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        output_lines = []
        for line in process.stdout:
            line = line.rstrip()
            output_lines.append(line)
            print(f"  {line}")
            
            if "To https://github.com" in line:
                print("\n✅ Connection established to GitHub")
            elif "Writing objects" in line:
                print("📤 Uploading project files...")
            elif "remote:" in line and ("warning" not in line.lower()):
                print(f"  📬 {line}")
        
        process.wait()
        
        if process.returncode == 0:
            print("\n" + "=" * 70)
            print("✅ SUCCESS! Project pushed to GitHub!")
            print("=" * 70)
            print(f"\n🎉 Your repository is now available at:")
            print(f"   https://github.com/gayathri0811-git/retina-ai")
            print(f"\nNext steps:")
            print(f"  1. Visit: https://github.com/gayathri0811-git/retina-ai")
            print(f"  2. Follow HF_SPACES_DEPLOYMENT.md for Hugging Face deployment")
            print(f"  3. Download models from:")
            print(f"     - Hugging Face: huggingface.co/gayathri0811-git/retina-ai")
            print(f"     - Direct: https://github.com/gayathri0811-git/retina-ai/releases")
            return True
        else:
            print(f"\n⚠️  Push returned exit code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR during push: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
