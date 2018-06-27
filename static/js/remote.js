/**
 * Created by weiyz18939 on 2017/10/20.
 */

$(document).ready(function () {

    //输入IP和端口后先校验IP能否接通
    $('.ip-input,.port-input').blur(function(event){
        var otherX = $(this).parent().parent().find('input').not(this);
        var ip,port,otherY;
        if ($(this).hasClass('ip-input')){
            otherY = $('.ip-input').not(this);
            ip = $(this).val();
            port = $(otherX).val();
        }
        else{
            otherY = $('.port-input').not(this);
            port = $(this).val();
            ip = $(otherX).val();
        }
        if (ip == '' || port == ''){
            // IP或端口为空时无法检测
            return;
        }
        if ($('#ipInputA').val() == $('#ipInputB').val() && $('#portInputA').val() == $('#portInputB').val()){
            // 两个IP一样，需要提醒
            layer.alert('请注意，输入的两个套接字一样！',{icon: 7});
        }
        $(this).next('img').show();
        var tinput = this;
        $.ajax({
            type: 'get',
            url: '/remote/help',
            dataType: 'json',
            data: {
                ope: 'checkIp',
                host: ip,
                port: port
            },
            success: function(data){
                $(tinput).next('img').hide();
                if (data.code != 200){
                    layer.tips('无法连通' + ip + '的' + port + '端口',tinput);
                }
                else{
                    layer.tips('可以连通',tinput);
                }
            }
        });
    });

    //输入目录后检查目录是否存在
    $('.path-input').blur(function (event){
        var tinput = $(this);
        var rootDiv = $(this).parent().parent();
        var ip = $(rootDiv).find('.ip-input').val();
        var port = $(rootDiv).find('.port-input').val();
        var user = $(rootDiv).find('.user-input').val();
        var psw = $(rootDiv).find('.psw-input').val();
        var path = $(tinput).val();
        if (path == ''){
            return;
        }
        if (ip == '' || port == '' || user == '' || psw == ''){
            layer.tips('请填写完整其他信息后再填写路径',tinput);
            return;
        }
        $(tinput).next('img').show();
        $.ajax({
            type: 'get',
            url: '/remote/help',
            data: {
                ope: 'checkDir',
                host: ip,
                port: port,
                u: user,
                p: psw,
                dir: path
            },
            dataType: 'json',
            success: function(data){
                $(tinput).next('img').hide();
                if (data.code != 200){
                    layer.tips('目录校验失败:' + data.msg,tinput);
                }
                else{
                    layer.tips('目录校验成功',tinput);
                }
            }
        });
    });

    //目录部分提交
    $('.download-btn').click(function(event){
        var submit = $(this);
        var rootDiv = $(this).parent().parent();
        var ip = $(rootDiv).find('.ip-input').val();
        var port = $(rootDiv).find('.port-input').val();
        var user = $(rootDiv).find('.user-input').val();
        var psw = $(rootDiv).find('.psw-input').val();
        var path = $(rootDiv).find('.path-input').val();
        if (ip=='' || port=='' || user == '' || psw == '' || path == ''){
            layer.alert('参数不能为空',{icon: 2});
            return;
        }
        $(submit).prop('disabled','disabled');
        layer.tips('开始下载...',submit,{time: 99999});
        $.ajax({
            type: 'post',
            url: '/remote/download',
            dataType: 'json',
            data: {
                host: ip,
                port: port,
                u: user,
                p: psw,
                dir: path
            },
            success: function(data){
                if (data.code != 200){
                    layer.alert('error:' + data.msg,{icon: 5});
                }
                else{
                    processQuery(data.id,function(process){
                        layer.tips(process,submit,{time: 99999,anim: -1});
                    });
                }
            }
        });
    });
});

function processQuery(target,show){
    $.ajax({
        type : 'get',
        url : '/remote/help/pq',
        data : {t:target},
        dataType : 'json',
        success : function(data){
            if (data.pr.indexOf('EFF') != 0 && data.pr != '__Done__'){
                show(data.pr);
                processQuery(target,show);
            }
            else if (data.pr.indexOf('EFF') == 0){
                if (data.pr.length > 3){
                    show(data.pr.substr(4));
                }
                else{
                    show('Done!');
                }
                processQuery('__EFF__'+target,show);
            }
        }
    });
}


//点击提交按钮，整体提交对比目录请求
$('#submitAll').click(function(event){
    var aIp = $('#ipInputA').val();
    var bIp = $('#ipInputB').val();
    var aDir = $('#pathInputA').val();
    var bDir = $('#pathInputB').val();
    if (aIp == '' || bIp == '' || aDir == '' || bDir == ''){
        return;
    }
    function basename(path){
        inodes = path.split(/\/|\\/);
        return inodes[inodes.length - 1];
    }
    var aBase = basename(aDir);
    var bBase = basename(bDir);
    $.ajax({
        type : 'post',
        url : '/res',
        data : {da:aBase+'@@'+aIp,db:bBase+'@@'+bIp},
        dataType : 'html',
        success : function(data){
            $('body').html(data);
        }
    })


});