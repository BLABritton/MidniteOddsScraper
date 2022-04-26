from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import datetime
import csv

date = datetime.datetime.now()
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.midnite.com/esports/csgo/")

WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[component=Match]")))

load_more_button = driver.find_element_by_css_selector("#content > div > div.simplebar-wrapper > div.simplebar-mask > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(3) > button")
#load all matches by clicking the load more button until it is gone
while True:
	try:
		load_more_button.click()
	except:
		break
#list of matches, each match is a list ordered by: [game_date, game_time, tourney_name, team_one, team_two, matchid, victor, team_one_odds, team_two_odds]
matches = []
#loop over matches to scrape info from each and append to master match list
for match in driver.find_elements_by_css_selector("div[component=Match]"):
	match_info = []
	#if it is a three way bet, skip adding
	if len(match.find_element_by_xpath("div[2]/a/div[2]/div/div[1]").find_elements_by_tag_name("button")) == 3:
		continue
	team_one = match.find_element_by_xpath("div[2]/a/div[1]/div[1]/div[1]/div[1]/div[2]/span").text
	team_two = match.find_element_by_xpath("div[2]/a/div[1]/div[1]/div[1]/div[2]/div[2]/span").text
	tourney_name = match.find_element_by_xpath("div[1]/div/div[1]/div/span[1]").text
	game_date = match.find_element_by_xpath("div[2]/a/div[1]/div[1]/div[2]/span[2]").text
	game_time = match.find_element_by_xpath("div[2]/a/div[1]/div[1]/div[2]/span[1]").text
	#if the match is in progress, set the date to today.
	if len(game_date) == 1:
		game_date = "{0} {1} {2}".format(date.strftime("%d"), date.strftime("%b"), date.year)
	try:
		team_one_odds = match.find_element_by_xpath("div[2]/a/div[2]/div/div[1]/button[1]/span[2]").text
	except:
		team_one_odds = "None"
	try:
		team_two_odds = match.find_element_by_xpath("div[2]/a/div[2]/div/div[1]/button[2]/span[2]").text
	except:
		team_two_odds = "None"
	if team_one_odds == "":
		team_one_odds = "None"
	if team_two_odds == "":
		team_two_odds = "None"
	matchid = match.find_element_by_xpath("div[2]/a").get_attribute("href").split("/")[6]
	if game_date == "Today":
		game_date = "{0} {1} {2}".format(date.strftime("%d"), date.strftime("%b"), date.year)
	else:
		game_date = "{0} {1}".format(game_date, date.year)
	match_info.append(game_date)
	match_info.append(game_time)
	match_info.append(tourney_name)
	match_info.append(team_one)
	match_info.append(team_two)
	match_info.append(matchid)
	match_info.append("None,")
	match_info.append(team_one_odds)
	match_info.append(team_two_odds)
	matches.append(match_info)

driver.quit()
#list of past results, will be added to from csv file below
pastResults = {}
#add all old match odds already recorded to update any odds if they have changed.
with open("results.csv", "r") as file:
	reader = csv.reader(file)
	for row in reader:
		match_info = ",".join(row[:-2])
		match_odds = ",".join(row[-2:][:2])
		pastResults[match_info] = match_odds
	file.close()
#update any old matches with new odds
for match in matches:
	match_info = ",".join(match[:-2])
	match_odds = ",".join(match[-2:][:2])
	if match_info in pastResults:
		pastResults.update({match_info: match_odds})
	else:
		pastResults[match_info] = match_odds

try:
	pastResults.pop("")
except:
	pass

with open("results.csv", "w", newline="") as write_file:
	writer = csv.writer(write_file)
	for match in pastResults.items():
		writer.writerow([match[0]+match[1]])
	file.close()