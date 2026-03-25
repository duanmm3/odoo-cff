odoo.define('custom_price_module.price_query', function (require) {
    "use strict";
    
    var core = require('web.core');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    
    var _t = core._t;
    var QWeb = core.qweb;
    
    var PriceQueryWidget = Widget.extend({
        template: 'custom_price_module.PriceQueryWidget',
        events: {
            'click .price-query-submit': '_onSubmit',
            'click .price-query-refresh': '_onRefresh',
            'click .price-query-download': '_onDownload',
            'click .price-query-history': '_onHistory',
            'click .price-query-clear-cache': '_onClearCache',
        },
        
        init: function (parent, options) {
            this._super(parent, options);
            this.ic_model = options.ic_model || '';
            this.results = options.results || null;
            this.loading = false;
        },
        
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._renderResults();
            });
        },
        
        _renderResults: function () {
            if (this.results) {
                var $results = $(QWeb.render('custom_price_module.PriceQueryResults', {
                    results: this.results,
                    ic_model: this.ic_model,
                }));
                this.$('.price-query-results-container').html($results);
            }
        },
        
        _onSubmit: function (e) {
            e.preventDefault();
            var self = this;
            var ic_model = this.$('.price-query-input').val().trim();
            var force_refresh = this.$('.price-query-refresh-checkbox').is(':checked');
            
            if (!ic_model) {
                this._showError(_t('Please enter an IC model'));
                return;
            }
            
            this.loading = true;
            this._showLoading();
            
            ajax.jsonRpc('/price/api/query/' + encodeURIComponent(ic_model), 'call', {
                refresh: force_refresh ? 1 : 0,
            }).then(function (result) {
                self.loading = false;
                self.ic_model = ic_model;
                self.results = result;
                self._renderResults();
                self._hideLoading();
            }).catch(function (error) {
                self.loading = false;
                self._hideLoading();
                self._showError(_t('Query failed: ') + (error.message || error));
            });
        },
        
        _onRefresh: function (e) {
            e.preventDefault();
            if (this.ic_model) {
                this.$('.price-query-refresh-checkbox').prop('checked', true);
                this._onSubmit(e);
            }
        },
        
        _onDownload: function (e) {
            e.preventDefault();
            if (this.ic_model) {
                window.location.href = '/price/download/csv/' + encodeURIComponent(this.ic_model);
            }
        },
        
        _onHistory: function (e) {
            e.preventDefault();
            if (this.ic_model) {
                ajax.jsonRpc('/price/api/history/' + encodeURIComponent(this.ic_model), 'call', {})
                    .then(function (result) {
                        var history_html = '<h4>' + _t('Price History for ') + result.ic_model + '</h4>';
                        history_html += '<ul class="list-group">';
                        
                        if (result.dates && result.dates.length > 0) {
                            for (var i = 0; i < Math.min(result.dates.length, 10); i++) {
                                var date = result.dates[i];
                                var data = result.history[date];
                                history_html += '<li class="list-group-item">';
                                history_html += '<strong>' + date + '</strong>: ';
                                history_html += _t('Found ') + (data ? data.count : 0) + _t(' quotes');
                                history_html += '</li>';
                            }
                        } else {
                            history_html += '<li class="list-group-item">' + _t('No history found') + '</li>';
                        }
                        
                        history_html += '</ul>';
                        
                        new Dialog(this, {
                            title: _t('Price History'),
                            $content: $(history_html),
                            buttons: [
                                {text: _t('Close'), close: true}
                            ],
                        }).open();
                    }.bind(this))
                    .catch(function (error) {
                        this._showError(_t('Failed to load history: ') + (error.message || error));
                    }.bind(this));
            }
        },
        
        _onClearCache: function (e) {
            e.preventDefault();
            if (this.ic_model) {
                var self = this;
                new Dialog(this, {
                    title: _t('Clear Cache'),
                    $content: $('<div>').text(_t('Are you sure you want to clear the cache for ') + this.ic_model + '?'),
                    buttons: [
                        {
                            text: _t('Clear'),
                            classes: 'btn-primary',
                            click: function () {
                                ajax.jsonRpc('/price/clear/cache/' + encodeURIComponent(self.ic_model), 'call', {})
                                    .then(function () {
                                        self._showSuccess(_t('Cache cleared successfully'));
                                    })
                                    .catch(function (error) {
                                        self._showError(_t('Failed to clear cache: ') + (error.message || error));
                                    });
                            }
                        },
                        {text: _t('Cancel'), close: true}
                    ],
                }).open();
            }
        },
        
        _showLoading: function () {
            this.$('.price-query-loading').show();
            this.$('.price-query-submit').prop('disabled', true);
        },
        
        _hideLoading: function () {
            this.$('.price-query-loading').hide();
            this.$('.price-query-submit').prop('disabled', false);
        },
        
        _showError: function (message) {
            this.$('.price-query-error-message').html(message).show();
            setTimeout(function () {
                this.$('.price-query-error-message').fadeOut();
            }.bind(this), 5000);
        },
        
        _showSuccess: function (message) {
            this.$('.price-query-success-message').html(message).show();
            setTimeout(function () {
                this.$('.price-query-success-message').fadeOut();
            }.bind(this), 3000);
        },
    });
    
    return {
        PriceQueryWidget: PriceQueryWidget,
    };
});