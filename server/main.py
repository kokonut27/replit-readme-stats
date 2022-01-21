import os
import json
import requests
from flask import Flask, render_template, send_from_directory, url_for, request
import shutil

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
app.config['static'] = 'static/'


ROLES = """
	id
	name
	key
	tagline
"""
SUBSCRIPTION = """
	id
	planId
	quantity
	timeCreated
"""
BOARD = """
	id
	name
	color
	description
"""
LANGUAGE = """
	id
	key
	displayName
	tagline
	icon
	category
"""
USER = f"""
	id
	fullName
  firstName
  lastName
	username
	image
	bio
	karma
	isHacker
	timeCreated
  isBannedFromBoards
	roles {{
					{ROLES}
				}}
"""
REPL = f"""
	id
	url
	title
	description
	timeCreated
	size
	imageUrl
	isPrivate
	isAlwaysOn
  user {{
					{USER}
	}}
	lang {{
					{LANGUAGE}
	}}
	origin {{
					url
	}}
"""
COMMENT = f"""
	id
	body
	timeCreated
	url
	isAnswer
	voteCount
	canVote
	hasVoted
	post {{
					id
	}}
  user {{
					{USER}
	}}
"""
POST = f"""
	id
	title
	body
	url
	commentCount
	isHidden
	isPinned
	isLocked
	isAnnouncement
	timeCreated
	isAnswered
  isAnswerable		
	voteCount
	canVote
	hasVoted
	user {{
    {USER}
  }}
	repl {{
					{REPL}
	}}
	board {{
					{BOARD}
	}}
	answer {{
					{COMMENT}
	}}
"""

url = 'https://replit.com/graphql'
headers = {
  'X-Requested-With': 'JBloves27',
  'Referrer': 'https://replit.com/graphql'
}

def parse_json(tjson):
  return json.dumps(tjson, sort_keys=True, indent=2)

def UserData(username):
  body = {'query': "query UserData { userByUsername(username: \""+str(username)+"\") { "+USER+" } }"}
  requeste = requests.post(url, data=body, headers=headers) # ['data']['userByUsername']
  if requeste.status_code != 200:
    raise Exception("Invalid User: "+username)
  else:
    return parse_json(json.loads(requests.post(url, data=body, headers=headers).text)['data']['userByUsername'])



# print(UserData("JBloves27"))



card_styles = ["default", "dark", "gradient", "gray"]

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/api/', methods=["POST", "GET"])
def all_repl_user():
  repl_user = request.args.get('username')
  style = request.args.get('style')
  if repl_user is None:
    return render_template("invalidUser.html")
  if style is None:
    style = "default"
  userexist = requests.get(f"https://replit.com/@{repl_user}/")
  if userexist.status_code != 200:
    return render_template("invalidUser.html")
  if style not in card_styles:
    return render_template("invalidStyle.html")
  if style == "default":
    body = {'query': "query UserData { userByUsername(username: \""+str(repl_user)+"\") { "+USER+" } }"}
    img_body = {'query': "query UserData { userByUsername(username: \""+str(repl_user)+"\") { image } }"}
    # request2 = Requests.post(url, data=body, headers=headers)
    avatar_url = parse_json(json.loads(requests.post(url, data=img_body, headers=headers).text)['data']['userByUsername']['image'])
    avatar_url = avatar_url.replace("\"", "")
    filename = avatar_url.split("/")[-1]
    if "\"" in filename:
      filename = filename.replace("\"", "")
    res = requests.get(avatar_url, stream = True)
    cycles = json.loads(requests.post(url, data=body, headers=headers).text)['data']['userByUsername']['karma']
    nickname = json.loads(requests.post(url, data=body, headers=headers).text)['data']['userByUsername']['fullName']


    if res.status_code == 200:
      res.raw.decode_content = True

      with open("server/static/"+filename, 'wb') as f:
        shutil.copyfileobj(res.raw, f)

      avatar = filename 
      # return send_from_directory(app.config['static'], filename, as_attachment=True)
      f.close()
    '''
        Grades:
        If grade = 1: Regular grade (A)
        If grade = 2: A little higher grade (A+)
        If grade = 3: Pretty high grade (A++)
        If grade = 4: High grade (S)
        If grade = 5: Super high grade (S+)
        If grade = 6: Pretty much only top 10% (S++)
        '''

    if int(cycles) >= 2000:
      grade = 0 + 1
    return render_template("user.html", avatar=avatar, user=repl_user, cycles=cycles, nickname=nickname)
      
@app.errorhandler(404)
def page_not_found(error):
  return render_template('404.html')
  

app.run(host="0.0.0.0", port=8080)