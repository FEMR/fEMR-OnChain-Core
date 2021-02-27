let day = $("#date_filter_day");
let start = $("#date_filter_start");
let end = $("#date_filter_end");
let select = $("#filter_list");
let apply = $("filter_apply_button");

function check_dates() {
  let good = true;
  if (select.val() == "4") {
    if (day.val() == "") {
        $('[data-toggle="popover"]').popover('enable');
        day.popover('show');
        $('[data-toggle="popover"]').popover('disable');
        good = false;
    }
  } else if (select.val() == "5") {
    if (start.val() == "") {
        $('[data-toggle="popover"]').popover('enable');
        start.popover('show');
        $('[data-toggle="popover"]').popover('disable');
        good = false;
    }
    if (end.val() == "") {
        $('[data-toggle="popover"]').popover('enable');
        end.popover('show');
        $('[data-toggle="popover"]').popover('disable');
        good = false;
    }
  }
  return good;
}