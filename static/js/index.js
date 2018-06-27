/**
 * Created by weiyz18939 on 2017/10/17.
 */

$(document).ready(function(){
    $('a#localCmp').mouseenter(function(event){
        $(this).after('<p>将待对比目录放在本工具同级目录下的Compare中</p>')
    }).mouseleave(function(event){
       $(this).next('p').first().remove();
    });

    $('a#remoteCmp').mouseenter(function(event){
       $(this).after('<p>输入两个IP和相关目录</p><p>将花费时间将目录下载到本地进行比较</p>')
    }).mouseleave(function(event){
        $(this).nextAll('p').remove();
    });
});