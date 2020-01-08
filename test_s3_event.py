import utils
import unittest
import requests
import json

logger = utils.logger

""" trigger API test """


def f_create_s3_feed(trg_name, trg_desp, feed_ns, feed_pkg, feed_nm, prm_ak, prm_sk, prm_region, prm_bucket, prm_pfx,
                     prm_sfx, prm_evts):
    """
    create s3 event feed source
    """
    payload = {
        "query": "mutation {saveTrigger(input:{name:\"" + trg_name + "\",description:\"" + trg_desp + "\",feed:{namespace:\"" + feed_ns + "\",package:\"" + feed_pkg + "\",name:\"" + feed_nm + "\"},params:[{key:\"accessKeyId\",value:\"" + prm_ak + "\"},{key:\"secretAccessKey\",value:\"" + prm_sk + "\"},{key:\"region\",value:\"" + prm_region + "\"}, {key:\"bucket\",value:\"" + prm_bucket + "\"},{key:\"prefix\",value:\"" + prm_pfx + "\"},{key:\"suffix\",value:\"" + prm_sfx + "\"},{key:\"events\",value:\"" + prm_evts + "\"}]}) {name description version feed {name namespace package __typename} parameters {key value __typename} url __typename}}"}
    return requests.post(utils.g_backend_url, data=json.dumps(payload), headers=utils.g_headers)


def f_delete_s3_feed(trg_name):
    payload = {"query": "mutation {q0: deleteTrigger(name:\"" + trg_name + "\")}"}
    return requests.post(utils.g_backend_url, data=json.dumps(payload), headers=utils.g_headers)


def f_trigger_s3_sns_event():
    api_host = "faas-beta-test.samsungcloud.org"
    auth = "23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP"
    trg_ns = "guest"
    trg_name = "_python_test_s3event_"
    webhook_endpoint = "https://" + api_host + "/api/v1/web/whisk.system/aws/from-sns?trigger=" + auth + "/" + trg_ns + "/" + trg_name

    payload = {
        "Type": "SubscriptionConfirmation",
        "SubscribeURL": "https://httpbin.org/status/200"
    }
    return requests.post(webhook_endpoint, json.dumps(payload), headers=utils.g_headers)


class S3EventSource(unittest.TestCase):
    """
    test S3EventSource API
    """

    def setUp(self):
        response = f_create_s3_feed('_python_test_s3event_', 's3 event source', 'whisk.system', 'aws', 'events',
                                    'AKIA2EMK6BP4BJYBKSYM',
                                    'prKb99bo6MAqXM2F3m3+sK8GRs0Qe+Xem+t5X02R', 'ap-northeast-2', 'f-dev', 'image',
                                    'gif', 's3:ObjectCreated:*,s3:ObjectRemoved:*')
        time.sleep(6)

    def tearDown(self):
        response = f_delete_s3_feed('_python_test_s3event_')

    def test_MockS3SNS_event(self):
        response = f_trigger_s3_sns_event()
        self.assertEqual(response.status_code, 200)
        logger.debug('S3EventSource response body:{0}'.format(response.content))
        self.assertTrue(b"errors" not in response.content)
        logger.info("S3EventSource pass")


if __name__ == '__main__':
    unittest.main(verbosity=1)
"""
    s = unittest.TestSuite()
    s.addTest(DeleteFeed("test_DeleteFeed"))
    runner = unittest.TextTestRunner()
    runner.run(s)
"""
