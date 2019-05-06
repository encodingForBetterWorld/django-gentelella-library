/**
 * Created by Wang.suqi on 2017/10/9.
 */
(function($){
    $.fn.search_labelauty_choices=function() {
        var self = this;
        self.on('input', function () {
            show_search_item(self.val());
        });
    }
    $.extend({
    //For labelauty select widget
        use_labelauty_in_modal:function(title, model, search_placeholder, target_id, is_multiple) {
            var $context = $('#select_items_modal');
            var choices = [], picked_items=[];
            var $options = $('#'+target_id+' > option');
            $options.each(function(idx, option){
                option = $(option);
                choices.push([option.val(), option.text()]);
                if(option.prop("selected")){
                    picked_items.push(option.val());
                }
            });
            if($context.length==0){
                $context = init_modal_context(title, model, search_placeholder, generate_choices_html(choices, picked_items, is_multiple));
                $(".list-choice-item > input[name='choice']").labelauty();
                $context.attr('toggle_flag', model);
            }else{
                var $search_choice_field = $context.find('#search_choice_item')
                if($context.attr('toggle_flag') != model) {
                    $context.find('.modal-title:first').text(title);
                    $search_choice_field.attr('placeholder', search_placeholder);
                    var confirm_choice_btn = document.getElementById("confirm_choice_btn");
                    confirm_choice_btn.onclick = function () {
                        return $.confirm_labelauty_in_modal_choice(model);
                    }
                    $context.attr('toggle_flag', model);
                }
                $context.find('.modal-body:first').html(generate_choices_html(choices, picked_items, is_multiple));
                $(".list-choice-item > input[name='choice']").labelauty();
                show_search_item($search_choice_field.val());
            }
            $context.modal('show');
        },
        confirm_labelauty_in_modal_choice:function(model) {
            var $target_options = $("#id_"+model).find("option");
            var show_text = "";
            $('.modal-body').find("input[name='choice']").each(function(){
                var choice = $(this);
                if(show_text.length<30 && choice.prop('checked')){
                    if(show_text!="")show_text+=","
                    show_text += choice.next().children(".labelauty-unchecked").text()
                    if(show_text.length >=30)show_text+="..."
                }
                for(var i=0; i < $target_options.length; i++){
                    var option = $($target_options[i]);
                    if(option.val() == choice.val()){
                        if(choice.prop('checked'))option.prop('selected',true);
                        else option.prop('selected',false);
                        break;
                    }
                }
            });
            $("#extend_id_"+model).val(show_text);
        },
    //For add multiple text_field widget
        use_add_multi_in_modal:function(title, cols, target_id){
            var $context = $('#add_multi_modal');
            if($context.length==0){
                $context=init_add_multi_text_field(title, cols, target_id);
            }else{
                if($context.attr('toggle_flag')!=target_id){
                    var $tbody = $context.find("tbody");
                    $tbody.html(generate_multi_tbody_html(target_id, cols));
                    document.getElementById("add-item-btn").onclick = function(){
                        $tbody.append("<tr>"+generate_multi_field_html(cols)+"</tr>")
                    }
                    $context.attr('toggle_flag', target_id);
                }
            }
            $context.modal('show');
        }
    });
    function hereDoc(func) {
        var long_str = func.toString().replace(/(^[^\/]+\/\*!?\s?)|(\*\/[^\/]+$)/g, '');
        for(var i=1; i < arguments.length; i++){
            long_str=long_str.replace(eval("/\\\{"+(i-1)+"\\\}/g"), arguments[i]);
        }
        return long_str;
    }
    function generate_choices_html(choices, picked_items, is_multiple){
        var html = "<div class='list-choices_container'>";
        choices.forEach(function(choice){
            var value = choice[0], name = choice[1];
            html += "<div class='list-choice-item'>";
            html += "<input type='"+(is_multiple?"checkbox":"radio")+"' name='choice' value='" + value +"' data-labelauty='"+name+"' "+(picked_items.indexOf(value)==-1?"":"checked")+">";
            html += "</div>";
        })
        html += "</div>"
        return html
    }
    function generate_multi_field_html(cols, value){
        var body_col_html = "";
        var is_empty = value === void 0||$.isEmptyObject(value);
        for(var head_col in cols){
            var body_col = cols[head_col];
            var choices = body_col["choices"];
            if(choices instanceof Array){
                var option_html = "";
                choices.forEach(function(item){
                    if(is_empty||item[0]!=value[head_col]){
                        option_html += "<option value='"+item[0]+"'>"+item[1]+"</option>";
                    }else{
                        option_html += "<option value='"+item[0]+"' selected='selected'>"+item[1]+"</option>";
                    }
                });
                body_col_html += hereDoc(function () {
                    /*
                     <td class='col-sm-1'>
                     <select class="form-control" fake-name="{0}">
                     {1}
                     </select>
                     </td>
                     */
                }, head_col, option_html);
            }else{
                body_col_html += hereDoc(function () {
                    /*
                     <td class="col-sm-1"><input type="{1}" class="form-control" fake-name="{0}" placeholder="在此输入{3}" value="{2}"></td>
                     */
                }, head_col, body_col['type'], is_empty ? body_col['default']:value[head_col], body_col['label']||"");
            }
        }
        if(body_col!=""){
            body_col_html += hereDoc(function () {
                /*
                 <td class="col-sm-3"><button class="btn btn-danger btn-remove" onclick="javascript:(function($$){$$.parent().parent().remove();}($(this)))">撤销</button></td>
                */
            })
        }
        return body_col_html;
    }
    function generate_multi_tbody_html(target_id, cols){
        var tbody_html="", head_col_html="";
        var $target = $("#"+target_id);
        if($target.length == 0)return tbody_html;
        var values = $target.val();
        if(typeof values === "string" && values.length > 2){
            values = JSON.parse(values);
        }
        for(var head_col in cols){
            head_col_html += hereDoc(function () {
                /*
                <th class="col-sm-1">{0}</th>
                */
            },cols[head_col]["label"] || head_col);
        }
        tbody_html += ("<tr>"+head_col_html+"</tr>");
        if(!(values instanceof Array)){
            values=[{}];
        }
        values.forEach(function(value){
            tbody_html += ("<tr>"+generate_multi_field_html(cols, value)+"</tr>");
        });
        return tbody_html;
    }
    function init_modal_context(title, model, search_placeholder, body_content) {
        $('.main_container:first').append(hereDoc(function() {
            /*
             <div class='modal fade' tabindex='-1' role='dialog' aria-hidden='true' id="select_items_modal" data-keyboard="false" data-backdrop="static" toggle_flag="{1}">
             <div class='modal-dialog'>
             <div class='modal-content'>
             <div class='modal-header modal-header-default'>
             <button type='button' class='close' data-dismiss='modal'><span aria-hidden='true'>&times;</span><span class='sr-only'>关闭</span></button>
             <h4 class='modal-title'>{0}</h4>
             </div>
             <input type="text" id="search_choice_item" class="form-control" placeholder="{2}">
             <form class="navbar-form">
             <div class="modal-body">
             {3}
             </div>
             <div class="modal-footer">
             <button type="button" class="btn btn-primary" data-dismiss="modal" id="confirm_choice_btn" onclick="$.confirm_labelauty_in_modal_choice('{1}')">确认</button>
             <button type="button" class="btn btn-danger" data-dismiss="modal">取消</button>
             </div>
             </form>
             </div>
             </div>
             </div>
             <script>
             $('#search_choice_item').search_labelauty_choices();
             </script>
             */
        },title, model, search_placeholder, body_content));
        return $('#select_items_modal');
    }
    function show_search_item(search_info) {
        var items = $("#select_items_modal").find("input[name='choice']");
        items.each(function () {
            var item=$(this);
            var _scname = item.next().children(".labelauty-unchecked").text()
            if(_scname.split(search_info).length>1){
                item.parent(".list-choice-item").css({"display":"block"})
            }
            else {
                item.parent(".list-choice-item").css({"display":"none"})
            }
        })
    }
    function init_add_multi_text_field(title, cols, target_id) {
        $('.main_container:first').append(hereDoc(function() {
            /*
             <div class='modal fade' tabindex='-1' role='dialog' aria-hidden='true' id="add_multi_modal" data-keyboard="false" data-backdrop="static" toggle_flag="{0}">
             <div class='modal-dialog'>
             <div class='modal-content'>
             <div class='modal-header modal-header-default'>
             <button type='button' class='close' data-dismiss='modal'><span aria-hidden='true'>&times;</span><span class='sr-only'>关闭</span></button>
             <h4 class='modal-title'>{1}</h4>
             </div>
             <form class="navbar-form">
             <div class="modal-body">
             <table>
             <tbody>
             {2}
             </tbody>
             </table>
             </div>
             <div class="modal-footer">
             <button type="button" id="add-item-btn" style="margin-right: 3rem" class="btn btn-primary">新增条目</button>
             <button type="button" id="confirm-item-btn" class="btn btn-primary" data-dismiss="modal">确认</button>
             <button type="button" class="btn btn-danger" data-dismiss="modal">取消</button>
             </div>
             </form>
             </div>
             </div>
             </div>
             */
        }, target_id, title, generate_multi_tbody_html(target_id, cols)));
        var $tbody = $("#add_multi_modal").find('tbody');
        document.getElementById("add-item-btn").onclick=function(){
            $tbody.append("<tr>"+generate_multi_field_html(cols)+"</tr>")
        }
        $("#confirm-item-btn").on('click', function () {
            var send_list=[]
            $("#add_multi_modal").find("tr").each(function () {
                var send_obj = {}
                $(this).find("td").children().not("button").each(function(){
                    var $self = $(this);
                    send_obj[$self.attr('fake-name')] = $self.val();
                })
                if(!$.isEmptyObject(send_obj)){
                    send_list.push(send_obj);
                }
            });
            $("#"+target_id).val(send_list.length==0 ? void 0:JSON.stringify(send_list));
        })
        return $('#add_multi_modal');
    }
}(jQuery));