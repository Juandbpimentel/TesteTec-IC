mv Dockerfile.prod Dockerfile

gcloud app deploy app.yaml --quiet

rm Dockerfile