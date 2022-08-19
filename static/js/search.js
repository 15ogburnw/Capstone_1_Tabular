$(document).ready(function () {
  const $searchForm = $("#search-form");
  const $searchBtn = $("#search-button");
  const $searchInput = $("#search-input");
  const $resultsList = $("#results-list");

  //  When the user clicks on a 'search by' tab, clear the results and input contents, and change
  // the placeholder of the input accordingly

  $(".nav-tabs").on("click", ".nav-link.search", function (e) {
    $resultsList.empty();
    $searchInput.val("");
    const $tabType = $(this).attr("data-search");

    if ($tabType === "users") {
      $searchInput.attr("placeholder", "Search Users by Username");
    } else if ($tabType === "songs") {
      $searchInput.attr("placeholder", "Search Songs by Artist or Song Title");
    }
  });

  // submits the search query when the button is pressed

  $searchBtn.on("click", (e) => {
    $searchForm.submit();
  });

  // event listener for search submission

  $searchForm.on("submit", handleSubmit);

  // handles search submission

  function handleSubmit(e) {
    // prevent page refresh, clear input and search area
    e.preventDefault();
    $resultsList.empty();
    const query = $searchInput.val();
    const $searchType = $("a.search.active").attr("data-search");

    // If searching songs, call the function to query songs
    if ($searchType === "songs") {
      querySongs(query);
    }
    // if searching users, call the function to query users
    else if ($searchType === "users") {
      queryUsers(query);
    }
    $searchInput.val("");
  }

  // Query songs from the songsterr api using the search term submitted
  async function querySongs(query) {
    const response = await axios.get(
      `https://www.songsterr.com/a/ra/songs.json?pattern=${query}`
    );
    // call function to display results

    showSongResults(response.data);
  }

  // get HTML for each song in the results object and append them to the page
  async function showSongResults(songs) {
    let html;
    // get all liked songs
    const likes = await getLikedSongs();

    // Display a message if no songs are returned
    if (songs.length < 1) {
      $resultsList.append(
        $("<h4>No songs found! Please try another search term.</h4>")
      );
    }

    //Check if the song is present in the user's likes and get the HTML accordingly
    for (let song of songs) {
      if (likes.includes(song.id)) {
        html = getSongHTML(song, true);
      } else {
        html = getSongHTML(song, false);
      }

      $resultsList.append(html);
    }
  }

  // Get HTML elements to display for each song
  function getSongHTML(song, isLiked) {
    const $newLI = $("<li>");
    const $tabLink = $("<a>");

    // object with song info to store in HTML
    const songInfo = {
      id: song.id,
      title: song.title,
      artist: song.artist.name,
      tab_url: `https://www.songsterr.com/a/wa/song?id=${song.id}`,
    };

    $tabLink.attr("href", songInfo.tab_url);
    $tabLink.append(`${song.title} by ${song.artist.name}`);
    $newLI.append($tabLink);

    // If song is liked, include an 'Unlike' button; if song is not liked, include a 'Like' button
    if (!isLiked) {
      const $like = $("<a href='#'>").append("Like");
      $like
        .attr("data-song-info", JSON.stringify(songInfo))
        .attr("data-is-liked", false)
        .addClass("like");
      const html = $newLI.append("<br>").append($like);
      return html;
    } else {
      const $unlike = $("<a href='#'>").append("Unlike");
      $unlike
        .attr("data-song-info", JSON.stringify(songInfo))
        .attr("data-is-liked", true)
        .addClass("like");
      const html = $newLI.append("<br>").append($unlike);
      return html;
    }
  }

  // Get all liked songs from the database
  async function getLikedSongs() {
    resp = await axios.get("/api/likes");
    return resp.data;
  }

  //handle clicks on the Like/Unlike buttons
  $resultsList.on("click", ".like", toggleLike);

  //Toggle a song from a user's likes by sending a post request to the database
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

  //Get a list of users from the database using a search query
  async function queryUsers(query) {
    const resp = await axios.get("http://localhost:5000/api/users", {
      params: { query: query },
    });

    showUserResults(resp.data);
  }

  function showUserResults(users) {
    let html;

    // Display a message if no users are returned
    if (users.length < 1) {
      $resultsList.append(
        $("<h4>No users found! Please try another search term.</h4>")
      );
    }

    //Get the HTML for each user and append it to the results section
    for (let user of users) {
      user = JSON.parse(user);
      console.log(user);
      html = getUserHTML(user);
      $resultsList.append(html);
    }
  }

  function getUserHTML(user) {
    const $userLink = $(
      `<a href="/users/${user.id}/profile">${user.username}</a>`
    );
    return $("<li>").append($userLink);
  }
});
