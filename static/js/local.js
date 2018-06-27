/**
 * Created by weiyz18939 on 2017/10/18.
 */

$(document).ready(function(){
    //$(document).ajaxStart(function(){
    //    $('.mask').show();
    //}).ajaxStop(function(){
    //    $('.mask').hide();
    //});

    // 点选其他时给出输入框
    $('input[type=radio]:not(\'.other-option\')').change(function(event){
        $(this).parents('tbody').find('.other-input').hide();
    });
    $('.other-option').click(function(event){
        $(this).parents('tbody').find('.other-input').show();
    });

    // 反斜杠不合规输入提醒
    $('.other-input').blur(function(event){
        event.preventDefault();
        var _path = $(this).val();
        if (_path.indexOf('\\\\') != -1){
            layer.tips('路径中反斜杠写一个就行，如C:\\Users\\xxx',this);
            var before = $(this).val();
            $(this).val(before.replace(/\\\\/g,'\\'));
        }
    });

    $('a#submit').unbind('click').click(function(event){
        event.preventDefault();
        var leftDir,rightDir;
        var leftSDFlag = false;
        var rightSDFlag = false;

        var _left = $('input[name=lst-a-option]:checked').val();
        if (_left == '__OTHER__') {
            leftDir = $('.lst-a-option.other-input').val().replace(/\\/g,'/');
            leftSDFlag = true;
        }
        else{
            leftDir = _left;
        }

        var _right = $('input[name=lst-b-option]:checked').val();
        if (_right == '__OTHER__'){
            rightDir = $('.lst-b-option.other-input').val().replace(/\\/g,'/');
            rightSDFlag = true;
        }
        else{
            rightDir = _right;
        }

        if (!leftDir || !rightDir){
            layer.alert('未选择目录！');
            return;
        }
        if (leftDir == rightDir){
            layer.alert('所选两者为相同目录');
            return;
        }
        var loading = layer.load(1,{shade:[0.3]});
        $.ajax({
            type : 'post',
            data : {
                da:leftDir,
                asdf: leftSDFlag,
                db:rightDir,
                bsdf: rightSDFlag
            },
            url : '/res',
            dataType : 'html',
            success : function(data){
                //var originSize = $('html').css('font-size');
                $('body').html(data);
            },
            error: function(xml,err,exc){
                layer.alert(JSON.parse(xml.responseText).msg,{icon:2});
            },
            complete: function(){
                layer.close(loading);
            }
        })
    });
});