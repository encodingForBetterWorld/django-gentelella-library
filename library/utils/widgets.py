# coding=utf-8
from django.forms import widgets


def render_labelauty(name, value, label, is_multiple=False, attrs=None, choices=()):
    widget_id = attrs.get('id')
    extend_screen_widget_id = 'extend_' + widget_id

    attrs['id'] = extend_screen_widget_id
    attrs['class'] = "form-control extend_screen_widget"
    attrs['onclick'] = u"$.use_labelauty_in_modal('在此选择{0}', '{1}', '模糊查询{0}', '{2}', {3})".format(label.decode("utf8"),
                                                                                                   name, widget_id,
                                                                                                   is_multiple and 1 or 0)
    attrs['readonly'] = True
    attrs['placeholder'] = '点击选择%s' % label
    extend_screen_widget = widgets.TextInput(attrs)
    htm = extend_screen_widget.render(None, None, attrs).replace("name=\"None\"", "")
    attrs.__delitem__('onclick')
    attrs.__delitem__('readonly')
    attrs.__delitem__('placeholder')

    attrs['id'] = widget_id
    attrs['class'] = "form-control screen_widget"
    if is_multiple:
        screen_widget = widgets.SelectMultiple(attrs, choices)
    else:
        screen_widget = widgets.Select(attrs, choices)
    htm += screen_widget.render(name, value, attrs)
    script = """
        <script>
            $(function(){
                var $target_options = $("#%s").find("option");
                var show_text = "";
                $target_options.each(function () {
                    var $option = $(this);
                    if(show_text.length<30 && $option.prop('selected')){
                        if(show_text!="")show_text+=","
                        show_text += $option.text()
                        if(show_text.length >=30)show_text+="..."
                    }
                });
                $("#%s").val(show_text);
            })
        </script>
    """ % (widget_id, extend_screen_widget_id)
    return htm + script


class LabelautySelect(widgets.Select):
    def render(self, name, value, attrs=None, choices=()):
        return render_labelauty(name, value, self.choices.field.label, False, attrs, self.choices)


class LabelautyMultipleSelect(widgets.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        return render_labelauty(name, value, self.choices.field.label, True, attrs, self.choices)


class GentelellaDatePicker(widgets.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        wid = attrs.get('id')
        attrs['class'] = "form-control has-feedback-left"
        attrs['aria-describedby'] = "input"+wid
        htm = super(GentelellaDatePicker, self).render(name, value, attrs, renderer)
        return htm + """
        <span class="fa fa-calendar-o form-control-feedback left" aria-hidden="true"></span>
        <span id="%s" class="sr-only">(success)</span>
        <script>
        $('#%s').daterangepicker({
            singleDatePicker: true,
            singleClasses: "picker_3",
            locale: {format: 'YYYY-MM-DD HH:mm:ss'}
        });
        </script>
        """ % ("input"+wid, wid)


