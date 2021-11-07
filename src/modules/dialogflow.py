import os
from google.cloud import dialogflow_v2 as Dialogflow
from dotenv import dotenv_values


class DialogFlow:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/config/creds.twilio.json"
        self.session_client = Dialogflow.SessionsClient()
        self.PROJECT_ID = dotenv_values()["PROJECT_ID"]

    def DetectIntent(self, text, session_id, language_code='pt-br'):
        session = self.session_client.session_path(self.PROJECT_ID, session_id)
        text_input = Dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = Dialogflow.types.QueryInput(text=text_input)
        _response = self.session_client.detect_intent(
            session=session, query_input=query_input).query_result.fulfillment_messages
        response = []

        for fragment in _response:
            response.append(fragment.text.text[0])

        return response

    def FetchReply(self, query, session_id):
        response = self.DetectIntent(query, session_id)
        return response
