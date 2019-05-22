# -*- coding: utf-8 -*-
import base64

from blueapps.utils.esbclient import get_client_by_user
from pipeline.conf import settings
# from pipeline.components.utils import cc_get_ips_info_by_str
from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component

JOB_SUCCESS = [3, 11]

__group_name__ = u"自定义原子(TEST)"


class GetDfUsageService(Service):
    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        client = get_client_by_user(executor)
        client.set_bk_api_ver('v2')

        host_ip = data.get_one_of_inputs('host_ip')
        ip_list = [{'bk_cloud_id': 0, 'ip': host_ip}]
        host_partition = data.get_one_of_inputs('host_partition')
        content = "df -h | awk '($6==\"%s\"){print $5}'" % host_partition
        script_content = base64.encodestring(content)
        script_timeout = data.get_one_of_inputs('script_timeout')

        script_kwargs = {
            'bk_biz_id': biz_cc_id,
            'script_type': 1,
            'script_content': script_content,
            'script_timeout': script_timeout,
            'account': 'root',
            'ip_list': ip_list,
        }
        script_result = client.job.fast_execute_script(script_kwargs)
        if script_result['result']:
            data.set_outputs('job_instance_id', script_result['data']['job_instance_id'])
            data.set_outputs('client', client)
            return True
        else:
            data.set_outputs('ex_data', script_result['message'])
            return False

    def schedule(self, data, parent_data, callback_data=None):
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        job_instance_id = data.get_one_of_outputs('job_instance_id')
        client = data.get_one_of_outputs('client')
        client.set_bk_api_ver('v2')

        job_kwargs = {
            'bk_biz_id': biz_cc_id,
            'job_instance_id': job_instance_id,
        }
        job_result = client.job.get_job_instance_log(job_kwargs)
        if not job_result['result']:
            data.set_outputs('ex_data', job_result['message'])
            self.finish_schedule()
            return False
        # 任务执行结束
        job_data = job_result['data']
        if job_data[0]['is_finished']:
            # 执行成功
            if job_data[0]['status'] in JOB_SUCCESS:
                log_content = job_data[0]["step_results"][0]["ip_logs"][0]["log_content"]
                result_data = log_content.split('\n')[0]
                print '-------------' + result_data + '---------------'
                data.set_outputs('result_data', result_data)
                self.finish_schedule()
                return True
            # 执行失败
            else:
                data.set_outputs('ex_data', u"任务执行失败，作业ID: %s" % job_instance_id)
                self.finish_schedule()
                return False

    def outputs_format(self):
        return [
            self.OutputItem(name=u'JOB任务ID', key='job_instance_id', type='int'),
        ]


class GetDfUsageComponent(Component):
    name = u'磁盘分区使用率'
    code = 'get_df_usage'
    bound_service = GetDfUsageService
    form = settings.STATIC_URL + 'custom_atoms/get_usage/get_df_usage.js'