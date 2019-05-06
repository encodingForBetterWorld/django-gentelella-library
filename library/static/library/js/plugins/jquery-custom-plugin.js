"use strict";
(function (t,e) {
    if (typeof jQuery === 'function') {
        e(jQuery);
    }
    else {
        throw new Error('jquery-custom-plugin JavaScript requires jQuery')
    }
})(this, function ($) {
    var WEB = {
        request: function(param){
            return new Promise(function(resolve, reject){
                if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(param.type.toUpperCase()))){
                    var csrfmiddlewaretoken = $("[name=csrfmiddlewaretoken]").val();
                    if (csrfmiddlewaretoken){
                        param.data = param.data || {}
                        param.data['csrfmiddlewaretoken'] = csrfmiddlewaretoken
                    }
                }
                $.ajax({
                    type:param.type || "get",
                    async:param.async || true,
                    url: param.url,
                    data:param.data || "",
                    success: function (res) {
                        if (res.status != 0) {
                            $.alert_modal_tip(res.msg, $.modal_message_type.ERROR);
                            reject();
                        } else {
                            resolve(res.data);
                        }
                    },
                    error: function (err) {
                        reject(err);
                        $.alert_modal_tip("网络异常", $.modal_message_type.ERROR);
                    }
                })
            })
        }
    }
    return $.extend({
        x_request:WEB.request
    })
})