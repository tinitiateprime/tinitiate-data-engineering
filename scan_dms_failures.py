git push origin jay-api-coverage-13fix 

# 1. Create the new branch FROM your current state
git switch -c jay-api-coverage-13fix

# 2. Confirm you are on the new branch
git branch --show-current

# Expected:
# jay-api-coverage-13fix

# 3. Confirm only the intended files differ from main
git diff --name-only origin/main...HEAD

# 4. Confirm commits ahead of main
git log --oneline origin/main..HEAD

# 5. Push the new branch
git push -u origin jay-api-coverage-13fix

git diff --name-only origin/main...HEAD


git switch main
git fetch origin
git reset --hard origin/main

git status
