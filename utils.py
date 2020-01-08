import logging
import os

g_log_file_name = "result.log"
g_test_result_file_name = "result.txt"

log_file = os.path.abspath('.') + '/' + g_log_file_name;
if (os.path.exists(log_file)):
    os.remove(log_file)

#logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(level = logging.DEBUG,format = '%(message)s')
logging.basicConfig(level = logging.INFO,format = '%(message)s')
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
handler = logging.FileHandler(os.path.abspath('.')+'/'+g_log_file_name)
handler.setFormatter(formatter)
logger.addHandler(handler)

#g_backend_url = "http://10.0.8.198:3000/graphql"
g_backend_url = "http://internal-faas-beta-elb-backend-556539127.ap-northeast-2.elb.amazonaws.com:3000/graphql"
g_headers = {
    "Content-Type": "application/json; charset=UTF-8",
}
g_test_package_name = "_python_test_package_"
g_test_function_name = "_python_test_function_"
g_test_function_type = "nodejs:6"
g_test_function_code = "function main() {return { msg:  20000 }; }"
g_test_function_docker = "python-test-docker:latest"
g_test_sequence_name = "_python_test_sequence_"
g_test_sequence_fun_1 = "_python_test_sequence_fun_1"
g_test_sequence_fun_2 = "_python_test_sequence_fun_2"
g_test_package_name = "_python_test_package_"
g_test_api_path = "/hello/_python_test_aqi_"
g_test_api_function = "_python_test_aqi_"
g_test_api_method = "GET"
g_test_rule_name = "_python_test_rule_"
g_test_trigger_name = "_python_test_trigger_"
g_test_feed_name = "_python_test_feed_"



