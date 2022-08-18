$(document).ready(function () {
  const $songsList = $(".songs-list");
  const $likedSongs = $(".liked-songs");

  if ($likedSongs.length > 0) {
    $likedSongs.on("click", ".like", removeLike);
  }

  if ($songsList.length > 0) {
    $songsList.on("click", ".like", toggleLike);
  }

  async function toggleLike(e) {
    e.preventDefault();
    const songInfo = $(this).attr("data-song-info");
    const isLiked = $(this).attr("data-is-liked");

    if (isLiked === "false") {
      const resp = await axios.post("http://localhost:5000/users/likes", {
        json: songInfo,
      });
      $(this).empty().append("Unlike").attr("data-is-liked", true);
    } else {
      const resp = await axios.post("http://localhost:5000/users/likes", {
        json: songInfo,
      });
      $(this).empty().append("Like").attr("data-is-liked", false);
    }
  }

  async function removeLike(e) {
    e.preventDefault();
    const songInfo = $(this).attr("data-song-info");

    const resp = await axios.post("http://localhost:5000/users/likes", {
      json: songInfo,
    });
    $(this).parent().remove();
  }
});
