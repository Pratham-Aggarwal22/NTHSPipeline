# The funtion that reads the repsonse from the speech_handler takes the question from the call_handler (sends the id of question for which the response was generated) and then checks the response

# IF-else condition, if answer is correct, return "Next" to the call_handler and sends the exact answer to be stored to the storage_handler
# if answer is incorrect, generates the follow-up question, sends the "No" to call_handler, sneds the follow-up question to Speech_handler (to covnert from text to speech)