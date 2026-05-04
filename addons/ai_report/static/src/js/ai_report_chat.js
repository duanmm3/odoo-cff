// AI Report Chat - Conversation Style
(function() {
    'use strict';

    console.log('[AI Report] Chat JS loaded');

    var currentSessionId = null;
    var chartInstance = null;
    var sessions = [];

    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function generateSessionTitle(query) {
        return query.length > 30 ? query.substring(0, 30) + '...' : query;
    }

    function escapeHtml(str) {
        if (!str && str !== 0) return '';
        return String(str).replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function formatTime(date) {
        var now = new Date();
        var diff = now - date;
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
        if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
        return date.toLocaleString('zh-CN', {month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit'});
    }

// ===== Chart Functions =====
    function normalizeChartType(chartType) {
        if (!chartType) return 'bar';
        var type = chartType.toString().trim().toLowerCase();
        if (['bar', 'column', '柱状', '柱形', '柱状图', '柱形图'].indexOf(type) !== -1) return 'bar';
        if (['line', '折线', '折线图', '趋势'].indexOf(type) !== -1) return 'line';
        if (['area', '面积', '面积图'].indexOf(type) !== -1) return 'line';
        if (['pie', '饼', '饼图'].indexOf(type) !== -1) return 'pie';
        if (['radar', '雷达', '雷达图'].indexOf(type) !== -1) return 'radar';
        if (['tree', '树', '树形', '树图'].indexOf(type) !== -1) return 'tree';
        return 'bar';
    }

    function getChartIcon(chartType) {
        var icons = {
            'bar': '<i class="fa fa-bar-chart"></i>',
            'line': '<i class="fa fa-line-chart"></i>',
            'area': '<i class="fa fa-area-chart"></i>',
            'pie': '<i class="fa fa-pie-chart"></i>',
            'radar': '<i class="fa fa-compass"></i>',
            'tree': '<i class="fa fa-sitemap"></i>',
            'table': '<i class="fa fa-table"></i>'
        };
        return icons[chartType] || icons['bar'];
    }

    function getChartIcon(chartType) {
        var icons = {
            'bar': '<i class="fa fa-bar-chart"></i>',
            'line': '<i class="fa fa-line-chart"></i>',
            'area': '<i class="fa fa-area-chart"></i>',
            'pie': '<i class="fa fa-pie-chart"></i>',
            'radar': '<i class="fa fa-compass"></i>',
            'tree': '<i class="fa fa-sitemap"></i>',
            'table': '<i class="fa fa-table"></i>'
        };
        return icons[chartType] || icons['bar'];
    }

    function normalizeChartType(chartType) {
        if (!chartType) return 'bar';
        var type = chartType.toString().trim().toLowerCase();
        if (['bar', 'column', '柱状', '柱形', '柱状图', '柱形图'].indexOf(type) !== -1) return 'bar';
        if (['line', '折线', '折线图', '趋势'].indexOf(type) !== -1) return 'line';
        if (['area', '面积', '面积图'].indexOf(type) !== -1) return 'line';  // 面积图用 line 实现
        if (['pie', '饼', '饼图'].indexOf(type) !== -1) return 'pie';
        if (['radar', '雷达', '雷达图'].indexOf(type) !== -1) return 'radar';
        if (['tree', '树', '树形', '树图'].indexOf(type) !== -1) return 'tree';
        return 'bar';
    }

    function buildChartData(columns, data) {
        if (!data || !columns || data.length === 0 || columns.length < 2) return null;
        
        console.log('[AI Report] buildChartData columns:', columns);
        console.log('[AI Report] buildChartData first row:', data[0]);
        
        // 查找 index 列（指标）、label 列（X轴标签）
        var indexCol = -1;
        var labelCol = -1;
        
        for (var i = 0; i < columns.length; i++) {
            var colName = String(columns[i]).toLowerCase();
            if (colName === 'index' || colName === 'value' || colName === 'amount' || colName === 'total' || colName === 'sum') {
                indexCol = i;
            }
            if (colName === 'month' || colName === '日期' || colName === 'date') {
                labelCol = i;
            }
            if (colName === 'product_name' || colName === 'name') {
                labelCol = i;
            }
        }
        
        // 默认使用第一列作为 X 轴标签，第二列作为数据
        if (labelCol === -1) labelCol = 0;
        if (indexCol === -1) indexCol = 1;
        
        var labels = [];
        var values = [];
        var labelName = columns[labelCol] || '标签';
        
        data.forEach(function(row) {
            var rawLabel = row[labelCol];
            var labelStr = '';
            
            // 详细检查每个值的类型
            console.log('[AI Report] rawLabel:', rawLabel, 'type:', typeof rawLabel);
            
            if (rawLabel === null || rawLabel === undefined) {
                labelStr = '空';
            } else if (typeof rawLabel === 'object') {
                // 如果是对象，检查是否有 name 属性
                if (rawLabel.name) {
                    labelStr = String(rawLabel.name);
                } else if (rawLabel.toString && rawLabel.toString() !== '[object Object]') {
                    labelStr = rawLabel.toString();
                } else {
                    // 如果无法解析，显示原始值
                    labelStr = JSON.stringify(rawLabel);
                }
            } else {
                labelStr = String(rawLabel);
            }
            
            labels.push(escapeHtml(labelStr));
            
            var num = Number(row[indexCol]);
            values.push(isNaN(num) ? 0 : num);
        });
        
        console.log('[AI Report] Chart data built:', {labels, values, labelName});
        
        return { labels: labels, values: values, label: labelName };
    }

    function renderChart(columns, data, chartType, containerId) {
        console.log('[AI Report] renderChart called:', {columns, dataLength: data ? data.length : 0, chartType, containerId});
        
        if (!data || data.length === 0) return '<div class="no-data"><p>暂无数据</p></div>';
        
        // 打印列名用于调试
        console.log('[AI Report] columns:', columns);
        if (data.length > 0) {
            console.log('[AI Report] first row:', data[0]);
        }
        
        var originalType = chartType;
        var type = normalizeChartType(chartType);
        var chartData = buildChartData(columns, data);
        if (!chartData) return '<div class="no-data"><p>数据格式不支持图表展示</p></div>';
        
        if (chartInstance) {
            try { chartInstance.destroy(); } catch(e) {}
            chartInstance = null;
        }
        
        var canvasId = 'chart_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
        
        var html = '<div class="chart-container" id="' + containerId + '" style="height:350px;position:relative;margin:20px 0;padding:16px;background:#fff;border-radius:12px;">';
        html += '<canvas id="' + canvasId + '"></canvas>';
        html += '</div>';
        
        // 创建图表
        var canvas = document.getElementById(canvasId);
        console.log('[AI Report] Canvas element:', canvas);
        
        if (!canvas) {
            // 元素还没渲染，延迟执行
            console.log('[AI Report] Canvas not found immediately, delaying...');
            setTimeout(function() {
                var c = document.getElementById(canvasId);
                console.log('[AI Report] Delayed canvas found:', !!c);
                console.log('[AI Report] window.Chart available:', typeof window.Chart);
                if (c && window.Chart) {
                    console.log('[AI Report] Calling createChart...');
                    createChart(c, chartData, type, originalType);
                } else {
                    console.log('[AI Report] Cannot create chart - missing canvas or Chart');
                }
            }, 200);
            return html;
        }
        
        if (window.Chart) {
            createChart(canvas, chartData, type, originalType);
        }
        
        return html;
    }
    
    function createChart(canvas, chartData, type, originalType) {
        console.log('[AI Report] ===== Creating chart =====');
        console.log('[AI Report] canvas:', canvas);
        console.log('[AI Report] chartData:', chartData);
        console.log('[AI Report] type:', type);
        
        if (chartInstance) {
            try { chartInstance.destroy(); } catch(e) {}
            chartInstance = null;
        }
        
        var colors = [
            '#3E6AE1', '#34D399', '#F59E0B', '#EF4444', '#8B5CF6',
            '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
        ];
        
        var isArea = originalType === 'area';
        
        console.log('[AI Report] Chart config prepared, creating Chart instance...');
        
        var chartConfig = {
            type: type,
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: chartData.label,
                    data: chartData.values,
                    backgroundColor: type === 'pie' 
                        ? chartData.labels.map(function(_, i) { return colors[i % colors.length]; })
                        : isArea 
                            ? 'rgba(62, 106, 225, 0.3)'
                            : type === 'line' 
                                ? colors[0] + '20' 
                                : colors[0],
                    borderColor: type === 'pie' 
                        ? chartData.labels.map(function(_, i) { return colors[i % colors.length]; })
                        : colors[0],
                    borderWidth: type === 'pie' ? 2 : 2,
                    fill: isArea || type === 'line',
                    tension: isArea || type === 'line' ? 0.3 : 0,
                    pointBackgroundColor: colors[0],
                    pointRadius: isArea || type === 'line' ? 4 : 0,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        display: type === 'pie' || type === 'radar',
                        position: 'right'
                    }
                },
                scales: type === 'pie' || type === 'radar' ? {} : {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        grid: { color: '#EEEEEE' }
                    }
                }
            }
        };
        
        try {
            chartInstance = new window.Chart(canvas, chartConfig);
            console.log('[AI Report] Chart created successfully');
        } catch(e) {
            console.error('[AI Report] Chart creation error:', e);
        }
    }

    function renderTable(columns, data) {
        if (!data || data.length === 0) return '<div class="no-data"><p>暂无数据</p></div>';
        
        var html = '<div class="data-table-wrapper"><table class="data-table"><thead><tr>';
        columns.forEach(function(col) {
            html += '<th>' + escapeHtml(col) + '</th>';
        });
        html += '</tr></thead><tbody>';
        
        data.forEach(function(row) {
            html += '<tr>';
            row.forEach(function(cell) {
                var cellValue = cell === null ? '-' : String(cell);
                html += '<td>' + escapeHtml(cellValue) + '</td>';
            });
            html += '</tr>';
        });
        html += '</tbody></table></div>';
        
        return html;
    }

    // ===== Session Management =====
    function createNewSession() {
        currentSessionId = generateSessionId();
        var session = { id: currentSessionId, title: '新会话', time: new Date() };
        sessions.unshift(session);
        renderSessionList();
        renderEmptyState();
        var input = document.getElementById('aiQuestionInput');
        if (input) input.focus();
    }

    function renderSessionList() {
        var list = document.getElementById('chatSessionList');
        if (!list) return;
        
        if (sessions.length === 0) {
            list.innerHTML = '<div class="text-center text-muted p-3"><small>暂无历史会话</small></div>';
            return;
        }
        
        var html = '';
        sessions.forEach(function(sess) {
            var active = sess.id === currentSessionId ? 'active' : '';
            html += '<div class="session-item ' + active + '" data-id="' + sess.id + '">';
            html += '<div class="session-title">' + escapeHtml(sess.title) + '</div>';
            html += '<div class="session-time">' + formatTime(sess.time) + '</div>';
            html += '</div>';
        });
        
        list.innerHTML = html;
        
        list.querySelectorAll('.session-item').forEach(function(item) {
            item.addEventListener('click', function() {
                currentSessionId = this.getAttribute('data-id');
                renderSessionList();
            });
        });
    }

    function renderEmptyState() {
        var messages = document.getElementById('chatMessages');
        if (!messages) return;
        
        messages.innerHTML = '<div class="welcome-message">' +
            '<div style="margin-bottom: 20px;"><i class="fa fa-chart-line fa-4x"></i></div>' +
            '<h4>欢迎使用 AI 智能报表</h4>' +
            '<p>用自然语言描述您的数据分析需求</p>' +
            '<div class="example-queries">' +
            '<p>示例查询：</p>' +
            '<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px;">' +
            '<button class="btn example-query" data-query="今年的销售额">今年的销售额</button>' +
            '<button class="btn example-query" data-query="月度销售趋势分析">月度销售趋势分析</button>' +
            '<button class="btn example-query" data-query="畅销产品TOP10排行榜">畅销产品TOP10排行榜</button>' +
            '<button class="btn example-query" data-query="产品销售汇总视图">产品销售汇总视图</button>' +
            '<button class="btn example-query" data-query="各产品销量排名">各产品销量排名</button>' +
            '<button class="btn example-query" data-query="年度采购分析">年度采购分析</button>' +
            '<button class="btn example-query" data-query="采购产品排行">采购产品排行</button>' +
            '<button class="btn example-query" data-query="采购趋势分析">采购趋势分析</button>' +
            '<button class="btn example-query" data-query="库存不足产品预警">库存不足产品预警</button>' +
            '</div></div></div></div>';
        
        messages.querySelectorAll('.example-query').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                var query = e.target.getAttribute('data-query');
                var input = document.getElementById('aiQuestionInput');
                if (input) {
                    input.value = query;
                    sendQuery(query);
                }
            });
        });
    }

    // ===== Render Functions =====
    function appendUserMessage(message) {
        var messages = document.getElementById('chatMessages');
        if (!messages) return;
        
        var html = '<div class="chat-bubble user clearfix">' +
            '<div class="bubble-content">' + escapeHtml(message) + '</div>' +
            '<div class="bubble-time">' + formatTime(new Date()) + '</div>' +
            '</div>';
        messages.insertAdjacentHTML('beforeend', html);
        messages.scrollTop = messages.scrollHeight;
    }

    function appendAssistantTyping() {
        var messages = document.getElementById('chatMessages');
        if (!messages) return;
        
        var html = '<div class="chat-bubble assistant clearfix" id="typingIndicator">' +
            '<div class="bubble-content"><div class="chat-loading"><div class="loading-spinner"></div>AI 正在分析中...</div></div>' +
            '</div>';
        messages.insertAdjacentHTML('beforeend', html);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeTypingIndicator() {
        var typing = document.getElementById('typingIndicator');
        if (typing) typing.remove();
    }

    function renderResult(data) {
        var messages = document.getElementById('chatMessages');
        if (!messages) return;
        
        // 生成唯一ID
        var resultId = 'result_' + Date.now();
        
        var html = '<div class="chat-bubble assistant clearfix">';
        html += '<div class="bubble-content">';
        
        if (data.type === 'error') {
            html += '<div class="error-message">' + escapeHtml(data.message) + '</div>';
        } else {
            html += '<div class="result-card">';
            
            if (data.explanation) {
                html += '<div class="result-explanation"><i class="fa fa-lightbulb-o"></i> ' + escapeHtml(data.explanation) + '</div>';
            }
            
            if (data.columns && data.data) {
                html += '<div class="result-stats">';
                html += '<div class="stat-item"><i class="fa fa-database"></i> 数据行数: <span class="stat-value">' + data.row_count + '</span></div>';
                if (data.execution_time) {
                    html += '<div class="stat-item"><i class="fa fa-clock-o"></i> 耗时: <span class="stat-value">' + data.execution_time.toFixed(2) + 's</span></div>';
                }
                html += '</div>';
                
                // 数据表格
                html += '<div id="' + resultId + '_tableArea"></div>';
                
                // 可视化区域 - 默认显示柱图
                html += '<div class="chart-selector" style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 16px;">';
                html += '<span class="text-muted me-2" style="font-size: 13px;">可视化：</span>';
                html += '<button class="chart-btn active" data-type="bar" data-result-id="' + resultId + '">' + getChartIcon('bar') + ' 柱状图</button>';
                html += '<button class="chart-btn" data-type="line" data-result-id="' + resultId + '">' + getChartIcon('line') + ' 折线图</button>';
                html += '<button class="chart-btn" data-type="pie" data-result-id="' + resultId + '">' + getChartIcon('pie') + ' 饼图</button>';
                html += '<button class="chart-btn" data-type="area" data-result-id="' + resultId + '">' + getChartIcon('area') + ' 面积图</button>';
                html += '<button class="chart-btn" data-type="radar" data-result-id="' + resultId + '">' + getChartIcon('radar') + ' 雷达图</button>';
                html += '</div>';
                
                html += '<div id="' + resultId + '_chartArea"></div>';
            } else {
                html += '<div class="no-data"><p>暂无数据</p></div>';
            }
            
            html += '</div>';
        }
        
        html += '</div></div>';
        
        messages.insertAdjacentHTML('beforeend', html);
        messages.scrollTop = messages.scrollHeight;
        
        // 延迟渲染表格和图表，确保DOM已更新
        if (data.columns && data.data) {
            setTimeout(function() {
                var tableArea = document.getElementById(resultId + '_tableArea');
                var chartArea = document.getElementById(resultId + '_chartArea');
                var buttons = document.querySelectorAll('.chart-btn[data-result-id="' + resultId + '"]');
                
                console.log('[AI Report] Rendering for result:', resultId);
                console.log('[AI Report] tableArea:', !!tableArea, 'chartArea:', !!chartArea);
                
                // 渲染表格
                if (tableArea) {
                    tableArea.innerHTML = renderTable(data.columns, data.data);
                }
                
                // 默认渲染柱图
                if (chartArea) {
                    chartArea.innerHTML = renderChart(data.columns, data.data, 'bar', resultId + '_chart');
                }
                
                // 绑定图表切换事件 - 表格始终显示，只切换图表
                buttons.forEach(function(btn) {
                    btn.addEventListener('click', function() {
                        var type = this.getAttribute('data-type');
                        buttons.forEach(function(b) { b.classList.remove('active'); });
                        this.classList.add('active');
                        
                        // 表格始终显示，只切换图表
                        if (chartArea) {
                            chartArea.innerHTML = renderChart(data.columns, data.data, type, resultId + '_chart');
                        }
                    });
                });
            }, 100);
        }
    }

    // ===== API Call =====
    function sendQuery(query) {
        if (!query.trim()) return;
        
        console.log('[AI Report] sendQuery called with:', query);
        
        if (!currentSessionId) {
            currentSessionId = generateSessionId();
            var session = { id: currentSessionId, title: generateSessionTitle(query), time: new Date() };
            sessions.unshift(session);
            renderSessionList();
        } else {
            var sess = sessions.find(function(s) { return s.id === currentSessionId; });
            if (sess && sess.title === '新会话') {
                sess.title = generateSessionTitle(query);
                renderSessionList();
            }
        }
        
        appendUserMessage(query);
        appendAssistantTyping();
        
        var input = document.getElementById('aiQuestionInput');
        if (input) input.value = '';
        
        console.log('[AI Report] Sending fetch request to /ai_report/chat');
        
        var sendBtn = document.getElementById('sendBtn');
        if (sendBtn) sendBtn.disabled = true;
        
        fetch('/ai_report/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: query, session_id: currentSessionId })
        })
        .then(function(response) {
            console.log('[AI Report] Response status:', response.status);
            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            console.log('[AI Report] Response data:', data);
            console.log('[AI Report] columns:', data.columns);
            console.log('[AI Report] data:', data.data);
            if (sendBtn) sendBtn.disabled = false;
            removeTypingIndicator();
            if (data.session_id) currentSessionId = data.session_id;
            renderResult(data);
        })
        .catch(function(error) {
            console.error('[AI Report] Fetch error:', error);
            if (sendBtn) sendBtn.disabled = false;
            removeTypingIndicator();
            var messages = document.getElementById('chatMessages');
            if (messages) {
                messages.insertAdjacentHTML('beforeend', '<div class="chat-bubble assistant clearfix"><div class="bubble-content"><div class="error-message">请求失败: ' + escapeHtml(error.message) + '</div></div></div>');
                messages.scrollTop = messages.scrollHeight;
            }
        });
    }

    // ===== Event Bindings =====
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[AI Report] DOM ready');
        
        var input = document.getElementById('aiQuestionInput');
        var sendBtn = document.getElementById('sendBtn');
        var newChatBtn = document.querySelector('.new-chat-btn');
        
        // 绑定示例查询按钮事件
        console.log('[AI Report] Binding example query buttons');
        var exampleButtons = document.querySelectorAll('.example-query');
        console.log('[AI Report] Found example buttons:', exampleButtons.length);
        exampleButtons.forEach(function(btn) {
            console.log('[AI Report] Binding button:', btn.getAttribute('data-query'));
            btn.addEventListener('click', function(e) {
                console.log('[AI Report] Example button clicked');
                var query = e.target.getAttribute('data-query');
                console.log('[AI Report] Query:', query);
                if (input && query) {
                    input.value = query;
                    sendQuery(query);
                }
            });
        });
        
        if (sendBtn) {
            sendBtn.addEventListener('click', function() {
                if (input) sendQuery(input.value);
            });
        }
        
        if (input) {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendQuery(input.value);
                }
            });
        }
        
        if (newChatBtn) {
            newChatBtn.addEventListener('click', createNewSession);
        }
    });

    window.createNewSession = createNewSession;
})();