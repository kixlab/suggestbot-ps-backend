# Backend API server for conversation annotation

This repository contains a backend API for crowdsourcing annotations on the utterances that would affect the psychological safety of the group. This interface should be used with the [frontend](https://github.com/kixlab/suggestbot-ps-front).

## Installation

```bash
git clone https://github.com/kixlab/suggestbot-instagram-context-annotator
pip install -r requirements.txt
```

## Loading datasets

```bash
python manage.py loaddata {filename} {dataset}
```

```dataset``` is the name of dataset that will be stored in the database and ```filename``` is the name of the file containing the dataset. The file should be in JSON format, and it should contain one list of utterances. Each utterance has the following structure:

```js
{
    "speaker": "C", // ID of the speaker
    "starttime": 0.08, // starttime of the utterance
    "endtime": 4.8, // endtime of the utterance
    "text": "Uh, making a profit of fifty million Euros." // content of each utterance
}
```

## Running

```bash
python manage.py runserver
```

## Available endpoints

This API server provides following endpoints for management purposes:

- ```GET /moments/export_csv/?dataset_id={dataset_id}```: Get all annotations on the dataset as a csv file.
- ```GET /moments/export_stats/```: Get an overview information of the annotation progress. e.g. number of annotations, timestamp of the last annotation, etc.
- ```PUT /moments/deduplicate/```: Remove annotations from duplicate submissions (i.e. with the same open-ended comment)
- ```PUT /surveys/export_csv/```: Get all survey responses as a csv file.
- ```PUT /surveys/deduplicate/```: Remove survey entries from duplicate submissions
- ```PUT /deactivate/```: Removes submissions from specified workers. The list of ```username``` used in ```/register/``` endpoint should be provided as a JSON.

This API server provides following API endpoints with the client.

- ```POST /register/```: Create a new session. Requires post data in the following JSON format:

```js
{
  username: {turkerId}-{dataset}-{taskType}-{initialTime}, // initialTime is the timestamp of the meeting where the turker starts annotation
  password: String // Any string is fine, as the user will participate the same batch only once
  first_name: {taskType} // Type of task
  last_name: {turkerId} Token {token}, // Stores task completion code
}
```

- ```GET /lines/get_dataset/?dataset={dataset}```: Retrieve all utterances in the specified dataset
- ```GET /moments/?dataset_id={dataset_id}```: Retrieve all annotations on the specified ```dataset_id```
- ```POST /moments/```: Create a new annotation. The client should be authenticated with a token, and the post data should be in the following JSON format:

```js
{
  affected_speaker: String,  // ID of the affected meeting participant from the annotated line. Unused in the current version
  timestamp: Number, // starttime of the line
  direction: String, // direction of the effect, either POSITIVE or NEGATIVE
  reason: String, // Reasoning from the worker
  possible_comment: String, // Any open-ended on the annotation comments
  possible_line: String, // Possible alternative utterance submitted by the worker. 
  dataset: String, // ID of dataset
  line: Number // pk of the line the annotation is attached
}
```

- ```POST /surveys/```: Create a new survey response. The client should be authenticated with a token, post data should be in the following JSON format:

```js
{
  fas1: Number,
  fas2: Number,
  fas3: Number,
  pus1: Number,
  pus2: Number,
  pus3: Number,
  aes1: Number,
  aes2: Number,
  aes3: Number,
  rws1: Number,
  rws2: Number, // Answers to UES-SF questionnnaire.
  rws3: Number, // Questions could be found from the frontend (Survey.vue)
  sanity_check: Number, // Answer on the attention check question
  free_response: String, // Feedback on the task submitted by the worker
  topic: String, // Summary of the annotated meeting log submitted by the worker
  status: String // Type of task. Current client uses Moderate-Debriefing
},
```

- ```POST /logs/```: Create a new user log. Requires token authentication and post data with following JSON format: 

```js
{
  event_name: String, // name of the event
  status: {taskType},
  payload: String // Any other relevant information, stored as JSON
}
```

