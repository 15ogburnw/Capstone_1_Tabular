$(document).ready(function () {
  const BASE_URL = window.location.protocol + "//" + window.location.host;
  const $songsList = $("#songs-list");
  const $likedSongs = $("#liked-songs");

  if ($likedSongs.length > 0) {
    $likedSongs.on("click", ".like", removeLike);
  }

  if ($songsList.length > 0) {
    $songsList.on("click", ".like", toggleLikeSong);
  }

  async function toggleLikeSong(e) {
    e.preventDefault();

    let songInfo = $(this).attr("data-song-info");
    let isLiked = $(this).attr("data-is-liked");

    const $likedIcon = $("<a>")
      .attr("href", "#")
      .attr("style", "font-size: 18px;")
      .addClass("mr-2")
      .append(
        $("<i>")
          .addClass("fa-solid like fa-heart")
          .attr("data-is-liked", "true")
          .attr("data-song-info", songInfo)
          .attr("style", "color:red;cursor:pointer;")
      );

    const $unlikedIcon = $("<a>")
      .attr("href", "#")
      .attr("style", "font-size: 18px;")
      .addClass("mr-2")
      .append(
        $("<i>")
          .addClass("fa-regular like fa-heart")
          .attr("data-is-liked", "false")
          .attr("data-song-info", songInfo)
          .attr("style", "color:red;cursor:pointer;")
      );

    if (isLiked === "false") {
      const resp = await axios.post(`${BASE_URL}/users/likes`, {
        json: songInfo,
      });
      const parent = $(this).parent().parent();
      $(this).parent().remove();
      parent.prepend($likedIcon);
    } else {
      const resp = await axios.post(`${BASE_URL}/users/likes`, {
        json: songInfo,
      });
      const parent = $(this).parent().parent();
      $(this).parent().remove();
      parent.prepend($unlikedIcon);
    }
  }

  async function removeLike(e) {
    e.preventDefault();
    const songInfo = $(this).attr("data-song-info");

    const resp = await axios.post(`${BASE_URL}/users/likes`, {
      json: songInfo,
    });
    $(this).closest("tr").remove();

    if ($likedSongs.find("tbody").children().length < 1) {
      $("<h5>")
        .append("You have no liked songs!")
        .append(
          $("<a>").attr("href", `${BASE_URL}/search`).append("Search for songs")
        )
        .insertBefore($("#liked-songs"));
      $("table").hide();
    }
  }

  $(".main-panel").on("click", "#playlist-liked", toggleLikePlaylist);
  $(".main-panel").on("click", "#playlist-unliked", toggleLikePlaylist);

  async function toggleLikePlaylist(e) {
    const playlistID = $(this).data("playlist-id");
    const $likedIcon = $(
      `<a href="#" class="h3 ml-3"><i class="fa-solid fa-heart" id="playlist-liked" data-playlist-id="${playlistID}" style="color:red;cursor:pointer;"></i></a>`
    );
    const $unlikedIcon = $(
      `<a href="#" class="h3 ml-3"><i class="fa-regular fa-heart" id="playlist-unliked" data-playlist-id="${playlistID}" style="color:red;cursor:pointer;"></i></a>`
    );

    if ($(this).attr("id") === "playlist-unliked") {
      const resp = await axios.post(`${BASE_URL}/playlists/${playlistID}/like`);
      $(this).parent().replaceWith($likedIcon);
    } else if ($(this).attr("id") === "playlist-liked") {
      const resp = await axios.post(
        `${BASE_URL}/playlists/${playlistID}/unlike`
      );
      $(this).parent().replaceWith($unlikedIcon);
    }
  }
});
