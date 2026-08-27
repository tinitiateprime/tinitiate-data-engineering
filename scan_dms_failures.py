27b3cf6  Add unit tests for API

# 1. Make sure the current commit is safely pushed
git status
git push origin jay-api-coverage-fix

# 2. Switch to main
git checkout main

# 3. Update local main
git pull origin main

# 4. Create a NEW clean branch from main
git checkout -b jay-api-coverage-fix-13

# 5. Bring ONLY your 13-file commit into the new branch
git cherry-pick 27b3cf6

# 6. Verify what changed compared with main
git diff --name-only main..HEAD

# 7. Check status
git status

# 8. Push the new branch
git push -u origin jay-api-coverage-fix-13
