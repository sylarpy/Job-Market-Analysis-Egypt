import requests as rq 
from bs4 import BeautifulSoup 
import csv 
from itertools import zip_longest
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import statistics as sts 


page_num = 0

jop_title = []
company_name = []
location = [] 
date = [] 
skills_reqire = [] 
Job_Description = [] 
links = [] 
#web scrabing
while True:
    try:
        req = rq.get(f"https://wuzzuf.net/search/jobs/?a=hpb&q=python%20developer&start={page_num}")
        src = req.content
        soup = BeautifulSoup(src, "lxml")

        jop_titles = soup.find_all("h2", {"class":"css-m604qf"})
        for title in jop_titles:
            link = title.find("a")
            if link:
                links.append("https://wuzzuf.net" + link["href"])
        company_names = soup.find_all("a", {"class":"css-17s97q8"})
        locations = soup.find_all("span", {"class":"css-5wys0k"})
        skills_reqires = soup.find_all("div", {"class":"css-y4udm8"})
        posted_new = soup.find_all("div", {"class":"css-4c4ojb"})
        posted_old = soup.find_all("div", {"class":"css-do6t5g"})
        posted = [*posted_new, *posted_old]

        count = min(len(jop_titles), len(company_names), len(locations), len(skills_reqires), len(posted), len(links))
        print(len(jop_titles), len(company_names), len(locations), len(skills_reqires), len(posted), len(links))
        for i in range(count):
            jop_title.append(jop_titles[i].text.strip())
            company_name.append(company_names[i].text.strip())
            location.append(locations[i].text.strip())
            date.append(posted[i].text.strip())
            skills_reqire.append(skills_reqires[i].text.strip())

        strong_tag = soup.find("strong")
        if strong_tag:
            paging_limit = int(strong_tag.text.strip())
        else:
            print("not found strong_tag")
            break
        if page_num > paging_limit // 15:
            print("pageing limit reached")
            break 

        page_num +=1
        print("the page reached:", page_num)

    except Exception as e:
        print("error from:", e)

for link in links:
    try:
        if not link.startswith("http"):
            link = "https://wuzzuf.net" + link
        req = rq.get(link)
        src = req.content
        soup = BeautifulSoup(src, "lxml")
        jop_divs = soup.find_all("div", {"class":"css-1uobp1k"})
        jop_ds = ""
        for ul in jop_divs:
            for li in ul.find_all("li"):
                jop_ds += li.text.strip() + "| " 

        Job_Description.append(jop_ds if jop_ds else None)
    except:
        Job_Description.append("not found") 

#make csv file
file_list = [jop_title, company_name, skills_reqire, Job_Description, date, location, links]
exported = zip_longest(*file_list)
with open(r"C:\Users\apdoi\Downloads\python developer\py_project.csv", "w", newline="", encoding="utf-8") as mf:
    wr = csv.writer(mf)
    wr.writerow(["jop_title", "company_name", "skills_reqire", "Job_Description", "date", "location", "links"])
    wr.writerows(exported)
    print("file written successfully")
 
#get top companys
df = pd.read_csv(r"C:\Users\apdoi\Downloads\python developer\py_project.csv")
top_10_company = df["company_name"].value_counts().head(10).index
df["top_10_company"] = df["company_name"].apply(lambda c: "the_top" if c in top_10_company else "Other")

def convert_to_day(text):
    if "just now" in str(text).lower() or "Today" in str(text).lower():
        return 0 
    try:
        return int(str(text).split()[0])
    except:
        return None

df["days_ago"] = df["date"].apply(convert_to_day)
#count_the top company
top_companys = df["company_name"].value_counts()
df["top_companys"] = df["company_name"].map(top_companys)
df.to_csv(r"C:\Users\apdoi\Downloads\python developer\py_project.csv", index=False)
#get the top companys stays after 10 days
the_greadet = df[(df["days_ago"] >= 10) & (df["top_companys"] >= 3) & (df["top_10_company"] == "the_top")]
the_greadet.to_csv(r"C:\Users\apdoi\Downloads\python developer\project.csv", index=False) 

days_array = df["days_ago"].dropna().values
avg = np.mean(days_array)
sum_np = np.sum(days_array > 20)

df["averge_day"] = avg
df["post_jop_than_20_d"] = sum_np
df.to_csv(r"C:\Users\apdoi\Downloads\python developer\py_project.csv", index=False)

#make matplotib art to explain  
top_companies = df["company_name"].value_counts().head(10)

plt.figure(figsize=(12, 6))
top_companies.plot(kind="bar", color="skyBlue")
plt.title("top 10 companies hiring python developer")
plt.xlabel("company_name")
plt.ylabel("Number of jop posts")
plt.tight_layout()
plt.savefig(r"C:\Users\apdoi\Downloads\python developer\pyt_project.png") 

df["days_ago"].dropna().value_counts().sort_index().plot(kind="bar", figsize=(12, 6), color="blue")
plt.title("jop posted Detibtion by days ago")
plt.xlabel("Days ago")
plt.ylabel("Number of jops")
plt.tight_layout()
plt.savefig(r"C:\Users\apdoi\Downloads\python developer\plt_project.png") 
#make seaborn art to explain
sns.barplot(x="company_name", y="days_ago", color="red", data=df)
plt.title("old vs new company posted")
plt.tight_layout()
plt.savefig(r"C:\Users\apdoi\Downloads\python developer\SNS_bar_project.png")

plt.figure(figsize=(15, 6))
sns.violinplot(x="company_name", y="days_ago", data=df[df["company_name"].isin(df["company_name"].value_counts().head(10).index)], color="red")
plt.title("avrege posting days (old vs new) per company")
plt.xlabel("company_name")
plt.ylabel("averge_days_ago")
plt.tight_layout()
plt.savefig(r"C:\Users\apdoi\Downloads\python developer\sns_vilion_project.png")
