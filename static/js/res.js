/**
 * Created by weiyz18939 on 2017/10/18.
 */

function togglePage(key) {
    $('div.show-res').hide();
    var text = $('div#' + key).show().text().trim();
    if (text == '') {
        $('button#return').before('<br><br>')
    }
    else {
        $('button#return').prevAll('br').each(function () {
            $(this).remove()
        });
    }
}

//function foldTree(node){
//    if ($(node).find('div.hitarea.collapsable-hitarea').length == 0){
//        $(node).click();
//    }
//    else{
//        foldTree($(node).find('div.hitarea.collapsable-hitarea').first());
//    }
//}

function getFullPath(file,side) {
    var filename = $(file).text();
    var nodes = [];
    $(file).parentsUntil('ul.filetree', 'li').each(function () {
        var node = $(this).find('span.folder').first().text();
        if (node) {
            nodes.push(node);
        }
    });
    nodes = nodes.slice(0,-1);
    console.log(nodes);
    nodes.push($(side == 'a' ? '#left_' : '#right_').text());
    nodes.reverse();
    nodes.push(filename);
    console.log(nodes.join('/'));
    return nodes.join('/');
}

$(document).ready(function () {
    $('ul#leftInfo').treeview();
    $('ul#rightInfo').treeview();
    $('ul#differInfo').treeview();
    //foldTree(firstNode);
    $('div.show-res').hide();
    $('button#return').before('<br><br>');

    //标签菜单设置部分
    $('a#left_').unbind('click').click(function () {
        togglePage('left');
    });
    $('a#right_').unbind('click').click(function () {
        togglePage('right');
    });
    $('a#differ_').unbind('click').click(function () {
        togglePage('differ');
    });

    //点击对比按钮事件设置
    //$('a.show-differ').click(function(){
        //var fullPath = getFullPath($(this));
        //console.log(fullPath);
        //alert('aaa');
        //console.log('aaa');
    //});

    //点击内容不同文件时查看对比
    $('div#differ span.file').click(function(event){
        var asdf = $('#lsdfInput').val() == 'True';
        var fullPatha = getFullPath(this,'a');
        var bsdf = $('#rsdfInput').val() == 'True';
        //var fullPathb = fullPatha.replace($('a#left_').text(),$('a#right_').text());
        var fullPathb = getFullPath(this,'b');


        var showWidth = $('input#showWidth').val();
        if (showWidth == ''){
            showWidth = '70';
        }
        var isContext = $('input#isContext').is(':checked');
        var isDetailed = $('input#isDetailed').is(':checked');
        $.ajax({
            type : 'post',
            url : '/filediffer',
            data : {
                fa:fullPatha,
                asdf:asdf,
                fb:fullPathb,
                bsdf: bsdf,
                sw:showWidth,
                isc:isContext,
                isd:isDetailed
            },
            dataType : 'json',
            success: function(data){
                if (data.code == '201'){
                    alert('该文件在两个目录下内容实质相同，但编码不同：左边文件编码是'+data.codeca+' 右边文件编码是'+data.codecb);
                }
                else if (data.code == '202'){
                    alert('该文件在两个目录下换行符不同，请保证文件在统一的Unix或Dos平台上编辑保存');
                }
                else if (data.code == '203'){
                    alert('两文件差别在于文件末尾的差了一个换行符');
                }
                else if(data.code == '400'){
                    alert('对比失败，发生错误：' + data.msg)
                }
            }
        });

    });

});