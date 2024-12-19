# pubsub-webhook

![cloud build status](https://storage.googleapis.com/louis-garman-ci-badges/builds/pubsub-webhook/branches/master.svg)

Convert webhooks requests to PubSub messages.

This is a Google Cloud Function that takes an incoming HTTP POST payload and forwards it to a Pub/Sub topic. That's it. It's particularly useful if you want to serve a single webhook on Google Cloud and have it trigger multiple subscribers, whether it be Cloud Functions or App Engine applications, or anything else subscribing to the topic.

![Diagram](pubsub-webhook.svg)

## Requirements

* Google Cloud

## Installation

Set some environment variables first:

* `GOOGLE_CLOUD_PROJECT`: the project in which to deploy the function
* `TOPIC_NAME`: the Pub/Sub topic to which to forward the POST payloads
* `TOPIC_PROJECT`: (optional) the project hosting the Pub/Sub topic; the default is the same project as the function

### Create Topic

Create a Cloud Pub/Sub topic:

```bash
gcloud pubsub topics create $TOPIC_NAME
```

### Configure IAM

Create a new service account for use by the Cloud Function:

```bash
gcloud iam service-accounts create webhook

```

Grant your service account permissions to publish to the topic:

```bash
gcloud pubsub topics add-iam-policy-binding $TOPIC_NAME \
    --member "serviceAccount:webhook@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
    --role roles/pubsub.publisher \
    --project ${TOPIC_PROJECT}
```

[optional a] Create a new service account to build the Cloud Function:

```bash
gcloud iam service-accounts create webhook-build

```

[optional b] Grant the permissions to your build service account:

```bash
gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member=serviceAccount:webhook-build@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
    --role=roles/logging.logWriter

gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member=serviceAccount:webhook-build@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
    --role=roles/artifactregistry.writer

gcloud projects add-iam-policy-binding ${GOOGLE_CLOUD_PROJECT} \
    --member=serviceAccount:webhook-build@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com \
    --role=roles/storage.objectViewer
```


### Deploy

```bash
gcloud functions deploy webhook \
    --source . \
    --runtime python11 \
    --region us-central1 \
    --entry-point pubsub_webhook \
    --trigger-topic new-integration-one \
    --build-service-account projects/${TOPIC_PROJECT}/serviceAccounts/webhook-build@${TOPIC_PROJECT}.iam.gserviceaccount.com \
    --service-account webhook@${TOPIC_PROJECT}.iam.gserviceaccount.com \
    --set-env-vars TOPIC_NAME=${TOPIC_NAME},TOPIC_PROJECT=${TOPIC_PROJECT}
```
Note: Remove `--build-service-account` if you are using a default service account. This command will require an authenticated request.

### Test

Run an integration test against a deployed function:

```bash
make integration
```

Ensure you've set the environment variable `TOPIC_NAME` first.
