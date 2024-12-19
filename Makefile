SHELL := /bin/bash

deploy:
	gcloud beta functions deploy \
		webhook \
		--source . \
		--runtime python311 \
		--entry-point pubsub_webhook \
		--build-service-account=projects/${GOOGLE_CLOUD_PROJECT}/serviceAccounts/integration-one-webhook@nonprod-svc-lrk2.iam.gserviceaccount.com \
		--service-account integration-one-webhook@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
		--set-env-vars TOPIC_NAME=${TOPIC_NAME} \
		--trigger-http \
		--allow-unauthenticated

unit:
	python3.11 -m pytest -W ignore::DeprecationWarning -v

integration:
	./tests/integration.sh
