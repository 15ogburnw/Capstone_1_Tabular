const $sidebarCollapseBtn = $(".sidebar-collapse-btn");

$sidebarCollapseBtn.on("click", toggleSidebarCollapse);

function toggleSidebarCollapse(e) {
  if ($(this).attr("data-hidden") === "true") {
    $(".hide-container").attr("hidden", false);
    // for (let item of $navbarListItems) {
    //   item.show();
    // }
    $(".navbar-collapse-btn").attr("hidden", true);
    $("#panel-title").attr("hidden", true);
    $(this).attr("data-hidden", "false");
  } else {
    $(".hide-container").attr("hidden", true);
    $(this).attr("data-hidden", "true");
    $(".navbar-collapse-btn").attr("hidden", false);
    $("#panel-title").attr("hidden", false);
  }
}
