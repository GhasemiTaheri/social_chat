$(".menu a i").on("click", function () {
    $(".menu a i").removeClass("active");
    $(this).addClass("active")
});
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});
$(document).ready(function () {
    $(".filterDiscussions").not(".all").hide("3000");
    $(".filterDiscussionsBtn").click(function () {
        var t = $(this).attr("data-filter");
        $(".filterDiscussions").not("." + t).hide("3000");
        $(".filterDiscussions").filter("." + t).show("3000")
    })
});

$(".back").click(function () {
    $("#call" + $(this).attr("name")).hide();
    $("#chat" + $(this).attr("name")).removeAttr("style")
});
$(".connect").click(function () {
    $("#chat" + $(this).attr("name")).hide();
    $("#call" + $(this).attr("name")).show()
});