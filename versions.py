import urllib.request
import re
from bs4 import BeautifulSoup

final_dict ={}
parent_branch_list = []
child_branch_dict = {}
child_branch_list = []
desired_parent_branch_names_dict = {}
desired_child_branch_names_dict = {}
test_plans_name = "http://bamboo.calix.local/rest/api/latest/project/PREM?expand=plans.plan.branches.branch&max-result=500"
test_plan_name_extract = urllib.request.urlopen(test_plans_name).read()
test_plans_name_list = BeautifulSoup(test_plan_name_extract, 'lxml-xml')
parent_plans_name = test_plans_name_list.find_all('plan')
branch_plan_names = test_plans_name_list.find_all('branch')

#Extracts portion of the parent plan name
for items in parent_plans_name:
    plan_name=items['name']
    enabled_flag=items['enabled']
    regexp=re.compile(r'(PREM - Test\s[\d\.]+)\s\d')
    if regexp.search(str(plan_name)) and enabled_flag=="true":
        regexp=re.match("(.*\sTest.*)\s\d", str(plan_name)).group(1)
        if regexp not in parent_branch_list:
            parent_branch_list.append(regexp)


for ver_names in parent_branch_list:
    list_name = ver_names[12:]
    desired_parent_branch_names_dict[list_name] = []

#Extracts enabled, child branch names
for items in branch_plan_names:
    branch_names = items['shortName']
    enabled_flag = items['enabled']
    plan_name = items['name']
    for name in parent_branch_list:
        if plan_name.startswith(name) and enabled_flag=="true":
            if branch_names not in child_branch_list:
                child_branch_list.append(str(branch_names))
                child_branch_dict[name] = child_branch_list

for ver_names in child_branch_list:
    desired_child_branch_names_dict[ver_names] = []

#Collect plan keys for each child branch
for items in branch_plan_names:
    planname = items['name']
    for key, value in child_branch_dict.items():
        for names in value:
            if planname.startswith(key) and items['shortName'] == names:
                plankey = items['key']
                for k, v in desired_child_branch_names_dict.items():
                    if k == names:
                        v.append(str(plankey))

#Collect plan keys for each parent branch
for items in parent_plans_name:
    planname = items['name']
    for item in parent_branch_list:
        length = len(planname)
        if planname.startswith(item) and not planname[length-1].isdigit():
            plankey = items['key']
            for key, val in desired_parent_branch_names_dict.items():
                if key in item:
                    val.append(str(plankey))

final_dict = dict(desired_child_branch_names_dict, **desired_parent_branch_names_dict)

