git switch main
git fetch origin
git reset --hard origin/main

git switch -c jay-api-coverage-13fix-v2

git show --name-only --stat 27b3cf6
git show --name-only --stat 3bfcb74
git show --name-only --stat 75d574c
git show --name-only --stat 13472a3
git show --name-only --stat 5b53e67
git show --name-only --stat eaab0f5
git show --name-only --stat e17a6ae
git show --name-only --stat 0629222

git cherry-pick 27b3cf6
git cherry-pick 3bfcb74
git cherry-pick 75d574c
git cherry-pick 13472a3
git cherry-pick 5b53e67
git cherry-pick eaab0f5
git cherry-pick e17a6ae
git cherry-pick 0629222

git diff --name-only origin/main...HEAD

git push -u origin jay-api-coverage-13fix-v2

git log --oneline --reverse origin/main..jay-api-coverage-fix
