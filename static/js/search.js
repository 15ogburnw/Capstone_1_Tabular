$(document).ready(function () {
  const BASE_URL = window.location.protocol + "//" + window.location.host;
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
    // const $newLI = $("<li>");
    // const $tabLink = $("<a>");
    // const $addToPlaylist = getModalBtn(song);

    // object with song info to store in HTML
    const songInfo = {
      id: song.id,
      title: song.title,
      artist: song.artist.name,
      tab_url: `https://www.songsterr.com/a/wa/song?id=${song.id}`,
    };

    // $tabLink.attr("href", songInfo.tab_url);
    // $tabLink.append(`${song.title} by ${song.artist.name}`);
    // $newLI.append($tabLink);

    const $song = $("<div>").addClass("row d-flex align-items-center");

    const html = $("<div>")
      .addClass("list-group-item rounded ml-3")
      .attr("style", "background-color:transparent")
      .append($song);

    const $dropdown = $("<div>")
      .addClass("btn-group dropleft mr-4")
      .append(
        $("<a>")
          .attr({
            class: "ml-3",
            type: "button",
            "data-toggle": "dropdown",
            "aria-haspopup": "true",
            "aria-expanded": "false",
          })
          .append($("<i>").addClass("fa-solid fa-bars"))
      )
      .append(
        $("<div>")
          .addClass("dropdown-menu")
          .append(
            $("<a>")
              .attr({
                class: "dropdown-item",
                type: "button",
                "data-song-info": JSON.stringify(songInfo),
                "data-toggle": "modal",
                "data-target": "#addToPlaylist",
              })
              .append("Add Song to Playlist")
          )
      );

    const $titleAndArtist = $("<div>")
      .addClass("col")
      .append(
        $("<p>")
          .addClass("my-0")
          .attr("style", "font-size:18px;")
          .append(
            $("<a>")
              .addClass("text-info")
              .attr("href", `https://www.songsterr.com/a/wa/song?id=${song.id}`)
              .append($("<b>").append(song.title))
          )
      )
      .append(
        $("<p>")
          .addClass("my-0")
          .append($("<em>").append(`by ${song.artist.name}`))
      );

    const $liked = $("<a>")
      .attr({
        class: "mr-2",
        href: "#",
        style: "font-size:18px;",
      })
      .append(
        $("<i>").attr({
          class: "fa-solid like fa-heart",
          "data-is-liked": "true",
          "data-song-info": JSON.stringify(songInfo),
          style: "color:red;cursor:pointer;",
        })
      );

    const $unliked = $("<a>")
      .attr({
        class: "mr-2",
        href: "#",
        style: "font-size:18px;",
      })
      .append(
        $("<i>").attr({
          class: "fa-regular like fa-heart",
          "data-is-liked": "false",
          "data-song-info": JSON.stringify(songInfo),
          style: "color:red;cursor:pointer;",
        })
      );

    // If song is liked, include an 'Unlike' button; if song is not liked, include a 'Like' button
    if (isLiked) {
      $song
        .append($titleAndArtist)
        .append(
          $("<div>")
            .addClass("col d-flex justify-content-end")
            .append($liked)
            .append($dropdown)
        );

      return html;
    } else {
      $song
        .append($titleAndArtist)
        .append(
          $("<div>")
            .addClass("col d-flex justify-content-end")
            .append($unliked)
            .append($dropdown)
        );

      return html;
    }
  }

  // Get all liked songs from the database
  async function getLikedSongs() {
    resp = await axios.get(`${BASE_URL}/api/likes`);
    return resp.data;
  }

  //handle clicks on the Like/Unlike buttons
  $resultsList.on("click", ".like", toggleLike);

  //Toggle a song from a user's likes by sending a post request to the database
  async function toggleLike(e) {
    e.preventDefault();
    const songInfo = $(this).attr("data-song-info");
    const isLiked = $(this).attr("data-is-liked");
    const $liked = $("<a>")
      .attr({
        class: "mr-2",
        href: "#",
        style: "font-size:18px;",
      })
      .append(
        $("<i>").attr({
          class: "fa-solid like fa-heart",
          "data-is-liked": "true",
          "data-song-info": JSON.stringify(songInfo),
          style: "color:red;cursor:pointer;",
        })
      );

    const $unliked = $("<a>")
      .attr({
        class: "mr-2",
        href: "#",
        style: "font-size:18px;",
      })
      .append(
        $("<i>").attr({
          class: "fa-regular like fa-heart",
          "data-is-liked": "false",
          "data-song-info": JSON.stringify(songInfo),
          style: "color:red;cursor:pointer;",
        })
      );

    if (isLiked === "false") {
      const resp = await axios.post(`${BASE_URL}/users/likes`, {
        json: songInfo,
      });
      $(this).parent().replaceWith($liked);
    } else {
      const resp = await axios.post(`${BASE_URL}/users/likes`, {
        json: songInfo,
      });
      $(this).parent().replaceWith($unliked);
    }
  }

  //Get a list of users from the database using a search query
  async function queryUsers(query) {
    const resp = await axios.get(`${BASE_URL}/api/users`, {
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
      html = getUserHTML(user);
      $resultsList.append(html);
    }
  }

  function getUserHTML(user) {
    const $userLink = $("<a>")
      .attr("href", `${BASE_URL}/users/${user.id}/profile`)
      .addClass("list-group-item ml-3 rounded list-group-item-action");

    const $profilePic = $("<div>")
      .addClass("col-2 d-flex align-items-center")
      .append(
        $("<img>")
          .attr("src", `/static/${user.profile_pic}`)
          .addClass("shadow-sm border")
          .attr("style", "width:50px;height:50px;border-radius:50px;")
      );

    const $nameAndUsername = $("<div>")
      .addClass("col my-auto")
      .append(
        $("<h6>")
          .addClass("text-info")
          .append(`${user.first_name} ${user.last_name}`)
      )
      .append($("<p>").append(`@${user.username}`));

    const $instrument = $("<div>").addClass(
      "col d-flex justify-content-start align-items-center"
    );
    if (user.instrument_name && user.instrument_icon) {
      $instrument.append(
        $("<p>")
          .append(
            $("<span>")
              .addClass("iconify mr-2")
              .attr("data-icon", user.instrument_icon)
              .attr("data-width", "30")
              .attr("data-height", "30")
          )
          .append($("<span>").append(`${user.instrument_name}`))
      );
    }

    const html = $userLink.append(
      $('<div class="row"></div>')
        .append($profilePic)
        .append($nameAndUsername)
        .append($instrument)
    );

    return html;
  }
});
