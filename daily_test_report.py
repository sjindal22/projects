import urllib.request
import re
from bs4 import BeautifulSoup
from plotly.offline import plot
import plotly.graph_objs as go
import datetime
import calendar
plan_name = None

class DailyTest:
    def __init__(self, plankey=None, max_result=None):

        self.plankey = plankey
        self.max_result = max_result
        self.pass_tests_date = dict()
        self.fail_tests_date = dict()
        self.plan_name = None

    def plan_build_state(self):
        i = 0
        link = "http://bamboo.calix.local/browse/"
        global plan_name
        plan_rest_api_url = "http://bamboo.calix.local/rest/api/latest/result/" + self.plankey + \
                            "/?max-result=" + str(self.max_result) + "&expand=results[:].result.labels"
        url_data = urllib.request.urlopen(plan_rest_api_url).read()
        soup = BeautifulSoup(url_data, 'lxml-xml')
        build_state = soup.find_all('buildState')
        labels = soup.find_all("labels")
        plan_result_key = soup.find_all("buildResultKey")
        start_time = (soup.find_all("buildStartedTime"))
        find_plan_name = soup.find("plan")
        self.plan_name = find_plan_name.get('name', None)
        for item, dates in zip(build_state, start_time):
            state = item.get_text()
            if state == "Successful":
                test_date = re.search("(\d{4}\-\d{2}\-\d{2})", str(dates))
                self.pass_tests_date[test_date.group(1)] = self.pass_tests_date.get(test_date.group(1), 0) + 1
            else:
                test_date_search = re.search("(\d{4}\-\d{2}\-\d{2})", str(dates))
                self.fail_tests_date[test_date_search.group(1)] = self.fail_tests_date.get(test_date_search.group(1), 0) + 1
            i += 1

    def plot_daily_result(self, pass_date, pass_count, fail_date, fail_count):
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
            title = 'IB-PREM-12.3.0 CI Tests',
            xaxis = dict(
                autotick = False,
                title = 'TEST RUN DATES',
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
        fig = plot(go.Figure(data=data, layout=layout), filename="plot_result.html")
        print(fig)

def main():
    counter = 0
    final_passed_dict = {}
    final_failed_dict = {}
    test_plans = ['PREM-TI123B', 'PREM-TI123DT', 'PREM-TI123D', 'PREM-I6B800E123', 'PREM-TI123LSF', 'PREM-TI123LTA', 'PREM-TI1238AT', 'PREM-TI123RA',
    'PREM-TI123S', 'PREM-TI123WM', 'PREM-TI123GB', 'PREM-TI123GDML', 'PREM-TI123GD', 'PREM-TI123GLTAT', 'PREM-TI1238AA', 'PREM-TI123AB',
    'PREM-TI1238ASB', 'PREM-TI123AD', 'PREM-TI1238ALSF', 'PREM-TI1238ALTA', 'PREM-TI1238GA', 'PREM-TI123GGB', 'PREM-TI1238GD', 'PREM-TI1238GLTA',
    'PREM-TI123GPD', 'PREM-TI1238LTA', 'PREM-T818B', 'PREM-T818DML', 'PREM-T818GD', 'PREM-T818LTAT']
    queried_plans_list_length = len(test_plans)
    obj = [DailyTest(l, 200) for l in test_plans]

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
                    
        #print("sorted dates list for passed test runs" + str(strf_time))
        #print("Respective count for passed test runs on date " + str(count_list))

        for key, value in final_passed_dict.items():
            if key not in final_failed_dict.keys():
                final_failed_dict[key] = 0

        for key, value in final_failed_dict.items():
            fail_dates = datetime.datetime.strptime(key, '%Y-%m-%d')
            fail_dates_list.append(fail_dates)
        fail_dates_list.sort()
        strf_fail_time = [datetime.datetime.strftime(strf_fail_time, '%Y-%m-%d') for strf_fail_time in fail_dates_list]
        for lst_itm in strf_fail_time:
            for ky, va in final_failed_dict.items():
                if lst_itm == ky:
                    fail_count_list.append(va)
                else:
                    continue

        #print("sorted dates list for failed test runs " + str(strf_fail_time))
        #print("Respective count for failed test runs on date " + str(fail_count_list))
        #print(len(strf_fail_time) is len(strf_time))
        #print(len(count_list) is len(fail_count_list))
        if counter == queried_plans_list_length:
            o.plot_daily_result(strf_time, count_list, strf_fail_time, fail_count_list)

if __name__ == "__main__":
    main()
