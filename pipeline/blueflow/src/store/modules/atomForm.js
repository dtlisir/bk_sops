/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
import Vue from 'vue'
import api from '@/api/index.js'

const atomForm = {
    namespaced: true,
    state: {
        fetching: false,
        form: {},
        config: {},
        output: {}
    },
    mutations: {
        setFetching (state, status) {
            state.fetching = status
        },
        setAtomForm (state, payload) {
            Vue.set(state.form, payload.atomType, payload.data)
        },
        setAtomConfig (state, payload) {
            Vue.set(state.config, payload.atomType, payload.configData)
        },
        setAtomOutput (state, payload) {
            Vue.set(state.output, payload.atomType, payload.outputData)
        }
    },
    actions: {
        loadAtomConfig ({commit, state}, payload) {
            const { atomType } = payload
            const atomClassify = atomType === 'var_ip_picker' ? 'variable' : 'component'
            return api.$getAtomForm(atomType, atomClassify, state.cc_id).then(
                response => response.data
            )
        },
        loadSubflowConfig ({commit}, payload) {
            const { id } = payload
            return api.getFormByTemplateId(id).then(
                response => response.data
            )
        }
    }
}

export default atomForm