# Deploying
To deploy server to Cloud RunL
```
cd server/play
gcloud builds submit --config=cloudbuild-<staging|prod>.yaml
```

To deploy frontend site to Firebase Hosting
```
firebase deploy --only hosting --project sss-flash-math-fun
```
