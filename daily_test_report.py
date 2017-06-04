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
        self.passed_tests = dict()
        self.failed_tests = dict()
        self.pass_tests_date = dict()
        self.fail_tests_date = dict()
        self.bamboo_failed_test = {}
        self.bamboo_failed_versions_links = {}
        self.new_passed_dict = {}
        self.new_failed_dict = {}
        self.version1 = []
        self.version2 = []
        self.final_label = []
        self.passed_nums = []
        self.failed_nums = []
        self.list_of_urls = []
        self.final_failed_nums = []
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

        for key, value in self.bamboo_failed_test.items():
            key1 = key.split('_')
            key = key1[1]
            self.bamboo_failed_versions_links[key] = value

            # print ("Failed Test Run versions are" + str(self.bamboo_failed_versions_links))

    def dict_without_prem_tags(self, prem_tagged_versions_dictionary, untagged_passed_dict, version):

        for a, b in prem_tagged_versions_dictionary.items():
            a = str(a)
            a = a.split("_")
            version.append(a[1])
            untagged_passed_dict[a[1]] = b

    def print_new_passed_failed_dict(self):
        self.dict_without_prem_tags(self.passed_tests, self.new_passed_dict, self.version1)
        self.dict_without_prem_tags(self.failed_tests, self.new_failed_dict, self.version2)

    def sort_image_version_list(self):
        val1 = []
        parsed_version = []
        sorted_list = []

        for y, z in self.new_failed_dict.items():
            if y not in self.version1:
                self.version1.append(y)

        for label_values in self.version1:
            val1 = label_values.split("-")
            parsed_version.append(int(val1[-1]))
            sorted_list = sorted(parsed_version)

        branch = val1[0] + '-' + val1[1] + '-' + val1[2]

        for build_number in sorted_list:
            version = branch + '-' + str(build_number)
            self.final_label.append(version)

            # print("\nFinal sorted list of labels is " + str(self.final_label))

    def list_sorted_test_runs(self, new_untagged_dict, test_run_num_list):
        j = 0
        for items_in_list in self.final_label:
            j = 0
            for temp, values in new_untagged_dict.items():
                if items_in_list == temp:
                    test_run_num_list.append(values)
                else:
                    j += 1
                    if j == len(new_untagged_dict.values()):
                        test_run_num_list.append(0)
                        j = 0

    def failed_passed_list_nums(self):
        self.list_sorted_test_runs(self.new_passed_dict, self.passed_nums)
        self.list_sorted_test_runs(self.new_failed_dict, self.failed_nums)
        # print ("\nPassed test run numbers " + str(self.passed_nums))
        # print ("\nFailed test run numbers " + str(self.failed_nums))

    def sort_failed_urls(self):
        for items_in_list in self.final_label:
            h = 0
            m = 0
            for items, valu in self.new_failed_dict.items():
                if items_in_list == items:
                    self.final_failed_nums.append(valu)
                else:
                    h += 1
                    if h == len(self.new_failed_dict.values()):
                        self.final_failed_nums.append(0)
                        h = 0

            for key1, val1 in self.bamboo_failed_versions_links.items():
                if items_in_list == key1:
                    self.list_of_urls.append(val1)
                else:
                    m += 1
                    if m == len(self.bamboo_failed_versions_links.values()):
                        self.list_of_urls.append(0)
                        m = 0
                        # print("Sorted failed urls " + str(self.list_of_urls))

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
        #o.print_new_passed_failed_dict()
        #o.sort_image_version_list()
        #o.failed_passed_list_nums()
        #o.sort_failed_urls()

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
        print("Final passed date dictionary to be plotted is: " + str(final_passed_dict))

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
        print("Final failed date dictionary to be plotted is: " + str(final_failed_dict))

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
        print("sorted dates list for passed test runs" + str(strf_time))
        print("Respective count for passed test runs on date " + str(count_list))

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

        print("sorted dates list for failed test runs " + str(strf_fail_time))
        print("Respective count for failed test runs on date " + str(fail_count_list))
        print("\n--")
        print(len(strf_fail_time) is len(strf_time))
        print(len(count_list) is len(fail_count_list))
        print("\n--------")
        if counter == queried_plans_list_length:
            o.plot_daily_result(strf_time, count_list, strf_fail_time, fail_count_list)


if __name__ == "__main__":
    main()
