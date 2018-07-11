/**
 * Created by weiyz18939 on 2018/7/11.
 */

$(document).ready(function(){

    $('#toggle').click(function(event){
        event.preventDefault();
        var currentShowWidth = $('#showWidthInput').val();
        var currentIsContexted = $('#isContextedCheck').val().trim() === 'true';
        var paramForm = '<div class="form-group">' +
            '<label class="control-label" for="showWidthFormInput">展示宽度</label><input type="number" class="form-control" id="showWidthFormInput" value="'+currentShowWidth+'" /></div><div class="form-group">' +
            '<label class="control-label" for="isContextedFormCheck">是否只显示不同部分<input id="isContextedFormCheck" type="checkbox" class="form-control"'+ (currentIsContexted ? ' checked': '') +' /></label>' +
            '<div><button class="btn btn-xs btn-success" id="saveParam">保存</button></div>' +
        '</div>';
        $(this).popover({
            html: true,
            content: paramForm,
            placement: 'bottom'
        }).popover('show');
        $('#isContextedFormCheck').bootstrapSwitch({
            size: 'mini',
            onText: '是',
            offText: '否'
        });
    });

    $('body').on('click','#saveParam',function(event){
        var newWidth = $('#showWidthFormInput').val();
        var newIsContexted = $('#isContextedFormCheck').prop('checked').toString();
        $('#showWidthInput').val(newWidth);
        $('#isContextedCheck').val(newIsContexted);
        $('#toggle').popover('hide');
    });

    // 点击编辑/保存按钮
    $('.edit-save-filename').click(function(event){
        event.preventDefault();
        var tgtInput = $(this).parent().prev();
        $(this).text($(tgtInput).prop('readonly') ? '保存' : '编辑');
        $(tgtInput).prop('readonly',!$(tgtInput).prop('readonly'));
    });

    // 实时校验输入是否是合法的txt文件名
    $('#leftFilename,#rightFilename').keyup(function(event){
        //event.preventDefault();
        var raw = $(this).val();
        var patt = /^.+\.txt$/;
        if (!patt.test(raw)){
            layer.closeAll();
            layer.tips('请输入.txt结尾的文件名',$(this));
        }
        else{
            layer.closeAll();
        }
    });

    // 点击提交按钮
    function checkLength(str,n){
        return str.split('\n').length <= n;
    }
    $('#submit').click(function(event){
        event.preventDefault();
        var leftContent = $('#leftText').val();
        var rightContent = $('#rightText').val();
        var showWidth = $('#showWidthInput').val();
        var isContexted = $('#isContextedCheck').val() === 'true';
        var lim = 10000;
        //var lim = 1;
        if (!checkLength(leftContent,lim)){
            layer.tips('最多支持处理'+lim+'行内容',$('#leftText'));
        }
        else if (!checkLength(rightContent,lim)){
            layer.tips('最多支持处理'+lim+'行内容',$('#rightText'));
        }
        else{
            var leftFilename = $('#leftFilename').val();
            var rightFilename = $('#rightFilename').val();
            $.ajax({
                url: location.pathname,
                type: 'post',
                dataType: 'json',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({
                    ln: leftFilename,
                    rn: rightFilename,
                    lc: leftContent,
                    rc: rightContent,
                    sw: showWidth,
                    ic: isContexted
                }),
                error: function(xml,err,exc){
                    try{
                        layer.alert('发生错误: ' + JSON.parse(xml.responseText).errmsg,{icon: 2});
                    }
                    catch (e){
                        layer.alert('后端发生错误，请查看控制台');
                    }
                }
            })
        }
    });
});