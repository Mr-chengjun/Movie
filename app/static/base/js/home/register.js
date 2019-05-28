function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// $(document).ready(function() {
//     $("#mobile").focus(function(){
//         $("#mobile-err").hide();
//     });
//
//     $("#phonecode").focus(function(){
//         $("#phone-code-err").hide();
//     });
//     $("#password").focus(function(){
//         $("#password-err").hide();
//         $("#password2-err").hide();
//     });
//     $("#password2").focus(function(){
//         $("#password2-err").hide();
//     });
    // $(".form-register").submit(function(e){
    //     e.preventDefault();
    //     // mobile = $("#mobile").val();
    //     phoneCode = $("#phonecode").val();
    //     passwd = $("#password").val();
    //     passwd2 = $("#password2").val();
    //     // if (!mobile) {
    //     //     $("#mobile-err span").html("请填写正确的手机号！");
    //     //     $("#mobile-err").show();
    //     //     return;
    //     // }
    //     if (!phoneCode) {
    //         $("#phone-code-err span").html("请填写短信验证码！");
    //         $("#phone-code-err").show();
    //         return;
    //     }
    //     if (!passwd) {
    //         $("#password-err span").html("请填写密码!");
    //         $("#password-err").show();
    //         return;
    //     }
    //     if (passwd != passwd2) {
    //         $("#password2-err span").html("两次密码不一致!");
    //         $("#password2-err").show();
    //         return;
    //     }
    // });
// })