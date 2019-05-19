git config --global user.email "tech@stanforddaily.com"
git config --global user.name "The Stanford Daily Bot"
ls | grep "xx" | while read century ; do
    ls $century | grep "x" | while read decade; do
        rm -rf .git
        git init
        git remote add origin git@bitbucket.org:thestanforddaily/$decade.git
        git add $century/$decade
        git commit -m "Updates"
        git push -f origin HEAD:master
    done
done
