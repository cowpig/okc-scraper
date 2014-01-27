from Session import *
from BeautifulSoup import BeautifulSoup
import random, time, cPickle, re

def profile_dict(session, username, q_a):
	try:
		print "downloading profile info for user: {}".format(username)
	except:
		print "downloading profile info for user with non-ASCII name"

	html = session._request_page(u"http://www.okcupid.com/profile/{}".format(username))
	soup = BeautifulSoup(html)

	info = {}

	# get info from the right side panel
	for dd in soup.findAll("dd"):
		if "ajax" in dd.__str__():
			attribute = dd['id'][5:]
			if attribute == "height":
				h_re = re.search(".*\((.*)m\).*", dd.getString())
				if h_re != None:
					info[attribute] = float(h_re.group(1))
				else:
					info[attribute] = 0.0
			else:
				info[attribute] = dd.getString()

	for i in xrange(10):
		essay = soup.findAll("div", {"id":"essay_text_{}".format(i)})
		if len(essay):
			info['essay_{}'.format(i)] = essay[0].string

	userlist = soup.find("ul", {"id":"similar_users_list"})
	similar_users = []
	for l in userlist.findAll("li"):
		if int(l.find("span", {"class":"age"}).string) < 33:
			similar_users.append(l.find("a", {"class":"name"}).string)

	info["similar_users"] = similar_users

	wait(1, 4)

	info['q_a'] = getQuestions(session, username, q_a)

	return info

def getQuestions(session, username, q_a):
	questions = []

	html = session._request_page(u"http://www.okcupid.com/profile/{}/questions?cf=profile".format(username))
	link = u"http://www.okcupid.com/profile/{}/questions?she_care=1".format(username)
	while True:
		try:
			wait(0, 1)
			html = session._request_page(link)
			soup = BeautifulSoup(html)
			for q in soup.findAll("div", {"id":re.compile("question_")}):
				q_str = q.find("p", {"class":"qtext"}).string
				a_str = q.find("p", {"class":"answer target clearfix"})
				a_str = a_str.find("span", {"id":re.compile("answer_target")}).text

				if len(a_str):
					questions.append(q_a.get_indices(q_str, a_str))
			try:
				next_ = soup.find("li", {"class" : "next"})
				link = next_.find("a", {"href":re.compile("questions.*she_care")}).get("href")
				link = u"http://www.okcupid.com" + link
			except AttributeError:
				break
		except Exception as e:
			print e
			import pdb;pdb.set_trace()


	print "Scraped {} questions.".format(len(questions))
	return questions


def wait(i, j):
	time.sleep(i + random.random()*j)

def save_images(session, username):
	html = session._request_page(u"http://www.okcupid.com/profile/{}/photos?cf=profile".format(username))
	soup = BeautifulSoup(html)

def save_image(session, url, filename):
	r = session.session.get(url, stream=True)
	if r.status_code == 200:
	    with open(filename, 'wb') as f:
	        for chunk in r.iter_content(1024):
	            f.write(chunk)

def save(users, infos, q_a):
	with open("okc_data.pkl", "wb") as f:
		cPickle.dump((users, infos, q_a), f)

class Questions:
	def __init__(self):
		self.questions = {}

	def get_indices(self, question, answer):
		if question not in self.questions:
			i = len(self.questions.keys())
			self.questions[question] = {'i':i, 'a':[answer]}

		if answer not in self.questions[question]['a']:
			self.questions[question]['a'].append(answer)

		return (self.questions[question]['i'], self.questions[question]['a'].index(answer))


import argparse
parser = argparse.ArgumentParser(description='okc scraper')
parser.add_argument('username', help='username')
parser.add_argument('password', help='password')
args = parser.parse_args()

if __name__ == "main":
    session = OKCSession(args.username, args.password)
    session.login()

    users = set([u"RedRovir", u"DearPrudenceMTL", u"jennmtl", u"KimAmore", u"blondy90_", u"findmeparis", u"Nathalie90"])
    infos = {}
    q_a = Questions()
    unscraped_users = list(users - set(infos.keys()))

    while True:
	    next_one = random.choice(unscraped_users)
	    infos[next_one] = profile_dict(session, next_one, q_a)

	    if len(infos) % 20 == 0:
		    save(users, infos, q_a)

	    users.update(infos[next_one]['similar_users'])
	    unscraped_users = list(users - set(infos.keys()))

	    if len(unscraped_users) == 0:
		    break

    save(users, infos, q_a)
