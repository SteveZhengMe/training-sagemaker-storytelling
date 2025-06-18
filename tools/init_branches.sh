#! /bin/bash

# create 12 branches start with g_ and end with a month name, Ex. g_Jan, g_Feb, etc.

months=("Jan" "Feb" "Mar" "Apr" "May" "Jun" "Jul" "Aug" "Sep" "Oct" "Nov" "Dec")
prefix="g"

for month in "${months[@]}"; do
    branch_name="${prefix}_${month}"
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
done
git checkout story
# remove all branches except "story" in both local and remote
# git branch | grep -v "story" | xargs git branch -D
# git branch -r | grep -v "story" | sed 's/origin\///' | xargs -I {} git push origin --delete {}
