Git Steps - Create a Clean Branch for API Coverage Fix

Purpose: Create a new branch from the latest main branch so the new
merge request contains only the files changed for the current API
coverage work, instead of showing the previous 119 files again.

STEP 1 - CHECK YOUR CURRENT WORK

git status

If you have modified files that belong to the current work:

git add . git commit -m “API coverage fixes”

STEP 2 - FIND YOUR CURRENT COMMIT ID

git log –oneline -5

Example:

abc1234 API coverage fixes

Copy the commit ID for the work you want to move.

STEP 3 - SWITCH TO MAIN

git checkout main

STEP 4 - UPDATE MAIN

git pull origin main

This makes sure your local main contains the changes that were already
merged previously.

STEP 5 - CREATE A NEW CLEAN BRANCH

git checkout -b jay-api-coverage-fix-2

STEP 6 - CHERRY-PICK ONLY YOUR CURRENT WORK

git cherry-pick YOUR_COMMIT_ID

Example:

git cherry-pick abc1234

For multiple commits, cherry-pick oldest first:

git cherry-pick abc1234 git cherry-pick def5678 git cherry-pick ghi9012

IMPORTANT: If cherry-pick reports a conflict, STOP before pushing.

STEP 7 - VERIFY THE NEW BRANCH

git status

git diff –name-only main

git diff –stat main

The output should contain ONLY the files for the current work.

If you see approximately 119 files again, DO NOT create the merge
request yet.

STEP 8 - RUN TESTS

py -m pytest main-function/tests/unit -v

STEP 9 - PUSH THE NEW BRANCH

git push -u origin jay-api-coverage-fix-2

STEP 10 - CREATE THE MERGE REQUEST

Confirm:

Source branch: jay-api-coverage-fix-2

Target branch: main

Before creating the merge request, verify the changed-file count. It
should show only the files changed for the current work, not the
previous 119 files.

IMPORTANT - DO NOT DELETE THE OLD BRANCH YET

Do not delete jay-api-coverage-fix until:

1.  jay-api-coverage-fix-2 has been created successfully.
2.  Your current commits are present.
3.  Your tests pass.
4.  The new merge request contains only the expected files.

QUICK COMMAND REFERENCE

git status git add . git commit -m “API coverage fixes”

git log –oneline -5

git checkout main git pull origin main

git checkout -b jay-api-coverage-fix-2

git cherry-pick YOUR_COMMIT_ID

git status git diff –name-only main git diff –stat main

py -m pytest main-function/tests/unit -v

git push -u origin jay-api-coverage-fix-2

IF SOMETHING GOES WRONG

If git cherry-pick produces a conflict, stop before pushing.

If git diff –name-only main shows the old 119 files, stop before
creating the merge request.
