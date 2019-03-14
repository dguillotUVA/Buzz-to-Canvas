from canvasapi import Canvas
import json
import requests
import time

API_URL = "https://canvas.instructure.com" #free Canvas URL, modify as needed

buzz_username = "" #string with username
buzz_password = "" #string with password
API_KEY = "" #string with Canvas API key generated in account
buzz_course_id = 1 #int with Buzz course ID
canvas_course_id = 1 #int with Canvas course ID

canvas = Canvas(API_URL, API_KEY)
#account = canvas.get_account(1)

cookies = {
}

headers = {
    'Content-Type': 'application/json',
    'accept': 'application/json',
}

data = '{"request": {"cmd": "login", "username": "uva/{}", "password": "{}}"} }'.format(buzz_username, buzz_password)

response = requests.post('https://gls.agilix.com/cmd', headers=headers, cookies=cookies, data=data)
login_info = json.loads(response.text)
token = login_info["response"]["_token"]

print("Logged in")

params = (
    ('cmd', 'getitemlist'),
    ('entityid', buzz_course_id),
    ('query', '/type="Assessment"'),
    ('_token', token)
)

response = requests.get('https://gls.agilix.com/cmd', headers=headers, params=params, cookies=cookies)

all_assess = json.loads(response.text)

course = canvas.get_course(canvas_course_id)

for assess in all_assess["response"]["items"]["item"]:
	new_quiz = {}
	new_quiz["title"] = assess["data"]["title"]["$value"]
	new_quiz["scoring_policy"] = "keep_highest"
	try:
		if assess["data"]["gradable"]["$value"] == "true":
			new_quiz["quiz_type"] = "assignment"
	except:
		new_quiz["quiz_type"] = "practice_quiz"

	quiz = course.create_quiz(quiz=new_quiz)
	print("Quiz {} created".format(new_quiz["title"]))
#	try:
	for question in assess["data"]["questions"]["question"]:
		params = (
		    ('cmd', 'getquestion'),
		    ('entityid', buzz_course_id),
		    ('questionid', question["id"]),
		    ('_token', token)
		)
		response = requests.get('https://gls.agilix.com/cmd', headers=headers, params=params, cookies=cookies)
		question_details = json.loads(response.text)["response"]["question"]
		
		new_question = {}

		new_question["question_text"] = question_details["body"]["$value"]
		try:
			new_question["points_possible"] = question_details["points"]
		except:
			new_question["points_possible"] = 1

		if question_details["interaction"]["type"] == "choice":
			new_question["question_type"] = "multiple_choice_question"
			ans = []
			for x in question_details["interaction"]["choice"]:
				if x["id"] == question_details["answer"]["value"][0]["$value"]:
					weight = 1
				else:
					weight = 0
				ans += [{"answer_text": x["body"]["$value"], "answer_weight": weight}]
			new_question["answers"] = ans

		elif question_details["interaction"]["type"] == "answer":
			new_question["question_type"] = "multiple_answer_question"

		elif question_details["interaction"]["type"] == "match":
			new_question["question_type"] = "matching_question"

		#elif question_details["interaction"]["type"] == "order": #Does this exist in Canvas?
		#	new_question["question_type"] = "multiple_choice_question"

		elif question_details["interaction"]["type"] == "text": #may be short answer or fill in multiple blanks
			new_question["question_type"] = "short_answer_question"

		elif question_details["interaction"]["type"] == "essay":
			new_question["question_type"] = "essay_question"

		elif question_details["interaction"]["type"] == "composite":
			new_question["question_type"] = "multiple_choice_question"

		elif question_details["interaction"]["type"] == "custom":
			new_question["question_type"] = "multiple_choice_question"

		else:
			new_question["question_type"] = "essay_question"
		print(new_question)
		quiz.create_question(question = new_question)
		print("Question added")
		time.sleep(.5)

#	except:
#		pass
	time.sleep(.1)