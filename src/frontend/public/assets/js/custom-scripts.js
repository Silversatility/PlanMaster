$("document").ready( function(){

    $(".upload-span").click(function () {
        $(".add-job-file-js").click();
    });

    $(".add-job-file-js").change(function () {
        $(".file-name-js").html($(this).val().replace(/.*[\/\\]/, ''));
    });

    $(".cb-ham-js").click(function () {
        $(".dropdown").toggleClass("is-active");
        $(this).toggleClass("open");
    });

});
