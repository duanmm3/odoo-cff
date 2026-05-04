odoo.define('ai_report.ai_report', function (require) {
    'use strict';

    var AIReporter = {
        init: function () {
            this.sessionId = this.generateSessionId();
            this.chartType = 'table';
            this.currentResult = null;
            console.log('AI Report module loaded (no Odoo deps)');
        },

        generateSessionId: function () {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        },

        processQuestion: async function (question) {
            var self = this;
            
            if (!question || !question.trim()) {
                return {type: 'error', message: '请输入问题'};
            }

            try {
                var url = '/ai_report/chat?question=' + encodeURIComponent(question) + '&session_id=' + encodeURIComponent(self.sessionId);
                var response = await fetch(url);
                var result = await response.json();
                return result;
            } catch (e) {
                console.error('AI Report error:', e);
                return {type: 'error', message: '请求失败: ' + e.message};
            }
        },

        renderResult: function (result) {
            var html = '';
            
            if (result.type === 'error') {
                html = '<div class="ai-error-message">' + result.message + '</div>';
            } else if (result.type === 'query') {
                html = this.renderQueryResult(result);
            } else if (result.type === 'dml') {
                html = this.renderDMLResult(result);
            } else {
                html = '<div class="ai-success-message">' + (result.message || JSON.stringify(result)) + '</div>';
            }
            
            return html;
        },

        renderQueryResult: function (result) {
            var html = '<div class="ai-result-card">';
            
            if (result.explanation) {
                html += '<div class="ai-result-explanation">' + result.explanation + '</div>';
            }
            
            if (result.sql) {
                html += '<div class="ai-result-sql"><pre>' + this.escapeHtml(result.sql) + '</pre></div>';
            }
            
            html += '<div class="ai-chart-selector">';
            html += this.renderChartButtons(result.chart_suggestion);
            html += '</div>';
            
            html += '<div class="ai-chart-container">';
            html += '<canvas id="ai-result-chart"></canvas>';
            html += '</div>';
            
            if (result.columns && result.data) {
                html += this.renderTable(result.columns, result.data);
            }
            
            html += '</div>';
            return html;
        },

        renderChartButtons: function (suggestion) {
            var types = ['bar', 'line', 'pie', 'table'];
            var labels = {bar: '柱形图', line: '折线图', pie: '饼图', table: '表格'};
            var html = '';
            
            types.forEach(function (type) {
                var active = (type === suggestion || type === 'table') ? 'active' : '';
                html += '<button class="btn btn-sm btn-outline-secondary ' + active + '" data-chart="' + type + '">' + 
                       labels[type] + '</button>';
            });
            
            return html;
        },

        renderTable: function (columns, data) {
            var html = '<table class="ai-data-table"><thead><tr>';
            
            columns.forEach(function (col) {
                html += '<th>' + this.escapeHtml(col) + '</th>';
            });
            
            html += '</tr></thead><tbody>';
            
            data.forEach(function (row) {
                html += '<tr>';
                row.forEach(function (cell) {
                    html += '<td>' + this.escapeHtml(String(cell)) + '</td>';
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            return html;
        },

        renderDMLResult: function (result) {
            var html = '<div class="ai-result-card">';
            if (result.success) {
                html += '<div class="ai-success-message">' + result.message + '</div>';
            } else {
                html += '<div class="ai-error-message">' + result.message + '</div>';
            }
            html += '</div>';
            return html;
        },

        escapeHtml: function (str) {
            if (!str) return '';
            return str.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;')
                   .replace(/"/g, '&quot;')
                   .replace(/'/g, '&#039;');
        }
    };

    AIReporter.init();

    console.log('AI Report module loaded');

    return AIReporter;
});