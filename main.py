import os
import pickle
import seaborn as sns
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt


# Check whether a paper is related to LLMs
def is_LM_papers(title: str) -> bool:
    LM_WORDs = ["language model", "llm"]
    _is_llm_paper = False
    for _lmword in LM_WORDs:
        if _lmword in title.lower():
            _is_llm_paper = True
    return _is_llm_paper

# List of ML conference
ml_conf_names = ["neurips", "icml", "iclr"]
ml_conf_years = ["2021", "2022", "2023"]

# URL for accepted papers 
confs = {}
for _name in ml_conf_names:
    for _year in ml_conf_years:
        confs[_name + '_' + _year] = "https://" + _name + ".cc/Conferences/" + _year + "/Schedule"

# Only ICLR has the accepted paper list in 2024
confs['iclr_2024'] = "https://iclr.cc/Conferences/2024/Schedule"

for _conf_name in confs:
    _file_name = 'data/' + _conf_name + '.txt'
    
    if not os.path.isfile(_file_name):
        # Send a GET request to the URL
        response = requests.get(confs[_conf_name])

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract paper titles
            paper_titles = [title.text.strip() for title in soup.find_all('div', class_='maincardBody')]

        f = open(_file_name, 'wb')
        pickle.dump(paper_titles, f)

    else:
        f = open(_file_name, 'rb')
        paper_titles = pickle.load(f)

    confs[_conf_name] = {"lm_paper": []}

    for idx, title in enumerate(paper_titles, start=1):
        if is_LM_papers(title):
            confs[_conf_name]["lm_paper"].append(title)
    
    confs[_conf_name]["lm_paper_ratio"] = len(confs[_conf_name]["lm_paper"]) / len(paper_titles)
    
    print(_conf_name, len(paper_titles), len(confs[_conf_name]["lm_paper"]), confs[_conf_name]["lm_paper_ratio"])

plot_data = {}
for _name in ml_conf_names:
    plot_data[_name] = []
    for _year in ml_conf_years:
        plot_data[_name].append(confs[_name + '_' + _year]["lm_paper_ratio"] * 100)

plot_data["iclr"].append(confs["iclr_2024"]["lm_paper_ratio"] * 100)

sns.set_theme(font_scale=3)

for _name in ml_conf_names:
    if _name == "iclr":
        plt.plot(ml_conf_years + [2024], plot_data[_name], 'o-', label=_name)
    else:
        plt.plot(ml_conf_years, plot_data[_name], 'o-', label=_name)

plt.legend()
plt.xlabel("Year")
plt.ylabel("Ratio of LLM Papers [%]")
plt.show()
