/**
 * Created by mavarick on 16/8/5.
 */


// 获取用户的整个分类
function updateTopic(username, topics_id, target_topic_id) {
    $.ajax({
        url: "/user/api/get_cate_topics/?username="+username+"&topic_id="+base_topic_id,
        dataType: "JSON",
        success: function (resp) {
            var data = resp['data'];
            var cate_info = buildCates(data, target_topic_id);
            $(topics_id).html(cate_info);
        }
    })
};

// 操作
function buildCates(cate_info, topic_id) {
    topic_options = "";

    var buildTopic = function (topic_info, level) {
        var id = topic_info.child_id;
        var name = topic_info.name;
        if (id == topic_id) {
            var op = "<option style='margin-left:" + 10 * level + "px;' value='" + id + "' selected='selected'>" + name + "</option>"
        } else {
            var op = "<option style='margin-left:" + 10 * level + "px;' value='" + id + "'>" + name + "</option>"
        }

        topic_options += op;
        var sub_topics = topic_info.sub;
        if (sub_topics) {
            for (var i = 0; i < sub_topics.length; i++) {
                var sub_topic = sub_topics[i];
                buildTopic(sub_topic, level + 1);
            }
        }
    };
    //topic_options += "<OPTGROUP label='" + name + "'>"
    buildTopic(cate_info, 0);

    return topic_options
}


$(function(){
    $('#uploadAvatarBtnLayout button').addClass('button-deep-color');

    $('#uploadAvatarInputFile').mouseover(function(){
        $('#uploadAvatarBtnLayout button').removeClass('button-deep-color').addClass('button-light-color');
    }).mouseout(function(){
        $('#uploadAvatarBtnLayout button').removeClass('button-light-color').addClass('button-deep-color');
    });

    $('#uploadAvatarCropSubmit').addClass('button-deep-color').mouseover(function(){
        $(this).removeClass('button-deep-color').addClass('button-light-color');
    }).mouseout(function(){
        $(this).removeClass('button-light-color').addClass('button-deep-color');
    });
});