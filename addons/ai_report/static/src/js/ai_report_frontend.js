odoo.define('ai_report.frontend', function (require) {
    'use strict';

    var currentData = null;
    var chartInstance = null;
    var sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    function escapeHtml(str) {
        if (!str && str !== 0) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    function renderTable(columns, data) {
        if (!data || data.length === 0) return '<div class="alert alert-warning">无数据</div>';
        var html = '<table class="table table-striped table-bordered mt-3"><thead><tr>';
        columns.forEach(function(col) { html += '<th>' + escapeHtml(col) + '</th>'; });
        html += '</tr></thead><tbody>';
        data.forEach(function(row) {
            html += '<tr>';
            row.forEach(function(cell) {
                html += '<td>' + escapeHtml(cell === null ? 'NULL' : String(cell)) + '</td>';
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        return html;
    }

    function normalizeChartType(chartType) {
        if (!chartType) return 'bar';
        var type = chartType.toString().trim().toLowerCase();
        if (['bar', 'column', '柱状', '柱形', '柱状图', '柱形图'].indexOf(type) !== -1) return 'bar';
        if (['line', '折线', '折线图'].indexOf(type) !== -1) return 'line';
        if (['pie', '饼', '饼图'].indexOf(type) !== -1) return 'pie';
        if (['radar', '雷达', '雷达图'].indexOf(type) !== -1) return 'radar';
        return 'bar';
    }

    function buildChartPayload(columns, data) {
        if (!data || !columns || data.length === 0 || columns.length < 2) {
            return null;
        }
        var labels = [];
        var values = [];
        data.forEach(function(row) {
            labels.push(escapeHtml(row[0] === null ? 'NULL' : row[0]));
            var num = Number(row[1]);
            values.push(isNaN(num) ? 0 : num);
        });
        return {
            labels: labels,
            values: values,
            label: columns[1] || columns[0] || '值'
        };
    }

    function renderChart(columns, data, chartType) {
        if (!data || data.length === 0) return '';
        var type = normalizeChartType(chartType);
        var payload = buildChartPayload(columns, data);
        if (!payload) return '';

        if (chartInstance) {
            try { chartInstance.destroy(); } catch (err) { }
            chartInstance = null;
        }

        var canvas = document.createElement('canvas');
        canvas.style.maxHeight = '400px';
        canvas.style.width = '100%';
        var container = document.createElement('div');
        container.style.marginTop = '20px';
        container.appendChild(canvas);

        if (window.Chart) {
            chartInstance = new window.Chart(canvas, {
                type: type,
                data: {
                    labels: payload.labels,
                    datasets: [{
                        label: payload.label,
                        data: payload.values,
                        backgroundColor: payload.labels.map(function(_, idx) {
                            var colors = ['rgba(54, 162, 235, 0.6)', 'rgba(255, 99, 132, 0.6)', 'rgba(75, 192, 192, 0.6)', 'rgba(255, 206, 86, 0.6)', 'rgba(153, 102, 255, 0.6)'];
                            return colors[idx % colors.length];
                        }),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: type !== 'bar' },
                        title: { display: true, text: payload.label }
                    }
                }
            });
        }
        return container.outerHTML;
    }

    function renderResult(data) {
        if (data.type === 'error') {
            return '<div class="alert alert-danger">' + escapeHtml(data.message) + '</div>';
        }

        var html = '<div class="card mt-3"><div class="card-body">';
        if (data.explanation) {
            html += '<p class="text-muted small mb-3">' + escapeHtml(data.explanation) + '</p>';
        }
        if (data.sql) {
            html += '<div class="mb-3"><pre class="bg-light p-2 small"><code>' + escapeHtml(data.sql) + '</code></pre></div>';
        }
        if (data.columns && data.data && data.data.length > 0) {
            var defaultType = normalizeChartType(data.chart_suggestion || 'bar');
            html += '<div class="mb-3">';
            html += '<button class="btn btn-sm btn-outline-secondary me-1 chart-btn" data-type="bar">柱状图</button>';
            html += '<button class="btn btn-sm btn-outline-secondary me-1 chart-btn" data-type="line">折线图</button>';
            html += '<button class="btn btn-sm btn-outline-secondary me-1 chart-btn" data-type="pie">饼图</button>';
            html += '<button class="btn btn-sm btn-outline-secondary me-1 chart-btn" data-type="radar">雷达图</button>';
            html += '<button class="btn btn-sm btn-outline-secondary chart-btn" data-type="table">表格</button>';
            html += '</div>';
            html += '<div id="chartContainer"></div>';
            html += '<div id="tableContainer">' + renderTable(data.columns, data.data) + '</div>';
            setTimeout(function() {
                document.querySelectorAll('.chart-btn').forEach(function(btn) {
                    btn.addEventListener('click', function() {
                        var type = this.getAttribute('data-type');
                        if (type === 'table') {
                            if (chartInstance) {
                                try { chartInstance.destroy(); } catch (err) { }
                                chartInstance = null;
                            }
                            document.getElementById('chartContainer').innerHTML = '';
                            document.getElementById('tableContainer').style.display = '';
                        } else {
                            document.getElementById('tableContainer').style.display = 'none';
                            document.getElementById('chartContainer').innerHTML = renderChart(data.columns, data.data, type);
                        }
                    });
                });
                if (defaultType !== 'table') {
                    document.getElementById('tableContainer').style.display = 'none';
                    document.getElementById('chartContainer').innerHTML = renderChart(data.columns, data.data, defaultType);
                }
            }, 50);
        }
        html += '</div></div>';
        currentData = data;
        return html;
    }

    window.doAiQuery = function() {
        var question = document.getElementById('ai_question');
        var resultDiv = document.getElementById('ai_result');
        var query = question && question.value.trim();
        if (!query) { alert('请输入问题'); return; }
        resultDiv.innerHTML = '<div class="alert alert-info">查询中...</div>';
        fetch('/ai_report/chat?question=' + encodeURIComponent(query) + '&session_id=' + encodeURIComponent(sessionId))
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.session_id) {
                    sessionId = data.session_id;
                }
                resultDiv.innerHTML = renderResult(data);
            })
            .catch(function(error) {
                resultDiv.innerHTML = '<div class="alert alert-danger">错误: ' + escapeHtml(error.message || '请求失败') + '</div>';
            });
    };

    return {doQuery: window.doAiQuery};
});