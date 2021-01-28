function check_filter() {
    console.log('Firing event.');
    if ($('#filter_list').val() == "1") {
        $('#date_filter_day').css("visibility", "hidden");
        $('#date_filter_day').css("display", "none");
        $('#date_filter_start').css("visibility", "hidden");
        $('#date_filter_start').css("display", "none");
        $('#date_filter_end').css("visibility", "hidden");
        $('#date_filter_end').css("display", "none");
    } else if ($('#filter_list').val() == "2") {
        $('#date_filter_day').css("visibility", "hidden");
        $('#date_filter_day').css("display", "none");
        $('#date_filter_start').css("visibility", "hidden");
        $('#date_filter_start').css("display", "none");
        $('#date_filter_end').css("visibility", "hidden");
        $('#date_filter_end').css("display", "none");
    } else if ($('#filter_list').val() == "3") {
        $('#date_filter_day').css("visibility", "hidden");
        $('#date_filter_day').css("display", "none");
        $('#date_filter_start').css("visibility", "hidden");
        $('#date_filter_start').css("display", "none");
        $('#date_filter_end').css("visibility", "hidden");
        $('#date_filter_end').css("display", "none");
    } else if ($('#filter_list').val() == "4") {
        $('#date_filter_day').css("visibility", "visible");
        $('#date_filter_day').css("display", "block");
        $('#date_filter_start').css("visibility", "hidden");
        $('#date_filter_start').css("display", "none");
        $('#date_filter_end').css("visibility", "hidden");
        $('#date_filter_end').css("display", "none");
    } else if ($('#filter_list').val() == "5") {
        $('#date_filter_day').css("visibility", "hidden");
        $('#date_filter_day').css("display", "none");
        $('#date_filter_start').css("visibility", "visible");
        $('#date_filter_start').css("display", "block");
        $('#date_filter_end').css("visibility", "visible");
        $('#date_filter_end').css("display", "block");
    } else {
        $('#date_filter_day').css("visibility", "hidden");
        $('#date_filter_day').css("display", "none");
        $('#date_filter_start').css("visibility", "hidden");
        $('#date_filter_start').css("display", "none");
        $('#date_filter_end').css("visibility", "hidden");
        $('#date_filter_end').css("display", "none");
    }
}

$('#filter_list').on('change', check_filter);