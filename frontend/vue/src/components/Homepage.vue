<template>
  <div>

        <div class="main-content">

            <div class="db-schema">
                <div class="loader-wrapper">
                    <div class="preloader-wrapper big active">
                        <div class="spinner-layer spinner-blue-only">
                          <div class="circle-clipper left">
                            <div class="circle"></div>
                          </div><div class="gap-patch">
                            <div class="circle"></div>
                          </div><div class="circle-clipper right">
                            <div class="circle"></div>
                          </div>
                        </div>
                    </div>
                </div>

                <ul class="collapsible" data-collapsible="accordion" style="display: none;"></ul>
            </div>

            <div class="sql-editor">

                <div class="sql-editor__header">

                    <p class="sql-editor__note">
                        <a href="https://steemsql.com" target="_blank">
                            Note: you can support SteemSQL — just buy a subscription!
                        </a>
                    </p>

                    <div class="sql-editor__info-text">
                        <p>Based on <a href="http://steemsql.com" target="_blank">SteemSQL</a></p>
                        <p>Developed by <a href="https://steemit.com/@emptyname" target="_blank">@emptyname</a></p>
                        <p><a href="https://www.w3schools.com/sql/default.asp" target="_blank">Learn SQL</a></p>
                        <p>Delay: <span id="delay">loading...</span></p>
                        <p><a href="javascript:void(0)" id="share-query">Share Query</a></p>
                    </div>

                    <div class="undo-redo right-align">
                        <i class="undo material-icons">&#xE166;</i> <!-- undo -->
                        <i class="redo material-icons">&#xE15A;</i> <!-- redo -->
                    </div>
                </div>

                <div class="input-field">

                    <codemirror
                        v-model="code"
                        :options="cmOptions"
                        class="materialize-textarea"
                        id="sqlarea">
                    </codemirror>

                    <div class="loader-wrapper valign-wrapper">
                        <div class="preloader-wrapper big active">
                            <div class="spinner-layer spinner-blue-only">
                              <div class="circle-clipper left">
                                <div class="circle"></div>
                              </div><div class="gap-patch">
                                <div class="circle"></div>
                              </div><div class="circle-clipper right">
                                <div class="circle"></div>
                              </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="sql-editor__footer">
                    <div class="card limit-rows">
                        <div class="limit-rows__header">
                            <p>Limit Rows</p>
                            <input type="number" min="1" max="5000" id="limit-rows-value" />
                        </div>

                        <div id="limit-rows-slider"></div>
                    </div>

                    <div>
                        <a href="#" class="run-query-btn button" @click="loadData">Run Query</a>
                    </div>
                </div>

            </div> <!-- sql-editor -->
        </div> <!-- main-content -->

    <example-list @setNewExampleCode="changeCode" />

    <div id="table">

      <div class="table__header" v-if="tableData.length">

        <div class="card execution_time">
          <div class="card-content">
            <p class="card-title">
              Execution time: <span id="execution_time__value">{{this.executionTime}}</span>
            </p>
          </div>
        </div>

        <div class="export">
          <div class="button">Export</div>

          <div class="export-options center-align">
            <div class="export-btn" data-export-format="markdown">Markdown</div>
            <div class="export-btn" data-export-format="xlsx">Excel</div>
            <div class="export-btn" data-export-format="csv">CSV</div>
            <div class="export-btn" data-export-format="json">JSON</div>
          </div>
        </div>
      </div> <!-- /.table__header -->

      <!--
      <table class="bordered highlight responsive-table">
        <thead></thead>
        <tbody></tbody>
      </table>
      -->
      <el-card>
        <el-table :data="tableData">
          <el-table-column
            v-for="header in tableHeaders"
            :prop="header"
            :label="header"
            :key="header">
          </el-table-column>
        </el-table>
      </el-card>
    </div>

  </div>
</template>

<script>

import { codemirror } from 'vue-codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/sql/sql';

import { Input, Button, Table, TableColumn, Card } from 'element-ui';

import ExampleList from './ExampleList';

export default {
  name: 'Homepage',
  components: {
    codemirror,
    'example-list': ExampleList,
    'el-table': Table,
    'el-table-column': TableColumn,

    'el-input': Input,
    'el-button': Button,
    'el-card': Card,
  },
  data() {
    return {
      isLoading: false,
      code: '',
      tableData: [],
      tableHeaders: [],
      executionTime: '',
      cmOptions: {
        mode: 'text/x-mssql',
        // indentWithTabs: true,
        lineNumbers: true,
      },
    };
  },
  methods: {
    loadData() {
      if (this.isLoading) {
        alert('Please wait results of the first request.');
        return;
      }

      if (!this.code) {
        return;
      }

      this.isLoading = true;

      const ajaxData = {
        query: this.code,
        // limit_rows: parseInt($('#limit-rows-value').val()),
      };

      fetch('https://sql.steemhelpers.com/api', {
        method: 'post',
        headers: {
          'Content-type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(ajaxData),
        mode: 'cors',
        dataType: 'json',
      })
        .then((response) => {
          if (response.status >= 400 && response.status < 600) {
            // return Promise.reject(new Error(response.statusText));
            throw new Error(response.statusText);
          }
          return response.json();
        })
        .then((data) => {
          // this.tableData = data.rows;
          this.tableHeaders = data.headers;
          this.tableData = data.rows;
          this.executionTime = data.execution_time;
          console.log(data);
        })
        .catch((error) => {
          this.isLoading = false;
          console.log('Request failed', error);
        });
    }, // loadData

    changeCode(newSql) {
      if (this.isLoading) {
        return;
      }

      const currrentDate = new Date().toJSON().slice(0, 10).replace(/-/g, '/');

      const nextDateRaw = new Date();
      nextDateRaw.setDate(nextDateRaw.getDate() + 1);
      const nextDate = nextDateRaw.toJSON().slice(0, 10).replace(/-/g, '/');

      const dateWeekAgoRaw = new Date();
      dateWeekAgoRaw.setDate(dateWeekAgoRaw.getDate() - 7);
      const dateWeekAgo = dateWeekAgoRaw.toJSON().slice(0, 10).replace(/-/g, '/');

      let rawSql = newSql.replace(/&#10;/g, '\n');
      rawSql = rawSql.replace('{date}', currrentDate);
      rawSql = rawSql.replace('{nextDate}', nextDate);
      rawSql = rawSql.replace('{dateWeekAgo}', dateWeekAgo);

      this.code = rawSql;
    }, // changeCode
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
