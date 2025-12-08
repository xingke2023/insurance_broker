#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import os
import json
import requests
from time import sleep

from .helper import raise_exception_when_reqeust_failed
from .config import Config
from .status_object import Status, StatusObject


class Consent(StatusObject):
    def __init__(self, json_dict: dict):
        super().__init__(json_dict)
        # 保存原始JSON数据用于调试
        self.raw_data = json_dict
        if 'voiceTalentName' not in json_dict:
            raise ValueError("could not find 'voiceTalentName' in json_dict")
        self.voice_talent_name = json_dict['voiceTalentName']
        if 'companyName' not in json_dict:
            raise ValueError("could not find 'companyName' in json_dict")
        self.company_name = json_dict['companyName']
        if 'locale' not in json_dict:
            raise ValueError("could not find 'locale' in json_dict")
        self.locale = json_dict['locale']
        if 'projectId' not in json_dict:
            raise ValueError("could not find 'projectId' in json_dict")
        self.project_id = json_dict['projectId']

    # get all consents in project
    # when project_id is None, get all consents in current speech account
    @staticmethod
    def list(config: Config, project_id: str = None):
        config.logger.debug('Consent.list')
        consents = []
        api_url = config.url_prefix + 'consents' + '?' + config.api_version
        if project_id is not None and len(project_id) > 0:
            api_url += "&filter=projectId eq '%s'" % project_id
        headers = {'Ocp-Apim-Subscription-Key': config.key}
        while api_url is not None and len(api_url) > 0:
            response = requests.get(api_url, headers=headers)
            raise_exception_when_reqeust_failed('GET', api_url, response, config.logger)
            response_dict = response.json()
            for json_dict in response_dict['value']:
                consent = Consent(json_dict)
                consents.append(consent)
            if 'nextLink' in response_dict:
                api_url = response_dict['nextLink']
            else:
                api_url = None
        return consents

    @staticmethod
    def get(config: Config, consent_id: str):
        config.logger.debug('Consent.get consent_id = %s' % consent_id)
        if consent_id is None or len(consent_id) == 0:
            raise ValueError("'consent_id' is None or empty")
        api_url = config.url_prefix + 'consents/' + consent_id + '?' + config.api_version
        headers = {'Ocp-Apim-Subscription-Key': config.key}
        response = requests.get(api_url, headers=headers)
        raise_exception_when_reqeust_failed('GET', api_url, response, config.logger)
        consent = Consent(response.json())
        return consent

    @staticmethod
    def create(config: Config, project_id: str, consent_id: str, voice_talent_name: str, company_name: str,
               audio_file_path: str, locale: str, consent_text: str = None, description: str = None):
        config.logger.debug('Consent.create consent_id = %s' % consent_id)
        if project_id is None or len(project_id) == 0:
            raise ValueError("'project_id' is None or empty")
        if consent_id is None or len(consent_id) == 0:
            raise ValueError("'consent_id' is None or empty")
        if voice_talent_name is None or len(voice_talent_name) == 0:
            raise ValueError("'voice_talent_name' is None or empty")
        if company_name is None or len(company_name) == 0:
            raise ValueError("'company_name' is None or empty")
        if audio_file_path is None or len(audio_file_path) == 0:
            raise ValueError("'audio_file_path' is None or empty")
        if locale is None or len(locale) == 0:
            raise ValueError("'locale' is None or empty")
        if not os.path.exists(audio_file_path):
            raise ValueError("can't find file 'audio_file_path' = %s" % audio_file_path)
        audio_file_name = os.path.basename(audio_file_path)

        # 如果没有提供consent_text，使用默认的同意声明文本
        # 注意：不要在中文文本中添加多余的空格，以便与语音识别结果匹配
        if consent_text is None or len(consent_text) == 0:
            if locale.lower().startswith('zh'):
                # 中文不添加空格，使用句号分隔
                consent_text = f"我{voice_talent_name}知道我的录音将被{company_name}用于创建和使用我的语音合成版本。"
            else:
                consent_text = f"I {voice_talent_name} am aware that recordings of my voice will be used by {company_name} to create and use a synthetic version of my voice."

        config.logger.info(f'Consent文本: {consent_text}')

        headers = {'Ocp-Apim-Subscription-Key': config.key}
        api_url = config.url_prefix + 'consents/' + consent_id + '?' + config.api_version
        request_dict = {
            'projectId': project_id,
            'voiceTalentName': voice_talent_name,
            'companyName': company_name,
            'locale': locale,
            'consentText': consent_text,
            'description': description
        }

        config.logger.info(f'发送Consent创建请求: {api_url}')
        config.logger.info(f'请求参数: {json.dumps(request_dict, ensure_ascii=False)}')

        file = ('audiodata', (audio_file_name, open(audio_file_path, 'rb'), 'audio/wav'))
        response = requests.post(api_url, data=request_dict, headers=headers, files=[file])
        raise_exception_when_reqeust_failed('POST', api_url, response, config.logger)

        response_data = response.json()
        config.logger.info(f'Consent创建响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}')

        consent = Consent(response_data)
        consent_id = consent.id

        # Wait for consent ready. It takes 2-3 seconds.
        while (consent.status != Status.Succeeded and consent.status != Status.Failed):
            sleep(1)
            consent = Consent.get(config, consent_id)
        if consent.status == Status.Succeeded:
            config.logger.debug('Consent.create succeeded consent_id = %s' % consent_id)
        elif consent.status == Status.Failed:
            config.logger.warning('Consent.create failed consent_id = %s' % consent_id)
            # 输出原始JSON数据
            if hasattr(consent, 'raw_data') and consent.raw_data:
                config.logger.error('Consent原始数据: %s' % json.dumps(consent.raw_data, indent=2, ensure_ascii=False))
            # 尝试从API重新获取详细信息
            try:
                api_url_detail = config.url_prefix + 'consents/' + consent_id + '?' + config.api_version
                headers = {'Ocp-Apim-Subscription-Key': config.key}
                response = requests.get(api_url_detail, headers=headers)
                if response.status_code == 200:
                    detail_data = response.json()
                    config.logger.error('Consent详细信息(从API获取): %s' % json.dumps(detail_data, indent=2, ensure_ascii=False))

                    # 记录Azure识别出的文本内容
                    if 'properties' in detail_data:
                        properties = detail_data['properties']
                        if 'recognizedText' in properties:
                            config.logger.error('Azure识别到的文本: %s' % properties['recognizedText'])
                        if 'recognitionScore' in properties:
                            config.logger.error('识别准确度: %s' % properties['recognitionScore'])
                else:
                    config.logger.error('无法获取consent详细信息, status code: %d' % response.status_code)
            except Exception as e:
                config.logger.error('获取consent详细信息异常: %s' % str(e))
        return consent

    @staticmethod
    def delete(config: Config, consent_id: str):
        config.logger.debug('Consent.delete consent_id = %s' % consent_id)
        if consent_id is None or len(consent_id) == 0:
            raise ValueError("'consent_id' is None or empty")
        api_url = config.url_prefix + 'consents/' + consent_id + '?' + config.api_version
        headers = {'Ocp-Apim-Subscription-Key': config.key}
        response = requests.delete(api_url, headers=headers)

        raise_exception_when_reqeust_failed('DELETE', api_url, response, config.logger)
