$(document).ready(function () {
  const BASE_URL = "http://localhost:5000";
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

    const songInfo = $(this).attr("data-song-info");
    const isLiked = $(this).attr("data-is-liked");

    if (isLiked === "false") {
      const resp = await axios.post(`${BASE_URL}/users/likes`, {
        json: songInfo,
      });
      $(this).empty().append("Unlike").attr("data-is-liked", true);
    } else {
      const resp = await axios.post(`${BASE_URL}/users/likes`, {
        json: songInfo,
      });
      $(this).empty().append("Like").attr("data-is-liked", false);
    }
  }

  async function removeLike(e) {
    e.preventDefault();
    const songInfo = $(this).attr("data-song-info");

    const resp = await axios.post(`${BASE_URL}/users/likes`, {
      json: songInfo,
    });
    $(this).closest("li").remove();
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
