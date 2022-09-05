$(document).ready(function () {
  const BASE_URL = window.location.protocol + "//" + window.location.host;

  $("#friend-request").on("click", async function (e) {
    const userID = $(this).data("user-id");
    const resp = await axios.post(`${BASE_URL}/users/request-friend/${userID}`);

    $(this).remove();
    const $success = $("<div>")
      .addClass("alert alert-success")
      .append("Friend request sent!");
    $(".button-container").append($success);
  });

  $("#notifications").on("click", ".accept-friend", async function (e) {
    const userID = $(this).data("user-id");
    const $success = $("<div>")
      .addClass("alert alert-success alert-dismissable fade show")
      .append("Success! You are now friends!")
      .append(
        $("<button>")
          .addClass("close")
          .attr("data-dismiss", "alert")
          .append($("<span>").append("&times;"))
      );
    const resp = await axios.post(`${BASE_URL}/users/accept-request/${userID}`);

    $(this).closest("div.notification-shell").empty().append($success);
    let numNotifications = parseInt($("#notifications-badge").text());
    numNotifications--;

    if (numNotifications === 0) {
      $("#notifications-badge").remove();
    } else {
      $("#notifications-badge").text(numNotifications);
    }
  });

  $("#notifications").on("click", ".deny-friend", async function (e) {
    const userID = $(this).data("user-id");

    const resp = await axios.post(`${BASE_URL}/users/deny-request/${userID}`);

    $(this).closest("div.notification-shell").empty();

    let numNotifications = parseInt($("#notifications-badge").text());
    numNotifications--;

    if (numNotifications === 0) {
      $("#notifications-badge").remove();
    } else {
      $("#notifications-badge").text(numNotifications);
    }
  });
});
