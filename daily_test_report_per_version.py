import urllib
from bs4 import BeautifulSoup
from plotly.offline import plot
import plotly.graph_objs as go

plan_name = None

class DailyTest:

    def __init__(self, plankey=None, max_result=None):

        self.plankey = plankey
        self.max_result = max_result
        self.passed_tests = dict()
        self.failed_tests = dict()
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
        url_data = urllib.urlopen(plan_rest_api_url).read()
        soup = BeautifulSoup(url_data, 'lxml-xml')
        build_state = soup.find_all('buildState')
        labels = soup.find_all("labels")
        plan_result_key = soup.find_all("buildResultKey")
        find_plan_name = soup.find("plan")
        self.plan_name = find_plan_name.get('name', None)
        for item in build_state:
            state = item.get_text()
            if state == "Successful":
                label = labels[i].find('label').get('name', None)
                self.passed_tests[label] = self.passed_tests.get(label, 0) + 1

            else:
                build_test_summary = soup.find("buildTestSummary")
                try:
                    if build_test_summary != "No tests found":
                        ver = labels[i].find('label').get('name', None)
                        self.failed_tests[ver] = self.failed_tests.get(ver, 0) + 1
                        self.bamboo_failed_test.setdefault(str(ver), []).append(str(link + plan_result_key[i].get_text()))
                    else:
                        raise
                except:
                    pass
            i += 1

        for key, value in self.bamboo_failed_test.items():
            key1 = key.split('_')
            key = key1[1]
            self.bamboo_failed_versions_links[key] = value

        #print ("Failed Test Run versions are" + str(self.bamboo_failed_versions_links))

    def dict_without_prem_tags(self, prem_tagged_versions_dictionary, untagged_passed_dict, version):

        for a, b in prem_tagged_versions_dictionary.items():
            a = str(a)
            a = a.split("_")
            version.append(a[1])
            untagged_passed_dict[a[1]] = b

    def print_new_passed_failed_dict(self):
        self.dict_without_prem_tags(self.passed_tests, self.new_passed_dict, self.version1)
        self.dict_without_prem_tags(self.failed_tests, self.new_failed_dict, self.version2)
        #print("New passed dictionary " + str(self.new_passed_dict))
        #print("New Failed dictionary " + str(self.new_failed_dict))

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

        #print("\nFinal sorted list of labels is " + str(self.final_label))

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
        #print ("\nPassed test run numbers " + str(self.passed_nums))
        #print ("\nFailed test run numbers " + str(self.failed_nums))

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
        #print("Sorted failed urls " + str(self.list_of_urls))

    def plot_daily_result(self):
        global plan_name
        x1 = range(len(self.failed_nums))
        y1 = self.failed_nums
        failed_test_run = self.list_of_urls
        plotannotes = []

        for p, q, r, s in zip(x1, y1, failed_test_run, self.final_label):
            count = 0
            if q != 0:
                length = len(r)
                while count < length:
                    insert_link = str('<a href="' + str(r[count]) + '">Test_Run</a>')
                    plotannotes.append(dict(x=s,
                                            y=1,
                                            text=insert_link,
                                            showarrow=False
                                            )
                                       )
                    count += 1
        trace1 = go.Bar(
            x=self.final_label,
            y=y1,
            marker=dict(color='red')
        )
        trace2 = go.Bar(
            x=self.final_label,
            y=self.passed_nums,
            marker=dict(color='green')
        )
        data = [trace1, trace2]
        layout = go.Layout(
            showlegend=False,
            title=self.plan_name,
            annotations=plotannotes
        )
        fig = plot(go.Figure(data=data, layout=layout), filename=self.plankey+".html")
        print(fig)

def main():
    obj = [DailyTest(l, 75) for l in ['PREM-TI123LTA', 'PREM-TI1228WM', 'PREM-TI123B', 'PREM-TI123RA', 'PREM-TI123WM', 'PREM-TI1238AA', 'PREM-T1128LSF']]
    for o in obj:
        o.plan_build_state()
        o.print_new_passed_failed_dict()
        o.sort_image_version_list()
        o.failed_passed_list_nums()
        o.sort_failed_urls()
        o.plot_daily_result()

if __name__ == "__main__":
    main()

