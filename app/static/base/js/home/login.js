function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 保存图片验证码编号
var imageCodeId = "";

function generateUUID() {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}

function generateImageCode() {
    // 形成图片验证码的后端地址，设置到页面中，让浏览器请求验证码图片
    // 1. 生成图片验证码的编号，两种方式
    // 1. 时间戳(可能问题，两人同时获取验证码)
    // 2. uuid：全局唯一标识符
    // 使用uuid作为唯一表示符
    imageCodeId = generateUUID();
    // 设置图片的url
    var url = "/image_codes/" + imageCodeId;

    $(".image-code img").attr("src", url);
}

$(document).ready(function () {
    generateImageCode();
    $("#mobile").focus(function () {
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function () {
        $("#image-code-err").hide();
    });
    $("#password").focus(function () {
        $("#password-err").hide();
    });


    $("#submit").submit(function (e) {
        // e.preventDefault();  // 阻止默认功能，即提交功能
        // 获取图片验证码
        var imageCode = $("#imagecode").val();
        conlse(imageCode)
        if (!imageCode) {
            $("#image-code-err span").html("请填写验证码！");
            $("#image-code-err").show();
            return;
        }
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
    });
})