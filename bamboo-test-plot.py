import urllib.request
import unittest
import argparse
import sys
import re
from bs4 import BeautifulSoup
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.figure_factory as ff
import datetime
from versions import final_dict

plan_name = None
d = len(final_dict.keys())
count_loop = 0
data_matrix =[['P-R Release', 'Plot Result']]
'''
def parse_max_age():
    parse = argparse.ArgumentParser()
    parse.add_argument("--max_age", help="Retrieves past N days test results", type=int, default=10)
    args = parse.parse_args()
    return args.max_age
'''
def extract_test_run_data(test_plans, branch):
    counter = 0
    final_passed_dict = {}
    final_failed_dict = {}
    queried_plans_list_length = len(test_plans)
    obj = [DailyTest(10, l, 1000, branch) for l in test_plans]

    for o in obj:
        counter += 1
        final_failed_tests_date = dict()
        final_passed_tests_date = dict()
        dates = []
        fail_dates_list = []
        strf_time = []
        count_list = []
        fail_count_list = []
        strf_fail_time = []

        o.plan_build_state()

        for k, v in o.pass_tests_date.items():
            count = 0
            dates_count = len(final_passed_dict.keys())
            if len(final_passed_dict.keys()) == 0:
                final_passed_dict[k] = v
            else:
                for itm, val in final_passed_dict.items():
                    if itm == k:
                        val += v
                        final_passed_dict[itm] = val
                        break
                    count += 1
                    if count == dates_count:
                        final_passed_dict[k] = v
                        break

        for k, v in o.fail_tests_date.items():
            count = 0
            dates_count = len(final_failed_dict.keys())
            if len(final_failed_dict.keys()) == 0:
                final_failed_dict[k] = v
            else:
                for itm, val in final_failed_dict.items():
                    if itm == k:
                        val += v
                        final_failed_dict[itm] = val
                        break
                    count += 1
                    if count == dates_count:
                        final_failed_dict[k] = v
                        break

        for key, value in final_failed_dict.items():
            if key not in final_passed_dict.keys():
                final_passed_dict[key] = 0

        for k, v in final_passed_dict.items():
            pass_dates = datetime.datetime.strptime(k, '%Y-%m-%d')
            dates.append(pass_dates)
        dates.sort()
        strf_time = [datetime.datetime.strftime(strf_time, '%Y-%m-%d') for strf_time in dates]
        for lst_itm in strf_time:
            for ky, va in final_passed_dict.items():
                if lst_itm == ky:
                    count_list.append(va)
                else:
                    continue

        for key, value in final_passed_dict.items():
            if key not in final_failed_dict.keys():
                final_failed_dict[key] = 0

        for key, value in final_failed_dict.items():
            fail_dates = datetime.datetime.strptime(key, '%Y-%m-%d')
            fail_dates_list.append(fail_dates)
        fail_dates_list.sort()
        strf_fail_time = [datetime.datetime.strftime(strf_fail_time, '%Y-%m-%d') for strf_fail_time in
                          fail_dates_list]
        for lst_itm in strf_fail_time:
            for ky, va in final_failed_dict.items():
                if lst_itm == ky:
                    fail_count_list.append(va)
                else:
                    continue

        if counter == queried_plans_list_length:
            o.plot_daily_result(strf_time, count_list, strf_fail_time, fail_count_list)

class DailyTest:
    global count_loop

    def __init__(self, max_age, plankey=None, max_result=None, release_branch=None):

        self.plankey = plankey
        self.max_result = max_result
        self.pass_tests_date = dict()
        self.fail_tests_date = dict()
        self.plan_name = None
        self.release_branch = release_branch
        self.max_age = max_age

    def plan_build_state(self):
        i = 0
        queried_test_runs = []
        link = "http://bamboo.calix.local/browse/"
        global plan_name
        time_now = datetime.datetime.now()
        queried_time = time_now - datetime.timedelta(self.max_age)
        plan_rest_api_url = "http://bamboo.calix.local/rest/api/latest/result/" + self.plankey + \
                            "/?max-result=" + str(self.max_result) + "&expand=results[:].result.labels"

        url_data = urllib.request.urlopen(plan_rest_api_url).read()
        soup = BeautifulSoup(url_data, 'lxml-xml')
        build_state = soup.find_all('buildState')
        labels = soup.find_all("labels")
        plan_result_key = soup.find_all("buildResultKey")
        start_time = soup.find_all("buildStartedTime")
        find_plan_name = soup.find("plan")
        self.plan_name = find_plan_name.get('name', None)

        for test_run_date in start_time:
            parsed_test_run = re.search(".*>(\d{4}-\d{2}-\d{2})T([\d\:\.]*)-", str(test_run_date))
            time = parsed_test_run.group(1) + " " + parsed_test_run.group(2)
            extracted_time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
            if queried_time < extracted_time :
                queried_test_runs.append(extracted_time)

        for item, dates in zip(build_state, queried_test_runs):
            state = item.get_text()
            if state == "Successful":
                test_date = re.search("(\d{4}\-\d{2}\-\d{2})", str(dates))
                self.pass_tests_date[test_date.group(1)] = self.pass_tests_date.get(test_date.group(1), 0) + 1
            else:
                test_date_search = re.search("(\d{4}\-\d{2}\-\d{2})", str(dates))
                self.fail_tests_date[test_date_search.group(1)] = self.fail_tests_date.get(test_date_search.group(1), 0) + 1
            i += 1

    def plot_daily_result(self, pass_date, pass_count, fail_date, fail_count):
        global count_loop
        temp_list =[]
        trace1 = go.Bar(
            x=pass_date,
            y=pass_count,
            name = 'Successful CI Tests',
            marker=dict(color='green')
        )
        trace2 = go.Bar(
            x=fail_date,
            y=fail_count,
            name='Failed CI Tests',
            marker=dict(color='red')
        )
        data = [trace1, trace2]
        layout = go.Layout(
            showlegend=True,
            title = self.release_branch,
            xaxis = dict(
                autotick = False,
                title = 'TEST RUNS FOR PAST ' + str(self.max_age) + ' DAY/DAYS',
                titlefont =dict(
                    size=15,
                    color='black'
                )
            ),
            yaxis = dict(
                autotick=False,
                dtick=3,
                title = 'NUMBER OF TEST RUNS',
                titlefont =dict(
                    size=15,
                    color='black'
            )
        )
        )
        fig = plot(go.Figure(data=data, layout=layout), filename="plot_result_" + self.release_branch + ".html")
        data_matrix.append([self.release_branch, '<a href="http://' + fig + '">Test Run Plot</a>'])
        count_loop += 1

class DynamicClassBase(unittest.TestCase):
    longMessage = True

def results(plans, build_branch):
    global count_loop
    global data_matrix
    def test(self):
        extract_test_run_data(plans, build_branch)
        if count_loop == d:
            table = ff.create_table(data_matrix)
            plot(table, filename='report_table.html')
    return test

if __name__ == '__main__':
    klass_suite = []
    test_branches = final_dict
    for release_name, test_plans in test_branches.items():
        test_final_report = results(test_plans, release_name)
        class_name = 'test_{0}'.format(release_name)
        globals()[class_name] = type(class_name,
                                   (DynamicClassBase,),
                                   {'test_gen_{0}'.format(release_name): test_final_report})
        klass_suite.append(globals()[class_name])

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in klass_suite:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
