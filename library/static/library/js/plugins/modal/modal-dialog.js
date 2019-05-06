(function ($) {
    $.extend({
        modal_message_type:{
            INFO:"提示",
            ERROR:"错误",
            WARN:"警告"
        },
        show_modal_confirm:function (o) {
            var $dialog=$('#modal-confirm');
            if ($dialog.length == 0) return;
            var $title=$dialog.find(".modal-title");
            var $body=$dialog.find(".modal-body");
            var $confirm_btn=$dialog.find(".modal-footer>.btn-primary");
            $confirm_btn.unbind('click').on('click', function (e) {
                e.preventDefault()
                $dialog.modal('hide')
                if (typeof o === 'string'){
                    window.location.href = o
                    return
                }else if(typeof o['confirm'] === 'function'){
                    return o['confirm'](e)
                }
            })
            o['title'] && $title.text(o['title']);
            o['content'] && $body.children('p').text(o['content'])
            $dialog.modal('show')
        },
        alert_modal_tip:function (content, message_type) {
            var $dialog = $("#modal-tip");
            var $title=$dialog.find(".modal-title");
            var $content=$dialog.find(".modal-content");
            var $header=$dialog.find(".modal-header");
            var $body=$dialog.find(".modal-body");
            var $footer=$dialog.find(".modal-footer");
            $title.text(message_type);
            $body.children('p').text(content);
            switch(message_type){
                case $.modal_message_type.INFO:
                    if(!$header.hasClass("modal-header-default")){
                        $header.prop('class', 'modal-header modal-header-default');
                        $content.prop('class', 'modal-content modal-content-default');
                        $footer.children('.tip-btn').prop('class', 'tip-btn btn btn-primary');
                    }
                    break;
                case $.modal_message_type.ERROR:
                    if(!$header.hasClass("modal-header-error")){
                        $header.prop('class', "modal-header modal-header-error");
                        $content.prop('class', "modal-content modal-content-error");
                        $footer.children('.tip-btn').prop('class', 'tip-btn btn btn-danger');
                    }
                    break;
                case $.modal_message_type.WARN:
                    if(!$header.hasClass("modal-header-warn")){
                        $header.prop('class', "modal-header modal-header-warn");
                        $content.prop('class', "modal-content modal-content-warn");
                        $footer.children('.tip-btn').prop('class', 'tip-btn btn btn-warning');
                    }
                    break;
                default:
                    break;
            }
            $dialog.modal('show');
        }
    })
})("function" == typeof jQuery?jQuery:{fn:{}})